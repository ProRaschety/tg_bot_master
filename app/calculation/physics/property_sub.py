
class PropertySub:
    def __init__(self, temperature_gas=333, name_sub=None):
        self.temperature_gas: float = temperature_gas  # K
        self.name_sub: str = name_sub

    def get_property_species(self) -> dict:
        name_sub = self.name_sub

        property_species = {"molar_mass": 42.08}

        return property_species

    def calc_density_gas(self):
        molar_mass = self.get_property_species()["molar_mass"]
        temperature_gas_C = self.temperature_gas - 273
        density_gas = molar_mass / (22.413 * (1 + 0.00367 * temperature_gas_C))
        return density_gas
