from typing import List

from drums import BassDrum
from drums import HighHat
from drums import SnareDrum
from gui import GUI
from sequencer import Sequencer
from sequencer_gui_interface import SequencerGUIInterface


def true_at_indices(indices: List[int], length: int = 16) -> List[bool]:
    """
    Zero-indexed indices only please
    """
    if max(indices) > length:
        raise ValueError('indices cannot exceed list length')
    return [i in indices for i in range(length)]


if __name__ == '__main__':
    sequencer_gui_interface = SequencerGUIInterface()

    sequencer = Sequencer(
        pattern={
            BassDrum: true_at_indices([0, 8]),
            SnareDrum: true_at_indices([4, 12]),
            HighHat: [1, 1, 1, 0],
        },
        sequencer_gui_interface=sequencer_gui_interface,
        bpm=110,
    )
    gui = GUI(sequencer_gui_interface=sequencer_gui_interface)
