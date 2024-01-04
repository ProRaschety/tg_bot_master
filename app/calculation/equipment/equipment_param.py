import logging

import math as m

log = logging.getLogger(__name__)


class Equipment:
    _data = {
        "pump": {},
        "compressor": {},
        "vessel": {
            "pressure_vessel": 1,
            "technological apparatus": 2,
            "chemical reactors": 3},
        "isothermal_storage": {},
        "tank": {
            "single wall tank": {},
            "tank with outer protective shell": {},
            "double shell tank": {},
            "full seal tank": {},
            "membrane reservoir": {},
            "underground reservoir": {},
            "reservoir covered with soil": {}, },
        "heat_exchanger": {},
        "road_tanks": {},
        "rail_tanks": {}
    }

    """Геометрические параметры оборудования"""

    def __init__(self):
        pass

    def calc_volume_equipment(self,
                              height: int | float = None,
                              length: int | float = None,
                              radius: int | float = None,
                              width: int | float = None,
                              diameter: int | float = None) -> float:
        if radius and height:
            volume = m.pi * radius ** 2 * height
            log.info(f"Объем вертикального цилиндра, м3: {volume:.2f}")
        elif diameter and height:
            volume = m.pi * diameter ** 2 / 4 * height
            log.info(f"Объем вертикального цилиндра, м3: {volume:.2f}")
        elif diameter and length:
            volume = m.pi * diameter ** 2 / 4 * height
            log.info(f"Объем горизонтаьного цилиндра, м3: {volume:.2f}")
        elif width and length and height:
            volume = width * length * height
            if width == length == height:
                log.info(f"Объем куба, м3: {volume:.2f}")
            elif width != height or width != length:
                log.info(f"Объем параллелепипеда, м3: {volume:.2f}")
            elif height != length or length != width:
                log.info(f"Объем параллелепипеда, м3: {volume:.2f}")
        elif radius:
            volume = (4 / 3) * m.pi * radius ** 3
            log.info(f"Объем сферы, м3: {volume:.2f}")
        elif diameter:
            volume = (1 / 6) * m.pi * diameter ** 3
            log.info(f"Объем сферы, м3: {volume:.2f}")
        else:
            volume = None
            log.info("Введено недостаточно данных для индентификации объекта")
        return volume

    def calc_pipe_inner_diameter(self, pipe_outer_diameter, pipe_wall_thickness):
        """
        Calculate inner diameter of pipe

        Parameters
        ----------
        pipe_outer_diameter : float
            Outer diameter of pipe

        pipe_wall_thickness : float
            Wall thickness of pipe

        Returns
        -------
        pipe_inner_diameter : float
            Inner diameter of pipe
        """
        pipe_inner_diam = pipe_outer_diameter - 2 * pipe_wall_thickness
        return pipe_inner_diam

    def calc_pipe_flow_area(self, pipe_inner_diameter):
        """
        Calculate flow area of pipe

        Parameters
        ----------
        pipe_inner_diameter : float
            Inner diameter of pipe

        Returns
        -------
        pipe_flow_area : float
            Inner cross-sectional area of pipe
        """
        pipe_flow_area = m.pi * (pipe_inner_diameter / 2) ** 2
        return pipe_flow_area

    def calc_orifice_diameter(self, pipe_flow_area, leak_size_fraction):
        """
        Рассчитать диаметр круглого отверстия
        на основе дробного размера утечки в проходном участке трубы.

        Parameters
        ----------
        pipe_flow_area : float
            Inner cross-sectional area of pipe

        leak_size_fraction : float
            Leak size in terms of fraction of pipe flow area

        Returns
        -------
        leak_diameter : float
            Diameter of circular leak orifice
        """
        leak_area = pipe_flow_area * leak_size_fraction
        leak_diameter = m.sqrt(4 * leak_area / math.pi)
        return leak_diameter
