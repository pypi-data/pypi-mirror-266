"""AWS ECR Repository/Algorithm names"""
from enum import Enum


class Algorithm_Names(Enum):
    """Enum class to define Libera Algorithm Names"""
    l2cf = 'l2-cloud-fraction'
    l2_stf = 'l2-ssw-toa'
    adms = 'libera-adms'
    l2_surface_flux = 'l2-ssw-surface-flux'
    l2_firf = 'l2-far-ir-toa-flux'
    unfilt = 'l1c-unfiltered'
    spice_az = 'libera_spice_az'
    spice_el = 'libera-spice-el'
    spice_jpss = 'jpss-spice'
    pds_ingest = 'l0-ingest-docker-repo'
