from whitebox_workflows import LicenseType, Raster, WbEnvironmentBase
from .utils import LicenseError, print_tool_header

def sieve(wbe: WbEnvironmentBase, input_raster: Raster, threshold: int = 1, zero_background: bool = False) -> Raster:
    if wbe.license_type != LicenseType.WbWPro:
        raise LicenseError()
    
    reset_verbose = wbe.verbose
    if wbe.verbose:
        print_tool_header("sieve")
        print("\nPerforming operation...")

    wbe.verbose = False # suppress the output from each of the workflow components

    clump = wbe.clump(input_raster, diag=True, zero_background=False)
    area, report = wbe.raster_area(clump, units="cells", zero_background=False)
    mask = area >= threshold
    mask = mask.con('value==0', mask.configs.nodata, mask)
    sieved = wbe.nibble(input_raster, mask)

    if zero_background:
        sieved = (input_raster != 0.0) * sieved

    wbe.verbose = reset_verbose

    return sieved