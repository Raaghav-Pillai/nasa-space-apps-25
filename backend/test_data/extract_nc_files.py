import csv
import requests
import re
from pathlib import Path
from datetime import datetime

def extract_date_from_filename(filename):
    """Extract date from filename format: CLDPROP_D3_VIIRS_NOAA20.A2024365.011.2025003003300.nc"""
    match = re.search(r'\.A(\d{7})', filename)
    if match:
        year_doy = match.group(1)
        year = int(year_doy[:4])
        doy = int(year_doy[4:])
        date = datetime.strptime(f"{year}-{doy}", "%Y-%j")
        return date.strftime("%Y-%m-%d")
    return None

def download_nc_files(csv_path, output_dir):
    """Download .nc files from CSV and rename them by date"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader, 1):
            url = row['fileUrls for custom selected']
            filename = url.split('/')[-1]

            # Extract date from filename
            date_str = extract_date_from_filename(filename)
            if date_str:
                new_filename = f"{date_str}.nc"
            else:
                new_filename = filename

            output_file = output_path / new_filename

            print(f"[{idx}] Downloading: {filename}")
            print(f"    Saving as: {new_filename}")

            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"    ✓ Downloaded successfully")
            except Exception as e:
                print(f"    ✗ Error: {e}")

if __name__ == "__main__":
    csv_file = r"c:\Users\Raaghav\Desktop\Raaghav\Projects\Work\nasa-space-apps-25\backend\data\Cloud\list_nc.csv"
    output_directory = r"c:\Users\Raaghav\Desktop\Raaghav\Projects\Work\nasa-space-apps-25\backend\data\Cloud\nc_files"

    download_nc_files(csv_file, output_directory)
