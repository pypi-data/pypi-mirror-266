import os
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from .convert_units import convert_units




def time_list(datasets):
    """
    Reads all the datasets and reutrns the timestamps listed in there.
    
    Args:
    - datasets (xarray): The loaded dataset opened using xarray.

    Returns:
    - timestamps (array): An array of numpy datimetime64 timestamps for all the time entries in the datasets.
    """
    
    # Extract timestamps from each file
    timestamps = []
    for ds, filename in datasets:
        file = str(filename)
        for timestamp in ds['time'].values:
            #mtime=str(get_mtime(ds,timestamp))
            #timestamps.append((str(timestamp),mtime,file))
            timestamps.append(timestamp)
    return timestamps

def var_list(datasets):
    """
    Reads all the datasets and reutrns the variables listed in there.
    
    Args:
    - datasets (xarray): The loaded dataset opened using xarray.

    Returns:
    - variables (array): An array of variable entries in the datasets.
    """
    
    unique_variables = set()

    for ds, filename in datasets:
        # Convert the current dataset's variables to a set
        current_variables = set(ds.data_vars)
        # Union the current variables with the existing unique variables
        unique_variables = unique_variables.union(current_variables)
    variables = sorted(unique_variables)
    return variables    

def var_time (datasets, variable_name, selected_time, selected_unit=None):
    for ds, filenames in datasets:
        if selected_time in ds['time'].values:
            # Extract variable attributes
            variable_unit = ds[variable_name].attrs.get('units', 'N/A')
            variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
            selected_ut = ds['ut'].sel(time=selected_time).values.item() / (1e9 * 3600)
            selected_mtime = get_mtime(ds,selected_time)
            filename = filenames
            data = ds[variable_name].sel(time=selected_time)

            not_all_nan_indices = ~np.isnan(data.values).all(axis=1)
            variable_values = data.values[not_all_nan_indices, :]

            if selected_unit != None:
                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                

            try:
                levs_ilevs = data.lev.values[not_all_nan_indices]
            except:
                levs_ilevs = data.ilev.values[not_all_nan_indices]

            return(variable_values, levs_ilevs, variable_unit, variable_long_name, selected_ut, selected_mtime, filename)
    print(f"{selected_time} not found.")
    return None

def check_var_dims(ds, variable_name):
    # Check if the variable exists in the dataset
    if variable_name in ds:
        # Get the dimensions of the variable
        var_dims = ds[variable_name].dims

        # Check for 'lev' and 'ilev' in dimensions
        if 'lev' in var_dims:
            return 'lev'
        elif 'ilev' in var_dims:
            return 'ilev'
        else:
            return None
    else:
        return 'Variable not found in dataset'

def arr_lev_lon (datasets, variable_name, selected_time, selected_lat, selected_unit= None, plot_mode = False):
    """
    Extract data from the dataset based on the given variable name, timestamp, and lev value.
    
    Args:
    - datasets (xarray): The loaded dataset opened using xarray.
    - variable_name (str): Name of the variable to extract.
    - selected_time (str): Timestamp to filter the data.
    - selected_lev (float): Level value to filter the data.
    
    Returns:
    - variable_values (xarray): An xarray object of variable values for the given timestamp and latitude.
    - lons (xarray): An xarray object of longitude values.
    - levs_ilevs (xarray): An xarray object of selected lev or ilev values.
    - variable_unit (str): Unit of the variable.
    - variable_long_name (str): Long name of the variable.
    - selected_ut (float): UT value in hours for selected_time.
    - selected_mtime (array): An array containing Day, Hour, Min of the model run
    """
    
    
    # Load the dataset using xarray
    #ds = xr.open_dataset(dataset)   
    for ds, filenames in datasets:
        if selected_time in ds['time'].values:
            # Extract variable attributes
            variable_unit = ds[variable_name].attrs.get('units', 'N/A')
            variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
            selected_ut = ds['ut'].sel(time=selected_time).values.item() / (1e9 * 3600)
            selected_mtime = get_mtime(ds,selected_time)
            filename = filenames
            if selected_lat == "mean":
                # if selected_lon is "mean", then we calculate the mean over all longitudes.
                data = ds[variable_name].sel(time=selected_time).mean(dim='lat')
            else:
                data = ds[variable_name].sel(time=selected_time, lat=selected_lat, method='nearest')
            lons = data.lon.values

            not_all_nan_indices = ~np.isnan(data.values).all(axis=1)
            variable_values = data.values[not_all_nan_indices, :]

            if selected_unit != None:
                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                

            try:
                levs_ilevs = data.lev.values[not_all_nan_indices]
            except:
                levs_ilevs = data.ilev.values[not_all_nan_indices]
  
            if plot_mode == True:    
                return variable_values, lons, levs_ilevs, selected_lat, variable_unit, variable_long_name, selected_ut, selected_mtime, filename
            else:
                return variable_values
    print(f"{selected_time} not found.")
    return None



