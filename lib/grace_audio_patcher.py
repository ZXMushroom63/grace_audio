import time
import os
import random
import shutil
import subprocess
import ctypes
from ctypes import wintypes
from watchdog.observers import Observer
import stat
import sys
from watchdog.events import FileSystemEventHandler

os.system('')

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
DELETE = 0x00010000
OPEN_ALWAYS = 4
OPEN_EXISTING = 3
CREATE_ALWAYS = 2
kernel32 = ctypes.windll.kernel32


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

SETMAP = {
    "UltrasonicFaith": [2957866], # filesize in bytes (not filesize on disk)
    "AmenReprise": [2989193],
    "AviaryAction": [3618798],
    "BlueLicorice": [2280850],
    "SavingYourGrace": [2205856],
    "ClocktowerMayhem": [3090144],
    "CollapsingTimeRift": [4191064],
    "CollapsingVoidRift": [3312430],
    "DarkMatter": [3102803],
    "ExpertRace": [1713565],
    "FloralFury": [3205327],
    "Glaggle": [2299803],
    "ItsHappyHour": [2913861],
    "ItsPizzaTime": [3242347],
    "Kitchen": [3350221],
    "RunningMan": [3136419],
    "TheWorldRevolving": [3253729],
    "TimeToSmile": [3016324],
    "ThousandMarch": [3903227],
    "8BIT": [2970465],
    "DTID": [2656276],
}
REVERSE_MAP = {}
for key in SETMAP:
    for sz in SETMAP[key]:
        REVERSE_MAP[sz] = key
startTriggers = (lambda x: [item for sublist in [q for q in x.values()] for item in sublist])(
    SETMAP
)
print(f"{ansi("yellow",0)}>> GRACE RUNTIME AUDIO PATCHER FOR ROBLOX ( Patch V: insanity )")
oggs = []

current_dir = os.getcwd() + "/playlist_cache"
for file in os.listdir(current_dir):
    if file.endswith(".ogg"):
        basename = os.path.basename(file)
        if (basename in CUSTOM_NAMES):
            print(f"  - Registered: {file} [SPECIAL]")
            CUSTOMS_FINAL[CUSTOMS_REVERSE[basename]] = current_dir + "/" + file
        else:
            print(f"  - Registered: {file}")
            oggs.append(current_dir + "/" + file)
if (len(oggs) == 0):
    print("First, put your songs in the PLAYLIST folder")
    print("Then, run UPDATE_PLAYLIST.bat")
    print("Finally, close this window, and run RUN.bat")
    print("(full instructions in HOW_TO_USE.bat)")
    time.sleep(1000)
    exit()
random.shuffle(oggs)
print(f"""{ansi("rst",0)}Target file sizes {ansi("magenta",0)}[USING FSIZE]: \n  - {
    "\n - ".join(
        map(
            lambda x: 
                f"{ansi("magenta",0)}{x} bytes{ansi("rst",0)} ({REVERSE_MAP[x]})",
            startTriggers
        )
    )
}{ansi("rst",0)}""")
path = os.path.expandvars("%temp%\\Roblox\\sounds")

last_ev = {"type": "none", "name": "none"}
FILE_ATTRIBUTE_READONLY = 0x01
FILE_ATTRIBUTE_NORMAL = 0x80

def set_readonly(file_path, enable=True):
    mode = os.stat(file_path).st_mode
    if enable:
        os.chmod(file_path, mode & ~stat.S_IWRITE)
    else:
        os.chmod(file_path, mode | stat.S_IWRITE)
    return True
def get_shared_lock(file_path):
    handle = kernel32.CreateFileW(
        file_path,
        GENERIC_READ | GENERIC_WRITE | DELETE,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_ALWAYS,
        0,
        None
    )
    
    if handle == -1:
        raise Exception(f"Failed to open file. Error code: {kernel32.GetLastError()}")
    
    return handle

