import os
import sys
from copy import deepcopy

import astropy.units as u
import numpy as np
import pytest
from astropy.table import QTable

from ctao_cr_spectra.spectral import (
    LogParabola,
    PowerLaw,
    PowerLawWithExponentialGaussian,
    TableInterpolationSpectrum,
    calculate_event_weights,
    cone_solid_angle,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

POINT_FLUX_UNIT = "cm-2 s-1 TeV-1"


@pytest.fixture()
def powerlaw_instance():
    normalization = 1e-11 * u.Unit(POINT_FLUX_UNIT)
    index = -2.3
    e_ref = 1 * u.TeV
    return PowerLaw(normalization, index, e_ref)


@pytest.fixture()
def powerlaw_instance_sr(powerlaw_instance):
    new_instance = deepcopy(powerlaw_instance)
    new_instance.normalization /= u.sr
    return new_instance


def test_is_diffuse(powerlaw_instance, powerlaw_instance_sr):
    assert powerlaw_instance_sr.is_diffuse is True
    assert powerlaw_instance.is_diffuse is False


def test_cone_solid_angle():
    angle = 30 * u.deg
    expected_solid_angle = 2 * np.pi * (1 - np.cos(angle.to(u.rad))) * u.sr
    assert cone_solid_angle(angle) == expected_solid_angle


def test_calculate_event_weights(powerlaw_instance):
    true_energy_values = np.array([1, 2, 3]) * u.TeV
    modified_pl = deepcopy(powerlaw_instance)
    modified_pl.index = -2.0
    weights = calculate_event_weights(
        true_energy_values,
        powerlaw_instance,
        modified_pl,
    )
    expected_weights = np.array([1, 0.8122524, 0.71922309])

    np.testing.assert_allclose(weights, expected_weights)


def test_powerlaw_init(powerlaw_instance):
    assert isinstance(powerlaw_instance, PowerLaw)


def test_powerlaw_call(powerlaw_instance):
    energy = 1 * u.TeV
    flux = powerlaw_instance(energy)
    expected_flux = (
        powerlaw_instance.normalization
        * (energy / powerlaw_instance.e_ref) ** powerlaw_instance.index
    )
    assert flux.value == pytest.approx(expected_flux.value)


def test_powerlaw_repr(powerlaw_instance):
    expected_repr = f"PowerLaw({powerlaw_instance.normalization} * (E / {powerlaw_instance.e_ref})**{powerlaw_instance.index})"
    assert repr(powerlaw_instance) == expected_repr


def test_powerlaw_integrate_time(powerlaw_instance):
    obs_time = 100 * u.s
    integrated_powerlaw = powerlaw_instance.integrate_time(obs_time)
    expected_normalization = powerlaw_instance.normalization * obs_time
    assert integrated_powerlaw.normalization == expected_normalization


def test_powerlaw_integrate_area(powerlaw_instance):
    observatory_area = 1000 * u.cm**2
    integrated_powerlaw = powerlaw_instance.integrate_area(observatory_area)
    expected_normalization = powerlaw_instance.normalization * observatory_area
    assert integrated_powerlaw.normalization == expected_normalization


def test_powerlaw_integrate_energy(powerlaw_instance):
    energy_min = 0.1 * u.TeV
    energy_max = 10 * u.TeV
    integrated_flux = powerlaw_instance.integrate_energy(energy_min, energy_max)
    expected_flux = (
        (
            energy_max ** (powerlaw_instance.index + 1)
            - energy_min ** (powerlaw_instance.index + 1)
        )
        / (
            (powerlaw_instance.index + 1)
            * powerlaw_instance.e_ref**powerlaw_instance.index
        )
        * powerlaw_instance.normalization
    )
    assert integrated_flux == expected_flux


def test_powerlaw_compute_events_rate(powerlaw_instance, powerlaw_instance_sr):
    inner = 0 * u.deg
    outer = 1 * u.deg
    area = 1e4 * u.cm**2
    energy_min = 0.1 * u.TeV
    energy_max = 10 * u.TeV
    events_rate = powerlaw_instance_sr.compute_events_rate(
        inner,
        outer,
        area,
        energy_min,
        energy_max,
    )
    integrated_flux = (
        powerlaw_instance_sr.integrate_cone(inner, outer)
        .integrate_area(area)
        .integrate_energy(energy_min, energy_max)
    )
    expected_events_rate = integrated_flux.decompose(bases=[u.cm, u.TeV, u.s, u.sr])
    assert events_rate == expected_events_rate

    # assert compute_events_rate works also for point-like flux
    integrated_flux = powerlaw_instance.compute_events_rate(
        inner,
        outer,
        area,
        energy_min,
        energy_max,
    )
    assert integrated_flux.unit == "1/s"


def test_powerlaw_integrate_cone_error(powerlaw_instance, powerlaw_instance_sr):
    with pytest.raises(
        ValueError,
        match="Outer angle 0.0 deg has to be larger than inner angle 10.0 deg.",
    ):
        powerlaw_instance_sr.integrate_cone(10 * u.deg, 0 * u.deg)

    with pytest.raises(
        ValueError,
        match="Can only integrate a diffuse flux over solid angle.",
    ):
        powerlaw_instance.integrate_cone(0 * u.deg, 10 * u.deg)


def test_powerlaw_compute_number_events(powerlaw_instance_sr):
    inner = 0 * u.deg
    outer = 1 * u.deg
    obs_time = 1 * u.hour
    area = 1e4 * u.cm**2
    energy_min = 0.1 * u.TeV
    energy_max = 10 * u.TeV
    number_of_events = powerlaw_instance_sr.compute_number_events(
        inner,
        outer,
        obs_time,
        area,
        energy_min,
        energy_max,
    )
    events_rate = powerlaw_instance_sr.compute_events_rate(
        inner,
        outer,
        area,
        energy_min,
        energy_max,
    )
    expected_number_of_events = events_rate * obs_time
    assert number_of_events == expected_number_of_events


# Define fixture for LogParabola instance
@pytest.fixture()
def log_parabola():
    normalization = 1e-11 * u.Unit(POINT_FLUX_UNIT)
    a = -2.3
    b = 0.1
    e_ref = 1 * u.TeV
    return LogParabola(normalization, a, b, e_ref)


# Test LogParabola initialization
def test_logparabola_init(log_parabola):
    assert log_parabola.normalization == 1e-11 * u.Unit(POINT_FLUX_UNIT)
    assert log_parabola.a == -2.3
    assert log_parabola.b == 0.1
    assert log_parabola.e_ref == 1 * u.TeV


# Test LogParabola __call__ method
def test_logparabola_call(log_parabola):
    energy = 1 * u.TeV
    flux = log_parabola(energy)
    expected_flux = 1e-11 * (energy / (1 * u.TeV)) ** (
        -2.3 + 0.1 * np.log10(energy / (1 * u.TeV))
    )
    assert flux == pytest.approx(expected_flux)


# Test LogParabola __repr__ method
def test_logparabola_repr(log_parabola):
    expected_repr = (
        "LogParabola(1e-11 1 / (TeV s cm2) * (E / 1.0 TeV)**(-2.3 + 0.1 * "
        "log10(E / 1.0 TeV))"
    )
    assert repr(log_parabola) == expected_repr


# Define fixture for PowerLawWithExponentialGaussian instance
@pytest.fixture()
def powerlaw_with_exponential_gaussian():
    normalization = 1e-11 * u.Unit(POINT_FLUX_UNIT)
    index = -2.3
    e_ref = 1 * u.TeV
    f = 0.1
    mu = 1
    sigma = 0.2
    return PowerLawWithExponentialGaussian(normalization, index, e_ref, f, mu, sigma)


# Test __call__ method
def test_powerlaw_with_exponential_gaussian_call(powerlaw_with_exponential_gaussian):
    energy = 1 * u.TeV
    flux = powerlaw_with_exponential_gaussian(energy)
    assert flux.unit == u.Unit(POINT_FLUX_UNIT)


# Test __repr__ method
def test_powerlaw_with_exponential_gaussian_repr(powerlaw_with_exponential_gaussian):
    expected_repr = (
        "PowerLawWithExponentialGaussian(1e-11 1 / (TeV s cm2) * "
        "(E / 1.0 TeV)**-2.3 * (1 + 0.1 * (exp(Gauss(log10(E / 1.0 TeV), 1, 0.2)) - 1))"
    )
    actual_repr = repr(powerlaw_with_exponential_gaussian)
    assert actual_repr == expected_repr


# Test initialization
def test_powerlaw_with_exponential_gaussian_init(powerlaw_with_exponential_gaussian):
    assert powerlaw_with_exponential_gaussian.normalization == 1e-11 * u.Unit(
        POINT_FLUX_UNIT,
    )
    assert powerlaw_with_exponential_gaussian.index == -2.3
    assert powerlaw_with_exponential_gaussian.e_ref == 1 * u.TeV
    assert powerlaw_with_exponential_gaussian.f == 0.1
    assert powerlaw_with_exponential_gaussian.mu == 1
    assert powerlaw_with_exponential_gaussian.sigma == 0.2


# Sample energy and flux values for testing
energy_values = np.array([1, 2, 3]) * u.TeV
flux_values = np.array([1e-11, 2e-11, 3e-11]) * u.Unit(POINT_FLUX_UNIT)
reference_energy = 1 * u.TeV


# Define fixture for TableInterpolationSpectrum instance
@pytest.fixture()
def table_interpolation_spectrum():
    return TableInterpolationSpectrum(energy_values, flux_values)


# Test __call__ method
def test_table_interpolation_spectrum_call(table_interpolation_spectrum):
    energy = 1 * u.TeV
    flux = table_interpolation_spectrum(energy)
    assert flux.unit == u.Unit(POINT_FLUX_UNIT)


# Test from_table classmethod
def test_table_interpolation_spectrum_from_table():
    table = QTable({"energy": energy_values, "flux": flux_values})
    spectrum = TableInterpolationSpectrum.from_table(table)
    assert isinstance(spectrum, TableInterpolationSpectrum)
    assert np.all(spectrum.energy == energy_values)
    assert np.all(spectrum.flux == flux_values)


# Test from_file classmethod (assuming the file exists)
def test_table_interpolation_spectrum_from_file(tmp_path):
    file_path = tmp_path / "test_spectrum.fits"
    QTable({"energy": energy_values, "flux": flux_values}).write(file_path)
    spectrum = TableInterpolationSpectrum.from_file(file_path)
    assert isinstance(spectrum, TableInterpolationSpectrum)
    assert np.all(spectrum.energy == energy_values)
    assert np.all(spectrum.flux == flux_values)


# Test initialization
def test_table_interpolation_spectrum_init():
    spectrum = TableInterpolationSpectrum(energy_values, flux_values)
    assert np.all(spectrum.energy == energy_values)
    assert np.all(spectrum.flux == flux_values)
    assert spectrum.log_energy
    assert spectrum.log_flux
    assert spectrum.reference_energy == reference_energy
