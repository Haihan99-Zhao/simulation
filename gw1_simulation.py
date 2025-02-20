from typing import Callable, List, Dict, Any # We need to initialize the elemends of the class and this helps us to do that. 
from bisect import bisect_right
import random

print("simulation.py loaded successfully")
class Driver:
    def __init__(self, driver_id: int, location: list, working_time: float, offline_time: float, available_state: bool, earning:float):
        self.driver_id = driver_id         # each driver's id
        self.location = location           # available location for each driver
        self.working_time = working_time   # the time when driver starts being available
        self.offline_time = offline_time   # driver's working time, we plus 
        self.available_state = available_state           # 0 means idle, but 1 means busy
        self.earning = earning

    def update_location(self, new_location: list):
        """
        直接覆盖当前的坐标
        """
        self.location = new_location

    def update_earning(self, new_earning: float):
        self.earning = new_earning

class Rider:
    def __init__(self, rider_id: int, demand_location: list, destination: None, patience_time: float,demand_state: bool, assigned_driver: None):
        self.rider_id = rider_id       # 乘客唯一标识
        self.demand_location = demand_location  # 请求发出地点
        self.destination = destination         # 目的地（可选）
        self.patience_time = patience_time     # allowable waiting time for a driver
        self.demand_state = demand_state
        self.assigned_driver = assigned_driver            # 分配到的司机（初始为None）


class Distributions:
    def __init__(self, simulation):
        self.simulation = simulation
    
    def generate_Rider_DemandTime(self)->float:
        '''
        Generate a DemandTime for each Rider, lambda = 30
        '''
        rate = 30  # λ (rate parameter)
        Rider_Demandtime = random.expovariate(rate)  # Generate exponential RV
        return Rider_Demandtime
    
    def generate_Rider_Patience_time(self)->float:
        '''
        Generate a WaitingTime for each Rider, lambda = 5
        '''
        rate = 5  # λ (rate parameter)
        Rider_WaitingTime = random.expovariate(rate)  # Generate exponential RV
        return Rider_WaitingTime
    
    def generate_Driver_AvailableTime(self)->float:
        '''
        Generate a availableTime for each Driver, lambda = 3
        '''
        rate = 3 # λ (rate parameter)
        Driver_AvailableTime = random.expovariate(rate)  # Generate exponential RV
        return Driver_AvailableTime
    
    def generate_Driver_OfflineTime(self)->float:
        '''
        Generate a OfflineTime for each Driver, uniformly distributed between 5 and 8 hours
        '''
        a = 5
        b = 8
        Driver_OfflineTime = random.random.uniform(a, b)  # Generate exponential RV
        return Driver_OfflineTime
    
    def generate_Rider_Location(self)->list:
        '''
        Generate a location for each rider, uniformly distributed between 0 and 20 mile in Squareshire
        '''
        a = 0
        b = 20
        Rider_Locationx = random.random.uniform(a, b)  # Generate exponential RV
        Rider_Locationy= random.random.uniform(a, b)  # generate a location uniformly distributed between 0 and 20
        return [Rider_Locationx, Rider_Locationy]
    
    def generate_Driver_Location(self)->list:
        '''
        Generate a available location for each driver, uniformly distributed between 0 and 20 mile in Squareshire
        '''
        a = 0
        b = 20
        Driver_Locationx = random.random.uniform(a, b)
        Driver_Locationy= random.random.uniform(a, b)  # generate a location uniformly distributed between 0 and 20
        return [Driver_Locationx, Driver_Locationy]
    
    def generate_Destination_Location(self)->list:
        '''
        Generate a destination location, uniformly distribut ed between 0 and 20 mile in Squareshire
        '''
        a = 0
        b = 20
        Destination_Locationx = random.random.uniform(a, b)
        Destination_Locationy= random.random.uniform(a, b)  # generate a location uniformly distributed between 0 and 20
        return [Destination_Locationx, Destination_Locationy]                 
    
    def generate_Pickup_Time(self)->float:
        '''
        Generate a OfflineTime for each Driver, uniformly distributed between 5 and 8 hours
        '''
        a = 5
        b = 8
        Driver_OfflineTime = random.random.uniform(a, b)  # Generate exponential RV
        return Driver_OfflineTime
            
