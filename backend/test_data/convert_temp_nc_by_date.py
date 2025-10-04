import pandas as pd

def create_daily_csv_from_full_data(full_csv_path, output_csv_path):
    """
    Since temp.nc doesn't have date information and nc_files are corrupted,
    we'll create a single-row CSV with global averages from the full dataset.

    For actual date-based analysis, you'll need to download proper NetCDF files.
    """
    print(f"Loading full dataset from {full_csv_path}...")
    df = pd.read_csv(full_csv_path)

    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")

    # Calculate mean across all lat/lon points for each variable
    result = {}

    for col in df.columns:
        if col not in ['latitude', 'longitude']:
            result[col] = df[col].mean()

    # Create a single-row DataFrame
    result_df = pd.DataFrame([result])

    # Save to CSV
    result_df.to_csv(output_csv_path, index=False)

    print(f"\nCreated summary CSV with global averages:")
    print(f"  Columns: {len(result_df.columns)}")
    print(f"  Output: {output_csv_path}")

    return True

if __name__ == "__main__":
    import os

    # Convert the full CSV to a summary
    full_csv = os.path.join('backend', 'data', 'Cloud', 'cloud_data_full.csv')
    output_csv = os.path.join('backend', 'data', 'Cloud', 'cloud_data_summary.csv')

    create_daily_csv_from_full_data(full_csv, output_csv)

    print("\n" + "="*70)
    print("IMPORTANT NOTE:")
    print("="*70)
    print("The nc_files folder contains HTML login pages, not actual NetCDF data.")
    print("temp.nc does not contain date information - it's aggregated global data.")
    print("\nTo get date-based data, you need to:")
    print("1. Download actual NetCDF files from the URLs in list_nc.csv")
    print("2. Use proper authentication with NASA Earthdata")
    print("\nFor now, cloud_data_full.csv contains all spatial data (64,800 lat/lon points)")
    print("and cloud_data_summary.csv contains global averages for all variables.")
    print("="*70)
