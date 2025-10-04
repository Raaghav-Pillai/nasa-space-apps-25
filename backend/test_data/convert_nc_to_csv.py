import netCDF4
import pandas as pd
import numpy as np
import os

def convert_nc_with_groups_to_csv(nc_file_path, output_csv_path, selected_groups=None):
    """
    Convert NetCDF file with groups to CSV format (vectorized for speed).
    Each group's variables (Mean, Standard_Deviation, etc.) are flattened into columns.

    Args:
        nc_file_path: Path to the NetCDF file
        output_csv_path: Path where CSV should be saved
        selected_groups: List of group names to include (None = all groups)
    """
    try:
        # Open NetCDF file
        nc = netCDF4.Dataset(nc_file_path, 'r')

        print(f"Converting {os.path.basename(nc_file_path)} to CSV...")

        # Get dimensions
        latitude = nc.variables['latitude'][:]
        longitude = nc.variables['longitude'][:]

        print(f"Grid size: {len(latitude)} lat x {len(longitude)} lon = {len(latitude) * len(longitude)} points")

        # Get all groups
        all_groups = list(nc.groups.keys())
        if selected_groups is None:
            groups = all_groups
        else:
            groups = [g for g in selected_groups if g in all_groups]

        print(f"Processing {len(groups)} groups (out of {len(all_groups)} total)")

        # Create meshgrid for lat/lon
        lon_grid, lat_grid = np.meshgrid(longitude, latitude)

        # Flatten to 1D arrays
        lat_flat = lat_grid.flatten()
        lon_flat = lon_grid.flatten()

        # Initialize dictionary with lat/lon
        data_dict = {
            'latitude': lat_flat,
            'longitude': lon_flat
        }

        # Extract data from each group (vectorized)
        print("Extracting data from groups...")
        for idx, group_name in enumerate(groups):
            group = nc.groups[group_name]

            # Get all variables in this group
            for var_name in group.variables.keys():
                var = group.variables[var_name]
                col_name = f"{group_name}_{var_name}"

                # Extract and flatten the entire array at once
                if var.ndim == 2:
                    # Transpose to match (lat, lon) order, then flatten
                    data = var[:].T.flatten()

                    # Handle masked arrays
                    if isinstance(data, np.ma.MaskedArray):
                        data = data.filled(np.nan)

                    data_dict[col_name] = data
                else:
                    # Skip non-2D variables
                    print(f"  Skipping {col_name} (ndim={var.ndim})")

            # Progress indicator
            print(f"  Processed group {idx + 1}/{len(groups)}: {group_name}")

        # Create DataFrame
        print("Creating DataFrame...")
        df = pd.DataFrame(data_dict)

        # Save to CSV
        print("Saving to CSV...")
        df.to_csv(output_csv_path, index=False)

        print(f"\nSuccessfully saved CSV:")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  File size: ~{os.path.getsize(output_csv_path) / (1024*1024):.1f} MB")
        print(f"  Output: {output_csv_path}")

        # Close NetCDF file
        nc.close()

        return True

    except Exception as e:
        print(f"Error converting {nc_file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def convert_nc_files_by_date_to_csv(nc_files_dir, output_csv_path):
    """
    Convert multiple NetCDF files (one per date) to a single CSV.
    Each row represents one date with averaged values across all lat/lon points.

    Args:
        nc_files_dir: Directory containing NC files named by date (e.g., 2020-01-01.nc)
        output_csv_path: Path where CSV should be saved
    """
    import glob
    from datetime import datetime

    # Get all .nc files
    nc_files = sorted(glob.glob(os.path.join(nc_files_dir, '*.nc')))

    if not nc_files:
        print(f"No .nc files found in {nc_files_dir}")
        return False

    print(f"Found {len(nc_files)} NetCDF files to process")

    all_data = []

    for idx, nc_file_path in enumerate(nc_files):
        try:
            # Extract date from filename (e.g., 2020-01-01.nc)
            filename = os.path.basename(nc_file_path)
            date_str = filename.replace('.nc', '')

            # Validate it's a proper date file
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                print(f"Skipping {filename} - not a valid date format")
                continue

            # Open NetCDF file
            nc = netCDF4.Dataset(nc_file_path, 'r')

            # Check if file has groups (actual NetCDF data)
            if not nc.groups:
                print(f"Skipping {filename} - no groups found (might be HTML or corrupted)")
                nc.close()
                continue

            row_data = {'date': date_str}

            # Get all groups
            groups = list(nc.groups.keys())

            # Extract data from each group
            for group_name in groups:
                group = nc.groups[group_name]

                # Get all variables in this group
                for var_name in group.variables.keys():
                    var = group.variables[var_name]
                    col_name = f"{group_name}_{var_name}"

                    # Calculate mean across all lat/lon points
                    if var.ndim == 2:
                        data = var[:]

                        # Handle masked arrays and fill values
                        if isinstance(data, np.ma.MaskedArray):
                            # Calculate mean ignoring masked values
                            mean_value = data.mean()
                            if isinstance(mean_value, np.ma.MaskedArray):
                                mean_value = float(mean_value.filled(np.nan))
                        else:
                            mean_value = float(np.nanmean(data))

                        row_data[col_name] = mean_value

            all_data.append(row_data)
            nc.close()

            # Progress indicator
            if (idx + 1) % 50 == 0:
                print(f"  Processed {idx + 1}/{len(nc_files)} files...")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue

    if not all_data:
        print("No valid data extracted from any files")
        return False

    # Create DataFrame
    print(f"\nCreating DataFrame from {len(all_data)} dates...")
    df = pd.DataFrame(all_data)

    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)

    # Save to CSV
    print("Saving to CSV...")
    df.to_csv(output_csv_path, index=False)

    print(f"\nSuccessfully saved CSV:")
    print(f"  Dates: {len(df)} (from {df['date'].min()} to {df['date'].max()})")
    print(f"  Columns: {len(df.columns)}")
    print(f"  File size: ~{os.path.getsize(output_csv_path) / (1024*1024):.1f} MB")
    print(f"  Output: {output_csv_path}")

    return True

if __name__ == "__main__":
    # Define paths
    nc_files_directory = os.path.join('backend', 'data', 'Cloud', 'nc_files')
    output_csv = os.path.join('backend', 'data', 'Cloud', 'cloud_data_by_date.csv')

    # Convert all NC files by date
    convert_nc_files_by_date_to_csv(nc_files_directory, output_csv)
