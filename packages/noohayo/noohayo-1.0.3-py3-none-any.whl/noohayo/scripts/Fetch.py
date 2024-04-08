import platform
import psutil
from noohayo.scripts.Config import Config
import subprocess

def newProfile(profileName) :

    

    info = f"色1{profileName}止\n色1----------------------止\n"

    os_info = platform.platform().replace("-"," ")
    info += f"色2OS: 色1{os_info}止\n"


    hostname = platform.node().replace("-"," ")
    info += f"色2Host: 色1{hostname}止\n"


    kernel_version = platform.version()
    info += f"色2Kernel: 色1{kernel_version}止\n"


    uptime_seconds = psutil.boot_time()
    uptime_days = uptime_seconds // (24 * 3600)
    uptime_hours = (uptime_seconds % (24 * 3600)) // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    info += "色2Uptime:色1 {} days, {} hours, {} minutes".format(uptime_days, uptime_hours, uptime_minutes)+"止\n"

    ####
    rs = runCommand("wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution")
    if rs[1] :
        resolution = rs[0]
        rs[0] = resolution[len(resolution)-1].replace("                         "," x ")
    info+=f"色2Resolution: 色1{rs[0]}止\n"


    ####
    pk = runCommand("pip list")
    if pk[1] :
        result = pk[0]
        packages = len(result)-2
        pk[0] = f"{packages} (python)"

    info += f"色2Packages: 色1{pk[0]}止\n"


    cpu_info = platform.processor()

    info += f"色2CPU: 色1{cpu_info}止\n"
    
    ####
    gpui = runCommand("wmic path win32_videocontroller get caption")
    if gpui[1] :
        result = gpui[0]
        gpu_info = [x for x in result[1].split("\n") if x!=""]
        gpui[0] = gpu_info[len(gpu_info)-1]

    info+=f"色2GPU: 色1{gpui[0]}止\n"


    memory_info = psutil.virtual_memory()
    mem = "{:.2f} MiB".format(memory_info.total / (1024 * 1024))
    info += f"色2Memory: 色1{mem}止"


    Config().CreatProfile(info,f"{profileName}.json")

    print(f"\nProfile {profileName}.json was created successfully.")
    print(f"To select it run the following command -> noohayo -s {profileName}.\n")
    
def runCommand(command) :
    try :
        result = subprocess.getstatusoutput(command)
        gpu_info = [x for x in result[1].split("\n") if x!=""]
        return [gpu_info,True]
    except FileNotFoundError:
        gpu_info = "Not found"
        return [gpu_info,False]
        