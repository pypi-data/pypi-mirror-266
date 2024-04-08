from whitebox_workflows import LicenseType, Raster, WbEnvironmentBase
from .utils import LicenseError, print_tool_header

def nibble(wbe: WbEnvironmentBase, input_raster: Raster, mask: Raster, use_nodata: bool = False, nibble_nodata: bool = True) -> Raster:
    if wbe.license_type != LicenseType.WbWPro:
        raise LicenseError()
    
    reset_verbose = wbe.verbose
    if wbe.verbose:
        print_tool_header("nibble")
        print("\nPerforming operation...")

    wbe.verbose = False # suppress the output from each of the workflow components
    
    # Nodata values and zero values are both treated the same in the mask layer
    mask = mask.con('value==nodata', 0.0, 1.0)

    # Find the nodata values in the input raster
    input_nodata_mask = input_raster.con('value==nodata', 1.0, 0.0)
    input_nodata = input_raster.configs.nodata

    max_class_val = input_raster.configs.maximum
        
    if use_nodata:
        # Reset nodata cells in the input raster to some arbitrary, but 
        # previously unused, class value. This is necessary because the 
        # eculidean_allocation function will simply ignore nodata values.
        # This way eculidean_allocation will treat input raster nodata values
        # like they are non-background values.
        input_raster = input_raster.con('value==nodata', max_class_val + 1.0, input_raster) 
    else:
        # Convert all nodata values in the input raster to 0.0, so that it
        # is treated like background values by euclidean_allocation. This
        # will be rectified after the allocation.
        input_raster = input_raster.con('value==nodata', 0.0, input_raster)
    
    tmp1 = input_raster * mask
    nibble = wbe.euclidean_allocation(tmp1)

    if use_nodata:
        nibble = nibble.con(f"value=={max_class_val + 1.0}", input_nodata, nibble)
    else:
        nibble = (mask*input_nodata_mask).con('value==1.0', input_nodata, nibble)

    if nibble_nodata:
        tmp1 = (mask==0.0)*input_nodata_mask
        nibble = tmp1.con('value==1.0', input_nodata, nibble)

    wbe.verbose = reset_verbose

    return nibble