from ast import Return
import mesa
import numpy as np
class Car(mesa.Agent):
    def _init_(self, unique_id, start_parking, target_parking, model):
        super()._init_(model)
        self.unique_id = unique_id
        self.start_parking = start_parking
        self.target_parking = target_parking
        self.state = "idle"
        self.direction = None
        self.last_pos = None
        self.exited_parking = False

        # Movement restrictions
        self.y_change_down = [0, 1, 12, 13] + self.generate_range(15, 22, 6, 7) #15 y 21 son filas, 6 y 7 son columnas
        self.y_change_up = [14, 15, 22, 23] + self.generate_range(22, 15, 18, 19) + self.generate_range(12, 1, 6, 7)
        self.x_change_left = [0, 1, 12, 13] + self.generate_range(6, 7, 22, 15) + self.generate_range(5, 6, 12, 7) + self.generate_range(18, 19, 6, 1)
        self.x_change_right = [14, 15, 22, 23] + self.generate_range(18, 19, 7, 12)


    def generate_range(self, start_x, end_x, start_y, end_y):
        cells = []
        if start_x <= end_x:
            x_range = range(start_x, end_x + 1)
        else:
            x_range = range(start_x, end_x - 1, -1)

        if start_y <= end_y:
            y_range = range(start_y, end_y + 1)
        else:
            y_range = range(start_y, end_y - 1, -1)

        for x in x_range:
            for y in y_range:
                cells.append((x, y))

        return cells


    def step(self):
        if not self.exited_parking:
          self.exit_parking()
        else:
          if self.pos != self.target_parking:
            self.move()
          else:
            self.state = "arrived"
            self.direction = None
            print(f"Car {self.unique_id} has reached its target parking at {self.target_parking}. No more moves.")


    def exit_parking(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)

        valid_steps = [
            step for step in possible_steps
            if self.model.grid.properties["city_objects"].data[step] == 0
        ]

        if valid_steps:
            new_position = self.random.choice(valid_steps)
            self.model.grid.properties["city_objects"].set_cell(self.pos, 0)
            self.model.grid.move_agent(self, new_position)
            self.model.grid.properties["city_objects"].set_cell(new_position, -1)
            self.exited_parking = True
            self.state = "moving"
            print(f"Car {self.unique_id} exited parking to {new_position}.")
        else:
            print(f"Car {self.unique_id} cannot exit parking from {self.pos}.")


    def move(self):
        #print(f"Car starts at {self.start_parking} and goes to {self.target_parking}")
        print(f"Car {self.unique_id} at position {self.pos} moving in direction {self.direction}")

        adjacent_cells = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)

        possible_adjacent_cells = [
            step for step in adjacent_cells
            if self.model.grid.properties["city_objects"].data[step] == 0
        ]

        print(f"Adjacent cells: {adjacent_cells}. Possible cells: {possible_adjacent_cells}")

        if self.target_parking in possible_adjacent_cells:
            print(f"Car {self.unique_id} is adjacent to target parking. Moving directly to {self.target_parking}.")
            self.model.grid.properties["city_objects"].set_cell(self.pos, 0)
            self.last_pos = self.pos
            self.model.grid.move_agent(self, self.target_parking)
            self.model.grid.properties["city_objects"].set_cell(self.target_parking, -1)

            self.state = "moving"
            print(f"Car {self.unique_id} moved to target parking at {self.target_parking}.")
        else:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            valid_steps = [step for step in possible_steps if self.is_valid_step(step)]

            if not valid_steps:
                print(f"No valid steps for car {self.unique_id} at position {self.pos}.")
                self.state = "idle"
                return

            new_position = self.random.choice(valid_steps)
            self.update_direction(new_position)

            self.model.grid.properties["city_objects"].set_cell(self.pos, 0)
            self.last_pos = self.pos
            self.model.grid.move_agent(self, new_position)
            self.model.grid.properties["city_objects"].set_cell(new_position, -1)
            self.state = "moving"
            print(f"Car {self.unique_id} moved to {new_position}")


    def can_move(self):
        current_position = self.pos
        cell_value = self.model.grid.properties["city_objects"].data[current_position]

        if cell_value == 18:
            return True

        if cell_value == 19:
            for neighbor in self.model.grid.iter_neighbors(current_position, moore=False, include_center=False):
                if isinstance(neighbor, SemaphoreAgent) and neighbor.light_state == "green":
                    return True
            return False

        return True


    def is_valid_step(self, step):
        current_x, current_y = self.pos
        step_x, step_y = step

        if self.last_pos and step == self.last_pos:
            return False

        cell_value = self.model.grid.properties["city_objects"].data[step]
        if cell_value == 19:
            for neighbor in self.model.grid.iter_neighbors(step, moore=False, include_center=False):
                if isinstance(neighbor, SemaphoreAgent) and neighbor.light_state == "green":
                    return True
            else:
                return False

        # Restricciones para columnas completas (y_change_down y y_change_up)
        if step_y in self.y_change_down[:4]:
            if step_x > current_x:
                return True

        if step_y in self.y_change_up[:4]:
            if step_x < current_x:
                return True

        # Restricciones para filas completas (x_change_left y x_change_right)
        if step_x in self.x_change_left[:4]:
            if step_y < current_y:
                return True

        if step_x in self.x_change_right[:4]:
            if step_y > current_y:
                return True

        # Restricciones para regiones específicas (rectángulos)
        if (step_x, step_y) in self.y_change_down[4:]:
            if step_x > current_x:
                return True

        if (step_x, step_y) in self.y_change_up[4:]:
            if step_x < current_x:
                return True

        if (step_x, step_y) in self.x_change_left[4:]:
            if step_y < current_y:
                return True

        if (step_x, step_y) in self.x_change_right[4:]:
            if step_y > current_y:
                return True

        return False


    def update_direction(self, new_position):
        if new_position[1] < self.pos[1]:
            self.direction = "left"
        elif new_position[1] > self.pos[1]:
            self.direction = "right"
        elif new_position[0] < self.pos[0]:
            self.direction = "up"
        elif new_position[0] > self.pos[0]:
            self.direction = "down"



