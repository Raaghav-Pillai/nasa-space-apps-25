import netCDF4
import csv
import os

def get_cloud_title():
    """Extract variable names from NetCDF file in Cloud folder"""
    nc_file = os.path.join('..','backend', 'data', 'Cloud', 'temp.nc')
    try:
        with netCDF4.Dataset(nc_file, 'r') as nc:
            variables = list(nc.variables.keys())
            print("=== Cloud Folder (NetCDF) ===")
            print(f"File: {os.path.basename(nc_file)}")
            print(f"Variables: {variables}")
            # Get global attributes if available
            if hasattr(nc, 'title'):
                print(f"Title: {nc.title}")
            print()
    except Exception as e:
        print(f"Error reading Cloud data: {e}\n")

def get_daymet_title():
    """Extract column headers from CSV file in Daymet folder"""
    csv_file = os.path.join('..','backend', 'data', 'Daymet', 'Daymet-Chicago-Past-Year-DAYMET-004-results.csv')
    try:
        print("=== Daymet Folder (CSV) ===")
        print(f"File: {os.path.basename(csv_file)}")

        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            print(f"Number of columns: {len(headers)}")
            print(f"Column headers:")
            for i, header in enumerate(headers, 1):
                print(f"  {i}. {header}")

        print()
    except Exception as e:
        print(f"Error reading Daymet data: {e}\n")

def get_modis_title():
    """Extract column headers from CSV file in Modis folder"""
    csv_file = os.path.join('..','backend', 'data', 'Modis', 'MODIS-Chicago-2020-2024-Retry-MOD09GA-061-results.csv')
    try:
        print("=== Modis Folder (CSV) ===")
        print(f"File: {os.path.basename(csv_file)}")

        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            print(f"Number of columns: {len(headers)}")
            print(f"First 10 column headers:")
            for i, header in enumerate(headers, 1):
                print(f"  {i}. {header}")
            if len(headers) > 10:
                print(f"  ... and {len(headers) - 10} more columns")

        print()
    except Exception as e:
        print(f"Error reading Modis data: {e}\n")

if __name__ == "__main__":
    print("Extracting titles from data folders...\n")
    get_cloud_title()
    get_daymet_title()
    get_modis_title()
    print("Done!")