def arr_lat_lon(datasets, variable_name, selected_time, selected_lev_ilev = None, selected_unit = None, plot_mode = False):
    if selected_lev_ilev != None:
        selected_lev_ilev = float(selected_lev_ilev)
    if isinstance(selected_time, str):
        selected_time = np.datetime64(selected_time, 'ns')
    first_pass = True
    for ds, filenames in datasets:
        if first_pass == True:
            lev_ilev = check_var_dims(ds, variable_name)
        if lev_ilev == 'lev':
            first_pass == False
            if selected_time in ds['time'].values:
                if 'lev' not in ds[variable_name].dims:
                    raise ValueError("The variable "+variable_name+" doesn't use the dimensions 'lat', 'lon', 'lev'")
                    return 0

                # Extract variable attributes
                variable_unit = ds[variable_name].attrs.get('units', 'N/A')
                variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
                selected_ut = ds['ut'].sel(time=selected_time).values.item() / (1e9 * 3600)
                selected_mtime = get_mtime(ds,selected_time)
                filename = filenames


                if selected_lev_ilev == "mean":
                    # if selected_lon is "mean", then we calculate the mean over all longitudes.
                    data = ds[variable_name].sel(time=selected_time).mean(dim='lev')
                    lons = data.lon.values
                    lats = data.lat.values
                    variable_values = data.values
                    if selected_unit != None:
                        variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                        
                else:
                    # Extract the data for the given selected_time and lev
                    if selected_lev_ilev in ds['lev'].values:
                        data = ds[variable_name].sel(time=selected_time, lev=selected_lev_ilev)
                        lons = data.lon.values
                        lats = data.lat.values
                        variable_values = data.values
                        if selected_unit != None:
                            variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                            
                    else:
                        print(f"The lev {selected_lev_ilev} isn't in the listed valid values.")
                        lev_max = ds['lev'].max().values.item()
                        lev_min = ds['lev'].min().values.item()
                        if selected_lev_ilev > lev_max:
                            print(f"Using maximun valid lev {lev_max}")
                            selected_lev_ilev = lev_max
                            data = ds[variable_name].sel(time=selected_time, lev=selected_lev_ilev)
                            lons = data.lon.values
                            lats = data.lat.values
                            variable_values = data.values
                            if selected_unit != None:
                                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                        elif selected_lev_ilev < lev_min:
                            print(f"Using minimum valid lev {lev_min}")
                            selected_lev_ilev = lev_min
                            data = ds[variable_name].sel(time=selected_time, lev=selected_lev_ilev)
                            lons = data.lon.values
                            lats = data.lat.values
                            variable_values = data.values
                            if selected_unit != None:
                                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                        else:
                            sorted_levs = sorted(ds['lev'].values, key=lambda x: abs(x - selected_lev_ilev))
                            closest_lev1 = sorted_levs[0]
                            closest_lev2 = sorted_levs[1]
                            print(f"Averaging from the closest valid levs: {closest_lev1} and {closest_lev2}")
                            # Extract data for the two closest lev values using .sel()
                            data1 = ds[variable_name].sel(time=selected_time, lev=closest_lev1)
                            lons = data1.lon.values
                            lats = data1.lat.values
                            variable_values_1 = data1.values

                            data2 = ds[variable_name].sel(time=selected_time, lev=closest_lev2)
                            variable_values_2 = data2.values
                            # Return the averaged data
                            variable_values = (variable_values_1 + variable_values_2) / 2
                            if selected_unit != None:
                                variable_values , selected_unit  = convert_units (variable_values, variable_unit, selected_unit)
                if plot_mode == True:    
                    return variable_values, selected_lev_ilev, lats, lons, variable_unit, variable_long_name, selected_ut, selected_mtime, filename
                else:
                    return variable_values

        elif lev_ilev == 'ilev':
            first_pass == False
            if selected_time in ds['time'].values:
                if 'ilev' not in ds[variable_name].dims:
                    raise ValueError("The variable "+variable_name+" doesn't use the dimensions 'lat', 'lon', 'ilev'")
                    return 0
                            
                # Extract variable attributes
                variable_unit = ds[variable_name].attrs.get('units', 'N/A')
                variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
                selected_ut = ds['ut'].sel(time=selected_time).values.item() / (1e9 * 3600)
                selected_mtime=get_mtime(ds,selected_time)
                filename = filenames

                if selected_lev_ilev == "mean":
                    # if selected_lon is "mean", then we calculate the mean over all longitudes.
                    data = ds[variable_name].sel(time=selected_time).mean(dim='lev')
                    lons = data.lon.values
                    lats = data.lat.values
                    variable_values = data.values
                    if selected_unit != None:
                        variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                        
                else:
                    # Extract the data for the given selected_time and lev
                    if selected_lev_ilev in ds['ilev'].values:
                        data = ds[variable_name].sel(time=selected_time, ilev=selected_lev_ilev)
                        lons = data.lon.values
                        lats = data.lat.values
                        variable_values = data.values
                        if selected_unit != None:
                            variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                            
                    else:
                        
                        print(f"The ilev {selected_lev_ilev} isn't in the listed valid values.")
                        ilev_max = ds['ilev'].max().values.item()
                        ilev_min = ds['ilev'].min().values.item()
                        if selected_lev_ilev > ilev_max:
                            print(f"Using maximun valid ilev {ilev_max}")
                            selected_lev_ilev = ilev_max
                            data = ds[variable_name].sel(time=selected_time, ilev=selected_lev_ilev)
                            lons = data.lon.values
                            lats = data.lat.values
                            variable_values = data.values
                            if selected_unit != None:
                                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                        elif selected_lev_ilev < ilev_min:
                            print(f"Using minimum valid ilev {ilev_min}")
                            selected_lev_ilev = ilev_min
                            data = ds[variable_name].sel(time=selected_time, ilev=selected_lev_ilev)
                            lons = data.lon.values
                            lats = data.lat.values
                            variable_values = data.values
                            if selected_unit != None:
                                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                        else:
                            sorted_levs = sorted(ds['ilev'].values, key=lambda x: abs(x - selected_lev_ilev))
                            closest_lev1 = sorted_levs[0]
                            closest_lev2 = sorted_levs[1]
                            print(f"Averaging from the closest valid ilevs: {closest_lev1} and {closest_lev2}")
                            # Extract data for the two closest lev values using .sel()
                            data1 = ds[variable_name].sel(time=selected_time, ilev=closest_lev1)
                            lons = data1.lon.values
                            lats = data1.lat.values
                            variable_values_1 = data1.values

                            data2 = ds[variable_name].sel(time=selected_time, ilev=closest_lev2)
                            variable_values_2 = data2.values
                            # Return the averaged data
                            variable_values = (variable_values_1 + variable_values_2) / 2
                            if selected_unit != None:
                                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                            
                if plot_mode == True:    
                    return variable_values, selected_lev_ilev, lats, lons, variable_unit, variable_long_name, selected_ut, selected_mtime, filename
                else:
                    return variable_values

        elif lev_ilev == None:
            first_pass == False
            selected_lev_ilev = None
            if selected_time in ds['time'].values:

                # Extract variable attributes
                variable_unit = ds[variable_name].attrs.get('units', 'N/A')
                variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
                selected_ut = ds['ut'].sel(time=selected_time).values.item() / (1e9 * 3600)
                selected_mtime = get_mtime(ds,selected_time)
                filename = filenames

                # Extract the data for the given selected_time and lev
                data = ds[variable_name].sel(time=selected_time)
                lons = data.lon.values
                lats = data.lat.values
                variable_values = data.values
                if selected_unit != None:
                    variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                
                
                if plot_mode == True:    
                    return variable_values, selected_lev_ilev, lats, lons, variable_unit, variable_long_name, selected_ut, selected_mtime, filename
                else:
                    return variable_values



    
