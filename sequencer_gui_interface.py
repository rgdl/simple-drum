from queue import Queue
import re
from threading import Thread
import time
from typing import Callable
from typing import Union


class Event:
    """
    `method` should be a method on the object that consumes the event
    Otherwise, it should be `set_*`, where the attribute `*` of the object will be set to method_args['*']
    """
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
        self._sequencer_events_queue.put(event)

    def push_to_gui_events_queue(self, event: GUIEvent) -> None:
        self._gui_events_queue.put(event)

    def get_from_sequencer_events_queue(self) -> Union[SequencerEvent, None]:
        if self._sequencer_events_queue.empty():
            return None
        return self._sequencer_events_queue.get()

    def get_from_gui_events_queue(self) -> Union[GUIEvent, None]:
        if self._gui_events_queue.empty():
            return None
        return self._gui_events_queue.get()


class ListenerThread(Thread):
    """
    Allows an object to poll queues for events
    """
    POLL_INTERVAL_SECONDS = 0.1

    def __init__(self, listener: Union['GUI', 'Sequencer'], getter_func: Callable):
        super().__init__()
        self.listener = listener
        self.getter_func = getter_func

    def run(self):
        while True:
            time.sleep(self.POLL_INTERVAL_SECONDS)
            event = self.getter_func()
            if event is None:
                continue
            getattr(self.listener, event.method)(**event.method_args)
