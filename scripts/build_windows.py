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

    nuitka_args = [
        python_path,
        "-m", "nuitka",
        "--standalone",
        "--windows-disable-console",
        "--windows-icon-from-ico=src/labelsmith/shyft/resources/icon.ico",
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

    logging.info("Starting Shyft build process for Windows...")
    try:
        subprocess.run(nuitka_args, check=True, env=env)
        logging.info("Shyft build for Windows completed successfully.")
        create_installer()
    except subprocess.CalledProcessError as e:
        logging.error(f"Build process failed with error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during build: {e}")

def create_installer():
    logging.info("Creating installer...")
    version = get_version()
    inno_script = f"""
#define MyAppName "Shyft"
#define MyAppVersion "{version}"
#define MyAppPublisher "Labelsmith Contributors"
#define MyAppURL "https://github.com/kosmolebryce/labelsmith"
#define MyAppExeName "Shyft.exe"

[Setup]
AppId={{5F3AC5D7-5105-4730-A01F-F2E66E718A9D}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=output
OutputBaseFilename=ShyftSetup-{{#MyAppVersion}}
SetupIconFile=src\\labelsmith\\shyft\\resources\\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "Shyft.dist\\Shyft.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "Shyft.dist\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\\labelsmith\\shyft\\resources\\nltk_data\\*"; DestDir: "{{app}}\\nltk_data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
    """
    
    with open("setup.iss", "w") as f:
        f.write(inno_script)
    
    try:
        subprocess.run(["iscc", "setup.iss"], check=True)
        logging.info(f"Installer for version {version} created successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Installer creation failed with error: {e}")
    except FileNotFoundError:
        logging.error("Inno Setup Compiler (iscc) not found. Please make sure it's installed and added to PATH.")
    finally:
        os.remove("setup.iss")

if __name__ == "__main__":
    build_shyft()