def arr_lev_var(datasets, variable_name, selected_time, selected_lat, selected_lon, selected_unit= None, plot_mode = False):
    """
    Extracts data from the dataset for a given variable name, latitude, longitude, and time.
    
    Parameters:
    - ds (xarray): The loaded dataset opened using xarray.
    - variable_name (str): Name of the variable to retrieve.
        - valid variables: ['TN', 'UN', 'VN', 'O2', 'O1', 'N4S', 'NO', 'HE', 'AR', 'OP', 'N2D','TI', 'TE', 'O2P', 'TN_NM', 
                            'UN_NM', 'VN_NM', 'O2_NM', 'O1_NM', 'N4S_NM', 'NO_NM', 'OP_NM', 'HE_NM', 'AR_NM', 'NE', 'OMEGA', 
                            'Z', 'POTEN']  
    - selected_time (str): Timestamp to filter the data.
    - selected_lat (float): Latitude value.
    - selected_lon (float): Longitude value.
    - selected_time (int): Index of the time dimension.
    
    Returns:
    - variable_values (xarray):  An xarray object of variable values for the given timestamp and lev.
    - levs_ilevs (xarray): An xarray object of selected lev or ilev values.
    - variable_unit (str): Unit of the variable.
    - variable_long_name (str): Long name of the variable.
    - selected_ut (float): UT value in hours for selected_time.
    - selected_mtime (array): An array containing Day, Hour, Min of the model run.
    """
    
    
    for ds, filenames in datasets:
        if selected_time in ds['time'].values:

            if selected_lon == "mean" and selected_lat == "mean":
                # if selected_lon is "mean", then we calculate the mean over all longitudes.
                data = ds[variable_name].sel(time=selected_time).mean(dim=['lon', 'lat'])
            elif selected_lon == "mean":
                data = ds[variable_name].sel(time=selected_time, lat=selected_lat, method="nearest").mean(dim='lon')  #look into method nearest
            elif selected_lat == "mean":
                data = ds[variable_name].sel(time=selected_time, lon=selected_lon).mean(dim='lat')
            else:
                data = ds[variable_name].sel(time=selected_time, lat=selected_lat, lon=selected_lon, method="nearest")


            variable_unit = ds[variable_name].attrs.get('units', 'N/A')
            variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
            selected_ut = ds['ut'].sel(time=selected_time).values.item() / (1e9 * 3600)
            selected_mtime=get_mtime(ds,selected_time)
            filename = filenames
            valid_indices = ~np.isnan(data.values)
            variable_values = data.values[valid_indices]
            if selected_unit != None:
                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                
            try:
                levs_ilevs = ds['lev'].values[valid_indices]
            except:
                levs_ilevs = ds['ilev'].values[valid_indices]
            if plot_mode == True:
                return variable_values , levs_ilevs, variable_unit, variable_long_name, selected_ut, selected_mtime, filename
            else:
                return variable_values 
    print(f"{selected_time} not found.")
    return None