class SemaphoreAgent(mesa.Agent):
    """An agent representing a traffic semaphore"""

    def _init_(self, unique_id, model, positions, green_duration=5, red_duration=5, paired_semaphore=None):
        super()._init_(model)
        self.positions = positions
       # self.light_state = "green" if unique_id % 2 == 0 else "red"
        self.light_state = "yellow"
        self.green_duration = green_duration
        self.red_duration = red_duration
        self.step_counter = 0
        self.nearby_cars = []


    def update_state(self):
        for position in self.positions:
            if self.light_state == "green":
                  state_value = 18
            elif self.light_state == "yellow":
                  state_value = 25
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

    def _init_(self, cars, seed=None):
        super()._init_(seed=seed)
        self.num_cars = cars
        self.cars_list = []
        self.grid = mesa.space.MultiGrid(24, 24, False)
        self.roundabout_cells = [(13, 13), (14, 13), (13, 14), (14, 14)]
        self.initialize_city_objects()
        self.initialize_semaphores()
        self.initialize_cars()
        self.steps = 0

    def initialize_cars(self):
      # Only 17 existing parking lots
      if self.num_cars > 17:
          raise ValueError("All parking lots have been assigned to a car. No more spaces.")

      for i in range(self.num_cars):
        start_parking = self.parking_lots[i % len(self.parking_lots)]
        if i == len(self.parking_lots) - 1:
          target_parking = self.parking_lots[0]
        else:
          target_parking = self.parking_lots[i + 1]

        """ # Assign target_parking lots randomly
        # Remove the selected parking lot from the available list
        target_parking = random.choice(target_parking_lots)   # Assign the random choice from the available
        available_parking_lots.remove(target_parking)"""

        car = Car(unique_id=-(i+1), start_parking=start_parking, target_parking=target_parking, model=self)
        self.cars_list.append(car)
        self.grid.place_agent(car, start_parking)
        print(f"Car {i + 1}: Start {start_parking}, Target {target_parking}")


    def initialize_semaphores(self):
        self.semaphores = {}
        #Define semaphores coordinates
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
        self.parking_lots = [(9, 2), (2, 3), (17, 3), (11, 4), (20, 4), (6, 5), (8, 8), (21, 9), (4, 10), (11, 10), (16, 10), (2, 17), (17, 17), (19, 17), (5, 20), (8, 20), (19, 20)]
        for parking_id, (x, y) in enumerate(self.parking_lots, start = 1):
            position = (x, y)
            value = self.grid.properties["city_objects"].data[position]
            if value == 0:
              self.grid.properties["city_objects"].set_cell(position, parking_id)
              self.parking_lot_map[parking_id] = position

        #Define cars coordinates
        for car in self.cars_list:
          position = car.pos
          value = self.grid.properties["city_objects"].data[position]
          if value is not None:
            self.grid.properties["city_objects"].set_cell(position, -1)

        # Define roundabout coordinates
        for position in self.roundabout_cells:
            self.grid.properties["city_objects"].set_cell(position, 21)


    def update_roundabout(self):
        for position in self.roundabout_cells:
            current_value = self.grid.properties["city_objects"].data[position]
            if current_value != -1:
                self.grid.properties["city_objects"].set_cell(position, 21)

    def step(self):
      print("Step ", self.steps)
      for semaphore in self.semaphores.values():
          semaphore.toggle_light()
      self.agents.shuffle_do("step")
      self.update_roundabout()
      print(self.grid.properties["city_objects"].data)
      all_arrived = all(car.state == "arrived" for car in self.cars_list)
      if all_arrived:
          print("All cars have parked.")
          self.running = False
        