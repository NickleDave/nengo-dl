import re

from nengo.exceptions import SimulationError
import numpy as np
import tensorflow as tf


def sanitize_name(name):
    """Remove illegal tensorflow name characters from string."""

    if not isinstance(name, str):
        name = str(name)

    name = name.replace(" ", "_")
    name = name.replace(":", "_")

    valid_exp = re.compile("[A-Za-z0-9_.\\-/]")

    return "".join([c for c in name if valid_exp.match(c)])


def function_name(func, sanitize=True):
    name = getattr(func, "__name__", type(func).__name__)
    if sanitize:
        name = sanitize_name(name)

    return name


def align_func(func, output_shape, output_dtype):
    # make sure the output of function is of the shape and dtype we expect
    def aligned_func(*args):
        tmp = func(*args)
        if tmp is None:
            raise SimulationError(
                "Function %r returned None" % function_name(
                    func, sanitize=False))
        tmp = np.asarray(tmp, dtype=output_dtype.as_numpy_dtype)
        tmp = tmp.reshape(output_shape)
        return tmp

    return aligned_func


def print_op(input, message):
    def print_func(x):
        print(message, str(x))
        return x

    output = tf.py_func(print_func, [input], input.dtype)
    output.set_shape(input.get_shape())

    return output


def cast_dtype(dtype, target):
    if not isinstance(dtype, tf.DType):
        dtype = tf.as_dtype(dtype)

    # casts float dtypes to the target dtype, leaves others unchanged
    if dtype.is_floating:
        dtype = target

    return dtype