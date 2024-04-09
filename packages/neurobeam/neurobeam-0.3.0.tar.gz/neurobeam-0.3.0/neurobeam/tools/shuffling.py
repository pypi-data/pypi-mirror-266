from typing import Sequence
from random import shuffle, sample


def random_shuffle(sequence: Sequence) -> tuple:
    """
    Randomly shuffle a sequence.

    :param sequence: The sequence to shuffle.
    :returns: A tuple containing the shuffled sequence.
    """
    sequence = list(sequence)
    shuffle(sequence)
    return tuple(sequence)


def balanced_shuffle(sequence: Sequence) -> tuple:
    """
    Counter-balanced shuffling of some sequence

    :param sequence: The sequence to shuffle.
    :returns: A tuple containing the shuffled sequence.
    """
    sequence = list(sequence)
    length = len(sequence)
    unique_values = list(set(sequence))
    iters_per_value = [sequence.count(value) for value in unique_values]
    if not all((iters == iters_per_value[0] for iters in iters_per_value)):
        raise ValueError("The sequence is not balanced.")
    n_blocks = iters_per_value[0]
    block = unique_values
    blocks = [block for _ in range(n_blocks)]
    shuffled_sequence = []
    for _ in range(n_blocks):
        shuffle(block)
        shuffled_sequence.extend(block)
    return tuple(shuffled_sequence)
