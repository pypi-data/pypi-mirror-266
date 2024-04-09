import pytest
from astropy.table import QTable

from ctao_cr_spectra.definitions import (
    CRAB_HEGRA,
    CRAB_MAGIC_JHEAP2015,
    IRFDOC_ELECTRON_SPECTRUM,
    IRFDOC_PROTON_SPECTRUM,
    PDG_ALL_PARTICLE,
)


@pytest.mark.parametrize(
    ("spectrum", "expected_repr"),
    [
        (CRAB_HEGRA, "PowerLaw(2.83e-11 1 / (TeV s cm2) * (E / 1.0 TeV)**-2.62)"),
        (
            CRAB_MAGIC_JHEAP2015,
            "LogParabola(3.23e-11 1 / (TeV s cm2) * (E / 1.0 TeV)**(-2.47 + -0.24 * "
            "log10(E / 1.0 TeV))",
        ),
        (PDG_ALL_PARTICLE, "PowerLaw(18000.0 1 / (GeV s sr m2) * (E / 1.0 GeV)**-2.7)"),
        (
            IRFDOC_PROTON_SPECTRUM,
            "PowerLaw(9.8e-06 1 / (TeV s sr cm2) * (E / 1.0 TeV)**-2.62)",
        ),
        (
            IRFDOC_ELECTRON_SPECTRUM,
            "PowerLawWithExponentialGaussian(2.385e-09 1 / (TeV s sr cm2) * (E / 1.0 TeV)**-3.43 *"
            " (1 + 1.95 * (exp(Gauss(log10(E / 1.0 TeV), -0.101, 0.741)) - 1))",
        ),
    ],
)
def test_spectrum_repr(spectrum, expected_repr):
    actual_repr = repr(spectrum)
    assert actual_repr == expected_repr


def test_dampe_p_he_spectrum():
    # Define the path to the ECSV file
    file_path = "src/ctao_cr_spectra/resources/dampe_p+he_2019.ecsv"
    # Read the ECSV file using QTable
    dampe_data = QTable.read(file_path, format="ascii.ecsv")
    # Assert that the data is read successfully
    assert len(dampe_data) > 0
