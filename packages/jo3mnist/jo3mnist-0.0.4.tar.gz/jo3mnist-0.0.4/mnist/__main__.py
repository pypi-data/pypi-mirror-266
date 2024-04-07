#! /usr/bin/env python3
# vim:fenc=utf-8

from .deps import *
from .l0_regularization import *

# Hyperparameters
OPTS = argtoml.parse_args()
BATCH_SIZE = OPTS.batch_size
EPSILON = OPTS.epsilon
LEARNING_RATE = OPTS.learning_rate
MNIST_LOC = OPTS.mnist_loc
MODEL_PATH = OPTS.model_path
PRINT_EVERY = OPTS.print_every
STEPS = OPTS.steps

key = jax.random.PRNGKey(OPTS.seed)
key, subkey = jax.random.split(key)
e = sample_epsilon(subkey, (100,))
log_a = -1.0  # jnp.linspace(-1, 2, 100)
beta = 0.5
y = quantile_concrete(e, log_a, beta)
plt.scatter(e, y)


class CNN(eqx.Module):
    layers: list

    def __init__(self, key):
        key1, key2, key3, key4 = jax.random.split(key, 4)
        # Standard CNN setup: convolutional layer, followed by flattening,
        # with a small MLP on top.
        self.layers = [
            eqx.nn.Conv2d(1, 3, kernel_size=4, key=key1),
            eqx.nn.MaxPool2d(kernel_size=2),
            jnp.ravel,
            jax.nn.relu,
            L0Dense(1728, 512, key=key2),
            jax.nn.sigmoid,
            L0Dense(512, 64, key=key3),
            jax.nn.relu,
            L0Dense(64, 10, key=key4),
            jax.nn.log_softmax,
        ]

    def __call__(self, x: Float[Array, "1 28 28"], key) -> Float[Array, "10"]:
        for l, layer in enumerate(self.layers):
            if type(layer) == L0Dense:
                key, subkey = jax.random.split(key)
                e = sample_epsilon(subkey, x.shape)
                x = layer(x, e)
            else:
                x = layer(x)
        return x

    def regularization(self):
        reg = 0.0
        for l, layer in enumerate(self.layers):
            if type(layer) == L0Dense:
                reg -= layer.regularization() / 1000
        return reg


@eqx.filter_jit
def loss(
    model: CNN, x: Float[Array, "batch 1 28 28"], y: Int[Array, " batch"], key: Key
) -> Float[Array, ""]:
    # Our input has the shape (BATCH_SIZE, 1, 28, 28), but our model operations on
    # a single input input image of shape (1, 28, 28).
    #
    # Therefore, we have to use jax.vmap, which in this case maps our model over the
    # leading (batch) axis.
    key_0, key_1 = jax.random.split(key)
    pred_y = jax.vmap(model, (0, None))(x, key_0)
    ce = cross_entropy(y, pred_y, key_1)
    reg = model.regularization()
    return ce + jnp.log(reg) + ce * reg


def cross_entropy(
    y: Int[Array, " batch"], pred_y: Float[Array, "batch 10"], key: Key
) -> Float[Array, ""]:
    # y are the true targets, and should be integers 0-9.
    # pred_y are the log-softmax'd predictions.
    pred_y = jnp.take_along_axis(pred_y, jnp.expand_dims(y, 1), axis=1)
    return -jnp.mean(pred_y)


@eqx.filter_jit
def compute_accuracy(
    model: CNN,
    x: Float[Array, "batch 1 28 28"],
    y: Int[Array, " batch"],
    key: Key,
) -> Float[Array, ""]:
    """This function takes as input the current model
    and computes the average accuracy on a batch.
    """
    pred_y = jax.vmap(model, (0, None))(x, key)
    pred_y = jnp.argmax(pred_y, axis=1)
    return jnp.mean(y == pred_y)


