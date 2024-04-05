"""
The :mod:`vlcsim.controller` module is in charge of managing the connections and the physical sustrate.
"""

from .scene import *
from enum import Enum
import math
import sys


class Connection:
    """
    The :class:`vlcsim.controller.Connection` contains the connection information. Each :class:`vlcsim.controller.Connection` object contains an ID connection, the Access Point (AP) that uses the :class:`vlcsim.controller.Connection` object, the receiver connected to the AP, and finally if the connection was successfully allocated.
    """

    def __init__(self, id: int, receiver: Receiver, time: float) -> None:
        """
        :class:`vlcsim.controller.Connection` constructor.

        :param id: The connection ID.
        :type id: int
        :param receiver: The receiver of this connection.
        :type receiver: :class:`vlcsim.scene.Receiver`
        :return: :class:`vlcsim.controller.Connection` object
        :rtype: :class:`vlcsim.controller.Connection`
        """
        self.__id = id
        self.__ap = None
        self.__receiver = receiver
        self.__allocated = True
        self.__frameSlice = []
        self.__timesAssigned = []
        self.__goalTime = None
        self.__time = time
        self.__capacityRequired = None
        self.__snr = sys.float_info.min

    @property
    def snr(self):
        return self.__snr

    @snr.setter
    def snr(self, value):
        self.__snr = value

    @property
    def capacityRequired(self) -> float:
        return self.__capacityRequired

    @capacityRequired.setter
    def capacityRequired(self, value: float):
        self.__capacityRequired = value

    @property
    def time(self):
        return self.__time

    @time.setter
    def _time(self, value):
        self.__time = value

    @property
    def goalTime(self):
        return self.__goalTime

    @goalTime.setter
    def goalTime(self, value):
        self.__goalTime = value

    @property
    def frameSlice(self):
        return self.__frameSlice

    @frameSlice.setter
    def frameSlice(self, value):
        self.__frameSlice = value

    def getNextTime(self):
        return self.__timesAssigned.pop(0)

    def insertTime(self, time):
        for i in range(len(self.__timesAssigned)):
            if self.__timesAssigned[i] > time:
                self.__timesAssigned.insert(i, time)
                break
        self.__timesAssigned.append(time)

    def assignFrameSlice(self, frame, slice):
        self.__frameSlice.append([frame, slice])

    def numberOfSlicesNeeded(
        self, capacityRequired: float, capacityFromAP: float
    ) -> int:
        return math.ceil(capacityRequired / capacityFromAP)

    def nextSliceInAPWhenArriving(self, ap):
        return math.ceil(self.__time / ap.sliceTime) % ap.slicesInFrame

    @property
    def receiver(self) -> Receiver:
        """
        Receiver of this connection

        :return: The receiver of this connection.
        :rtype: :class:`vlcsim.scene.Receiver`
        """
        return self.__receiver

    @receiver.setter
    def receiver(self, value: Receiver):
        self.__receiver = value

    @property
    def id(self):
        """
        ID of this connection

        :return: The ID of this connection.
        :rtype: int
        """
        return self.__id

    @property
    def AP(self) -> AccessPoint:
        """
        Acces Point of this connection

        :return: The Access Point used by this connection.
        :rtype: :class:`vlcsim.scene.Receiver`
        """
        return self.__ap

    @AP.setter
    def AP(self, ap: AccessPoint):
        self.__ap = ap

    @property
    def allocated(self):
        """
        Is this connection allocated?

        :return: True if the connection was allocated. False otherwise.
        :rtype: bool
        """
        return self.__allocated

    @allocated.setter
    def allocated(self, value):
        self.__allocated = value


