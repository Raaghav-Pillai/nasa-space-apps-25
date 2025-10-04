import pandas as pd
import requests
import os
from datetime import datetime
import time
from requests.auth import HTTPBasicAuth

def download_nc_files_from_csv(csv_path, output_dir, username=None, password=None, max_files=None):
    """
    Download NetCDF files from URLs listed in a CSV file using NASA Earthdata authentication.

    Args:
        csv_path: Path to CSV file containing URLs (list_nc.csv)
        output_dir: Directory where NC files will be saved
        username: NASA Earthdata username (will use .netrc if not provided)
        password: NASA Earthdata password (will use .netrc if not provided)
        max_files: Maximum number of files to download (None = all)
    """

    # Read CSV
    print(f"Reading URLs from {csv_path}...")
    df = pd.read_csv(csv_path)

    # The CSV has columns: fileId, fileUrls for custom selected, size
    url_column = 'fileUrls for custom selected'

    if url_column not in df.columns:
        print(f"Error: Column '{url_column}' not found in CSV")
        print(f"Available columns: {list(df.columns)}")
        return False

    urls = df[url_column].tolist()

    if max_files:
        urls = urls[:max_files]

    print(f"Found {len(urls)} URLs to download")

    # Setup authentication
    auth = None
    if username and password:
        auth = HTTPBasicAuth(username, password)
        print("Using provided credentials")
    else:
        print("Using .netrc file for authentication")
        print("(Run setup_earthdata_auth.py if you haven't configured it)")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Download files
    downloaded = 0
    failed = 0
    skipped = 0

    for idx, url in enumerate(urls):
        try:
            # Extract date from URL (CLDPROP_D3_VIIRS_NOAA20.A2025001...)
            parts = url.split('.')
            date_part = None
            for part in parts:
                if part.startswith('A') and len(part) >= 8:
                    date_part = part[1:8]
                    break

            if date_part:
                year = int(date_part[:4])
                day_of_year = int(date_part[4:])
                date_obj = datetime(year, 1, 1) + pd.Timedelta(days=day_of_year - 1)
                filename = f"{date_obj.strftime('%Y-%m-%d')}.nc"
            else:
                filename = f"file_{idx:04d}.nc"

            output_path = os.path.join(output_dir, filename)

            # Skip if already exists and is valid NetCDF
            if os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    first_bytes = f.read(100)
                    # Check for NetCDF magic number or HDF5 signature
                    if (first_bytes[:3] == b'CDF' or  # NetCDF classic
                        first_bytes[:4] == b'\x89HDF' or  # HDF5/NetCDF4
                        (b'<!DOCTYPE' not in first_bytes and b'<html' not in first_bytes)):
                        print(f"[{idx+1}/{len(urls)}] Skipping {filename} - already exists")
                        skipped += 1
                        continue

            print(f"[{idx+1}/{len(urls)}] Downloading {filename}...")

            # Create session for handling redirects
            with requests.Session() as session:
                # If credentials provided, use them
                if auth:
                    session.auth = auth

                # Make request
                response = session.get(url, allow_redirects=True, timeout=180)

                # Handle redirects for authentication
                if response.status_code == 401:
                    print(f"  ✗ Authentication failed - check credentials")
                    failed += 1
                    continue

                if response.status_code == 200:
                    # Check if response is HTML
                    content_type = response.headers.get('Content-Type', '')

                    if ('text/html' in content_type or
                        b'<!DOCTYPE' in response.content[:200] or
                        b'<html' in response.content[:200] or
                        b'Earthdata Login' in response.content[:1000]):

                        print(f"  ✗ Received HTML (login page) - authentication issue")
                        print(f"     Please run: python setup_earthdata_auth.py")
                        failed += 1

                        # Save the HTML for debugging
                        debug_path = output_path.replace('.nc', '_debug.html')
                        with open(debug_path, 'wb') as f:
                            f.write(response.content[:5000])
                    else:
                        # Save NetCDF file
                        with open(output_path, 'wb') as f:
                            f.write(response.content)

                        file_size_mb = len(response.content) / (1024 * 1024)
                        print(f"  ✓ Downloaded {file_size_mb:.1f} MB")
                        downloaded += 1
                else:
                    print(f"  ✗ HTTP {response.status_code}: {response.reason}")
                    failed += 1

            # Rate limiting
            time.sleep(0.5)

            # Progress update
            if (idx + 1) % 10 == 0:
                print(f"\nProgress: {idx+1}/{len(urls)} | Downloaded: {downloaded} | Failed: {failed} | Skipped: {skipped}\n")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
            continue

    print("\n" + "="*70)
    print("Download Summary:")
    print("="*70)
    print(f"Total URLs: {len(urls)}")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Failed: {failed}")
    print(f"Output directory: {output_dir}")
    print("="*70)

    if failed > 0 and downloaded == 0:
        print("\n⚠ All downloads failed. This is likely an authentication issue.")
        print("Try running: python setup_earthdata_auth.py")
        print("Or check: https://urs.earthdata.nasa.gov/")

    return downloaded > 0

if __name__ == "__main__":
    # Determine if running from backend/ or project root
    current_dir = os.getcwd()
    if os.path.basename(current_dir) == 'backend':
        csv_file = os.path.join('data', 'Cloud', 'list_nc.csv')
        output_directory = os.path.join('data', 'Cloud', 'nc_files')
    else:
        csv_file = os.path.join('backend', 'data', 'Cloud', 'list_nc.csv')
        output_directory = os.path.join('backend', 'data', 'Cloud', 'nc_files')

    # Credentials (None = use .netrc)
    EARTHDATA_USERNAME = None
    EARTHDATA_PASSWORD = None

    # Test with fewer files first
    MAX_FILES = 5  # Change to None to download all

    print("="*70)
    print("NASA Earthdata NetCDF File Downloader")
    print("="*70)
    print(f"\nCSV file: {csv_file}")
    print(f"Output directory: {output_directory}")

    if MAX_FILES:
        print(f"\n⚠ Testing mode: Limiting to first {MAX_FILES} files")
        print("Set MAX_FILES = None in the script to download all files")

    print("\n" + "="*70 + "\n")

    download_nc_files_from_csv(
        csv_file,
        output_directory,
        username=EARTHDATA_USERNAME,
        password=EARTHDATA_PASSWORD,
        max_files=MAX_FILES
    )
