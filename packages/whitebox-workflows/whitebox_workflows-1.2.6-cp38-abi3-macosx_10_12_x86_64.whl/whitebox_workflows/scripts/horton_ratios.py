from math import log, log2, exp
from typing import Tuple
from whitebox_workflows import PhotometricInterpretation, RasterDataType, Raster, WbEnvironmentBase
from .utils import print_tool_header

def horton_ratios(wbe: WbEnvironmentBase, dem: Raster, streams_raster: Raster) -> Tuple[float, float, float, float]:
    
    reset_verbose = wbe.verbose
    if wbe.verbose:
        print_tool_header("horton_ratios")
        print("\nPerforming operation...")

    wbe.verbose = False # suppress the output from each of the workflow components
    
    esri_pntr = False
    zero_background = True

    if reset_verbose:
        print("Calculating the D8 pointer raster...")
    d8_pntr = wbe.d8_pointer(dem, esri_pntr)

    if reset_verbose:
        print("Calculating the stream order raster...")
    strahler_order = wbe.strahler_stream_order(d8_pntr, streams_raster, esri_pntr, zero_background)

    if reset_verbose:
        print("Calculating the stream link ID raster...")
    out_configs = dem.configs
    out_configs.data_type = RasterDataType.I16
    out_configs.photometric_interp = PhotometricInterpretation.Categorical
    stream_link_id = wbe.new_raster(out_configs)
    num_inflowing = wbe.new_raster(out_configs)

    dx = (1, 1, 1, 0, -1, -1, -1, 0)
    dy = (-1, 0, 1, 1, 1, 0, -1, -1)
    inflowing_neighbour = (16, 32, 64, 128, 1, 2, 4, 8)
    channel_heads = []
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            so = strahler_order[row, col]
            if so > 0.0:
                inflowing = 0
                for n in range(8):
                    fd = d8_pntr[row + dy[n], col + dx[n]]
                    if fd == inflowing_neighbour[n] and streams_raster[row + dy[n], col + dx[n]] > 0.0:
                        inflowing += 1
                
                if inflowing == 0: # It's a channel head
                    channel_heads.append((row, col))
                
                num_inflowing[row, col] = inflowing
                

    link_id = 0
    while len(channel_heads) > 0:
        (row, col) = channel_heads.pop(0)
        link_id += 1
        so = strahler_order[row, col]
        row_n = row
        col_n = col
        flag = True
        while flag:
            stream_link_id[row_n, col_n] = link_id

            fd = d8_pntr[row_n, col_n]
            if fd > 0.0:
                n = int(log2(fd))
                row_n += dy[n]
                col_n += dx[n]
                if strahler_order[row_n, col_n] > 0: # It's still a stream cell
                    num_inflowing[row_n, col_n] -= 1
                    if stream_link_id[row_n, col_n] < 1.0: # It hasn't yet been assigned
                        if num_inflowing[row_n, col_n] < 1.0: # We've solved all inflowing cells
                            if strahler_order[row_n, col_n] != so: # We've encountered a differing stream order
                                so = strahler_order[row_n, col_n]
                                link_id += 1
                        else:
                            flag = False
                    else:
                        flag = False
                else:
                    flag = False
            else:
                flag = False


    if reset_verbose:      
        print("Calculating the stream length raster...")
    stream_length = wbe.stream_link_length(d8_pntr, stream_link_id, esri_pntr, zero_background)
    
    if reset_verbose:
        print("Calculating the drainage area raster...")
    drainage_area = wbe.d8_flow_accum(d8_pntr, out_type = "CA", log_transform = False, clip = False, input_is_pointer = True, esri_pntr = esri_pntr)

    if reset_verbose:
        print("Calculating the stream link slope raster...")
    stream_link_slope = wbe.stream_link_slope(d8_pntr, stream_link_id, dem, esri_pntr, zero_background)



    max_order = 0
    link_order = {}
    link_length = {}
    link_area = {}
    link_slope = {}
    old_progress = -1 # initialize the variable
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            id = stream_link_id[row, col]
            if id > 0.0:
                order = int(strahler_order[row, col])
                if order > max_order:
                    max_order = order

                link_order[id] = order
                link_length[id] = stream_length[row, col] 
                link_area[id] = max(link_area.get(id, 0.0), drainage_area[row, col])
                link_slope[id] = stream_link_slope[row, col]
                
        # Update the progress once we've completed another 1% of points.
        progress = int((row + 1.0) / dem.configs.rows * 100.0)
        if progress != old_progress and reset_verbose:
            old_progress = progress
            print(f'Progress: {progress}%')

    #####################
    # Bifurcation ratio #
    #####################
    stream_num = [0] * max_order
    for id in link_order:
        so = link_order[id]
        stream_num[so-1] += 1

    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_xx = 0.0
    sum_yy = 0.0
    n = 0.0
    for so in range(max_order):
        sn = stream_num[so]
        if sn > 0.0:
            x = so + 1.0
            y = log(sn)

            sum_x += x
            sum_y += y
            sum_xy += x * y
            sum_xx += x * x
            sum_yy += y * y
            n += 1.0


    slope = (n * sum_xy - (sum_x * sum_y)) / (n * sum_xx - (sum_x * sum_x))

    bifurcation_ratio = exp(-slope)


    #######################
    # Stream-length ratio #
    #######################

    # We need to calculate the mean length for each stream order
    total_length = [0] * max_order
    for id in link_length:
        so = link_order[id]
        length = link_length[id]
        total_length[so-1] += length

    average_length = []
    for so in range(max_order):
        sn = stream_num[so]
        average_length.append(total_length[so]/ sn)

    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_xx = 0.0
    sum_yy = 0.0
    n = 0.0
    for so in range(max_order):
        sn = stream_num[so]
        if sn > 0.0:
            x = so + 1.0
            y = log(total_length[so] / sn)

            sum_x += x
            sum_y += y
            sum_xy += x * y
            sum_xx += x * x
            sum_yy += y * y
            n += 1.0


    slope = (n * sum_xy - (sum_x * sum_y)) / (n * sum_xx - (sum_x * sum_x))

    length_ratio = exp(slope)


    #######################
    # Drainage-area ratio #
    #######################

    # We need to calculate the mean drainage area for each stream order
    total_area = [0] * max_order
    for id in link_area:
        so = link_order[id]
        area = link_area[id]
        total_area[so-1] += area

    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_xx = 0.0
    sum_yy = 0.0
    n = 0.0
    for so in range(max_order):
        sn = stream_num[so]
        if sn > 0.0:
            x = so + 1.0
            y = log(total_area[so] / sn)

            sum_x += x
            sum_y += y
            sum_xy += x * y
            sum_xx += x * x
            sum_yy += y * y
            n += 1.0


    slope = (n * sum_xy - (sum_x * sum_y)) / (n * sum_xx - (sum_x * sum_x))

    area_ratio = exp(slope)


    ######################
    # Stream-slope ratio #
    ######################

    # We need to calculate the mean link slope for each stream order
    total_slope = [0] * max_order
    for id in link_slope:
        so = link_order[id]
        slope = link_slope[id]
        total_slope[so-1] += slope

    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_xx = 0.0
    sum_yy = 0.0
    n = 0.0
    for so in range(max_order):
        sn = stream_num[so]
        if sn > 0.0:
            x = so + 1.0
            y = log(total_slope[so] / sn)

            sum_x += x
            sum_y += y
            sum_xy += x * y
            sum_xx += x * x
            sum_yy += y * y
            n += 1.0


    slope = (n * sum_xy - (sum_x * sum_y)) / (n * sum_xx - (sum_x * sum_x))

    slope_ratio = exp(-slope)


    wbe.verbose = reset_verbose

    return (bifurcation_ratio, length_ratio, area_ratio, slope_ratio)

