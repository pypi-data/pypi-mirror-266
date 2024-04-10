import time
from threading import Thread
from queue import Queue
from enum import Enum
from . import Messenger


class Lifecycle(Enum):
    INIT = 0
    REGISTER = 1
    START = 2
    RUN = 3
    STOP = 4


class Reactive:

    def __init__(self,
                 name=None,
                 subjects=[],
                 timeout=0.01):
        # Set Lifecycle stage
        self.lifecycle = Lifecycle.INIT

        # Set Reactive Name, default to class name
        self.name = name.lower() if name else self.__class__.__name__.lower()

        # Save subscribed subjects
        self.subjects = subjects

        # Default Status
        self.status = {}

        # Default Uptime
        self.run_time = 0
        self.stop_time = 0

        # Create Thread for Reactive
        self.thread = Thread(target=self.run, daemon=True)

        # Create Queue for Reactive to listen
        self.queue = Queue()

        # Save message listen timeout
        self.timeout = timeout

        # Save instance of Messenger
        self.messenger = Messenger()

        # Run User Defined Init
        self.on_init()

        # Move to Register State
        self.register()

    def register(self):
        # Set Lifecycle stage
        self.lifecycle = Lifecycle.REGISTER

        # Register Reactive with Messenger
        self.messenger.register(self.name,
                                self.queue,
                                self.start,
                                self.stop,
                                self.get_status)

        # Subscribe to Subjects
        for subject in self.subjects:
            self.messenger.subscribe(subject)

        # Run user defined Register
        self.on_register()

    def start(self):
        # Check if Reactive is already Started
        if self.lifecycle == Lifecycle.START or self.lifecycle == Lifecycle.RUN:
            return

        # Set Lifecycle stage
        self.lifecycle = Lifecycle.START

        # Run user defined Start
        self.on_start()

        # Start Reactive Thread
        self.thread.start()

    def run(self):
        # Set Lifecycle stage
        self.lifecycle = Lifecycle.RUN

        # Start the uptime timer
        self.run_time = time.time()

        # Runtime Loop
        while self.lifecycle == Lifecycle.RUN:
            # Listen for new Message
            try:
                msg = self.queue.get(timeout=self.timeout)
            except:
                continue

            # Run user defined Run
            retVal = self.on_run(msg.message)

            # Return value to sender, if exists
            if retVal:
                self.messenger.send(msg.sender,
                                    retVal)

            # Mark task complete
            self.queue.task_done()

    def stop(self):
        # Check if Reactive is already Stopped
        if self.lifecycle == Lifecycle.STOP:
            return

        # Set Lifecycle stage
        self.lifecycle = Lifecycle.STOP

        # Wait for Thread to stop
        self.thread.join()

        # Stop the uptime timer
        self.stop_time = time.time()

        # Run user defined Stop
        self.on_stop()

    ###########
    # Utility #
    ###########

    def get_status(self):
        self.status['self'] = str(self)
        self.status['class'] = self.__class__.__name__
        self.status['lifecycle'] = self.lifecycle.name
        self.status['is_alive'] = self.thread.is_alive()
        self.status['subjects'] = self.subjects
        self.status['uptime'] = f"{self._get_uptime()} s"
        self.status['message_count'] = self.queue.qsize()
        return self.status

    def _get_uptime(self):
        if self.run_time <= 0:
            return 0

        if self.stop_time <= 0:
            return round(time.time() - self.run_time, 3)

        return round(self.stop_time - self.run_time, 3)

    ################
    # User Defined #
    ################

    def on_init(self):
        pass

    def on_register(self):
        pass

    def on_start(self):
        pass

    def on_run(self, **kwargs):
        raise NotImplementedError

    def on_stop(self):
        pass
