import random

class Human:
    def __init__(self, X, Y, Z):
        self.x = X
        self.y = Y
        self.z = Z
        self.thirst = 100
        self.hunger = 100
        self.energy = 100
        self.health = 100

    def move(self, X, Y, Z):
        energyused = abs(self.x - X) + abs(self.z - Z) // 5

        self.x = X
        self.y = Y
        self.z = Z
