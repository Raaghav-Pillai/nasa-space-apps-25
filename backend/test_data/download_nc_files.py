import pandas as pd
import requests
import os
from datetime import datetime
import time

def download_nc_files_from_csv(csv_path, output_dir, username=None, password=None, max_files=None):
    """
    Download NetCDF files from URLs listed in a CSV file.

    Args:
        csv_path: Path to CSV file containing URLs (list_nc.csv)
        output_dir: Directory where NC files will be saved
        username: NASA Earthdata username (will prompt if not provided)
        password: NASA Earthdata password (will prompt if not provided)
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

    # Get credentials if not provided
    if username is None:
        username = input("Enter NASA Earthdata username: ")
    if password is None:
        import getpass
        password = getpass.getpass("Enter NASA Earthdata password: ")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Download files
    downloaded = 0
    failed = 0
    skipped = 0

    for idx, url in enumerate(urls):
        try:
            # Extract date from URL (CLDPROP_D3_VIIRS_NOAA20.A2025001...)
            # Format: AYYDDD where YY is year and DDD is day of year
            parts = url.split('.')
            date_part = None
            for part in parts:
                if part.startswith('A') and len(part) >= 8:
                    date_part = part[1:8]  # Remove 'A' and get YYYYDDD
                    break

            if date_part:
                # Convert YYYYDDD to YYYY-MM-DD
                year = int(date_part[:4])
                day_of_year = int(date_part[4:])
                date_obj = datetime(year, 1, 1) + pd.Timedelta(days=day_of_year - 1)
                filename = f"{date_obj.strftime('%Y-%m-%d')}.nc"
            else:
                # Fallback: use index
                filename = f"file_{idx:04d}.nc"

            output_path = os.path.join(output_dir, filename)

            # Skip if already exists and is not HTML
            if os.path.exists(output_path):
                # Check if it's a valid NetCDF file (not HTML)
                with open(output_path, 'rb') as f:
                    first_bytes = f.read(100)
                    if b'<!DOCTYPE' not in first_bytes and b'<html' not in first_bytes:
                        print(f"[{idx+1}/{len(urls)}] Skipping {filename} - already exists")
                        skipped += 1
                        continue

            # Download with authentication
            print(f"[{idx+1}/{len(urls)}] Downloading {filename}...")

            # NASA Earthdata requires handling OAuth redirects
            session = requests.Session()

            # First request to get redirect to login
            response1 = session.get(url, allow_redirects=False, timeout=120)

            # Follow redirect to URS (Earthdata Login)
            if response1.status_code in [301, 302, 303, 307, 308]:
                auth_url = response1.headers.get('Location')

                # Authenticate with URS
                auth_response = session.get(
                    auth_url,
                    auth=(username, password),
                    allow_redirects=True,
                    timeout=120
                )

                # Now try the original URL again with the authenticated session
                response = session.get(url, allow_redirects=True, timeout=120)
            else:
                # Direct download with basic auth
                session.auth = (username, password)
                response = session.get(url, allow_redirects=True, timeout=120)

            if response.status_code == 200:
                # Check if response is HTML (login page)
                if b'<!DOCTYPE' in response.content[:100] or b'<html' in response.content[:100]:
                    print(f"  ⚠ Warning: Received HTML instead of NetCDF - check credentials")
                    failed += 1
                else:
                    # Save file
                    with open(output_path, 'wb') as f:
                        f.write(response.content)

                    file_size_mb = len(response.content) / (1024 * 1024)
                    print(f"  ✓ Downloaded {file_size_mb:.1f} MB")
                    downloaded += 1
            else:
                print(f"  ✗ Failed: HTTP {response.status_code}")
                failed += 1

            # Rate limiting - be nice to the server
            time.sleep(0.5)

            # Progress update every 10 files
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

    return True

if __name__ == "__main__":
    import sys

    # Determine if we're running from backend/ or project root
    current_dir = os.getcwd()
    if os.path.basename(current_dir) == 'backend':
        # Running from backend directory
        csv_file = os.path.join('data', 'Cloud', 'list_nc.csv')
        output_directory = os.path.join('data', 'Cloud', 'nc_files')
    else:
        # Running from project root
        csv_file = os.path.join('backend', 'data', 'Cloud', 'list_nc.csv')
        output_directory = os.path.join('backend', 'data', 'Cloud', 'nc_files')

    # You can set credentials here or leave None to be prompted
    EARTHDATA_USERNAME = None  # or set to your username
    EARTHDATA_PASSWORD = None  # or set to your password

    # Limit download for testing (None = download all)
    MAX_FILES = None  # Set to a small number like 10 for testing

    print("="*70)
    print("NASA Earthdata NetCDF File Downloader")
    print("="*70)
    print(f"\nCSV file: {csv_file}")
    print(f"Output directory: {output_directory}")

    if MAX_FILES:
        print(f"Limiting to first {MAX_FILES} files for testing")

    print("\nNOTE: You need a NASA Earthdata account to download these files.")
    print("Register at: https://urs.earthdata.nasa.gov/users/new")
    print("="*70 + "\n")

    proceed = input("Do you want to proceed? (yes/no): ").strip().lower()

    if proceed in ['yes', 'y']:
        download_nc_files_from_csv(
            csv_file,
            output_directory,
            username=EARTHDATA_USERNAME,
            password=EARTHDATA_PASSWORD,
            max_files=MAX_FILES
        )
    else:
        print("Download cancelled.")
