"""Collection of pre-defined spectra."""
from importlib.resources import as_file, files

import astropy.units as u

from .spectral import (
    LogParabola,
    PowerLaw,
    PowerLawWithExponentialGaussian,
    TableInterpolationSpectrum,
)

__all__ = [
    "CRAB_HEGRA",
    "CRAB_MAGIC_JHEAP2015",
    "PDG_ALL_PARTICLE",
    "IRFDOC_PROTON_SPECTRUM",
    "IRFDOC_ELECTRON_SPECTRUM",
    "DAMPE_P_He_SPECTRUM",
]

#: Power Law parametrization of the Crab Nebula spectrum as published by HEGRA
#:
#: From "The Crab Nebula and Pulsar between 500 GeV and 80 TeV: Observations with the HEGRA stereoscopic air Cherenkov telescopes",
#: Aharonian et al, 2004, ApJ 614.2
#: doi.org/10.1086/423931
CRAB_HEGRA = PowerLaw(
    normalization=2.83e-11 / (u.TeV * u.cm**2 * u.s),
    index=-2.62,
    e_ref=1 * u.TeV,
)

#: Log-Parabola parametrization of the Crab Nebula spectrum as published by MAGIC
#:
#: From "Measurement of the Crab Nebula spectrum over three decades in energy with the MAGIC telescopes",
#: Aleksìc et al., 2015, JHEAP
#: https://doi.org/10.1016/j.jheap.2015.01.002
CRAB_MAGIC_JHEAP2015 = LogParabola(
    normalization=3.23e-11 / (u.TeV * u.cm**2 * u.s),
    a=-2.47,
    b=-0.24,
)


#: All particle spectrum
#:
#: (30.2) from "The Review of Particle Physics (2020)"
#: https://pdg.lbl.gov/2020/reviews/rpp2020-rev-cosmic-rays.pdf
PDG_ALL_PARTICLE = PowerLaw(
    normalization=1.8e4 / (u.GeV * u.m**2 * u.s * u.sr),
    index=-2.7,
    e_ref=1 * u.GeV,
)

#: Proton spectrum definition defined in the CTA Prod3b IRF Document
#:
#: From "Description of CTA Instrument Response Functions (Production 3b Simulation)", section 4.3.1
#: https://gitlab.cta-observatory.org/cta-consortium/aswg/documentation/internal_reports/irfs-reports/prod3b-irf-description
IRFDOC_PROTON_SPECTRUM = PowerLaw(
    normalization=9.8e-6 / (u.cm**2 * u.s * u.TeV * u.sr),
    index=-2.62,
    e_ref=1 * u.TeV,
)

#: Electron spectrum definition defined in the CTA Prod3b IRF Document
#:
#: From "Description of CTA Instrument Response Functions (Production 3b Simulation)", section 4.3.1
#: https://gitlab.cta-observatory.org/cta-consortium/aswg/documentation/internal_reports/irfs-reports/prod3b-irf-description
IRFDOC_ELECTRON_SPECTRUM = PowerLawWithExponentialGaussian(
    normalization=2.385e-9 / (u.TeV * u.cm**2 * u.s * u.sr),
    index=-3.43,
    e_ref=1 * u.TeV,
    mu=-0.101,
    sigma=0.741,
    f=1.950,
)

#: Proton + Helium interpolated from DAMPE measurements
#:
#: Datapoints obtained from obtained from:
#: https://inspirehep.net/files/62efc8374ffced58ea7e3a333bfa1217
#: Points are from DAMPE, up to  8 TeV.
#: For higher energies we assume a
#: flattening of the dF/dE*E^2.7 more or less in the middle of the large
#: spread of the available data reported on the same proceeding
with as_file(files("ctao_cr_spectra.resources") / "dampe_p+he_2019.ecsv") as _path:
    DAMPE_P_He_SPECTRUM = TableInterpolationSpectrum.from_file(_path)