def evaluate(model: CNN, testloader: DataLoader, key: Key):
    """This function evaluates the model on the test dataset,
    computing both the average loss and the average accuracy.
    """
    avg_loss = 0
    avg_acc = 0
    for x, y in testloader:
        x = x.numpy()
        y = y.numpy()
        # Note that all the JAX operations happen inside `loss` and `compute_accuracy`,
        # and both have JIT wrappers, so this is fast.
        key, key_l, key_a = jax.random.split(key, 3)
        avg_loss += loss(model, x, y, key_l)
        avg_acc += compute_accuracy(model, x, y, key_a)
    return avg_loss / len(testloader), avg_acc / len(testloader)

def weight_sparsity(key, layer):
    e = sample_epsilon(key, (layer.weight.shape[0],))
    z = quantile_concrete(e, layer.z_loc, layer.z_temp).clip(0, 1)
    return int((z == 0).sum())

def model_sparsity(key, model, percent=False):
    report = []
    for i, layer in enumerate(model.layers):
        if type(layer) != L0Dense:
            continue

        key, subkey = jax.random.split(key)
        n_zeros = weight_sparsity(subkey, layer)
        report.append({
            "number": i,
            "in_size": layer.weight.shape[0],
            "n_zeros": n_zeros
        })

    if not percent:
        return report

    percentage = []
    for layer_stats in report:
        percentage.append(layer_stats["n_zeros"] / layer_stats["in_size"])
    return percentage

def pretty_float_list(l):
    out = []
    for f in l:
        out.append(f"{f:.3f}")
    return "[" + " ".join(out) + "]"

def train(
    model: CNN,
    trainloader: DataLoader,
    testloader: DataLoader,
    optim: optax.GradientTransformation,
    steps: int,
    print_every: int,
    key: Key,
) -> CNN:
    # Just like earlier: It only makes sense to train the arrays in our model,
    # so filter out everything else.
    opt_state = optim.init(eqx.filter(model, eqx.is_array))

    # Always wrap everything -- computing gradients, running the optimiser, updating
    # the model -- into a single JIT region. This ensures things run as fast as
    # possible.
    @eqx.filter_jit
    def make_step(
        model: CNN,
        opt_state: PyTree,
        x: Float[Array, "batch 1 28 28"],
        y: Int[Array, " batch"],
        key: Key,
    ):
        loss_value, grads = eqx.filter_value_and_grad(loss)(model, x, y, key)
        updates, opt_state = optim.update(grads, opt_state, model)
        model = eqx.apply_updates(model, updates)
        return model, opt_state, loss_value

    # Loop over our training dataset as many times as we need.
    def infinite_trainloader():
        while True:
            yield from trainloader

    for step, (x, y) in zip(range(steps), infinite_trainloader()):
        # PyTorch dataloaders give PyTorch tensors by default,
        # so convert them to NumPy arrays.
        x = x.numpy()
        y = y.numpy()
        key, subkey = jax.random.split(key)
        model, opt_state, train_loss = make_step(model, opt_state, x, y, subkey)
        if (step % print_every) == 0 or (step == steps - 1):
            test_loss, test_accuracy = evaluate(model, testloader, subkey)
            sparsities = model_sparsity(subkey, model, percent=True)
            print(
                f"{step=},",
                f"train_loss={train_loss.item():.2f},",
                f"test_loss={test_loss.item():.2f},",
                f"test_accuracy={test_accuracy.item():.4f}",
                f"sparsity={pretty_float_list(sparsities)}"
            )
    return model

key, subkey = jax.random.split(key)
trainloader, testloader = mnist.load(MNIST_LOC, BATCH_SIZE)
model = CNN(subkey)
optim = optax.adamw(LEARNING_RATE)

key, subkey = jax.random.split(key)
model = train(model, trainloader, testloader, optim, steps=STEPS, print_every=PRINT_EVERY, key=subkey)
eqx.tree_serialise_leaves(MODEL_PATH, model)