def arr_lev_lat (datasets, variable_name, selected_time, selected_lon, selected_unit=None, plot_mode = False):
    """
    Extract data from the dataset based on the given variable name, timestamp, and lev value.
    
    Args:
    - ds (xarray): The loaded dataset opened using xarray.
    - variable_name (str): Name of the variable to extract.
        - valid variables: ['TN', 'UN', 'VN', 'O2', 'O1', 'N2', 'NO', 'N4S', 'HE', 'TE', 'TI', 'O2P', 'OP', 'QJOULE']    
    - selected_time (str): Timestamp to filter the data.
    - selected_lon (float): Longitude to filter the data.
    
    Returns:
    - variable_values (xarray): An xarray object of variable values for the given timestamp and latitude.
    - lats (xarray): An xarray object of latgitude values.
    - levs_ilevs (xarray): An xarray object of selected lev or ilev values.
    - variable_unit (str): Unit of the variable.
    - variable_long_name (str): Long name of the variable.
    - selected_ut (float): UT value in hours for selected_time.
    - selected_mtime (array): An array containing Day, Hour, Min of the model run
    """
    
    for ds, filenames in datasets:
        if selected_time in ds['time'].values:
            # Extract variable attributes
            variable_unit = ds[variable_name].attrs.get('units', 'N/A')
            variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
            selected_ut = ds['ut'].sel(time=selected_time).values.item() / (1e9 * 3600)
            selected_mtime = get_mtime(ds,selected_time)
            filename = filenames
            if selected_lon == "mean":
                # if selected_lon is "mean", then we calculate the mean over all longitudes.
                data = ds[variable_name].sel(time=selected_time).mean(dim='lon')
            else:
                selected_lon = float(selected_lon)
                data = ds[variable_name].sel(time=selected_time, lon=selected_lon, method='nearest')
            lats = data.lat.values

            not_all_nan_indices = ~np.isnan(data.values).all(axis=1)
            variable_values = data.values[not_all_nan_indices, :]
            if selected_unit != None:
                variable_values ,variable_unit  = convert_units (variable_values, variable_unit, selected_unit)
                
            try:
                levs_ilevs = data.lev.values[not_all_nan_indices]
            except AttributeError:
                levs_ilevs = data.ilev.values[not_all_nan_indices]
            if plot_mode == True:
                return variable_values, lats, levs_ilevs, selected_lon, variable_unit, variable_long_name, selected_ut, selected_mtime,filename
            else:
                return variable_values
    print(f"{selected_time} not found.")
    return None



