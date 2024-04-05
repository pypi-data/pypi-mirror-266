from .controller import *
from .scene import *
import numpy as np
from enum import Enum

"""
The Module **Simulator** has all the Simulation Dynamics. 
"""


class Event:
    """This is a conceptual class representation of a simple BLE device
    (GATT Server). It is essentially an extended combination of the

    :param type: A handle to the :class:`simpleble.SimpleBleClient` client
        object that detected the device
    :type type: class:`Event.event`
    :param time: Device MAC address, defaults to None
    :type time: float, optional
    :param id_connection: Device address type - one of ADDR_TYPE_PUBLIC or
        ADDR_TYPE_RANDOM, defaults to ADDR_TYPE_PUBLIC
    :type id_connection: int, optional
    """

    event = Enum("event", "ARRIVE DEPARTURE PAUSE RESUME NEXT_CONNECTION_TRY")

    def __init__(self, type=None, time=-1, id_connection=-1):
        self.__time = time
        self.__id_connection = id_connection
        if type == None:
            self.__type = Event.event.ARRIVE
        else:
            self.__type = type
        self.__connection = None

    @property
    def type(self):
        return self.__type

    @property
    def time(self):
        return self.__time

    @property
    def id_connection(self):
        return self.__id_connection

    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, value):
        self.__connection = value


