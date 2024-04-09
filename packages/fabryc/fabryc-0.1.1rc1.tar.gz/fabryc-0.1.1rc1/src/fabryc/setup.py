import sys
import urllib.request
import zipfile
from pathlib import Path

from pythonnet import load

load("coreclr")

_IS_SETUP = False

NUGET_URL = "https://www.nuget.org/api/v2/package/{packageID}/{packageVersion}"

PACKAGES_DIR = "packages"
PACKAGES_PATH = Path(__file__).parent / PACKAGES_DIR

PACKAGES = [
    {
        "name": "Microsoft.AnalysisServices.NetCore.retail.amd64",
        "version": "19.77.0",
    }
]


def install_packages():
    """Download required .NET packages and install."""

    print("Installing required packages...")

    PACKAGES_PATH.mkdir(exist_ok=True)

    for package in PACKAGES:
        name = package["name"]
        version = package["version"]

        package_filename = f"{name}.{version}.nupkg"
        package_path = PACKAGES_PATH / package_filename

        url = NUGET_URL.format(packageID=name, packageVersion=version)

        print(f"Downloading {package}.{version}  to {package_path}...")

        urllib.request.urlretrieve(url, PACKAGES_PATH / package_path)

        with zipfile.ZipFile(package_path, "r") as zip_ref:
            zip_ref.extractall(PACKAGES_PATH)


def setup():

    if not is_setup():

        dll_folder = Path(PACKAGES_PATH) / "lib/netcoreapp3.0"

        if not (dll_folder / "Microsoft.AnalysisServices.dll").exists():
            install_packages()

        import clr

        sys.path.append(str(dll_folder))

        # pylint: disable=no-member
        clr.AddReference("Microsoft.AnalysisServices")  # type:ignore

        global _IS_SETUP  # pylint: disable=global-statement
        _IS_SETUP = True

        print("Setup completed.")


def is_setup() -> bool:
    return _IS_SETUP
