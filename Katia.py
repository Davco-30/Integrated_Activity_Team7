import mesa

# Data visualization tools.
import seaborn as sns

# Has multi-dimensional arrays and matrices. Has a large collection of
# mathematical functions to operate on these arrays.
import numpy as np

# Data manipulation and analysis.
import pandas as pd

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import random
import matplotlib.pyplot as plt

class CarAgent(mesa.Model):
    def __init__(self, unique_id, model, start_parking, target_parking):
        super().__init__(unique_id, model)
        self.start_parking = start_parking
        self.target_parking = target_parking
        self.state = "moving"  # Puede ser "moving" o "waiting"
        self.direction = "right"  # Dirección inicial
        self.position = model.parking_lot_map[start_parking]  # Inicia en el estacionamiento

    def step(self):
        # Verificar semáforo en posición actual
        if self.needs_to_wait():
            self.state = "waiting"
        else:
            self.state = "moving"
            self.move()

    def needs_to_wait(self):
        """Revisa el semáforo en la posición actual"""
        for semaphore in self.model.semaphores.values():
            if self.position in semaphore.positions and semaphore.light_state == "red":
                return True
        return False

    def move(self):
        """Realiza el movimiento según la dirección y las coordenadas de la calle"""
        if self.state == "moving":
            # Aquí debes implementar la lógica de dirección y calles específicas
            # Ejemplo para moverse hacia la derecha:
            new_position = (self.position[0] + 1, self.position[1])
            if self.model.grid.is_cell_empty(new_position) and self.is_within_street_bounds(new_position):
                self.model.grid.move_agent(self, new_position)
                self.position = new_position

    def is_within_street_bounds(self, position):
        """Verifica si la posición está dentro de una calle válida"""
        # Implementa la lógica específica para verificar límites de las calles
        return True

class Car(mesa.Agent):
    def __init__(self, unique_id, start_parking, target_parking, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.start_parking = start_parking
        self.target_parking = target_parking
        self.state = "idle"
        self.direction = None



        self.down_positions = [
            [(8, 0), (8, 12)], [(14, 0), (14, 12)], [(18, 0), (18, 12)],
            [(8, 16), (8, 23)], [(14, 16), (14, 23)], [(18, 16), (18, 23)]
        ]

        self.up_positions = [
            [(2, 23), (2, 12)], [(12, 23), (12, 12)], [(16, 23), (16, 12)]
        ]

        self.left_positions = [
            [(23, 2), (12, 2)], [(23, 12), (12, 12)], [(23, 16), (12, 16)]
        ]

        self.right_positions = [
            [(0, 8), (12, 8)], [(0, 14), (12, 14)], [(0, 18), (12, 18)],
            [(16, 8), (23, 8)], [(16, 14), (23, 14)], [(16, 18), (23, 18)]
        ]

        self.pos = start_parking #posicion Inicio, hay que cambiar a que inicie en algun estacionamiento


    def step(self):
        cell_state = self.model.cell_states[self.pos]
        if cell_state['Occupancy']:
            self.state = "idle"
            cell_state['Occupancy'] = False #if the cell is occupied it wont move
            if self.direction == "right":
              self.move_right()
            elif self.direction == "left":
                self.move_left()
            elif self.direction == "down":
                self.move_down()
            elif self.direction == "up":
                self.move_up()
        else:
            self.move()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        self.state = "idle"

    def move_down(self):
        """Mueve el agente hacia abajo siguiendo las coordenadas."""
        for street in self.vertical_streets_down:
            start, end = street
            if start[0] == self.pos[0] and start[1] <= self.pos[1] <= end[1]:  # Misma columna y dentro de la calle
                new_position = (self.pos[0], self.pos[1] + 1)  # Mueve una celda hacia abajo
                if new_position[1] <= end[1]:  # Asegura que no se salga del límite de la calle
                    self.model.grid.move_agent(self, new_position)
                    self.pos = new_position
                return
    def move_up(self):
        """Mueve el agente hacia arriba siguiendo las coordenadas."""
        for street in self.vertical_streets_up:
            start, end = street
            if start[0] == self.pos[0] and end[1] <= self.pos[1] <= start[1]:  # Misma columna y dentro de la calle
                new_position = (self.pos[0], self.pos[1] - 1)  # Mueve una celda hacia arriba
                if new_position[1] >= end[1]:  # Asegura que no se salga del límite de la calle
                    self.model.grid.move_agent(self, new_position)
                    self.pos = new_position
                return

    def move_left(self):
        """Mueve el agente hacia la izquierda siguiendo las coordenadas."""
        for street in self.horizontal_streets_left:
            start, end = street
            if start[1] == self.pos[1] and end[0] <= self.pos[0] <= start[0]:  # Mismo nivel y dentro de la calle
                new_position = (self.pos[0] - 1, self.pos[1])  # Mueve una celda a la izquierda
                if new_position[0] >= end[0]:  # Asegura que no se salga del límite de la calle
                    self.model.grid.move_agent(self, new_position)
                    self.pos = new_position
                return

    def move_right(self):
        """Mueve el agente hacia la derecha siguiendo las coordenadas."""
        # Encuentra la calle en la que está el agente
        for street in self.horizontal_streets_right:
            start, end = street
            if start[1] == self.pos[1] and start[0] <= self.pos[0] <= end[0]:  # Mismo nivel y dentro de la calle
                new_position = (self.pos[0] + 1, self.pos[1])  # Mueve una celda a la derecha
                if new_position[0] <= end[0]:  # Asegura que no se salga del límite de la calle
                    self.model.grid.move_agent(self, new_position)
                    self.pos = new_position
                return
