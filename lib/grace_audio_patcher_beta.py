import os
import sys
import stat
import time
import errno
import subprocess
import winreg
import platform
import random
import shutil
def ansi(color, background=0):
    ANSI = {
        "rst": 0,
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
    }
    return f"\033[{10*background + ANSI[color]}m"
print(f"Version: {sys.version}")
print(f"Platform Arch: {platform.architecture()[0]}")
os.system("")
CUSTOMS = {
    2259632: "special_lobby.ogg",
    875794: "special_dyson_vacuum.ogg",
    556944: "special_carnation.ogg",
    587519: "special_random_ass_scream.ogg",
}
CUSTOMS_REVERSE = {}
CUSTOM_NAMES = CUSTOMS_REVERSE.keys()
CUSTOMS_FINAL = {}
for k in CUSTOMS:
    CUSTOMS_REVERSE[CUSTOMS[k]] = k

def has_winfsp():
    service_path = r"SYSTEM\CurrentControlSet\Services\WinFsp.Launcher"
    
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, service_path, 0, winreg.KEY_READ) as key:
            return True
    except FileNotFoundError:
        return False
    return False

print("Checking for WinFSP...")
if not has_winfsp():
    print("WinFSP is not currently installed on this system.")
    print("Please proceed through the installation process.")
    os.system(".\\lib\\winfsp-2.1.25156.msi")
    while not has_winfsp():
        time.sleep(1)
    time.sleep(5)
print("")
print("WinFSP is installed!")

from winfspy import (
    FileSystem,
    NTStatusMediaWriteProtected,
)
from winfspy import memfs
from winfspy.memfs import InMemoryFileSystemOperations, FileObj, Path, FileSystem, filetime_now

targets = []
targetmap = {}



print(f"{ansi("yellow",0)}>> GRACE RUNTIME AUDIO PATCHER FOR ROBLOX ( Patch VII: dementia )")
print("   |- Made with suffering by @ZXMushroom63" + ansi("rst",0))
print(ansi("magenta", 0))
with open(".\\lib\\db.txt") as f:
    lines = f.readlines()
    for l in lines:
        if len(l) <= 1:
            continue
        parts = l.split(" ")
        targ = int(parts[0].strip())
        targets.append(targ)
        name = parts[1].strip().replace("\"", "")
        targetmap[targ] = name
        print(f"  - Target: {name} sz={targ}")
    f.close()

path = os.path.expandvars("%temp%\\Roblox\\sounds")
os.system("taskkill /F /IM RobloxPlayerBeta.exe /T >NUL 2>&1")
if os.path.exists(path):
    subprocess.run(f'del /s /q /f "{path}\\*" >NUL 2>&1', shell=True)
    subprocess.run(f'rd "{path}" >NUL 2>&1', shell=True)

oggs = []
random.seed(os.urandom(128))
current_dir = os.getcwd() + "/playlist_cache"
try:
    playlist_files = os.listdir(current_dir)
except:
    playlist_files = []
for file in playlist_files:
    if file.endswith(".ogg"):
        basename = os.path.basename(file)
        if (basename == "special_selectall.ogg"):
            selectall = current_dir + "/" + file
            break
        if (basename in CUSTOM_NAMES):
            print(f"  - Registered: {file} [SPECIAL]")
            CUSTOMS_FINAL[CUSTOMS_REVERSE[basename]] = current_dir + "/" + file
        else:
            print(f"  - Registered: {file}")
            oggs.append(current_dir + "/" + file)
if (len(oggs) == 0):
    print(ansi("rst", 0) + "First, put your songs in the PLAYLIST folder")
    print("Then, run UPDATE_PLAYLIST.bat")
    print("Finally, close this window, and run RUN.bat")
    print("(full instructions in HOW_TO_USE.txt)")
    time.sleep(1000)
    exit()
random.shuffle(oggs)
up_next = oggs[0]
def reroll_music():
    global up_next
    next = (oggs.index(up_next) + 1) % len(oggs)
    up_next = oggs[next]
recurse_blocker = False
class GraceOperations(InMemoryFileSystemOperations):
    def write(self, file_context, buffer, offset, write_to_end_of_file, constrained_io):
        global recurse_blocker
        if self.read_only:
            raise NTStatusMediaWriteProtected()

        if constrained_io:
            ret = file_context.file_obj.constrained_write(buffer, offset)
        else:
            ret = file_context.file_obj.write(buffer, offset, write_to_end_of_file)
        
        if recurse_blocker:
            return ret
        fsize = file_context.file_obj.file_size
        if fsize in targets and not recurse_blocker:
            recurse_blocker = True
            with open(up_next, "rb") as file:
                data = bytearray(file.read())
                file_context.file_obj.data = data
                file_context.file_obj.set_file_size(len(data))
                file_context.file_obj.data = data
                print(f"{ansi("green",0)}[SUCCESS] Piped cache file! :) {ansi("blue",0)} Up next: " + os.path.basename(up_next) + ansi("rst",0))
                reroll_music()
            recurse_blocker = False
        elif fsize in CUSTOMS_FINAL:
            recurse_blocker = True
            with open(CUSTOMS_FINAL[fsize], "rb") as file:
                data = bytearray(file.read())
                file_context.file_obj.data = data
                file_context.file_obj.set_file_size(len(data))
                file_context.file_obj.data = data
                print(f"{ansi("green",0)}[SUCCESS] Piped cache file! :) {ansi("blue",0)} Up next: " + os.path.basename(up_next) + ansi("rst",0))
            recurse_blocker = False
        
        return ret

def mk_grace_fs(mountpoint):
    mountpoint = Path(mountpoint)
    reject_irp_prior_to_transact0 = False

    operations = GraceOperations("GraceVFS")
    fs = FileSystem(
        str(mountpoint),
        operations,
        sector_size=512,
        sectors_per_allocation_unit=1,
        volume_creation_time=filetime_now(),
        volume_serial_number=0,
        file_info_timeout=1000,
        case_sensitive_search=1,
        case_preserved_names=1,
        unicode_on_disk=1,
        persistent_acls=1,
        post_cleanup_when_modified_only=1,
        um_file_context_is_user_context2=1,
        file_system_name=str(mountpoint),
        prefix="",
        debug=False,
        reject_irp_prior_to_transact0=reject_irp_prior_to_transact0,
        # security_timeout_valid=1,
        # security_timeout=10000,
    )
    return fs

def main(mountpoint):
    fs = mk_grace_fs(mountpoint)
    try:
        print(ansi("rst", 0) + "Starting FS")
        fs.start()
        print("FS started, keep it running forever")
        print("*** NOTICE **********************")
        print("* Press CTRL+C IN THIS TERMINAL *")
        print("* TO STOP, CLOSE THE WINDOW AF- *")
        print("* -TER, TO AVOID FUTURE ISSUES. *")
        print("*********************************")
        time.sleep(1)
        os.makedirs(mountpoint + "\\sounds")
        subprocess.run(f'mklink /d "{path}" "{mountpoint}\\sounds" >NUL 2>&1', shell=True)
        while True:
            cmd = input("")

    finally:
        print("Stopping FS")
        fs.stop()
        print("FS stopped")
        print("Unlinking sound directory from VFS")
        subprocess.run(f'rd "{path}" >NUL 2>&1', shell=True)
        subprocess.run(f'mkdir "{path}" >NUL 2>&1', shell=True)
        time.sleep(0.25)
        print("Bye!")
        time.sleep(0.35)

main("O:")
time.sleep(69420)