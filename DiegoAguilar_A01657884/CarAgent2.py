class Car(mesa.Agent):
    def __init__(self, unique_id, start_parking, target_parking, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.start_parking = start_parking
        self.target_parking = target_parking
        self.state = "idle"
        self.direction = None
        self.last_pos = None
        self.exited_parking = False

        # Movement restrictions
        self.y_change_down = [0, 1, 12, 13] + self.generate_range(15, 21, 6, 7)
        self.y_change_up = [14, 15, 22, 23] + self.generate_range(22, 16, 18, 19) + self.generate_range(12, 2, 6, 7)
        self.x_change_left = [0, 1, 12, 13] + self.generate_range(6, 7, 22, 16) + self.generate_range(5, 6, 12, 7) + self.generate_range(18, 19, 6, 1)
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
        elif self.pos != self.target_parking:
            self.move()
        else:
            self.state = "idle"
            self.direction = None
            print(f"Car {self.unique_id} has reached its target parking at {self.target_parking}. Stopping the model.")
            self.model.running = False 


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
        print(f"Car starts at {self.start_parking} and goes to {self.target_parking}")
        print(f"Car {self.unique_id} at position {self.pos} moving in direction {self.direction}")

        possible_adjacent_cells = [
        (self.pos[0] - 1, self.pos[1]),
        (self.pos[0] + 1, self.pos[1]),
        (self.pos[0], self.pos[1] - 1),
        (self.pos[0], self.pos[1] + 1),
        ]

        if self.target_parking in possible_adjacent_cells:
            print(f"Car {self.unique_id} is adjacent to target parking. Moving directly to {self.target_parking}.")
            self.model.grid.properties["city_objects"].set_cell(self.pos, 0)
            self.last_pos = self.pos
            self.model.grid.move_agent(self, self.target_parking)
            self.model.grid.properties["city_objects"].set_cell(self.target_parking, -1)

            self.state = "moving"
            print(f"Car {self.unique_id} moved to target parking at {self.target_parking}.")
        else:
            print(f"Car {self.unique_id} is not adjacent to target parking. Moving normally.")
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

        if step_y == current_y:
            if step_x < current_x and current_y in self.y_change_up:
                return True
            if step_x > current_x and current_y in self.y_change_down:
                return True

        if step_x == current_x:
            if step_y < current_y and current_x in self.x_change_left: 
                return True
            if step_y > current_y and current_x in self.x_change_right: 
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
