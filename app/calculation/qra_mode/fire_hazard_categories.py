# from ..physics.physics_utils import calc_characteristic_diameter, calc_reynolds_number
import logging


class FireHazardCategory:
    """Определние категорий по взрывопожарной и пожарной опасности"""

    def __init__(self):
        self.fire_risk: float = 10 ** -6
        self.burn_in_oxygen: bool = False

    def get_fire_category(self, type_obj: str):
        _category_out_inst = {
            "increased_explosion_and_fire_hazard": "Ан",
            "explosion_and_fire_hazard": "Бн",
            "fire_hazard": "Вн",
            "moderate_fire_hazard": "Гн",
            "reduced_fire_hazard": "Дн"
        }
        _category_room = {
            "increased_explosion_and_fire_hazard": "А",
            "explosion_and_fire_hazard": "Б",
            "fire_hazard_1": "В1",
            "fire_hazard_2": "В2",
            "fire_hazard_3": "В3",
            "fire_hazard_4": "В4",
            "moderate_fire_hazard": "Г",
            "reduced_fire_hazard": "Д"
        }
        _category_build = {
            "increased_explosion_and_fire_hazard": "А",
            "explosion_and_fire_hazard": "Б",
            "fire_hazard": "В",
            "moderate_fire_hazard": "Г",
            "reduced_fire_hazard": "Д"
        }

        if type_obj == "build":
            fire_category = _category_build
        elif type_obj == "room":
            fire_category = _category_room
        elif type_obj == "out_inst":
            fire_category = _category_out_inst
        else:
            fire_category = None
        return fire_category

    def calc_density_gas(self, temperature_gas_K: int | float, molar_mass: int | float):
        molar_mass = molar_mass
        temperature_gas_C = temperature_gas_K - 273
        density_gas = molar_mass / (22.413 * (1 + 0.00367 * temperature_gas_C))
        return density_gas

    def calc_fire_risk_equipment(self, distances=30):
        fire_risk = 10 ** -7
        return fire_risk

    def calc_excessive_pressure(self, distances=30):
        Q_cr = 45.604 * 10 ** 6  # J/kg
        Q_0 = 4.52 * 10 ** 6  # J/kg
        Z = 0.1
        mass = self.calc_mass()
        print(max(mass))
        reduced_mass = (Q_cr/Q_0) * Z * max(mass)
        pi_1 = (0.8 * (reduced_mass ** 0.33)) / distances
        pi_2 = (3.0 * (reduced_mass ** 0.66)) / distances ** 2
        pi_3 = (5.0 * reduced_mass) / distances ** 3
        excessive_pressure = 101*(pi_1 + pi_2 + pi_3)
        print(f"dP = {excessive_pressure:.2f} kPa")
        return excessive_pressure

    def calc_heat_flow(self, distances=30):
        heat_flow = 4.5
        return heat_flow

    def calc_zone_ehc(self):
        zone_ehc = 25.2
        return zone_ehc

    def calc_mass(self) -> list[float]:
        valve_closing_time = [120, 120, 120]
        d_eff = calc_characteristic_diameter(5184)
        Re = calc_reynolds_number(diameter=d_eff, velocity=3)

        # if type_substance == "СУГ":
        #     pass

        mass = [6617.8, 1899.5, 3526.3]
        return mass

    def get_property_sub(self) -> dict:
        substances = self.substances
        density_gas = self.calc_density_gas(
            temperature_gas_K=333, molar_mass=42.08)
        density_air = self.calc_density_gas(
            temperature_gas_K=293, molar_mass=28.97)
        aggregate_state: str = ["Твердое", "Жидкое", "Газообразное", "Пыль"]
        temperature_flash = 28

        property_sub = {
            "temperature_flash": 28,
            "burn_in_oxygen": False,  # False если не горит в кислороде
            "type_substance": "ГГ",
            "density_gas": density_gas,
            "aggregate_state": aggregate_state,
        }
        return property_sub


