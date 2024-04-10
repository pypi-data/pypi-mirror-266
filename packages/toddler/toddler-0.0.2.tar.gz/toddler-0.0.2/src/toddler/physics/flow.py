import numpy as np
from toddler.physics.const import *


def slm_to_moles(slm):
    """Converts a mass flow rate in Standard Liters per Minute (SLM) to a molar flow rate in mol/s."""
    return slm * (1e-3 / 60) * atm / R / 273


def plug_flow_average_mass_flux(slm, r):
    """Calculates the mass flux in a plug flow reactor in moles/s/m^2"""
    return slm_to_moles(slm) / (np.pi * r**2)


def plug_flow_velocity(slm, r, T=300, p=atm):
    """Calculates the velocity of a plug flow reactor in m/s"""
    return plug_flow_average_mass_flux(slm, r) / pressure_to_molar_density(atm, T)