# up_next = oggs[random.randint(0, len(oggs) - 1)]
# def reroll_music():
#     global up_next
#     next = up_next
#     while up_next == next:
#         next = oggs[random.randint(0, len(oggs) - 1)]
#     up_next = next
up_next = oggs[0]
def reroll_music():
    global up_next
    next = (oggs.index(up_next) + 1) % len(oggs)
    up_next = oggs[next]

def kill_handle(fd):
    kernel32.CloseHandle(fd)

def kernel_copy(src, dst):
    fd = get_shared_lock(dst)
    shared_copy(src, fd)
    kernel32.CloseHandle(fd)

def shared_copy(path_src, fd):
    h_src = kernel32.CreateFileW(
        path_src, GENERIC_READ, 
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None, OPEN_EXISTING, 0, None
    )

    if h_src == -1:
        print(f"Failed to open source. Error: {kernel32.GetLastError()}")
        return False
    
    if fd == -1:
        kernel32.CloseHandle(h_src)
        print(f"Failed to open destination. Error: {kernel32.GetLastError()}")
        return False

    try:
        buffer_size = 64 * 1024
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = wintypes.DWORD(0)
        bytes_written = wintypes.DWORD(0)

        while True:
            if not kernel32.ReadFile(h_src, buffer, buffer_size, ctypes.byref(bytes_read), None) or bytes_read.value == 0:
                break
            kernel32.WriteFile(fd, buffer, bytes_read.value, ctypes.byref(bytes_written), None)
            
        print(f"Copy complete to: {fd}")
        return True

    finally:
        kernel32.CloseHandle(h_src)

lock_map = {}

def patch(fname, event, readonly=False):
    try:
        shutil.copyfile(up_next, event.src_path)
        if (readonly):
            set_readonly(event.src_path, True)
        print(f"{ansi("green",0)}[SUCCESS] Piped cache file! :) {ansi("blue",0)} Up next: " + os.path.basename(up_next) + ansi("rst",0))
        reroll_music()
    except Exception as e:
        print(f"{ansi("red",0)+ansi("black",1)}[FAILURE] Failed to nuke the cache (File may be in use) :( [im gonna cry bro]")
        print(f"error: {e}{ansi("rst",0)+ansi("rst",1)}")
        if (fname in lock_map):
            shared_copy(up_next, lock_map[fname])

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global lock_map
        global last_ev
        
        if event.is_directory: return
        
        try:
            size = os.path.getsize(event.src_path)
        except:
            return
        fname = os.path.basename(event.src_path)

        if size in startTriggers:
            patch(fname, event)
        elif size in CUSTOMS_FINAL:
            try:
                shutil.copyfile(CUSTOMS_FINAL[size], event.src_path)
                print(f"{ansi("green",0)}applied {os.path.basename(CUSTOMS_FINAL[size])}{ansi("rst",0)}")
            except:
                print(f"{ansi("red",0)}failed to {os.path.basename(CUSTOMS_FINAL[size])}{ansi("rst",0)}")
            
        fname = os.path.basename(event.src_path)
        last_ev = {"type": "mod", "name": fname}

    def on_created(self, event):
        global last_ev
        fname = os.path.basename(event.src_path)
        
        try:
            size = os.path.getsize(event.src_path)
        except:
            return
        
        if (size in startTriggers):
            patch(fname, event, True)
            #print(f"[CR] Trigger Match Found: {fname}  - {time.time()}")
        elif (size == 0):
            print(f"[CR] Sleeping file handle???: {fname}  - {time.time()}")
        
        last_ev = {"type": "create", "name": fname}

if __name__ == "__main__":
    if not os.path.exists(path):
        os.makedirs(path)
    subprocess.run(f'del /s /q /f "{path}\\*" >NUL 2>&1', shell=True)
    

    print(f"{ansi("green",0)}Hooking into: {path}{ansi("rst",0)}")
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"{ansi("cyan",0)+ansi("black",1)}Waiting for asset fetch. You may have to rejoin.{ansi("rst",0)+ansi("rst",1)}")
    
    try:
        while True:
            cmd = input()
            print(f"terminal is useless for now")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
