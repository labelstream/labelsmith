import sys
import subprocess
from pathlib import Path
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_shyft():
    python_path = sys.executable
    src_path = Path("src/labelsmith/shyft/Shyft.py").resolve()

    if not src_path.exists():
        logging.error(f"Source file not found: {src_path}")
        return

    nuitka_args = [
        python_path,
        "-m", "nuitka",
        "--standalone",
        "--macos-create-app-bundle",
        "--macos-app-icon=src/labelsmith/shyft/resources/icon.icns",
        "--macos-app-name=Shyft",
        "--macos-sign-identity=-",  # Use ad-hoc signing
        '--macos-app-protected-resource="NSUserSelectedFilesReadWriteAccess:Read and write access to user-selected files"',
        '--macos-app-protected-resource="NSNetworkClientAccess:Outgoing network connections"',
        '--macos-app-protected-resource="NSFileManagerAccess:~/Library/Application Support/Labelsmith/,~/Library/Application Support/Labelsmith/Shyft/,~/Library/Caches/Labelsmith/,~/Library/Caches/Labelsmith/Shyft/,~/.config/Labelsmith/,~/.config/Labelsmith/Shyft/:Read and write access to application directories"',
        "--enable-plugin=tk-inter",
        "--include-package=tkinter",
        "--include-package=labelsmith",
        "--include-package=labelsmith.shyft",
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
        # "--include-module=multiprocessing",
        # "--include-module=threading",
        # "--include-module=subprocess",
        "--include-module=nltk",
        "--include-module=pandas",
        # "--include-module=typing",
        # "--include-module=json",
        # "--include-module=tempfile",
        # "--include-module=webbrowser",
        # "--include-module=logging",
        # "--include-module=datetime",
        str(src_path)
    ]

    # Set environment variables
    env = os.environ.copy()
    env['MPLBACKEND'] = 'TkAgg'
    env['NLTK_DATA'] = str(Path(__file__).parent.parent.resolve() / "src/labelsmith/shyft/resources/nltk_data")

    logging.info("Starting Shyft build process...")
    try:
        subprocess.run(nuitka_args, check=True, env=env)
        logging.info("Shyft build completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Build process failed with error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during build: {e}")

if __name__ == "__main__":
    build_shyft()