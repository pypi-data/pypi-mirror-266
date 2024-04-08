from whitebox_workflows import Lidar, WbEnvironmentBase, whitebox_workflows

def strip_last_return_points(wbe: WbEnvironmentBase, lidar: Lidar) -> Lidar:
    num_points = lidar.header.get_num_points()

    # Create a new lidar data set.
    lidar_out = wbe.new_lidar(lidar.header)
    lidar_out.vlr_data = lidar.vlr_data

    print('Filtering point data...')
    old_progress = -1 # initialize the variable
    for i in range(num_points):
        point_data, time, colour, waveform = lidar.get_point_record(i)

        # Now let's filter the data based on return data...
        if not point_data.is_last_return(): # point_data.is_first_return() or point_data.is_intermediate_return():
            lidar_out.add_point(point_data, time, colour, waveform)

        # Update the progress once we've completed another 1% of points.
        progress = int((i + 1.0) / num_points * 100.0)
        if progress != old_progress:
            old_progress = progress
            print(f'Progress: {progress}%')

    return lidar_out