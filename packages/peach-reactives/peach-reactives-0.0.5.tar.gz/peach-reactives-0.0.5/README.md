# Reactives

Library for easily launching threads that "react" to messages on a queue.

# Reactive
At its core, `Reactives` are independent threads with their own queues that "react" to messages.

Creating a `Reactive` is as simple as inheriting the class and overriding the `on_run(self, msg)` function.

```
from reactive import Reactive

class My_Reactive(Reactive):

    def on_run(self, msg):
        ...

```

There are 5 functions that the user can override, only the `on_run` is required.  Each function corresponds to a stage in the `Lifecycle` of a `Reactive`:
1. `on_init(self)`
2. `on_register(self)`
3. `on_start(self)`
4. `on_run(self, msg)`
5. `on_stop(self)`

It is important not to override the `__init__(self)` magic function.

When a `Reactive` is instantiated it can be given a unique name, if a name is not provided it will default to the name of the class. No two `Reactives` can have the same name, this will result in a exception raised during registration with the `Messenger`. The name is used by the `Messenger` to know where to send messages.

```
my_reactive_1 = My_Reactive()           <-- Defaults name to 'my_reactive'
my_reactive_2 = My_Reactive(name="r_2") <-- name is 'r_2'
my_reactive_3 = My_Reactive()           <-- Raises an `AlreadyRegistered' exception

```

## Lifecycle
Each `Reactive` has a `Lifecycle` that it follows. Some `Lifecycle states` are transitioned automatically, others are requested.  At each `Lifecycle state` the user has an opportunity to execute some function.

### Init
The `Init state` is entered when the `Reactive` is instantiated.  This `state` creates the `Reactive`, its queue, and any other necesseties.
The user defined `on_init(self)` function is executed at the end of this `state`.
The `Init state` automatically transitions to the `Register state` if successfully completed.

### Register
The `Register state` is automatically entered after the `Init state` is complete.  This `state` registers the `Reactive` with the `Messenger` and subscribes to any `subjects`.  
The user defined `on_register(self)` function is executed at the end of this `state`.
The `Register state` is held here, waiting further instruction before transitioning to the `Start state`.

### Start
The `Start state` is entered after user intervention, either manually executing `start()` or, more preferably, requesting it through the `Messenger`.
This `state` will execute the user defined `on_start(self)` function and start a new thread.
The `Start state` will automatically transition to the `Run state` if successfully completed.

### Run
The `Run state` is automatically entered after the `Start state` is complete.  This `state` is where the actual "work" happens. The thread will enter a loop listening for `messages` and running the user defined `on_run(self, msg)` function, passing along any messages in the queue.
The `Run state` is held in an infinite loop, reacting to `messages` or an instruction to transition to the `Stop state`.

### Stop
The `Stop state` is entered after user intervention, either manually executing `stop()` or, more preferable, requesting it through the `Messenger`.
This `state` will wait for the thread to complete, clear the queue, and run general cleanup tasks.
The user defined `on_stop(self)` function is executed at the end of this `state`.
The `Stop state` is the final `state` in the `Lifecycle` and will sit here until user intervention requests a transition to the `Start state`.

# Messenger
This is the means of communication with and between `Reactives`. Other than instantiating the `Reactives` all interaction is done through the `Messenger`.
The `Messenger` is a singleton that manages all of the `Reactive`'s queues and any `subjects` that `Reactives` can subscribe to.

## Direct Message
The `Messenger` can send messages directly to a `Reactive` by calling `send()` with the name of the `Reactive` along with a message.

```
from reactive import Messenger
def main():
    messenger = Messenger()
    messenger.send("my_reactive", "test")
```

## Pub-Sub
`Reactives` can subscribe to `subjects` for a Pub-Sub style messaging. `Reactives` register to listen to subjects during instantiation.  Messages sent to a `subject` are then forwarded to all `Reactives` that subscribe to that `subject`.

```
my_reactive = My_Reactive(subjects=['count'])
messenger.send('count', {increment: 2})
```

## Start
Request the `Reactive` enter the start state of the lifecycle.  If a subject is given, all subscribed `Reactives` will be requested to enter the start state. If no name is given, all registered `Reactives` will be requested to enter the start state.

```
messenger.start("r_2")   <-- Will only start the Reactive named 'r_2'
messenger.start("count") <-- Will start all Reactives subscribed to subject 'count'
messenger.start()        <-- Will start all registered Reactives
```

## Stop
Request the `Reactive` enter the stop state of the lifecycle.  If a subject is given, all subscribed `Reactives` will be requested to enter the stop state. If no name is given, all registered `Reactives` will be requested to enter the stop state.

```
messenger.stop("r_2")   <-- Will only stop the Reactive named 'r_2'
messenger.stop("count") <-- Will stop all Reactives subscribed to subject 'count'
messenger.stop()        <-- Will stop all registered Reactives
```

## Status
Request the status of a given `Reactive`.  If a subject is given, the status of all subscribed `Reactives` will be requested. If no name is given, the status of all registered `Reactives` will be requested.

```
messenger.status("r_2")   <-- Will only return the status of the Reactive named 'r_2'
messenger.status("count") <-- Will return the status of all Reactives subscribed to subject 'count'
messenger.status()        <-- Will return the status of all registered Reactives
```

# Getting started


## Installation
`pip install reactives`

## Support
I don't get paid for this and it is just a fun experiment so it is provided as-is.

## Roadmap
What will we think of next?

## Contributing
This is just a fun experiment built for my own exploration, education, and entertainment so no contributions are accepted at this time.
I am open to hearing about additional features, improvements, etc..

## Authors and acknowledgment
Me, myself, and I

## License
Beerware

## Project status
Experimental
