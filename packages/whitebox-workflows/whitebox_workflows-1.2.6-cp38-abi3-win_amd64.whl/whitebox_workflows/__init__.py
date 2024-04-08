from typing import Tuple
from .whitebox_workflows import *
from .scripts.horton_ratios import horton_ratios
from .scripts.nibble import nibble
from .scripts.ridge_and_valley_vectors import ridge_and_valley_vectors
from .scripts.sieve import sieve
from whitebox_workflows import Raster, Vector

__doc__ = whitebox_workflows.__doc__
if hasattr(whitebox_workflows, "__all__"):
    __all__ = whitebox_workflows.__all__

class WbEnvironment(WbEnvironmentBase):
    """The WbEnvironment class can be used to configure WbW settings (e.g. the working
directory, number of processors used, and verbose mode). It is also used to call
the various tool functions, which appear as methods of this class, and to read/write
spatial data."""
    def __init__(self, user_id: str = None):
        """Initializes a new WbEnvironment object with an optional user_id, i.e. a floating
license ID string used in WbW-Pro licenses.
        """
        # WbEnvironmentBase(user_id)

    def available_functions(self) -> None:
        """This function will list all of the available functions associated with a
WbEnvironment (wbe). The functions that are accessible will depend on the 
license level (WbW or WbWPro).
        """

        # Are we running a pro license?
        pro_license = self.license_type == LicenseType.WbWPro

        # Get all the non-dunder methods of WbEnvironment
        method_list = [func for func in dir(WbEnvironment) if callable(getattr(WbEnvironment, func)) and not func.startswith("__")]

        print(f"Available Methods ({self.license_type}):")

        j = 0
        s = ''
        for i in range(len(method_list)):
            val = method_list[i]
            val_len = len(f"{j}. {val}")
            is_pro_func = whitebox_workflows.is_wbw_pro_function(val)
            
            added = True
            if not is_pro_func and j % 2 == 0:
                s += f"{j+1}. {val}{' '* (50 - val_len)}"
                j += 1
            elif not is_pro_func and j % 2 == 1:
                s += f"{j+1}. {val}"
                j += 1
            elif (is_pro_func and pro_license) and j % 2 == 0:
                s += f"{j+1}. {val}{' '* (50 - val_len)}"
                j += 1
            elif (is_pro_func and pro_license) and j % 2 == 1:
                s += f"{j+1}. {val}"
                j += 1
            else:
                added = False
                

            if added and (j % 2 == 0 or i == len(method_list)-1):
                print(s)
                s = ''


    def horton_ratios(self, dem: Raster, streams_raster: Raster) -> Tuple[float, float, float, float]:
        '''This function can be used to calculate Horton's so-called laws of drainage network composition for a
input stream network. The user must specify an input DEM (which has been suitably hydrologically pre-processed
to remove any topographic depressions) and a raster stream network. The function will output a 4-element 
tuple containing the bifurcation ratio (Rb), the length ratio (Rl), the area ratio (Ra), and the slope ratio
(Rs). These indices are related to drainage network geometry and are used in some geomorphological analysis.
The calculation of the ratios is based on the method described by Knighton (1998) Fluvial Forms and Processes: 
A New Perspective.

# Code Example

```python
from whitebox_workflows import WbEnvironment

# Set up the WbW environment
wbe = WbEnvironment()
wbe.verbose = True
wbe.working_directory = '/path/to/data'

# Read the inputs
dem = wbe.read_raster('DEM.tif')
streams = wbe.read_raster('streams.tif')

# Calculate the Horton ratios
(bifurcation_ratio, length_ratio, area_ratio, slope_ratio) = wbe.horton_ratios(dem, streams)

# Outputs
print(f"Bifurcation ratio (Rb): {bifurcation_ratio:.3f}")
print(f"Length ratio (Rl): {length_ratio:.3f}")
print(f"Area ratio (Ra): {area_ratio:.3f}")
print(f"Slope ratio (Rs): {slope_ratio:.3f}")
```

# See Also
<a href="tool_help_wbwpro.md#horton_stream_order">horton_stream_order</a>

# Function Signature
```python
def horton_ratios(self, dem: Raster, streams_raster: Raster) -> Tuple[float, float, float, float]: ...
```
'''
        return horton_ratios(self, dem, streams_raster)


    def nibble(self, input_raster: Raster, mask: Raster, use_nodata: bool = False, nibble_nodata: bool = True) -> Raster:
        '''Use of this function requires a license for Whitebox Workflows for Python Professional (WbW-Pro).
Please visit www.whiteboxgeo.com to purchase a license.

The nibble function assigns areas within an input class map raster that are coincident with a mask the value 
of their nearest neighbour. Nibble is typically used to replace erroneous sections in a class map. Cells in the mask
raster that are either NoData or zero values will be replaced in the input image with their nearest non-masked
value. All input raster values in non-mask areas will be unmodified.

There are two input parameters that are related to how NoData cells in the input raster are handled during
the nibble operation. The use_nodata Boolean determines whether or not input NoData cells, not contained within masked
areas, are treated as ordinary values during the nibble. It is False by default, meaning that NoData cells 
in the input raster do not extend into nibbled areas. When the nibble_nodata parameter is True, any NoData cells
in the input raster that are within the masked area are also NoData in the output raster; when nibble_nodata is False
these cells will be nibbled.

# See Also:
<a href='https://www.whiteboxgeo.com/manual/wbw-user-manual/book/tool_help_wbwpro.html#sieve'>sieve</a>

# Function Signature
```python
def nibble(self, input_raster: Raster, mask: Raster, use_nodata: bool = False, nibble_nodata: bool = True) -> Raster:
```
'''
        return nibble(self, input_raster, mask, use_nodata, nibble_nodata)


    def ridge_and_valley_vectors(self, dem: Raster, filter_size: int = 11, ep_threshold: float = 30.0, slope_threshold: float = 0.0, min_length: int = 20) -> Tuple[Vector, Vector]:
        '''Use of this function requires a license for Whitebox Workflows for Python Professional (WbW-Pro).
Please visit www.whiteboxgeo.com to purchase a license.

This function can be used to extract ridge and channel vectors from an input digital elevation model (DEM).
The function works by first calculating elevation percentile (EP) from an input DEM using a neighbourhood size set by
the user-specified filter_size parameter. Increasing the value of filter_size can result in more continuous mapped ridge
and valley bottom networks. A thresholding operation is then applied to identify cells that have an EP less than the 
user-specified ep_threshold (valley bottom regions) and a second thresholding operation maps regions where EP is 
greater than 100 - ep_threshold (ridges). Each of these ridge and valley region maps are also multiplied by a slope 
mask created by identify all cells with a slope greater than the user-specified slope_threshold value, which is set 
to zero by default. This second thresholding can be helpful if the input DEM contains extensive flat areas, which 
can be confused for valleys otherwise. The filter_size and ep_threshold parameters are somewhat dependent on one 
another. Increasing the filter_size parameter generally requires also increasing the value of the ep_threshold. The 
ep_threshold can take values between 5.0 and 50.0, where larger values will generally result in more extensive and 
continuous mapped ridge and valley bottom networks. For many DEMs, a value on the higher end of the scale tends to 
work best.

After applying the thresholding operations, the function then applies specialized shape generalization, line thinning, 
and vectorization alorithms to produce the final ridge and valley vectors. The user must also specify the value of the
min_length parameter, which determines the minimum size, in grid cells, of a mapped line feature. The function outputs
a tuple of two vector, the first being the ridge network and the second vector being the valley-bottom network.

![](./img/ridge_and_valley_vectors.jpeg)

# Code Example

```python
from whitebox_workflows import WbEnvironment

# Set up the WbW environment
license_id = 'my-license-id' # Note, this tool requires a license for WbW-Pro
wbe = WbEnvironment(license_id)
try:
    wbe.verbose = True
    wbe.working_directory = '/path/to/data'

    # Read the input DEM
    dem = wbe.read_raster('DEM.tif')

    # Run the operation
    ridges, valleys = wbe.ridge_and_valley_vectors(dem, filter_size=21, ep_threshold=45.0, slope_threshold=1.0, min_length=25)
    wbe.write_vector(ridges, 'ridges_lines.shp')
    wbe.write_vector(valley, 'valley_lines.shp')

    print('Done!')
except Exception as e:
  print("Error: ", e)
finally:
    wbe.check_in_license(license_id)
```

# See Also:
<a href='https://www.whiteboxgeo.com/manual/wbw-user-manual/book/tool_help.html#extract_valleys'>extract_valleys</a>

# Function Signature
```python
def ridge_and_valley_vectors(self, dem: Raster, filter_size: int = 11, ep_threshold: float = 30.0, slope_threshold: float = 0.0, min_length: int = 20) -> Tuple[Raster, Raster]:
```
'''
        return ridge_and_valley_vectors(self, dem, filter_size, ep_threshold, slope_threshold, min_length)


    def sieve(self, input_raster: Raster, threshold: int = 1, zero_background: bool = False) -> Raster:
        '''Use of this function requires a license for Whitebox Workflows for Python Professional (WbW-Pro).
Please visit www.whiteboxgeo.com to purchase a license.

The sieve function removes individual objects in a class map that are less than a threshold
area, in grid cells. Pixels contained within the removed small polygons will be replaced with the nearest
remaining class value. This operation is common when generalizing class maps, e.g. those derived from an
image classification. Thus, this tool provides a similar function to the <a href='https://www.whiteboxgeo.com/manual/wbw-user-manual/book/tool_help_wbwpro.html#generalize_classified_raster'>generalize_classified_raster</a> and
<a href='https://www.whiteboxgeo.com/manual/wbw-user-manual/book/tool_help_wbwpro.html#generalize_with_similarity'>generalize_with_similarity</a> functions.

# See Also:
<a href='https://www.whiteboxgeo.com/manual/wbw-user-manual/book/tool_help_wbwpro.html#generalize_classified_raster'>generalize_classified_raster</a>, <a href='https://www.whiteboxgeo.com/manual/wbw-user-manual/book/tool_help_wbwpro.html#generalize_with_similarity'>generalize_with_similarity</a>

# Function Signature
```python
def sieve(self, input_raster: Raster, threshold: int = 1, zero_background: bool = False) -> Raster: ...
```
        '''
        return sieve(self, input_raster, threshold, zero_background)