import subprocess
import os
import sys
import shutil
from github import Github

reporthook = (
    lambda blocknum, blocksize, totalsize: print(
        f"\033[92mDownloaded {blocknum * blocksize}/{totalsize}\033[0m: {str("0"*int((2-int((100/totalsize)*(blocknum*blocksize))-1/10))) + str(round((100/totalsize)*(blocknum*blocksize), 2))[0:4]}% [{"\033[92m#\033[0m" * int((blocknum * blocksize) / totalsize * 100)}{' ' * (100 - int(int((blocknum * blocksize)) / totalsize * 100))}]",
        end="\r",
    ),
)


def run(urlList: list[str, str], postExecution: bool = True):
    try:
        gh = Github()
        for url, name in urlList:
            repo = gh.get_repo(url)
            print(f"Downloading {name} from {url}\n")
            if os.path.exists(name):
                os.remove(name)
                print(f"Removed existing {name}")

            for release in repo.get_releases():
                for asset in release.get_assets():
                    if asset.name != name:
                        continue
                    print(f"Downloading {asset.name} from {release.tag_name}")
                    asset.download_asset(name, reporthook=reporthook)
                    break
                break

            print(f"Downloaded {name} from {url}\n")

        newFilePath: str
        for newFilePath in urlList:
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


run([("MaybeBroken/Python-Installer", "Python-Installer.exe")])
