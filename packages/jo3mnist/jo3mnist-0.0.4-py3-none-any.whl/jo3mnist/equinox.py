#! /usr/bin/env python3
# vim:fenc=utf-8
from time import time
from typing import Callable, Optional

import jax
import jax.numpy as jnp
import optax
from jaxtyping import Array, Float, Int, Key, PyTree
from torch.utils.data import DataLoader

import equinox as eqx


def cross_entropy(
    y: Int[Array, " batch"], pred_y: Float[Array, "batch 10"], key: Key
) -> Float[Array, ""]:
    # y are the true targets, and should be integers 0-9.
    # pred_y are the log-softmax'd predictions.
    pred_y = jnp.take_along_axis(pred_y, jnp.expand_dims(y, 1), axis=1)
    return -jnp.mean(pred_y)


@eqx.filter_jit
def compute_accuracy(
    model: eqx.Module,
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


@eqx.filter_jit
def default_loss(
    model: eqx.Module,
    x: Float[Array, "batch 1 28 28"],
    y: Int[Array, " batch"],
    key: Key,
) -> Float[Array, ""]:
    # Our input has the shape (BATCH_SIZE, 1, 28, 28), but our model operations on
    # a single input input image of shape (1, 28, 28).
    #
    # Therefore, we have to use jax.vmap, which in this case maps our model over the
    # leading (batch) axis.
    key_0, key_1 = jax.random.split(key)

    pred_y = jax.vmap(model, (0, None))(x, key_0)

    return cross_entropy(y, pred_y, key_1)


def evaluate(model: eqx.Module, testloader: DataLoader, loss: Callable, key: Key):
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


def train(
    model: eqx.Module,
    trainloader: DataLoader,
    testloader: DataLoader,
    optim: optax.GradientTransformation,
    steps: int,
    key: Key,
    print_every: Optional[int] = None,
    loss: Callable = default_loss,
    model_to_str: Optional[Callable] = None,
) -> eqx.Module:
    # Just like earlier: It only makes sense to train the arrays in our model,
    # so filter out everything else.
    opt_state = optim.init(eqx.filter(model, eqx.is_array))
    loss = default_loss if loss is None else loss
    print_every = max(steps // 50, 1) if print_every is None else print_every

    # Always wrap everything -- computing gradients, running the optimiser, updating
    # the model -- into a single JIT region. This ensures things run as fast as
    # possible.
    @eqx.filter_jit
    def make_step(
        model: eqx.Module,
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

    t0 = time()
    for step, (x, y) in zip(range(steps), infinite_trainloader()):
        # PyTorch dataloaders give PyTorch tensors by default,
        # so convert them to NumPy arrays.
        x = x.numpy()
        y = y.numpy()
        key, subkey = jax.random.split(key)
        model, opt_state, train_loss = make_step(model, opt_state, x, y, subkey)
        if (step % print_every) == 0 or (step == steps - 1):
            t1 = time()
            test_loss, test_accuracy = evaluate(model, testloader, loss, subkey)
            print(
                f"{step=},",
                f"train_loss={train_loss.item():.2f},",
                f"test_loss={test_loss.item():.2f},",
                f"test_accuracy={test_accuracy.item():.4f}",
                f"step_time={(t1 - t0)/print_every:.3f}",
                model_to_str(model) if model_to_str is not None else "",
            )
            t0 = time()
    return model
