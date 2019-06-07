from typing import List

from drums import BassDrum
from drums import HighHat
from drums import SnareDrum
from sequencer import Sequencer


def true_at_indices(indices: List[int], length: int = 16) -> List[bool]:
    """
    Zero-indexed indices only please
    """
    if max(indices) > length:
        raise ValueError('indices cannot exceed list length')
    return [i in indices for i in range(length)]


if __name__ == '__main__':
    sequencer = Sequencer(
        pattern={
            BassDrum: true_at_indices([0, 2, 10, 15]),
            SnareDrum: true_at_indices([4, 7, 9, 12]),
            HighHat: [True],
        },
        bpm=200,
    )

    sequencer.play()
