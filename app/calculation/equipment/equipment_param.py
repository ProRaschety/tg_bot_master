

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
