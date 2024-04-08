from noohayo.scripts.Config import Config
from noohayo.scripts.General import General

def Select(target,current):
    profiles = Config().GetProfiles()
    if target!="" :
        if f"{target}.json" in profiles :
            Config().EditConfig(target)
            print(f"\n The profile {target} was selected successfully.")
        else :
            print(f"\n The profile {target} was not found in your profiles list.")
    elif len(profiles) > 0 :
        print("\nProfiles Found : ")
        for x in profiles :
            if ".json" in x :
                p0 = x.split('.')[0]
                p = f"{x.split('.')[0]}" if x.split('.')[0]!=current else f"{x.split('.')[0]} (selected)"
                print(f"\n--------------------------------------- Profile : {p} ---------------------------------------\n")
                General(p0)
                
        print()
    else :
        print("\n No profile was found, create one with -> noohayo -n profileName\n")
