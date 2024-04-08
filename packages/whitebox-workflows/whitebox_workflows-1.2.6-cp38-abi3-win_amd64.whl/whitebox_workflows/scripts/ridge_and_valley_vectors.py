from typing import Tuple
from whitebox_workflows import LicenseType, Raster, Vector, WbEnvironmentBase
from .utils import LicenseError, print_tool_header

def ridge_and_valley_vectors(wbe: WbEnvironmentBase, dem: Raster, filter_size: int = 11, ep_threshold: float = 30.0, slope_threshold: float = 0.0, min_length: int = 20) -> Tuple[Vector, Vector]:
    if wbe.license_type != LicenseType.WbWPro:
        raise LicenseError()
    
    reset_verbose = wbe.verbose
    if wbe.verbose:
        print_tool_header("ridge_and_valley_vectors")

    if ep_threshold < 5.0:
        ep_threshold = 5.0

    if ep_threshold > 50.0:
        ep_threshold = 50.0

    if slope_threshold < 0.0:
        slope_threshold = 0.0

    wbe.verbose = False # suppress the output from each of the workflow components
    
    if reset_verbose:
        print("Calculating EP and slope...")
    ep = wbe.elevation_percentile(dem, filter_size_x=filter_size, filter_size_y=filter_size, sig_digits=2)
    slope = wbe.slope(dem)

    if reset_verbose:
        print("\nMapping ridges and valleys...")
    ridges = (ep > (100.0 - ep_threshold))*(slope > slope_threshold)
    ridges = wbe.remove_raster_polygon_holes(ridges, 10, True) # Remove small holes
    ridges = wbe.closing(ridges, filter_size_x=5, filter_size_y=5) # Simplify the shapes
    ridge_lines = wbe.river_centerlines(ridges, min_length=min_length, search_radius=9)
    
    valleys = (ep < ep_threshold)*(slope > slope_threshold)
    valleys = wbe.remove_raster_polygon_holes(valleys, 10, True) # Remove small holes
    valleys = wbe.closing(valleys, filter_size_x=5, filter_size_y=5) # Simplify the shapes
    valley_lines = wbe.river_centerlines(valleys, min_length=min_length, search_radius=9)
    
    wbe.verbose = reset_verbose

    return (ridge_lines, valley_lines)