class Simulation:
    def __init__(self, handlers, distributions: Any = None, Driver: Any = None, Rider: Any = None):
        self.simulation_length = 1000 # Termination time
        self.current_time = 0         # Keep tracks of simulation clock
        self.money = 0                # Keep tracks of earnings

        self.riders_size = 0   # used
        self.rider_waiting_size = 0 # used
        self.driver_idle_size = 0   # used
        self.drivers_size = 0 #used
        self.rider_unsatisfied = 0 # used
        self.rider_satisfied = 0 #

        self.next_driver_id = 1
        self.next_rider_id = 1
    
        self.system_size = 0          # Keeps track of Q(t)
        self.ATM_state = 0            # Keeps track of B(t)
        self.area_system_size = 0
        self.area_ATM_state = 0
        
        self.event_calendar: List[Dict[str, Any]] = [] # Event calendar is initialized as empty
        self.distributions: Dict[str, Callable[[Any], None]] = {}
        self.event_handlers: Dict[str, Callable[[Any], None]] = {} # The event_handlers list will associate each event with the modules/functions necessary to execute that event. This list is empty and designed to be dynamic to flexiblity add or remove event types.
        
        self.drivers: Dict[int, Driver] = {}     # 用字典存储司机，key为司机ID
        self.riders: Dict[int, dict[str,Any]] = {}

        if distributions:
            self.register_distribution("rider_demand", distributions.generate_Rider_DemandTime)
            self.register_distribution("rider_waiting", distributions.generate_Rider_WaitingTime)
            self.register_distribution("driver_available", distributions.generate_Driver_AvailableTime)
            self.register_distribution("driver_offline", distributions.generate_Driver_OfflineTime)

            self.register_distribution("rider_location", distributions.generate_Rider_Location)
            self.register_distribution("driver_location", distributions.generate_Driver_Location)
            self.register_distribution("destination_location", distributions.generate_Destination_Location)
            self.register_distribution("pickup", distributions.generate_Driver_Location)
            self.register_distribution("service", distributions.generate_Destination_Location)           

        if handlers:
            self.register_event_handler("arrival", handlers.handle_arrival)
            self.register_event_handler("departure", handlers.handle_departure)
            self.register_event_handler("termination", handlers.handle_termination)
            
            self.register_event_handler("arrival", handlers.handle_arrival)
            self.register_event_handler("departure", handlers.handle_departure)
            self.register_event_handler("termination", handlers.handle_termination)


        first_arrival = self.current_time + self.distributions["inter-arrival"]()
        first_arrival = self.current_time + self.distributions["inter-arrival"]()
        first_arrival = self.current_time + self.distributions["inter-arrival"]()

        first_Rider_demand = self.current_time + self.distributions[]
        self.add_event(first_arrival, "arrival", None)
        self.add_event(self.simulation_length, "termination", None)
        self.add_driver(self.current_time, self.distributions['driver_offline'](),self.distributions['driver_location']())
    # 在simulation中，更新drivers和riders的字典，用于存储每个出现在系统中driver和rider的状态
    # 需要继续更新，每个driver 和 rider 的状态

    def output_driver_id(self):
        driver_index = self.next_driver_id
        self.next_driver_id += 1
        return driver_index
    
    def add_driver(self, driver: Driver):
        driver = Driver(self.output_driver_id(), self.distributions['driver_location'](), self.current_time, self.distributions['driver_offline'],True,0)
        self.drivers[driver.driver_id] = driver  

    def output_rider_id(self):
        rider_index = self.next_rider_id
        self.next_rider_id += 1
        return rider_index
        
    def add_rider(self, rider: Any):
        rider = Rider(self.output_rider_id(), self.distributions['rider_location'](), self.distributions['destination_location'](),self.distributions['rider_waiting'],True)
        self.riders[rider.rider_id] = rider  
 

    def add_driver_event(self, event_time:float, event_group: str, individual_id:int, event_type: str, event_data: Any = None)->None:
        event = {'time': event_time,'group': event_group, 'id': individual_id, 'type': event_type, 'data': event_data}
        index = bisect_right([e['time'] for e in self.event_calendar], event_time)
        self.event_calendar.insert(index, event)   

    def add_rider_event(self, event_time:float, event_group: str, individual_id:int, event_type: str, event_data: Any = None)->None:
        event = {'event_group': event_group, 'id': individual_id, 'time': event_time, 'type': event_type, 'data': event_data}
        index = bisect_right([e['time'] for e in self.event_calendar], event_time)
        self.event_calendar.insert(index, event) 

    def register_distribution(self, random_quantity: str, handler: Callable[[Any], None]):
        self.distributions[random_quantity] = handler
        
        
    def register_event_handler(self, event_type: str, handler: Callable[[Any], None]) -> None:
        # This function allows us to dynamically add event types to the list.
        self.event_handlers[event_type] = handler
        
    def progress_time(self) -> None:
        if not self.event_calendar:
            print("No more events to process.")
            return

        next_event = self.event_calendar.pop(0)
        previous_time = self.current_time
        self.current_time = next_event['time']
        event_type = next_event['type']
        event_data = next_event['data']
        
        self.area_system_size += self.system_size*(self.current_time - previous_time)
        self.area_ATM_state += self.ATM_state*(self.current_time - previous_time)

        print(f"Processing event: {event_type} at time {self.current_time}")

        if event_type in self.event_handlers:
            self.event_handlers[event_type](event_data)
        else:
            print(f"No handler registered for event type: {event_type}")
            
            
    def run(self) -> None:
        """
        Run the simulation until all events are processed or a 'termination' event is encountered.
        """
        print(self.event_calendar)
        terminate_sim = 0
        while self.event_calendar:
            next_event = self.event_calendar[0]  # Peek at the next event
            if next_event['type'] == "termination":
                terminate_sim = 1
            self.progress_time()
            if terminate_sim == 1:
                break
        if terminate_sim == 0:
            print("No more event to execute!")