def arr_lev_time (datasets, variable_name, selected_lat, selected_lon, selected_unit = None, plot_mode = False):
    """
    Extract data from the dataset based on the given variable name, timestamp, and lev value.
    
    Args:
    - ds (xarray): The loaded dataset opened using xarray.
    - variable_name (str): Name of the variable to extract.
        - valid variables: ['TN', 'UN', 'VN', 'O2', 'O1', 'N4S', 'NO', 'HE', 'AR', 'OP', 'N2D','TI', 'TE', 'O2P', 'TN_NM', 
                            'UN_NM', 'VN_NM', 'O2_NM', 'O1_NM', 'N4S_NM', 'NO_NM', 'OP_NM', 'HE_NM', 'AR_NM', 'NE', 'OMEGA', 
                            'Z', 'POTEN'] 
    - selected_lat (str): Latitude to filter the data.
    - selected_lon (float): Longitude to filter the data.
    
    Returns:
    - variable_values (xarray): An xarray object of variable values for the given timestamp and latitude.
    - levs_ilevs (xarray): An xarray object of selected lev or ilev values.
    - mtime_values (xarray): An xarray object of mtime arrays.
    - variable_unit (str): Unit of the variable.
    - variable_long_name (str): Long name of the variable.
    - selected_ut (float): UT value in hours for selected_time.
    - selected_mtime (array): An array containing Day, Hour, Min of the model run
    """
    
    selected_lon = float(selected_lon)
    
    variable_values_all = []
    combined_mtime = []
    levs_ilevs_all = []
    
    for ds, filenames in datasets:
        variable_unit = ds[variable_name].attrs.get('units', 'N/A')
        variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
        mtime_values = ds['mtime'].values
        if selected_lon == "mean" and selected_lat == "mean":

            # if selected_lon is "mean", then we calculate the mean over all longitudes.
            data = ds[variable_name].mean(dim=['lon', 'lat'])
        elif selected_lon == "mean":
            data = ds[variable_name].sel(lat=selected_lat).mean(dim='lon')

        elif selected_lat == "mean":
            data = ds[variable_name].sel(lon=selected_lon).mean(dim='lat')
        else:
            #data = ds[variable_name].sel(time=selected_time, lat=selected_lat, lon=selected_lon, method="nearest")    
            data = ds[variable_name].sel(lat=selected_lat, lon=selected_lon, method='nearest')

        variable_values = data.T 
        try:
            levs_ilevs = data.lev.values
        except:
            levs_ilevs = data.ilev.values
    
        # Adjusting levs_ilevs to match the shape of variable_values
        levs_ilevs = levs_ilevs[:variable_values.shape[0]]


        variable_values_all.append(variable_values)
        combined_mtime.extend(mtime_values)
        levs_ilevs_all.append(levs_ilevs)
    
    # Concatenate data along the time dimension
    variable_values_all = np.concatenate(variable_values_all, axis=1)
    mtime_values = combined_mtime
    
    # Mask out levels with all NaN values
    mask = ~np.isnan(variable_values_all).all(axis=1)
    variable_values_all = variable_values_all[mask, :]
    if selected_unit != None:
        variable_values_all ,variable_unit  = convert_units (variable_values_all, variable_unit, selected_unit)
        
    min_lev_size = min([len(lev) for lev in levs_ilevs_all])
    levs_ilevs = levs_ilevs_all[0][:min_lev_size][mask[:min_lev_size]]

    if plot_mode == True:
        return variable_values_all, levs_ilevs, mtime_values, selected_lon, variable_unit, variable_long_name
    else:
        return variable_values_all

