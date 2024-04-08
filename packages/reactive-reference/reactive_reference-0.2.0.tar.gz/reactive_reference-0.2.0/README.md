# Reactive Reference

This is a collection of mini projects with the intent to have a more reactive programming approach in Python.

## Event

A Producer/Subscriber library with Async capabilities.

### Main Entities

#### EventStream

A stream of data that triggers subscribers on new events. It is structured with Domains in mind, meaning the data can be sent to every subscriber listening or specifically to the Domain of the Producer.

#### EventSubscriber

A listener to the data emitted by the EventStream. Can listen to multiple Domains at a time, but can only have 1 main Domain.

#### EventProducer

Producer will emit data to the stream triggering the Subscribers. The data sent via the producer will be encapsulated in an Event object which will be stored in the stream and spread across.

### Key Points

* Each Subscriber can adhere to a ReplayStrategy for late joining
* Per design only one stream can exist (Singleton)
* Subscribers can also listen to lifecycle events emitted by the stream