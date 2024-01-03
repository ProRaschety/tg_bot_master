import logging
import json

import math as m
import numpy as np

from scipy import constants as const


class Const:
    def __init__(self):
        self.temperature_celsius: int | float = 20
        self.temperature_kelvin: int | float = const.zero_Celsius + self.temperature_celsius
        self.pressure_ambient: int | float = const.atm
