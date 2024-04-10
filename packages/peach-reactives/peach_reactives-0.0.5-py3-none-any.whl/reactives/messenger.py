import inspect
import uuid
from dataclasses import dataclass
from queue import Queue


@dataclass(frozen=True)
class Message:
    uuid: str
    sender: str
    receiver: str
    message: any


class Messenger:
    class UnknownReactive(Exception):
        pass

    class UnknownReceiver(Exception):
        pass

    class AlreadyRegistered(Exception):
        pass

    def __new__(cls):
        # Make singleton
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)

        # Return singleton
        return cls.instance

    def __init__(self):
        # Check flag before initializing
        if hasattr(self, "init"):
            return

        # Set flag to indicate already initialized
        self.init = True

        # Dict to hold reactive queue
        self.r_queues = {}
        self.r_queues['main'] = Queue()

        # Dict to hold subject subscribers
        self.r_subjects = {}

        # Dict to hold reactive start function
        self.r_start = {}
        # Dict to hold reactive stop function
        self.r_stop = {}

        # Dict to hold reactive status function
        self.r_status = {}

    def register(self,
                 name,
                 queue,
                 start_func,
                 stop_func,
                 status_func):
        # Normalize Reactive name
        name = name.lower()

        # Check if Reactive is already registered
        if name in self.r_queues.keys():
            raise self.AlreadyRegistered(f"{name} has already been registered")

        # Register the message queue
        self.r_queues[name] = queue

        # Register the Start Function
        self.r_start[name] = start_func

        # Register the Stop Function
        self.r_stop[name] = stop_func

        # REgister the Status Function
        self.r_status[name] = status_func

    def subscribe(self,
                  subject):
        # Normalize subject name
        subject = subject.lower()

        # Obtain calling reactive's name
        try:
            reactive = inspect.stack()[1][0].f_locals['self'].name
        except:
            raise self.UnknownReactive(f"{reactive} is not registered")

        # Create entry for subject, if doesn't exist
        if subject not in self.r_subjects.keys():
            self.r_subjects[subject] = []

        # Subscribe reactive to subject
        self.r_subjects[subject].append(reactive)

    def send(self,
             receiver,
             msg,
             blocking=False,
             timeout=1.0):
        retVal = []

        # Normalize receiver name
        receiver = receiver.lower()

        # Default sender
        sender = 'main'

        # Find sender of message
        try:
            sender = inspect.stack()[1][0].f_locals['self'].name
        except:
            # Default to 'main'
            sender = 'main'

        # Generate uuid for messenger
        m_uuid = str(uuid.uuid4())

        # Override sender if call is blocking
        if blocking:
            # Create new queue for unique message
            self.r_queues[m_uuid] = Queue()
            sender = m_uuid

        # Check if receiver is direct message to reactive
        if receiver in self.r_queues.keys():
            message = Message(m_uuid,
                              sender,
                              receiver,
                              msg)
            self.r_queues[receiver].put(message)

            # if blocking, wait for response
            if blocking:
                retVal = self.get(name=m_uuid,
                                  timeout=timeout)
                # Delete unique message queue
                del self.r_queues[m_uuid]
                # Return message
                return retVal

            return

        # Check if receiver is subscribed subject
        if receiver in self.r_subjects.keys():
            for r in self.r_subjects[receiver]:
                message = Message(sender,
                                  r,
                                  msg)
                self.r_queues[r].put(message)

                # if blocking, wait for responses
                if blocking:
                    retVal.append(self.get(name=m_uuid,
                                           timeout=timeout))
            if blocking:
                # Delete unique message queue
                del self.r_queues[m_uuid]
                # Return messages
                return retVal

            return

        # No Reactive or Subject found
        raise self.UnknownReceiver(f"{receiver} not registered")

    def start(self,
              name=None):

        # If no reactive given, start all
        if not name:
            for reactive, r_start in self.r_start.items():
                r_start()
            return

        # Normalize Reactive name
        name = name.lower()

        # Check if starting a Reactive
        if name in self.r_start.keys():
            self.r_start[name]()
            return

        # Check if start all Reactives subscribed to a subject
        if name in self.r_subject.keys():
            for r in self.r_subjects[name]:
                self.r_start[r]()
            return

        # Given name is neither a Reactive nor subject
        raise self.UnknownReactive(f"{name} not registered")

    def stop(self,
             name=None):
        # If no reactive given, stop all
        if not name:
            for reactive, r_stop in self.r_stop.items():
                r_stop()
            return

        # Normalize Reactive name
        name = name.lower()

        # Check if stopping a Reactive
        if name in self.r_stop.keys():
            self.r_stop[name]()
            return

        # Check if stop all Reactives subscribed to a subject
        if name in self.r_subjects.keys():
            for r in self.r_subjects[name]:
                self.r_stop[r]()

        # Given name is neither a Reactive nor a subject
        raise self.UnknownReactive(f"{name} not registered")

    def status(self,
               name=None):
        retVal = {}

        # If no Reactive specified, return everything
        if not name:
            # Collect list of Reactives
            for r, stats in self.r_status.items():
                retVal[r] = stats()

            return retVal

        # Normalize Reactive name
        name = name.lower()

        # Check if status a Reactive
        if name in self.r_status.keys():
            retVal[name] = self.r_status[name]()
            return retVal

        # Check if status all Reactives subscribed to a subject
        if name in self.r_subjects.keys():
            for r in self.r_subjects[name]:
                retVal[r] = self.r_status[name]()
            return retVal

        # Given name is neither a Reactive nor a subject
        raise self.UnknownReactive(f"{name} not registered")

    def get(self,
            name='main',
            timeout=0.01):
        try:
            msg = self.r_queues[name].get(timeout=timeout)
        except:
            return None

        self.r_queues[name].task_done()

        return msg
