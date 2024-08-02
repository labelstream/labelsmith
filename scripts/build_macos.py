import sys
import subprocess
from pathlib import Path
import os
import logging
import toml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_version():
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        pyproject_data = toml.load(pyproject_path)
        return pyproject_data["tool"]["poetry"]["version"]
    except Exception as e:
        logging.error(f"Failed to read version from pyproject.toml: {e}")
        return "0.0.0"  # Fallback version

def build_shyft():
    python_path = sys.executable
    src_path = Path("src/labelsmith/shyft/Shyft.py").resolve()

    if not src_path.exists():
        logging.error(f"Source file not found: {src_path}")
        return

    version = get_version()
    nuitka_args = [
        python_path,
        "-m", "nuitka",
        "--standalone",
        "--macos-create-app-bundle",
        "--macos-app-name=Shyft",
        "--macos-app-icon=src/labelsmith/shyft/resources/icon.icns",
        "--macos-sign-identity=-",  # Use ad-hoc signing
        '--macos-app-protected-resource="NSUserSelectedFilesReadWriteAccess:Read and write access to user-selected files"',
        '--macos-app-protected-resource="NSNetworkClientAccess:Outgoing network connections"',
        '--macos-app-protected-resource="NSFileManagerAccess:~/Library/Application Support/Labelsmith/,~/Library/Application Support/Labelsmith/Shyft/,~/Library/Caches/Labelsmith/,~/Library/Caches/Labelsmith/Shyft/,~/.config/Labelsmith/,~/.config/Labelsmith/Shyft/:Read and write access to application directories"',
        "--enable-plugin=tk-inter",
        "--include-package=tkinter",
        "--include-module=labelsmith",
        "--include-module=labelsmith.shyft",
        "--include-module=labelsmith.shyft.gui",
        "--include-module=labelsmith.shyft.core",
        "--include-module=labelsmith.shyft.utils",
        "--include-module=labelsmith.shyft.core.autologger",
        "--include-module=labelsmith.shyft.core.config_manager",
        "--include-module=labelsmith.shyft.core.data_manager",
        "--include-module=labelsmith.shyft.core.nltk_manager",
        "--include-module=labelsmith.shyft.gui.custom_widgets",
        "--include-module=labelsmith.shyft.gui.dialogs",
        "--include-module=labelsmith.shyft.gui.entry_forms",
        "--include-module=labelsmith.shyft.gui.main_window",
        "--include-module=labelsmith.shyft.gui.menu",
        "--include-module=labelsmith.shyft.gui.timer_window",
        "--include-module=labelsmith.shyft.utils.error_handler",
        "--include-module=labelsmith.shyft.utils.file_utils",
        "--include-module=labelsmith.shyft.utils.log_config",
        "--include-module=labelsmith.shyft.utils.plotting",
        "--include-module=labelsmith.shyft.utils.system_utils",
        "--include-module=labelsmith.shyft.utils.theme_manager",
        "--include-module=labelsmith.shyft.utils.time_utils",
        "--include-module=labelsmith.shyft.constants",
        "--include-module=labelsmith.shyft.Shyft",
        "--include-module=labelsmith.utils",
        "--include-module=labelsmith.utils.metrics",
        "--include-module=matplotlib",
        "--include-module=matplotlib.figure",
        "--include-module=matplotlib.pyplot",
        "--include-module=matplotlib.dates",
        "--include-module=mpld3",
        "--include-module=mpld3.plugins",
        "--include-module=nltk",
        "--include-module=pandas",
        str(src_path)
    ]

    # Set environment variables
    env = os.environ.copy()
    env['MPLBACKEND'] = 'TkAgg'
    env['NLTK_DATA'] = str(Path(__file__).parent.parent / "src" / "labelsmith" / "shyft" / "resources" / "nltk_data")

    logging.info(f"Starting Shyft build process for macOS (version {version})...")
    try:
        subprocess.run(nuitka_args, check=True, env=env)
        logging.info("Shyft build for macOS completed successfully.")
        create_dmg(version)
    except subprocess.CalledProcessError as e:
        logging.error(f"Build process failed with error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during build: {e}")

def create_dmg(version):
    logging.info("Creating DMG...")
    
    app_name = "Shyft.app"
    dmg_name = f"Shyft-{version}.dmg"
    source_dir = "./Shyft.app"
    dest_dir = "./output"
    background_img = "./src/labelsmith/shyft/resources/dmg-background.png"

    # Ensure source directory exists
    if not os.path.exists(source_dir):
        logging.error(f"Source directory does not exist: {source_dir}")
        return

    # Ensure destination directory exists, or create it
    os.makedirs(dest_dir, exist_ok=True)

    # Ensure background image exists
    if not os.path.exists(background_img):
        logging.error(f"Background image does not exist: {background_img}")
        return

    # Create the DMG
    cmd = [
        "create-dmg",
        "--volname", "Shyft Installer",
        "--background", background_img,
        "--window-size", "600", "400",
        "--icon-size", "100",
        "--app-drop-link", "400", "150",
        "--icon", app_name, "200", "150",
        f"{dest_dir}/{dmg_name}",
        source_dir
    ]

    try:
        subprocess.run(cmd, check=True)
        logging.info(f"DMG created successfully: {dest_dir}/{dmg_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to create DMG: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during DMG creation: {e}")

if __name__ == "__main__":
    build_shyft()