import subprocess
import os
import sys
import shutil
import urllib.request
import ctypes
from colorama import init, Fore, Style
from time import sleep

if not sys.platform == "win32":
    print("This script is only supported on Windows")
    sleep(0.2)
    exit()


# Initialize colorama
init()


try:
    from github import Github
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyGithub"])
    from github import Github
import traceback


def run(
    urlList: list[str, str],
    postExecution: bool = True,
    clearCache: bool = True,
    customGhObj: Github = None,
):
    try:
        gh = Github() if customGhObj is None else customGhObj
        for url, name in urlList:
            repo = gh.get_repo(url)
            print(f"Downloading {name} from {url}")
            if os.path.exists(name):
                os.remove(name)
                print(f"Removed existing {name}")

            release = repo.get_releases()[0]
            for asset in release.get_assets():
                if asset.name != name:
                    print(f"Skipping {asset.name} from {release.title}")
                    continue
                print(f"Downloading {asset.name} from {release.title}")
                if os.path.exists(name):
                    os.remove(name)
                urllib.request.urlretrieve(
                    asset.browser_download_url,
                    f"{name}-temp",
                    reporthook=lambda blocknum, blocksize, totalsize: print(
                        f"\r\033[K{Fore.GREEN}{name}: Downloaded {blocknum * blocksize}/{totalsize}{Style.RESET_ALL}: {str('0'*int((2-int((100/totalsize)*(blocknum*blocksize))-1/10))) + str(round((100/totalsize)*(blocknum*blocksize), 2))[0:4]}% [{'#' * int((blocknum * blocksize) / totalsize * 45)}{' ' * (45 - int(int((blocknum * blocksize)) / totalsize * 45))}]",
                        end="",
                        flush=True,
                    ),
                )
                print(f"Downloaded {name}")
                with open(f"{name}.version", "w") as f:
                    f.write(release.title)

            filePath: str
            for url, filePath in urlList:
                newFilePath = filePath.removesuffix("-temp")
                shutil.copy(f"{filePath}-temp", newFilePath)
                print(f"Renamed {filePath}-temp to {newFilePath}")
                print(f"File located at: {os.path.abspath(newFilePath)}")
                if clearCache:
                    print(f"Clearing cache for {filePath}")
                    os.remove(filePath + "-temp")
                    print(f"Cache cleared for {filePath}")
                break
            break

        newFilePath: str
        for url, newFilePath in urlList:
            if postExecution:
                if newFilePath.endswith(
                    (".exe", ".msi", ".bat", ".app", ".sh", ".pkg")
                ):
                    os.chmod(newFilePath, 0o755)
                    if newFilePath.endswith(".pkg"):
                        subprocess.Popen(
                            ["open", os.path.abspath(newFilePath)],
                            shell=False,
                        )
                    else:
                        subprocess.Popen(
                            executable=f"{os.path.abspath(newFilePath)}",
                            shell=False,
                            args=[],
                        )
                else:
                    print("Script is not an executable, skipping post execution")

        print("All downloads completed")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error: {e} at {fname}, line {exc_tb.tb_lineno}")
        traceback.print_exc()
        input("Press Enter to exit")
        exit()


def checkForUpdates(
    _repo,
    curVersion,
    update: bool = True,
    clearCache: bool = True,
    execute: bool = True,
):
    token = input("Enter your Github token, or press enter to skip: ")
    if len(token) > 0:
        gh = Github(token)
    else:
        gh = Github()
    try:
        for repo_name, name in _repo:
            repo = gh.get_repo(repo_name)
            release = repo.get_releases()[0]
            if release.title != curVersion:
                print(f"New version available: {release.title}")
                if update:
                    run([(repo_name, name)], execute, clearCache)
                else:
                    print(f"Update {release.title} skipped")
            else:
                print(
                    "No updates available, Current version is up to date: " + curVersion
                )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error: {e} at {fname}, line {exc_tb.tb_lineno}")
        input("Press Enter to exit")
        exit()


if __name__ == "__main__":
    print("This program should not be run directly")
    sleep(2)
else:

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        print(
            "Script is not running as administrator. Attempting to restart with admin privileges..."
        )
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
