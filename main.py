import urllib.request
import subprocess
import os
import sys
import shutil


def run(urlList: list, clearCache: bool = True, postExecution: bool = True):
    try:
        for key in urlList:
            print(f"Downloading {key} from {urlList[key]}\n")
            if os.path.exists(key):
                os.remove(key)
            urllib.request.urlretrieve(
                urlList[key],
                f"{key}-temp",
                reporthook=lambda blocknum, blocksize, totalsize: print(
                    f"\033[92mDownloaded {blocknum * blocksize}/{totalsize}\033[0m: {str("0"*int((2-int((100/totalsize)*(blocknum*blocksize))-1/10))) + str(round((100/totalsize)*(blocknum*blocksize), 2))[0:4]}% [{"\033[92m#\033[0m" * int((blocknum * blocksize) / totalsize * 100)}{' ' * (100 - int(int((blocknum * blocksize)) / totalsize * 100))}]",
                    end="\r",
                ),
            )
            print(f"Downloaded {key}")

        filePath: str
        for filePath in urlList:
            newFilePath = filePath.removesuffix("-temp")
            shutil.copy(f"{filePath}-temp", newFilePath)
            print(f"Renamed {filePath}-temp to {newFilePath}")
            print(f"File located at: {os.path.abspath(newFilePath)}")
            if clearCache:
                print(f"Clearing cache for {filePath}")
                os.remove(filePath + "-temp")
                print(f"Cache cleared for {filePath}")
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


def checkForUpdates(
    urlList: list[str, str], currentVersionList: list[str, str | int | float | bytes]
):
    raise NotImplementedError("This function is not implemented yet")
