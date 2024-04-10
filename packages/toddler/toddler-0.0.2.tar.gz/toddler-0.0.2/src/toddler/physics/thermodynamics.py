from toddler.physics.const import *


def pressure_to_density(pressure, temperature=293):
    return pressure * N_A / (R * temperature)


def pressure_to_molar_density(pressure, temperature=293):
    return pressure / (R * temperature)