def arr_lat_time(datasets, variable_name, selected_lon,selected_lev_ilev = None, selected_unit = None, plot_mode = False):
    
    if selected_lev_ilev != 'mean' and selected_lev_ilev != None:
        selected_lev_ilev = float(selected_lev_ilev)
    if selected_lon !='mean':
        selected_lon = float(selected_lon)
    first_pass = True
    variable_values_all = []
    combined_mtime = []
    lats_all = []
    avg_info_print = 0
    for ds, filenames in datasets:
        if first_pass == True:
            lev_ilev = check_var_dims(ds, variable_name)
        if lev_ilev == 'lev':
            first_pass == False            
            if 'lev' not in ds[variable_name].dims:
                raise ValueError("The variable "+variable_name+" doesn't use the dimensions 'lat', 'lon', 'lev'")
                return 0
            variable_unit = ds[variable_name].attrs.get('units', 'N/A')
            variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
            mtime_values = ds['mtime'].values
            filename = filenames

            if selected_lon == 'mean' and selected_lev_ilev == 'mean':
                data = ds[variable_name].sel(method='nearest').mean(dim=['lev', 'lon'])
                variable_values = data.T 
                lats = data.lat.values    
                lats_all = lats_all[:variable_values.shape[0]]
            if selected_lon =='mean' and selected_lev_ilev != 'mean':
                if selected_lev_ilev in ds['lev'].values:
                    data = ds[variable_name].sel(lev=selected_lev_ilev, method='nearest').mean(dim='lon')
                    variable_values = data.T 
                    lats = data.lat.values    
                    lats_all = lats_all[:variable_values.shape[0]]
                else:
                    sorted_levs = sorted(ds['lev'].values, key=lambda x: abs(x - selected_lev_ilev))
                    closest_lev1 = sorted_levs[0]
                    closest_lev2 = sorted_levs[1]
                    if avg_info_print == 0:
                        print(f"The lev {selected_lev_ilev} isn't in the listed valid values.")
                        print(f"Averaging from the closest valid levs: {closest_lev1} and {closest_lev2}")
                        avg_info_print = 1
                    data1 = ds[variable_name].sel(lev=closest_lev1, method='nearest').mean(dim='lon')
                    variable_values_1 = data1.T 
                    lats = data1.lat.values    
                    lats_all = lats_all[:variable_values_1.shape[0]]
                    data2 = ds[variable_name].sel(lev=closest_lev2, method='nearest').mean(dim='lon')
                    variable_values_2 = data2.T 
                    variable_values = (variable_values_1 + variable_values_2) / 2
            if selected_lon !='mean' and selected_lev_ilev == 'mean':
                data = ds[variable_name].sel(lon=selected_lon, method='nearest').mean(dim='lev')
                variable_values = data.T 
                lats = data.lat.values    
                lats_all = lats_all[:variable_values.shape[0]]
            if selected_lon !='mean' and selected_lev_ilev != 'mean':
                if selected_lev_ilev in ds['lev'].values:
                    data = ds[variable_name].sel(lev=selected_lev_ilev, lon=selected_lon, method='nearest')
                    variable_values = data.T 
                    lats = data.lat.values    
                    lats_all = lats_all[:variable_values.shape[0]]
                else:
                    sorted_levs = sorted(ds['lev'].values, key=lambda x: abs(x - selected_lev_ilev))
                    closest_lev1 = sorted_levs[0]
                    closest_lev2 = sorted_levs[1]
                    if avg_info_print == 0:
                        print(f"The lev {selected_lev_ilev} isn't in the listed valid values.")
                        print(f"Averaging from the closest valid levs: {closest_lev1} and {closest_lev2}")
                        avg_info_print = 1
                    data1 = ds[variable_name].sel(lev=closest_lev1, lon=selected_lon, method='nearest')
                    variable_values_1 = data1.T 
                    lats = data1.lat.values    
                    lats_all = lats_all[:variable_values_1.shape[0]]
                    data2 = ds[variable_name].sel(lev=closest_lev2, lon=selected_lon, method='nearest')
                    variable_values_2 = data2.T 
                    variable_values = (variable_values_1 + variable_values_2) / 2
            variable_values_all.append(variable_values)
            combined_mtime.extend(mtime_values)
            lats_all.append(lats)
        

        elif lev_ilev == 'ilev':
            first_pass == False
            
            avg_info_print = 0
            if 'ilev' not in ds[variable_name].dims:
                raise ValueError("The variable "+variable_name+" doesn't use the dimensions 'lat', 'lon', 'ilev'")
                return 0
            variable_unit = ds[variable_name].attrs.get('units', 'N/A')
            variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
            mtime_values = ds['mtime'].values
            filename = filenames
            
            if selected_lon == 'mean' and selected_lev_ilev == 'mean':
                data = ds[variable_name].sel(method='nearest').mean(dim=['ilev', 'lon'])
                variable_values = data.T 
                lats = data.lat.values    
                lats_all = lats_all[:variable_values.shape[0]]
            if selected_lon =='mean' and selected_lev_ilev != 'mean':
                if selected_lev_ilev in ds['ilev'].values:
                    data = ds[variable_name].sel(ilev=selected_lev_ilev, method='nearest').mean(dim='lon')
                    variable_values = data.T 
                    lats = data.lat.values    
                    lats_all = lats_all[:variable_values.shape[0]]
                else:
                    sorted_levs = sorted(ds['ilev'].values, key=lambda x: abs(x - selected_lev_ilev))
                    closest_lev1 = sorted_levs[0]
                    closest_lev2 = sorted_levs[1]
                    if avg_info_print == 0:
                        print(f"The ilev {selected_lev_ilev} isn't in the listed valid values.")
                        print(f"Averaging from the closest valid levs: {closest_lev1} and {closest_lev2}")
                        avg_info_print = 1
                    data1 = ds[variable_name].sel(ilev=closest_lev1, method='nearest').mean(dim='lon')
                    variable_values_1 = data1.T 
                    lats = data1.lat.values    
                    lats_all = lats_all[:variable_values_1.shape[0]]
                    data2 = ds[variable_name].sel(ilev=closest_lev2, method='nearest').mean(dim='lon')
                    variable_values_2 = data2.T 
                    variable_values = (variable_values_1 + variable_values_2) / 2
            if selected_lon !='mean'  and selected_lev_ilev == 'mean':
                data = ds[variable_name].sel(lon=selected_lon, method='nearest').mean(dim='ilev')
                variable_values = data.T 
                lats = data.lat.values    
                lats_all = lats_all[:variable_values.shape[0]]
            elif selected_lon !='mean'  and selected_lev_ilev != 'mean':
                if selected_lev_ilev in ds['ilev'].values:
                    data = ds[variable_name].sel(ilev=selected_lev_ilev, lon=selected_lon, method='nearest')
                    variable_values = data.T 
                    lats = data.lat.values    
                    lats_all = lats_all[:variable_values.shape[0]]
                else:
                    sorted_levs = sorted(ds['ilev'].values, key=lambda x: abs(x - selected_lev_ilev))
                    closest_lev1 = sorted_levs[0]
                    closest_lev2 = sorted_levs[1]
                    if avg_info_print == 0:
                        print(f"The ilev {selected_lev_ilev} isn't in the listed valid values.")
                        print(f"Averaging from the closest valid levs: {closest_lev1} and {closest_lev2}")
                        avg_info_print = 1
                    data1 = ds[variable_name].sel(ilev=closest_lev1, lon=selected_lon, method='nearest')
                    variable_values_1 = data1.T 
                    lats = data1.lat.values    
                    lats_all = lats_all[:variable_values_1.shape[0]]
                    data2 = ds[variable_name].sel(ilev=closest_lev2, lon=selected_lon, method='nearest')
                    variable_values_2 = data2.T 
                    variable_values = (variable_values_1 + variable_values_2) / 2

            variable_values_all.append(variable_values)
            combined_mtime.extend(mtime_values)
            lats_all.append(lats)
            

        elif lev_ilev == None:
            first_pass == False
            selected_lev_ilev = None

            avg_info_print = 0
            variable_unit = ds[variable_name].attrs.get('units', 'N/A')
            variable_long_name = ds[variable_name].attrs.get('long_name', 'N/A')
            mtime_values = ds['mtime'].values
            filename = filenames

            if selected_lon =='mean':
                data = ds[variable_name].sel(method='nearest').mean(dim='lon')
                variable_values = data.T 
                lats = data.lat.values    
                lats_all = lats_all[:variable_values.shape[0]]
            else:
                data = ds[variable_name].sel(lon=selected_lon, method='nearest')
                variable_values = data.T 
                lats = data.lat.values    
                lats_all = lats_all[:variable_values.shape[0]]
            

            variable_values_all.append(variable_values)
            combined_mtime.extend(mtime_values)
            lats_all.append(lats)
            
            # Concatenate data along the time dimension
        variable_values_all = np.concatenate(variable_values_all, axis=1)
        if selected_unit != None:
            variable_values_all ,variable_unit  = convert_units (variable_values_all, variable_unit, selected_unit)
            
        mtime_values = combined_mtime
        
        if plot_mode == True:    
            return variable_values_all, lats, mtime_values, selected_lon, variable_unit, variable_long_name, filename
        else:
            return variable_values_all