class Simulator:
    def __init__(self, x, y, z, nGrids, rho):
        self.__controller = Controller(x, y, z, nGrids, rho)
        self.__events = []
        self.__current_event = None

        self.__initReady = None
        self.__lambdaS = None
        self.__mu = None
        self.__seedArrive = None
        self.__seedDeparture = None
        self.__seedX = None
        self.__seedY = None
        self.__seedZ = None
        self.__seedRandomWait = None
        self.__seedCapacityRequired = None
        self.__numberOfConnections = None
        self.__goalConnections = None
        self.__arrival_variable = None
        self.__departure_variable = None
        self.__x_variable = None
        self.__y_variable = None
        self.__z_variable = None
        self.__random_wait_variable = None
        self.__capacity_required_variable = None
        self.__rtn_allocation = None

        self.__allocatedConnections = None
        # time
        self.__clock = None
        self.__time_duration = None

        self.__upper_random_wait = None
        self.__lower_random_wait = None

        self.__upper_capacity_required = None
        self.__lower_capacity_required = None

        self.__users_by_vlc = []
        self.__users_by_rf = []

        self.default_values()

    def default_values(self):
        self.__initReady = False
        self.__lambdaS = 3
        self.__mu = 10
        self.__seedArrive = 12345
        self.__seedDeparture = 1234
        self.__seedX = 1235
        self.__seedY = 1245
        self.__seedZ = 1345
        self.__seedRandomWait = 1345
        self.__seedCapacityRequired = 1345

        self.__numberOfConnections = 0
        self.__goalConnections = 10000
        self.__lower_random_wait = 5
        self.__upper_random_wait = 15

    @property
    def upper_capacity_required(self):
        return self.__upper_capacity_required

    @upper_capacity_required.setter
    def upper_capacity_required(self, value):
        self.__upper_capacity_required = value

    @property
    def lower_capacity_required(self):
        return self.__lower_capacity_required

    @lower_capacity_required.setter
    def lower_capacity_required(self, value):
        self.__lower_capacity_required = value

    @property
    def seedCapacityRequired(self) -> int:
        return self.__seedCapacityRequired

    @seedCapacityRequired.setter
    def seedCapacityRequired(self, value: int):
        self.__seedCapacityRequired = value

    @property
    def upper_random_wait(self):
        return self.__upper_random_wait

    @upper_random_wait.setter
    def upper_random_wait(self, value):
        self.__upper_random_wait = value

    @property
    def lower_random_wait(self):
        return self.__lower_random_wait

    @lower_random_wait.setter
    def lower_random_wait(self, value):
        self.__lower_random_wait = value

    @property
    def lambdaS(self):
        """
        Get or set the attribute lambda.
        """
        return self.__lambdaS

    @lambdaS.setter
    def lambdaS(self, lambdaS):
        if self.__initReady:
            print(
                "You can not set mu parameter AFTER calling init simulator " "method."
            )
            return
        self.__lambdaS = lambdaS

    @property
    def mu(self):
        """
        Get or set the attribute mu.
        """
        return self.__mu

    @mu.setter
    def mu(self, mu):
        if self.__initReady:
            print(
                "You can not set mu parameter AFTER calling init simulator " "method."
            )
            return
        self.__mu = mu

    @property
    def seedX(self):
        """
        Get or set the attribute seedArrive.
        """
        return self.__seedX

    @seedX.setter
    def seedX(self, seedX):
        if self.__initReady:
            print(
                "You can not set mu parameter AFTER calling init simulator " "method."
            )
            return
        self.__seedX = seedX

    @property
    def seedY(self):
        """
        Get or set the attribute seedDeparture.
        """
        return self.__seedY

    @seedY.setter
    def seedY(self, seedY):
        if self.__initReady:
            print(
                "You can not set mu parameter AFTER calling init simulator " "method."
            )
            return
        self.__seedY = seedY

    @property
    def seedZ(self):
        """
        Get or set the attribute seedBitRate.
        """
        return self.__seedZ

    @seedZ.setter
    def seedZ(self, seedZ):
        if self.__initReady:
            print(
                "You can not set mu parameter AFTER calling init simulator " "method."
            )
            return
        self.__seedZ = seedZ

    @property
    def seedRandomWait(self):
        """
        Get or set the attribute seedBitRate.
        """
        return self.__seedRandomWait

    @seedZ.setter
    def seedRandomWait(self, seedRandomWait):
        if self.__initReady:
            print(
                "You can not set mu parameter AFTER calling init simulator " "method."
            )
            return
        self.__seedRandomWait = seedRandomWait

    @property
    def goalConnections(self):
        """
        Get or set the attribute goalConnections.
        """
        return self.__goalConnections

    @goalConnections.setter
    def goalConnections(self, goalConnections):
        if self.__initReady:
            print(
                "You can not set mu parameter AFTER calling init simulator " "method."
            )
            return
        self.__goalConnections = goalConnections

    def print_initial_info(self):
        print(
            "Scenario:\t %s x %s x %s"
            % (
                self.__controller.scenario.length,
                self.__controller.scenario.width,
                self.__controller.scenario.height,
            )
        )

        print(f"Number of VLeds: {self.__controller.scenario.numberOfVLeds}")
        print("Positions:")
        print("        ID  |     X     |     Y    |     Z    |")
        print("-" * 47)
        for vled in self.__controller.scenario.vleds:
            print(
                "{:>10}  |  {:8.4f} | {:8.4f} | {:8.4f} |".format(
                    vled.ID, vled.x, vled.y, vled.z
                )
            )
        print()
        print(f"Number of RFs: {self.__controller.scenario.numberOfRFs}")
        print("Positions:")
        print("        ID  |     X     |     Y    |     Z    |")
        print("-" * 47)
        for rf in self.__controller.scenario.rfs:
            print(
                "{:>10}  |  {:8.4f} | {:8.4f} | {:8.4f} |".format(
                    rf.ID, rf.x, rf.y, rf.z
                )
            )
        print()

        print("=" * 146)
        print("|  Time  ", end="")
        print("|   Event   ", end="")
        print("|  Receiver   ", end="")
        print("|    X    ", end="")
        print("|    Y    ", end="")
        print("|    Z    ", end="")
        print("|  Access Point (A.C.) ", end="")
        print("|  Goal time  ", end="")
        print("|  Elapsed time  ", end="")
        print("|    SNR     ", end="")
        print("|  Req. Cap. |")
        print("=" * 146)

    def print_row(self, event):
        text = ""
        text = "{:9.4f}".format(event.time) + "|"
        if event.type == Event.event.ARRIVE:
            text += "   ARRIVE  |"
        elif event.type == Event.event.RESUME:
            text += "   RESUME  |"
        elif event.type == Event.event.PAUSE:
            text += "   PAUSE   |"
        elif event.type == Event.event.DEPARTURE:
            text += " DEPARTURE |"
        elif event.type == Event.event.NEXT_CONNECTION_TRY:
            text += " RETRYING  |"
        text += "{:>10}".format(event.id_connection) + "   |"
        text += "{:8.4f}".format(event.connection.receiver.x) + " |"
        text += "{:8.4f}".format(event.connection.receiver.y) + " |"
        text += "{:8.4f}".format(event.connection.receiver.z) + " |"
        if isinstance(event.connection.AP, VLed):
            text += (
                " VLed: {:>5}".format(event.connection.AP.ID)
                + " ({:^5})".format(
                    self.__controller.numberOfActiveConnections(event.connection.AP)
                )
                + "  |"
            )
        elif isinstance(event.connection.AP, RF):
            text += (
                "   RF: {:>5}".format(event.connection.AP.ID)
                + " ({:^5})".format(
                    self.__controller.numberOfActiveConnections(event.connection.AP)
                )
                + "  |"
            )
        else:
            text += "     NOT_SELECTED     |"
        if event.connection.allocated:
            text += "{:10.4f}".format(event.connection.receiver.goalTime) + "   |"
        else:
            text += "  NOT_ALLOC  |"
        text += "{:12.4f}".format(event.connection.receiver.timeActive) + "    |"
        #        if event.connection != None:
        #            print(
        #                event.time,
        #                event.type,
        #                event.id_connection,
        #                event.connection.receiver.goalTime,
        #                event.connection.receiver.timeActive,
        #            )
        #        else:
        #            print(
        #                event.time,
        #               event.type,
        #               event.id_connection,
        #           )
        text += "{:10.2e}".format(event.connection.snr) + "  |"
        text += "{:10.2e}".format(event.connection.capacityRequired) + "  |"
        print(text)

    def event_routine(self):
        self.__current_event = self.__events[0]
        self.__rtn_allocation = None
        self.__clock = self.__current_event.time
        # print()
        # print(self.__controller.activeConnections[0])
        # print(self.__controller.activeConnections[1])
        # print(self.__controller.activeConnections[2])
        # print(self.__controller.activeConnections[3])
        # print(self.__controller.activeConnections[4])
        if self.__current_event.type == Event.event.ARRIVE:
            next_event_time = self.__clock + self.__arrival_variable.exponential(
                self.__lambdaS
            )
            for pos in range(len(self.__events) - 1, -1, -1):
                if self.__events[pos].time < next_event_time:
                    self.__events.insert(
                        pos + 1,
                        Event(
                            Event.event.ARRIVE,
                            next_event_time,
                            self.__numberOfConnections,
                        ),
                    )
                    self.__numberOfConnections += 1
                    break

            self.__x = self.__x_variable.uniform(
                low=self.__controller.scenario.start_x,
                high=self.__controller.scenario.end_x,
            )
            self.__y = self.__y_variable.uniform(
                low=self.__controller.scenario.start_y,
                high=self.__controller.scenario.end_y,
            )
            self.__z = self.__z_variable.uniform(
                low=0,
                high=self.__controller.scenario.height,
            )
            receiver = Receiver(self.__x, self.__y, self.__z, 1e-4, 1.0, 1.5, 70.0)
            connection = Connection(
                self.__current_event.id_connection, receiver, self.__clock
            )
            connection.capacityRequired = self.__capacity_required_variable.uniform(
                self.__lower_capacity_required, self.__upper_capacity_required
            )
            # connection.receiver.goalTime = connection.goalTime
            next_status, time, connection = self.__controller.assignConnection(
                connection, self.__clock
            )
            if (
                next_status == Controller.nextStatus.RESUME
                or next_status == Controller.nextStatus.PAUSE
            ):
                if type(connection.AP) == VLed:
                    self.__users_by_vlc[connection.AP.ID] += 1
                elif type(connection.AP) == RF:
                    self.__users_by_rf[connection.AP.ID] += 1
                self.__current_event.connection = connection
                if next_status == Controller.nextStatus.RESUME:
                    for pos in range(len(self.__events) - 1, -1, -1):
                        if self.__events[pos].time <= time:
                            e = Event(
                                Event.event.RESUME,
                                time,
                                connection.id,
                            )
                            e.connection = connection
                            self.__events.insert(pos + 1, e)
                            break
                    self.__allocatedConnections += 1
            elif next_status == Controller.nextStatus.RND_WAIT:
                self.__current_event.connection = connection
                next_event_time = self.__clock + self.__random_wait_variable.uniform(
                    low=self.__lower_random_wait,
                    high=self.upper_random_wait,
                )
                next_event = Event(
                    Event.event.NEXT_CONNECTION_TRY,
                    next_event_time,
                    connection.id,
                )
                next_event.connection = connection
                next_event.connection.allocated = False
                for pos in range(len(self.__events) - 1, -1, -1):
                    if self.__events[pos].time < next_event_time:
                        self.__events.insert(pos + 1, next_event)
                        break
        elif self.__current_event.type == Event.event.NEXT_CONNECTION_TRY:
            next_status, time, connection = self.__controller.assignConnection(
                self.__current_event.connection, self.__clock
            )
            if (
                next_status == Controller.nextStatus.RESUME
                or next_status == Controller.nextStatus.PAUSE
            ):
                connection.receiver.goalTime = self.__departure_variable.exponential(
                    self.__mu
                )
                connection.allocated = True
                if next_status == Controller.nextStatus.RESUME:
                    for pos in range(len(self.__events) - 1, -1, -1):
                        if self.__events[pos].time <= time:
                            e = Event(
                                Event.event.RESUME,
                                time,
                                connection.id,
                            )
                            e.connection = connection
                            self.__events.insert(pos + 1, e)
                            break
                    self.__allocatedConnections += 1
            elif next_status == Controller.nextStatus.RND_WAIT:
                next_event_time = self.__clock + self.__random_wait_variable.uniform(
                    low=self.__lower_random_wait,
                    high=self.upper_random_wait,
                )
                next_event = Event(
                    Event.event.NEXT_CONNECTION_TRY,
                    next_event_time,
                    connection.id,
                )
                next_event.connection = connection
                for pos in range(len(self.__events) - 1, -1, -1):
                    if self.__events[pos].time < next_event_time:
                        self.__events.insert(pos + 1, next_event)
                        break
        elif self.__current_event.type == Event.event.PAUSE:
            next_status, time, connection = self.__controller.pauseConnection(
                self.__current_event.connection, self.__clock
            )
            for pos in range(len(self.__events) - 1, -1, -1):
                if self.__events[pos].time <= time:
                    e = Event(
                        Event.event.RESUME,
                        time,
                        connection.id,
                    )
                    e.connection = connection
                    self.__events.insert(pos + 1, e)
                    break
        elif self.__current_event.type == Event.event.RESUME:
            next_status, time, connection = self.__controller.resumeConnection(
                self.__current_event.connection, self.__clock
            )
            for pos in range(len(self.__events) - 1, -1, -1):
                if self.__events[pos].time <= time:
                    e = None
                    if next_status == Controller.nextStatus.PAUSE:
                        e = Event(
                            Event.event.PAUSE,
                            time,
                            connection.id,
                        )
                    else:
                        e = Event(
                            Event.event.DEPARTURE,
                            time,
                            connection.id,
                        )
                    e.connection = connection
                    self.__events.insert(pos + 1, e)
                    break
        elif self.__current_event.type == Event.event.DEPARTURE:
            next_status, time, connection = self.__controller.unassignConnection(
                self.__current_event.connection, self.__clock
            )
            # if next_status == Controller.nextStatus.RESUME:
            #     for pos in range(len(self.__events) - 1, -1, -1):
            #         if self.__events[pos].time <= time:
            #             e = Event(
            #                 Event.event.RESUME,
            #                 time,
            #                 connection.id,
            #             )
            #             e.connection = connection
            #             self.__events.insert(pos + 1, e)
            #             break
        self.__events.pop(0)
        self.print_row(self.__current_event)

        return self.__rtn_allocation

    def init(self):
        self.__initReady = True
        self.__clock = 0
        self.__arrival_variable = np.random.default_rng(self.__seedArrive)
        self.__departure_variable = np.random.default_rng(self.__seedDeparture)
        self.__x_variable = np.random.default_rng(self.__seedX)
        self.__y_variable = np.random.default_rng(self.__seedY)
        self.__z_variable = np.random.default_rng(self.__seedZ)
        self.__random_wait_variable = np.random.default_rng(self.__seedZ)
        self.__capacity_required_variable = np.random.default_rng(self.__seedZ)
        self.__events.append(
            Event(
                Event.event.ARRIVE,
                self.__arrival_variable.exponential(self.__lambdaS),
                self.__numberOfConnections,
            )
        )
        self.__numberOfConnections += 1
        self.__allocatedConnections = 0
        self.__controller.init()
        if (
            self.__controller.scenario.numberOfVLeds == 0
            and self.__controller.scenario.numberOfRFs == 0
        ):
            raise ("The scenario does not have any Vleds or RFs")
        for _ in range(self.__controller.scenario.numberOfVLeds):
            self.__users_by_vlc.append(0)
        for _ in range(self.__controller.scenario.numberOfRFs):
            self.__users_by_rf.append(0)
        return

    def run(self):
        self.print_initial_info()
        while self.__numberOfConnections <= self.__goalConnections:
            # for i in range(self.__goalConnections):
            self.event_routine()
        self.aggregated_metrics()

    def time_duration(self):
        return self.__time_duration

    def get_Blocking_Probability(self):
        blocking = round(
            1 - self.__allocatedConnections / self.__numberOfConnections, 2
        )
        return blocking

    def set_allocation_algorithm(self, alloc_alg):
        self.__controller.allocator = alloc_alg

    @property
    def scenario(self):
        return self.__controller.scenario

    def aggregated_metrics(self):
        print("Number of users connected to each VLed")
        for i in range(self.__controller.scenario.numberOfVLeds):
            id = self.__controller.scenario.vleds[i].ID
            print(f"VLed {id}: {self.__users_by_vlc[id]}")

        print("Number of users connected to each RF")
        for i in range(self.__controller.scenario.numberOfRFs):
            id = self.__controller.scenario.rfs[i].ID
            print(f"RF {id}: {self.__users_by_rf[id]}")
