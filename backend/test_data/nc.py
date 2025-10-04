import netCDF4

# Open the NetCDF file
file_path = 'C:/Users/Raaghav/Desktop/Raaghav/Projects/Work/nasa-space-apps-25/backend/data/Cloud/temp.nc'
dataset = netCDF4.Dataset(file_path, 'r')

# Display the file contents
print(dataset)

# To list all the variables in the file
variables = dataset.variables
print(variables)

# Example: To get a specific variable (e.g., 'temperature')
temperature = dataset.variables['temperature'][:]
print(temperature)

# Example: To get the dimensions of a variable (e.g., 'latitude')
latitude = dataset.variables['latitude']
print(latitude[:])  # Display latitude data

# Close the dataset after use
dataset.close()