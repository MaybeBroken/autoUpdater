import subprocess
import os
import sys
import shutil
import urllib.request
import ctypes
from colorama import init, Fore, Style
from time import sleep
from json import loads

userAppData = os.getenv("APPDATA")
appId = "MaybeBroken-Software-Updater"

if not os.path.exists(userAppData + "\\" + appId):
    os.makedirs(userAppData + "\\" + appId)

os.chdir(userAppData + "\\" + appId)

init()


class PACKAGE:
    def __init__(self, _dict: dict):
        self.name = _dict.get("name")
        self.version = _dict.get("currentVersion")
        self.url = _dict.get("currentPackageUrl")
        self.date = _dict.get("currentReleaseDate")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    exit()


def download_report_hook(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    print(f"\rDownloading: {percent}%", end="")
    sys.stdout.flush()


def download_file(url: str, filename: str) -> None:
    urllib.request.urlretrieve(url, filename, reporthook=download_report_hook)


def get_packages() -> list[dict]:
    download_file(
        "https://maybebroken.github.io/api/v1/software/index.json", "app_index.json"
    )
    with open("app_index.json", "r") as f:
        packages = loads(f.read())
    return packages


def build_package_index(packages: list[dict]) -> list[PACKAGE]:
    package_index = []
    for package in packages:
        package_index.append(PACKAGE(package))
    return package_index


def cleanup():
    if os.path.exists("app_index.json"):
        os.remove("app_index.json")
