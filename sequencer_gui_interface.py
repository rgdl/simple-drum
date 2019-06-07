from queue import Queue


class SequencerGUIInterface:
    """
    Maintains event queues so the sequence object and the GUI can intercommunicate.

    Just messages for sequencer. Think about how to handle messages from GUI to individual drums.
    """
    def __init__(self):
        self.sequencer_events_queue = Queue()
        self.gui_events_queue = Queue()