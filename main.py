from drums import BassDrum
from drums import HighHat
from drums import SnareDrum
from sequencer import Sequencer

sequencer = Sequencer(
    pattern={
        BassDrum: [True, True, False, True, False, True, False, False],
        SnareDrum: [False, False, True, False],
        HighHat: [False, True],
    },
    bpm=105,
)

sequencer.play()