def calc_avg_ht(datasets, selected_time, selected_lev_ilev):
    """
    Compute the average Z value for a given set of lat, lon, and lev from a dataset.
    
    Parameters:
    - ds (xarray): The loaded dataset opened using xarray.
    - selected_time (str): Timestamp to filter the data.
    - selected_lev_ilev (float): The level for which to retrieve data.
    
    Returns:
    - float: The average ZG value for the given conditions.
    """
    
    
    for ds, filenames in datasets:
        if selected_time in ds['time'].values:
            if selected_lev_ilev in ds['ilev'].values:
                heights = ds['ZG'].sel(time=selected_time, ilev=selected_lev_ilev).values
            else:
                sorted_levs = sorted(ds['ilev'].values, key=lambda x: abs(x - selected_lev_ilev))
                closest_lev1 = sorted_levs[0]
                closest_lev2 = sorted_levs[1]

                # Extract data for the two closest lev values using .sel()
                data1 = ds['ZG'].sel(time=selected_time, ilev=closest_lev1).values
                data2 = ds['ZG'].sel(time=selected_time, ilev=closest_lev2).values
                
                # Return the averaged data
                heights = (data1 + data2) / 2
            avg_ht= round(heights.mean()/ 100000, 2)
    return avg_ht

def min_max(variable_values):
    """Find the minimum and maximum values of varval from the 2D array
    
    Parameters:
    - variable_values (xarray): A list of variable values.
    
    Returns:
    - min_val (float): Minimum value of the variable in the array.
    - max_val (float): Maximum value of the variable in the array.
    """
    
    return np.nanmin(variable_values), np.nanmax(variable_values)

