import os
import stat

def setup_netrc(username, password):
    """
    Create .netrc file for NASA Earthdata authentication.
    This is the recommended method for authenticating with NASA Earthdata.
    """
    home = os.path.expanduser("~")
    netrc_path = os.path.join(home, ".netrc")

    # Content for .netrc file
    netrc_content = f"""machine urs.earthdata.nasa.gov
    login {username}
    password {password}
"""

    # Check if .netrc already exists
    if os.path.exists(netrc_path):
        print(f"⚠ Warning: {netrc_path} already exists")
        overwrite = input("Do you want to overwrite it? (yes/no): ").strip().lower()
        if overwrite not in ['yes', 'y']:
            print("Cancelled. Using existing .netrc file.")
            return netrc_path

    # Write .netrc file
    with open(netrc_path, 'w') as f:
        f.write(netrc_content)

    # Set proper permissions (required for .netrc)
    # On Windows, this is less critical, but we'll try
    try:
        os.chmod(netrc_path, stat.S_IRUSR | stat.S_IWUSR)
    except:
        pass  # Windows might not support this

    print(f"✓ Created {netrc_path}")
    print("✓ NASA Earthdata authentication configured")

    return netrc_path

if __name__ == "__main__":
    print("="*70)
    print("NASA Earthdata Authentication Setup")
    print("="*70)
    print("\nThis will create a .netrc file in your home directory.")
    print("The .netrc file stores your NASA Earthdata credentials securely.")
    print("\nIf you don't have an account, register at:")
    print("https://urs.earthdata.nasa.gov/users/new")
    print("="*70 + "\n")

    username = input("Enter your NASA Earthdata username: ").strip()

    import getpass
    password = getpass.getpass("Enter your NASA Earthdata password: ").strip()

    if username and password:
        setup_netrc(username, password)
        print("\n✓ Setup complete! You can now run download_nc_files.py")
    else:
        print("✗ Username or password cannot be empty")
