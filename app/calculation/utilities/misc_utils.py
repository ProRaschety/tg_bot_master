import logging
from logging.config import dictConfig
import os
import datetime
import re

from scipy.interpolate import RectBivariateSpline, interp1d
from CoolProp import CoolProp

log = logging.getLogger(__name__)


def clean_name(name):
    """
    Преобразовать имя строки в буквенно-цифровой строчный регистр

    """
    parsed = re.sub(r'\W+', '', name.lower())
    return parsed


def get_distance_at_value(x_values, y_values, value):
    func_value = interp1d(y_values, x_values, kind='linear',
                          bounds_error=False, fill_value=0)
    return func_value(value)


def get_value_at_distance(x_values, y_values, distance):
    func_distance = interp1d(x_values, y_values, kind='linear',
                             bounds_error=False, fill_value=0)
    return func_distance(distance)