def get_time(datasets, mtime):
    """
    This function takes a dataset and mtime as parameters, searches for the time value 
    in the dataset corresponding to mtime, and returns the np.datetime64 time value.
    
    :param dataset: xarray Dataset object
    :param mtime: List of integers representing [day, hour, minute]
    :return: np.datetime64 object representing the corresponding time value
    """
    for ds, filenames in datasets:
        # Convert mtime to numpy array for comparison
        mtime_array = np.array(mtime)
        
        # Find the index where mtime matches in the dataset
        idx = np.where(np.all(ds['mtime'].values == mtime_array, axis=1))[0]
        
        if len(idx) == 0:
            continue  # Return None if no matching time is found
        
        # Get the corresponding datetime64 value from the time variable
        time = ds['time'].values[idx][0]
        
        return time

def get_mtime(ds, selected_time):
    """Find the mtime array for the corresponding selected time.
    
    Parameters:
    - ds (xarray): The loaded dataset opened using xarray.
    - selected_time (str): Timestamp to filter the data.
    
    Returns:
    - array: mtime array containing [Day,Hour,Min].
    """
    # Convert input string to numpy datetime64 format
    

    # Extract time and mtime variables from the dataset
    time_variable = ds['time'].values
    mtime_variable = ds['mtime'].values

    # Find the index corresponding to the input time
    index = np.where(time_variable == selected_time)

    # Extract and return the corresponding mtime value
    if index[0].size > 0:
        return mtime_variable[index[0][0]]
    else:
        return None


def get_avg_ht_arr(ds, time, lat, lon):
    """
    Extracts ZG values for a given time, latitude, and longitude.
    
    Args:
    - time (str): Desired time in the format 'YYYY-MM-DDTHH:MM:SS'
    - lat (float): Desired latitude value
    - lon (float): Desired longitude value
    - dataset (xarray.Dataset): The dataset containing the ZG values. Default is the loaded dataset.
    
    Returns:
    - list: A list of lists where each inner list contains [ilev_val, ZG_val]
    """

    #ds = xr.open_dataset(dataset)
    # Extract the ZG values for the specified time, latitude, and longitude
    selected_zg = ds['ZG'].sel(time=time, lat=lat, lon=lon)

    # Convert the values from cm to km
    selected_zg_km = selected_zg / 100000  # 1 km = 100000 cm
    
    # Extract the ilev values for the same selection
    ilev_values = selected_zg['ilev'].values

    # Combine the ilev and ZG values into a single list
    combined_values = list(zip(ilev_values, selected_zg_km.values))

    averaged_array = []
    
    # Iterate over the zg_array and calculate the average for consecutive values
    for i in range(len(combined_values) - 1):
        avg_lev = (combined_values[i][0] + combined_values[i+1][0]) / 2
        avg_zg = (combined_values[i][1] + combined_values[i+1][1]) / 2
        averaged_array.append((avg_lev, avg_zg))
    averaged_array.append((7.25, float('nan')))
    zg_values_array = [item[1] for item in averaged_array]

    return zg_values_array

    #return combined_values