class FireCategoryBuild(FireHazardCategory):
    def __init__(self):
        self.build_type: str = "industrial"  # "storage_room"

    def get_category_room(self):
        fire_hazard_categories = None

        # if type_substance == "ГГ" or type_substance == "ЛВЖ" or burn_in_oxygen == True:
        #     if temperature_flash <= 28.0:
        #     # fire_hazard_categories = category("increased_explosion_and_fire_hazard")
        #     # fire_hazard_categories = increased_explosion_and_fire_hazard  # "Ан"
        #
        #     elif burn_in_oxigen == True:
        #         if self.fire_risk > 10 ** -6:
        # fire_hazard_categories = category("increased_explosion_and_fire_hazard")
        # fire_hazard_categories = increased_explosion_and_fire_hazard  # "Ан"
        #
        # if type_substance == "ГП" or type_substance == "ЛВЖ" or type_substance == "ГЖ" or burn_in_oxygen == True:
        #     if temperature_flash > 28 | (fire_hazard_categories != increased_explosion_and_fire_hazard):
        #         fire_hazard_categories = explosion_and_fire_hazard  # "Бн"
        #
        #     elif burn_in_oxigen == True:
        #         if fire_risk > 10 ** -6:
        #             fire_hazard_categories = explosion_and_fire_hazard  # "Бн"
        #
        # if fire_hazard_categories != increased_explosion_and_fire_hazard and fire_hazard_categories != explosion_and_fire_hazard:
        #     fire_hazard_categories = fire_hazard  # "Вн"
        #
        # if type_substance == "НГ" or burned_disposed_fuel == True:
        #     fire_hazard_categories = moderate_fire_hazard  # "Гн"
        #
        # if fire_hazard_categories == increased_explosion_and_fire_hazard:
        #     increased_explosion_and_fire_hazard = "Ан"
        # elif fire_hazard_categories == explosion_and_fire_hazard:
        #     explosion_and_fire_hazard = "Бн"
        # elif fire_hazard_categories == fire_hazard:
        #     fire_hazard = "Вн"
        # elif fire_hazard_categories == moderate_fire_hazard:
        #     moderate_fire_hazard = "Гн"
        # else:
        #     reduced_fire_hazard = "Дн"

    def get_category_build(self):
        pass


class FireCategoryOutInstall(FireHazardCategory):
    """Опеределение Категории по взрывопожароопасности по СП 12.13130 наружной установки"""

    def __init__(self, substances="Пропилен", ):
        self.substances: str = substances

    def get_fire_hazard_categories(self) -> str:
        category = FireHazardCategory.get_fire_category("out_inst")
        property_sub = self.get_property_sub()
        type_substance = property_sub["type_substance"]
        temperature_flash = property_sub["temperature_flash"]
        burn_in_oxigen = property_sub["burn_in_oxigen"]
        fire_risk = self.calc_fire_risk_equipment(distances=30)
        excessive_pressure_30m = self.calc_excessive_pressure(distances=30)
        heat_flow_30m = self.calc_heat_flow(distances=30)
        zone_ehc = self.calc_zone_ehc()

        burned_disposed_fuel = False

        fire_hazard_categories = None

        if type_substance == "ГГ" or type_substance == "ЛВЖ" or burn_in_oxigen == True:
            if temperature_flash <= 28.0:
                pass
                # fire_hazard_categories = category("increased_explosion_and_fire_hazard")
                # fire_hazard_categories = increased_explosion_and_fire_hazard  # "Ан"

            # elif burn_in_oxigen == True:
            #     if fire_risk > 10 ** -6:
            #         # fire_hazard_categories = category("increased_explosion_and_fire_hazard")
            #         # fire_hazard_categories = increased_explosion_and_fire_hazard  # "Ан"
        #
        # if type_substance == "ГП" or type_substance == "ЛВЖ" or type_substance == "ГЖ" or burn_in_oxigen == True:
        #     if temperature_flash > 28 | (fire_hazard_categories != increased_explosion_and_fire_hazard):
        #         fire_hazard_categories = explosion_and_fire_hazard  # "Бн"
        #
        #     elif burn_in_oxigen == True:
        #         if fire_risk > 10 ** -6:
        #             fire_hazard_categories = explosion_and_fire_hazard  # "Бн"
        #
        # if fire_hazard_categories != increased_explosion_and_fire_hazard and fire_hazard_categories != explosion_and_fire_hazard:
        #     fire_hazard_categories = fire_hazard  # "Вн"
        #
        # if type_substance == "НГ" or burned_disposed_fuel == True:
        #     fire_hazard_categories = moderate_fire_hazard  # "Гн"
        #
        # if fire_hazard_categories == increased_explosion_and_fire_hazard:
        #     increased_explosion_and_fire_hazard = "Ан"
        # elif fire_hazard_categories == explosion_and_fire_hazard:
        #     explosion_and_fire_hazard = "Бн"
        # elif fire_hazard_categories == fire_hazard:
        #     fire_hazard = "Вн"
        # elif fire_hazard_categories == moderate_fire_hazard:
        #     moderate_fire_hazard = "Гн"
        else:
            reduced_fire_hazard = "Дн"

        return fire_hazard_categories


class FireHazardousAreas(FireHazardCategory):
    pass


class FireExplosiveZones(FireHazardCategory):
    """Опеределение Класса зоны взрывопожароопасности по СП 423.1325800.2018"""
    pass