class EventHandlers:
    def __init__(self, simulation):
        self.simulation = simulation
    
    def handle_arrival(self, event_data: Any):
        Execute_functions.execute_arrival(self.simulation)
    
    def handle_departure(self, event_data: Any):
        Execute_functions.execute_departure(self.simulation)
        
    def handle_termination(self, event_data: Any):
        Execute_functions.execute_termination(self.simulation)

class Execute_functions:                   
    def execute_demand(sim_instance:Simulation):
        sim_instance.riders_size += 1
        if sim_instance.driver_idle_size > 0:
            sim_instance.driver_idle_size -= 1

            time_for_pickingup = sim_instance.current_time + sim_instance.distributions["pickup"]()
            sim_instance.add_rider_event(time_for_pickingup,'waiting', None)
        else:
            sim_instance.rider_waiting_size += 1
            patience_time = sim_instance.current_time + sim_instance.distributions['rider_waiting']()
            sim_instance.add_event(patience_time,'waiting', None)

        next_demand_time = sim_instance.current_time + sim_instance.distribution['rider_demand']()
        sim_instance.add_event(next_demand_time, "demand", None)

    def execute_pickup(sim_instance:Simulation):
        '''
        当我们接到顾客后 我们只需要生成服务完成的时间即可
        '''
        service_time = sim_instance.current_time + sim_instance.distribution['service']()
        sim_instance.add_event(service_time, "service", None)

    def execute_waiting(sim_instance:Simulation):

        '''
        正常来说 如果到了patience time乘客还没有被接走他就会直接离开 并记录一次不满意
        '''
        sim_instance.riders_size -= 1
        sim_instance.unsatisfied += 1

    def execute_arrival(sim_instance:Simulation):
        '''
        当我们把人送到destination后 我们将driver idle size变成+1 然后我们也记录一次满意的情况
        无论什么情况我们都需要把这个顾客送到目的地 所以我们在execute offline 的函数中才会考虑如
        果我们的车仍在service 的状态
        '''
        sim_instance.riders_size -= 1
        sim_instance.satisfied += 1
        
        sim_instance.driver_idle_size += 1

    def execute_available(sim_instance:Simulation):
        '''
        生成空闲的driver 并且需要对于每一个driver 也要生成其下班的时间 确定生成位置
        并且识别当前的系统中是否有未上车的旅客 并以此安排任务
        '''

    def execute_offline(sim_instance:Simulation):
        '''
        如果有driver 需要下线 需要先判断是仍在service 如果没有 我们则对这个司机在系统中删除
        因此我们的driver size会-1
        '''


    def execute_departure(sim_instance:Simulation):
        sim_instance.system_size -= 1
        if sim_instance.system_size > 0:
            departure_time = sim_instance.current_time + sim_instance.distributions["service"]()
            sim_instance.add_event(departure_time, "departure", None)
        else:
            sim_instance.ATM_state = 0
        

    def execute_termination(sim_instance:Simulation):
        print(f"Average System Size is {sim_instance.area_system_size/sim_instance.simulation_length}")
        print(f"Average Utilization is {sim_instance.area_ATM_state/sim_instance.simulation_length}")
            
            
                
                



    # def add_driver(self, current_time: float, offline_time: float, location: list)->None:
    #     info = {
    #             'location': location,
    #             'available_time': current_time, 
    #             'offline_time': offline_time,
    #             'money': 0,
    #             'available_state': True
    #             }
    #     index = self.next_driver_id
    #     self.next_driver_id += 1  # 更新计数器
    #     self.drivers[index] = info  

    # def add_rider(self, current_time: float, patience_time: float, location: list, destination: list)->None:
    #     info = {
    #             'demand_location': location, 
    #             'patience_time': patience_time, 
    #             'destination': destination,
    #             'demand_time': current_time,
    #             'waiting_state': True
    #             }
    #     index = self.next_rider_id
    #     self.next_rider_id += 1  # 更新计数器
    #     self.riders[index] = info                 
            
                
            
            