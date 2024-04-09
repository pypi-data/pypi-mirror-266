"""Reference Cosmic Ray Spectra definitions."""
from .definitions import (
    CRAB_HEGRA,
    CRAB_MAGIC_JHEAP2015,
    IRFDOC_ELECTRON_SPECTRUM,
    IRFDOC_PROTON_SPECTRUM,
    PDG_ALL_PARTICLE,
    DAMPE_P_He_SPECTRUM,
)
from .spectral import (
    DIFFUSE_FLUX_UNIT,
    POINT_SOURCE_FLUX_UNIT,
    LogParabola,
    PowerLaw,
    PowerLawWithExponentialGaussian,
    TableInterpolationSpectrum,
    calculate_event_weights,
)
from .version import __version__

__all__ = [
    "__version__",
    "calculate_event_weights",
    "POINT_SOURCE_FLUX_UNIT",
    "DIFFUSE_FLUX_UNIT",
    "PowerLaw",
    "LogParabola",
    "PowerLawWithExponentialGaussian",
    "TableInterpolationSpectrum",
    "CRAB_HEGRA",
    "CRAB_MAGIC_JHEAP2015",
    "PDG_ALL_PARTICLE",
    "IRFDOC_PROTON_SPECTRUM",
    "IRFDOC_ELECTRON_SPECTRUM",
    "DAMPE_P_He_SPECTRUM",
]
