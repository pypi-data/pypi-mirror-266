from scipy.constants import *


def wavelength_to_wavenumber(lambda_):
    return 1 / lambda_


def nm_to_per_cm(lambda_):
    return wavelength_to_wavenumber(lambda_ * 1e-9) / 1e2


def percm_to_nm(nu):
    return 1 / (nu * 1e2) * 1e9


def wavelength_to_energy(lambda_):
    return h * c / lambda_


def energy_to_wavelength(E):
    return h * c / E


def energy_to_wavenumber(E):
    return E / (h * c)


def wavenumber_to_energy(nu):
    return h * c * nu


def wavenumber_to_wavelength(nu):
    return 1 / nu


def wavelength_to_angular_frequency(lambda_):
    return 2 * pi * c / lambda_


def shift_to_photon_energy(delta_nu, lambda_l):
    return wavenumber_to_energy(wavelength_to_wavenumber(lambda_l) + delta_nu)


def shift_to_wavelength(delta_nu, lambda_l):
    return energy_to_wavelength(
        wavenumber_to_energy(delta_nu) + wavelength_to_energy(lambda_l)
    )


def wavelength_to_shift(lambda_, lambda_l):
    return wavelength_to_wavenumber(lambda_) - wavelength_to_wavenumber(lambda_l)
