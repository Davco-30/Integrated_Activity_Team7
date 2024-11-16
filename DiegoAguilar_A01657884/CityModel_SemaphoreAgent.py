class SemaphoreAgent(mesa.Agent):
    """An agent representing a traffic semaphore"""

    def __init__(self, unique_id, model, positions, green_duration=5, red_duration=5):
        super().__init__(model)
        self.positions = positions
        self.light_state = "green" if unique_id % 2 == 0 else "red"
        self.green_duration = green_duration 
        self.red_duration = red_duration      
        self.step_counter = 0
       
       
    def update_state(self):
        for position in self.positions:
            if self.light_state == "green":
                  state_value = 18
            else:
                  state_value = 19
            self.model.grid.properties["city_objects"].set_cell(position, state_value)


    def toggle_light(self):
        self.update_state()
        self.step_counter += 1
        if (self.light_state == "green" and self.step_counter >= self.green_duration) or (self.light_state == "red" and self.step_counter >= self.red_duration):
            if self.light_state == "red":
                self.light_state = "green"
            else:
                self.light_state = "red"
            self.step_counter = 0
            self.update_state()


class CityModel(mesa.Model):
    """A model of a city with some number of cars, semaphores, buildings, parking lots and a roundabout."""

    def __init__(self, cars, seed=None):
        super().__init__(seed=seed)
        self.num_cars = cars
        self.grid = mesa.space.MultiGrid(24, 24, False)
        self.initialize_city_objects()
        self.initialize_semaphores()

    def initialize_semaphores(self):
        self.semaphores = {}
        semaphores_positions = {
            1: [(18, 2), (19, 2)],
            2: [(17, 0), (17, 1)],
            3: [(22, 5), (23, 5)],
            4: [(2, 6), (2, 7)],
            5: [(0, 8), (1, 8)],
            6: [(7, 6), (7, 7)],
            7: [(5, 8), (6, 8)],
            8: [(21, 6), (21, 7)],
            9: [(14, 17), (15, 17)],
            10: [(16, 18), (16, 19)]
        }

        for semaphore_id, positions in semaphores_positions.items():
            semaphore = SemaphoreAgent(unique_id=semaphore_id, model = self, positions=positions)
            self.semaphores[semaphore_id] = semaphore
            self.grid.place_agent(semaphore, positions[0])


    def initialize_city_objects(self):
        """Initialize buildings, parking lots and a roundabout on the grid using PropertyLayer."""
        city_objects_layer = mesa.space.PropertyLayer("city_objects", self.grid.width, self.grid.height, np.int64(0), np.int64)
        self.grid.properties["city_objects"] = city_objects_layer

        #Define buildings coordinates
        buildings = [(2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (10, 2), (11, 2), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3),
                     (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (2, 5), (3, 5), (4, 5), (5, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5),
                     (2, 8), (3, 8), (4, 8), (7, 8), (9, 8), (10, 8), (11, 8), (2, 9), (3, 9), (4, 9), (7, 9), (8, 9), (9, 9), (10, 9), (11, 9), (2, 10), (3, 10), (7, 10),
                     (8, 10), (9, 10), (10, 10), (2, 11), (3, 11), (4, 11), (7, 11), (8, 11), (9, 11), (10, 11), (11, 11), (16, 2), (17, 2), (20, 2), (21, 2), (16, 3), (20, 3),
                     (21, 3), (16, 4), (17, 4), (21, 4), (16, 5), (17, 5), (20, 5), (21, 5), (16, 8), (17, 8), (20, 8), (21, 8), (16, 9), (17, 9), (20, 9), (17, 10), (20, 10), (21, 10),
                     (16, 11), (17, 11), (20, 11), (21, 11), (2, 16), (3, 16), (4, 16), (5, 16), (8, 16), (9, 16), (10, 16), (11, 16), (3, 17), (4, 17), (5, 17), (8, 17), (9, 17), (10, 17),
                     (11, 17), (2, 18), (3, 18), (4, 18), (5, 18), (8, 18), (9, 18), (10, 18), (11, 18), (2, 19), (3, 19), (4, 19), (5, 19), (8, 19), (9, 19), (10, 19), (11, 19), (2, 20),
                     (3, 20), (4, 20), (9, 20), (10, 20), (11, 20), (2, 21), (3, 21), (4, 21), (5, 21), (8, 21), (9, 21), (10, 21), (11, 21), (16, 16), (17, 16), (18, 16), (19, 16), (20, 16),
                     (21, 16), (16, 17), (18, 17), (20, 17), (21, 17), (16, 20), (17, 20), (18, 20), (20, 20), (21, 20), (16, 21), (17, 21), (18, 21), (19, 21), (20, 21), (21, 21)]
        for (x, y) in buildings:
            position = (x, y)
            if self.grid.properties["city_objects"].data[x, y] == 0:
                self.grid.properties["city_objects"].set_cell(position, 20)

        #Define parking lots coordinates
        self.parking_lot_map = {}
        parking_lots = [(9, 2), (2, 3), (17, 3), (11, 4), (20, 4), (6, 5), (8, 8), (21, 9), (4, 10), (11, 10), (16, 10), (2, 17), (17, 17), (19, 17), (5, 20), (8, 20), (19, 20)]
        for parking_id, (x, y) in enumerate(parking_lots, start = 1):
            position = (x, y)
            self.grid.properties["city_objects"].set_cell(position, parking_id)
            self.parking_lot_map[parking_id] = position

        #Define roundabout coordinates
        roundabout = [(13, 13), (14, 13), (13, 14), (14, 14)]
        for position in roundabout:
            self.grid.properties["city_objects"].set_cell(position, 21)

    def step(self):
        for semaphore in self.semaphores.values():
            semaphore.toggle_light()
            print(f"Semaphore {semaphore.unique_id} has a state of: {semaphore.light_state}") #Debug
        print(self.grid.properties["city_objects"].data)
