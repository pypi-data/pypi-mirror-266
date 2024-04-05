VLCSim is an Event-Oriented simulator package for Visible Light Communication.

# Features

- Dynamic Environment with in/out connections 
- Flexible resource allocation algorithm 
- Flexible VLC/room parameters

# Events

The simulator has 5 Type of events:

* **ARRIVE**: Every time when a connection arrives to the system
* **RESUME**: When a connection begin the transmission
* **PAUSE**: When a Connection PAUSES the transmission
* **DEPARTURE**: When a connectin ends its transmission
* **RETRYING**: WHen a connection is not allocated, and uses a WAIT status, it makes a new attepmt to connect.

# Code example

Next example could be used to start coding with the package:

```python
from vlcsim import *
import math


def alloc(receiver, connection: Connection, scenario: Scenario, controller: Controller):
    vleds = scenario.vleds
    capacities = []
    for vled in vleds:
        capacities.append(scenario.capacityVled(receiver, vled))
    posBestCapacity = capacities.index(max(capacities))
    numberOfSlices = 0
    if (
        controller.numberOfActiveConnections(vleds[posBestCapacity]) > 5
        or capacities[posBestCapacity] == 0
    ):
        connection.AP = scenario.rfs[0]
        connection.receiver.capacityFromAP = scenario.capacityRf(
            receiver, connection.AP
        )
        numberOfSlices = connection.numberOfSlicesNeeded(
            connection.capacityRequired, connection.receiver.capacityFromAP
        )
    else:
        connection.AP = vleds[posBestCapacity]
        connection.receiver.capacityFromAP = capacities[posBestCapacity]
        numberOfSlices = connection.numberOfSlicesNeeded(
            connection.capacityRequired, capacities[posBestCapacity]
        )

    actualSlice = connection.nextSliceInAPWhenArriving(connection.AP)
    aux = 0
    auxFrame = 0

    # Actual frame
    for slice in range(actualSlice, connection.AP.slicesInFrame):
        if (
            len(controller.framesState(connection.AP)) == 0
            or controller.framesState(connection.AP)[0][slice] == False
        ):
            connection.assignFrameSlice(0, slice)
            aux += 1
            break

    # next frames
    for frameIndex in range(1, len(controller.framesState(connection.AP))):
        for slice in range(connection.AP.slicesInFrame):
            if controller.framesState(connection.AP)[frameIndex][slice] == False:
                connection.assignFrameSlice(frameIndex, slice)
                aux += 1
                auxFrame = frameIndex
                break

        if aux == numberOfSlices:
            break

    frameIndex = auxFrame + 1
    while aux < numberOfSlices:
        connection.assignFrameSlice(frameIndex, 0)
        frameIndex += 1
        aux += 1
    return Controller.status.ALLOCATED, connection


if __name__ == "__main__":
    # Simulator Constructor: size of the room, with the numbrer of grids and the rho parameter

    sim = Simulator(20.0, 20.0, 2.15, 10, 0.8)

    # Adding Vleds to the room
    vled = VLed(-7.5, -7.5, 2.15, 60, 60, 20, 70)
    vled.sliceTime = 0.2
    vled.slicesInFrame = 10
    vled.B = 0.5e5
    sim.scenario.addVLed(vled)
    vled = VLed(-7.5, 7.5, 2.15, 60, 60, 20, 70)
    vled.sliceTime = 0.2
    vled.slicesInFrame = 10
    vled.B = 0.5e5
    sim.scenario.addVLed(vled)
    vled = VLed(7.5, -7.5, 2.15, 60, 60, 20, 70)
    vled.sliceTime = 0.2
    vled.slicesInFrame = 10
    vled.B = 0.5e5
    sim.scenario.addVLed(vled)
    vled = VLed(7.5, 7.5, 2.15, 60, 60, 20, 70)
    vled.sliceTime = 0.2
    vled.slicesInFrame = 10
    vled.B = 0.5e5
    sim.scenario.addVLed(vled)

    # Adding rf
    rf = RF(0, 0, 0.85)
    rf.sliceTime = 0.2
    rf.slicesInFrame = 10
    rf.B = 0.5e5
    sim.scenario.addRF(rf)

    # setting algorithm and number of connections
    sim.set_allocation_algorithm(alloc)
    sim.goalConnections = 60

    # changing Dynamic
    sim.lambdaS = 1
    sim.mu = 30

    # changing random wait limits

    sim.upper_random_wait = 20
    sim.lower_random_wait = 2

    sim.lower_capacity_required = 1e5
    sim.upper_capacity_required = 5e5

    # initialize and run
    sim.init()
    sim.run()