class Controller:
    """
    Class in charge of controlling which connections are assigned and which are not. Contains the routines necessary to assign, unassign, pause and resume a connection.
    """

    status = Enum("status", "ALLOCATED NOT_ALLOCATED WAIT")
    """
    Corresponds to the status that the allocation algorithm could return. The status **ALLOCATED** means that the connection was succesfully allocated. **NOT_ALLOCATED** means that the allocation algorithm could not allocate the connection, and this was refused. And finally, the **WAIT** means that the connection will wait to be allocated in the future, using the same allocation algorithm.
    """

    nextStatus = Enum("nextStatus", "PAUSE FINISH RESUME IDLE RND_WAIT")

    """
    Corresponds to the status used inside every allocation routine in the controller module. The status **PAUSE** means that the connection was PAUSED, and it will be resumed in the future. **FINISH** means that the connection completes its work, and finished. The **RESUME** means the connection will start again the transmission after a **PAUSE**. **IDLE** means that the AP is not connected to any receiver. Finally, **RND_WAIT** means that the connection could not be connected, and the controller will wait a random time to try again. 
    """

    def __init__(self, x, y, z, nGrids, rho) -> None:
        """
        Controller constructor

        :param x: Length of the scenario
        :type x: float
        :param y: Width of the scenario
        :type y: float
        :param z: Height of the scenario
        :type z: float
        :param nGrids: Number of segments on each dimension. Usefull for precision.
        :type nGrids: int
        :param rho: reflexion coefficient. A floating number between 0 and 1.
        :type rho: float
        """

        self.__scenario = Scenario(x, y, z, nGrids, rho)
        self.__allocator = None
        self.__allocationStatus = None
        # self.__activeConnections = [[]] * len(self.__scenario.vleds)

    @property
    def scenario(self):
        """
        Scenario controlled by this controller

        :return: The scenario of this controller
        :rtype: :class:`vlcsim.scene.Scenario`
        """
        return self.__scenario

    @property
    def allocationStatus(self):
        """
        The last status of the allocation process

        :return: The last status of the allocation process
        :rtype: :class:`vlcsim.controller.status`
        """
        return self.__allocationStatus

    @property
    def allocator(self):
        """
        The method used to allocate connections. This method could be replaced with any other method usiing always this sign:

        .. code-block:: python
            :linenos:

            def alloc_function(receiver: Receiver, connection: Connection, scenario: Scenario, controller: Controller):
                # Some allocation algorithm using the parameters.

                # It have to return an status and the connection in a tuple


        An example of an allocation method:

        .. code-block:: python
            :linenos:
            :emphasize-lines: 1,11

            def alloc(receiver, connection, scenario: Scenario, controller: Controller):
                vleds = scenario.vleds
                snrFromVleds = []
                for vled in vleds:
                    snrFromVleds.append(scenario.snrVled(receiver, vled))
                posBestSNR = snrFromVleds.index(max(snrFromVleds))
                if controller.numberOfActiveConnections(posBestSNR) > 2:
                    return Controller.status.WAIT, connection
                else:
                    connection.AP = vleds[posBestSNR]
                return Controller.status.ALLOCATED, connection
        """
        return self.__allocator

    @allocator.setter
    def allocator(self, allocator):
        self.__allocator = allocator

    def assignConnection(self, connection: Connection, time: float):
        """
        Routine that assign a connection to a specific AP. This routine uses the allocator method to make the assignment.

        :param connection: Connection object that will try to connect.
        :type connection: :class:`vlcsim.controller.Connection`
        :param time: Instant in which this connection was tryied to connect.
        :type time: float
        """
        self.__allocationStatus, connection = self.__allocator(
            connection.receiver, connection, self.__scenario, self
        )
        connection.receiver.timeFirstConnected = time

        if self.__allocationStatus == Controller.status.ALLOCATED:
            index = self.APPosition(connection.AP)
            self.__numberActiveConnections[index] += 1
            actualSlice = connection.nextSliceInAPWhenArriving(connection.AP) - 1
            actualTime = (
                (time // (connection.AP.slicesInFrame * connection.AP.sliceTime))
                * connection.AP.slicesInFrame
                * connection.AP.sliceTime
            )
            auxPreviousTime = 0
            if actualSlice == -1:
                auxPreviousTime = 1
            connection.receiver.goalTime = (
                connection.capacityRequired
                / connection.receiver.capacityFromAP
                * connection.AP.sliceTime
            )
            connection.goalTime = connection.receiver.goalTime
            for fs in connection.frameSlice:
                if fs[0] <= 0 and fs[1] <= actualSlice:
                    raise ("You are trying to assign a slice in the past...")
                self.assignSlice(index, fs[0], fs[1], connection)
                connection.insertTime(
                    actualTime
                    + connection.AP.sliceTime
                    * connection.AP.slicesInFrame
                    * (fs[0] + auxPreviousTime)
                    + fs[1] * connection.AP.sliceTime
                )
            time = connection.getNextTime()
            return Controller.nextStatus.RESUME, time, connection
        elif self.__allocationStatus == Controller.status.NOT_ALLOCATED:
            return Controller.nextStatus.IDLE, time, connection
        elif self.__allocationStatus == Controller.status.WAIT:
            return Controller.nextStatus.RND_WAIT, time, connection
        else:
            raise ("Return status of allocation algorithm not supported")

    def pauseConnection(self, connection, time):
        """
        Routine that pause a connection to a specific AP.

        :param connection: Connection object that will be paused.
        :type connection: :class:`vlcsim.controller.Connection`
        :param time: Instant in which this connection was paused.
        :type time: float
        """
        receiver = connection.receiver
        index = self.APPosition(connection.AP)
        receiver.timeActive += connection.AP.sliceTime
        timeNext = connection.getNextTime()
        nextSlice = connection.nextSliceInAPWhenArriving(connection.AP)
        flag = False
        for i in range(nextSlice, connection.AP.slicesInFrame):
            if len(self.__activeConnections[index]) == 0:
                flag = True
                break
            if self.__activeConnections[index][0][i] != False:
                flag = True
                break
        if not flag:
            self.__activeConnections[index].pop(0)
        return Controller.nextStatus.RESUME, timeNext, connection

    def resumeConnection(self, connection, time):
        """
        Routine that resume a connection to a specific AP.

        :param connection: Connection object that will be resumed.
        :type connection: :class:`vlcsim.controller.Connection`
        :param time: Instant in which this connection was resumed.
        :type time: float
        """
        receiver = connection.receiver
        if receiver.goalTime < receiver.timeActive + connection.AP.sliceTime:
            return (
                Controller.nextStatus.FINISH,
                time + receiver.goalTime - receiver.timeActive,
                connection,
            )
        else:
            return (
                Controller.nextStatus.PAUSE,
                time + connection.AP.sliceTime,
                connection,
            )

    def unassignConnection(self, connection, time):
        """
        Routine that unasign a connection to a specific AP.

        :param connection: Connection object that will be unassigned.
        :type connection: :class:`vlcsim.controller.Connection`
        :param time: Instant in which this connection was unassigned.
        :type time: float
        """
        index = self.APPosition(connection.AP)
        receiver = connection.receiver
        receiver.timeActive = receiver.goalTime
        receiver.timeFinished = time

        nextSlice = connection.nextSliceInAPWhenArriving(connection.AP)
        flag = False
        for i in range(nextSlice, connection.AP.slicesInFrame):
            if len(self.__activeConnections[index]) == 0:
                break
            if self.__activeConnections[index][0][i] != False:
                flag = True
        if flag:
            self.__activeConnections[index].pop(self.__activeConnection[index])
        self.__numberActiveConnections[index] -= 1
        return Controller.nextStatus.IDLE, time, None

    def init(self):
        """
        Initializatrion of this controller. This methods must be invoked before to start the simulation.
        """
        self.__activeConnections = []
        self.__numberActiveConnections = []

        nvleds = 0
        nrfs = 0
        actual = None

        for i in range(len(self.__scenario.vleds) + len(self.__scenario.rfs)):
            self.__numberActiveConnections.append(0)
            self.__activeConnections.append([])
            if (
                len(self.__scenario.vleds) > nvleds
                and self.APPosition(self.__scenario.vleds[nvleds]) == i
            ):
                actual = self.__scenario.vleds[nvleds]
                nvleds += 1
            else:
                actual = self.__scenario.rfs[nrfs]
                nrfs += 1

            self.__activeConnections[-1].append([])
            for j in range(actual.slicesInFrame):
                self.__activeConnections[-1][-1].append(False)
        self.__activeConnection = [0] * len(self.__activeConnections)

    def APPosition(self, ap):
        """
        Returns the AP position. The AP coulb be a VLed or a Femtocell, so this method get the position of this AP in the controller.

        :param ap: The AP.
        :type ap: :class:`vlcsim.scene.VLed` or :class:`vlcsim.scene.RF`
        :return: The position of the AP.
        :rtype: int
        """
        if isinstance(ap, VLed):
            return self.__scenario.vledsPositions[ap.ID]
        elif isinstance(ap, RF):
            return self.__scenario.rfsPositions[ap.ID]

    @property
    def activeConnections(self):
        """
        This attribute is a list o a list of Connections. Every element on the first list correspond to a list of active connections in every Access Point. In that way, the cardinality of the outer list is equal to the number of Access Points in the scenario, whilst that the numer o connection in every access point is the cardinality of each item of the outer list.

        :return: A list that contains *n* lists, where *n* is the number of APs in the scenario. Each item on the *n* lists corresponds to the connections associated to each AP.
        :rtype: list of lists
        """

        return self.__activeConnections

    def numberOfActiveConnections(self, ap: int):
        """
        The number of active connections in this AP.

        :param apID: ID of the access point. This ID corresponds to the position of the AP in the list of APs.
        :type apID: int
        :return: The number of active connections in this AP.
        :rtype: int
        """
        return self.__numberActiveConnections[self.APPosition(ap)]

    def assignSlice(self, apIndex, frame, slice, connection):
        numberOfFrames = len(self.__activeConnections[apIndex])
        if numberOfFrames < frame + 1:
            for _ in range(numberOfFrames, frame + 1):
                self.__activeConnections[apIndex].append([])
                for __ in range(connection.AP.slicesInFrame):
                    self.__activeConnections[apIndex][-1].append(False)

        if self.__activeConnections[apIndex][frame][slice] != False:
            raise (
                "The connection in frame: "
                + str(frame)
                + ", slice:"
                + str(slice)
                + " is already used."
            )
        else:
            self.__activeConnections[apIndex][frame][slice] = connection

    def framesState(self, ap):
        return self.__activeConnections[self.APPosition(ap)]
