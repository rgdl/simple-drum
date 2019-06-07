from queue import Queue


class Event:
    def __init__(self, method: str, method_args: dict = {}):
        self.method = method
        self.method_args = method_args

    def __repr__(self):
        return f'({self.method}, {self.method_args})'


class SequencerEvent(Event):
    pass


class GUIEvent(Event):
    pass


class SequencerGUIInterface:
    """
    Maintains event queues so the sequence object and the GUI can intercommunicate.

    Just messages for sequencer. Think about how to handle messages from GUI to individual drums.

    Event consumers should look for events with the name set_* and automatically set that attribute value. This will
    save writing heaps of setter functions explicitly.
    """
    def __init__(self):
        self._sequencer_events_queue = Queue()
        self._gui_events_queue = Queue()

    def push_to_sequencer_events_queue(self, event: SequencerEvent) -> None:
        print(event)
        self._sequencer_events_queue.put(event)

    def push_to_gui_events_queue(self, event: GUIEvent) -> None:
        self._gui_events_queue.put(event)

    def get_from_sequencer_events_queue(self) -> SequencerEvent:
        return self._sequencer_events_queue.get()

    def get_from_gui_events_queue(self) -> GUIEvent:
        return self._gui_events_queue.get()
