import os
import platform
import shutil
import zipfile

import banner


def zip_folder(folder_path: str, name: str):
    abs_folder_path = os.path.abspath(folder_path)

    local = os.getcwd()
    zip_file_path = os.path.join(local, name)
    archive = zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(abs_folder_path):
        for file in files:
            if file == name:
                continue
            file_path = os.path.join(root, file)
            if ".git" in file_path:
                continue
            print(f"Adding: {file_path}")
            archive.write(file_path, os.path.relpath(file_path, abs_folder_path))

    archive.close()
    print(f"Done!")


ZIP_WHITELIST = ["run", "run.exe", "bin", "LICENSE"]

print(f"\033[31m {banner.banner1} \033[0m")
print(f"Build for {platform.system()}")

os.system("pip install -r requirements.txt")

local = os.getcwd()

TARGET_ARCH = ARCH if (ARCH := platform.machine()) else ""
print(f"Target Arch: {TARGET_ARCH}")

if TARGET_PLATFORM := platform.system() == "Linux":
    name = "TIK-linux.zip"
else:
    name = "TIK-win.zip"

# build binary
os.system("pyinstaller -F run.py --exclude-module=numpy -i icon.ico")

if os.name == "nt":
    if os.path.exists(local + os.sep + "dist" + os.sep + "run.exe"):
        shutil.move(local + os.sep + "dist" + os.sep + "run.exe", local)
    if os.path.exists(local + os.sep + "bin" + os.sep + "Linux"):
        shutil.rmtree(local + os.sep + "bin" + os.sep + "Linux")
    if os.path.exists(local + os.sep + "bin" + os.sep + "Android"):
        shutil.rmtree(local + os.sep + "bin" + os.sep + "Android")
    if os.path.exists(local + os.sep + "bin" + os.sep + "Darwin"):
        shutil.rmtree(local + os.sep + "bin" + os.sep + "Darwin")
elif os.name == "posix":
    if os.path.exists(local + os.sep + "dist" + os.sep + "run"):
        shutil.move(local + os.sep + "dist" + os.sep + "run", local)
    for dirpath, dirnames, filenames in os.walk(local + os.sep + "bin"):
        for dirname in dirnames:
            if dirname != TARGET_PLATFORM:
                shutil.rmtree(dirpath + os.sep + dirname)
            # 再遍历这个dirname下的文件夹
            for sub_dir in os.listdir(dirpath + os.sep + dirname):
                if sub_dir != TARGET_ARCH:
                    shutil.rmtree(dirpath + os.sep + dirname + os.sep + sub_dir)

for i in os.listdir(local):
    if i not in ZIP_WHITELIST:
        print(f"Removing {i}")
        if os.path.isdir(local + os.sep + i):
            try:
                shutil.rmtree(local + os.sep + i)
            except Exception or OSError as e:
                print(e)
        elif os.path.isfile(local + os.sep + i):
            try:
                os.remove(local + os.sep + i)
            except Exception or OSError as e:
                print(e)
    else:
        print(i)

if os.name == "posix":
    for root, dirs, files in os.walk(local, topdown=True):
        for i in files:
            print(f"Chmod {os.path.join(root, i)}")
            os.system(f"chmod a+x {os.path.join(root, i)}")

zip_folder(".", name)
