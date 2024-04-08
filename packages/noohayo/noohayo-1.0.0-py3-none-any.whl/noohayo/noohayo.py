import argparse
import appdirs
import noohayo.scripts.Fetch as Fetch
from noohayo.scripts.General import General
from noohayo.scripts.Select import Select
from noohayo.scripts.Config import Config
from noohayo.scripts.Help import Help

def main():
    des = f'Description: command line interface tool that displays a banner when ever you open a new ternimal tab.'
    parser = argparse.ArgumentParser(prog="noohayo", description=des, usage="%(prog)s [option]", add_help=False)
    parser.add_argument('-h', '--help',action="store_true", help='\t\t Show this help message and exit.')
    parser.add_argument('-v','--version', action='version', version='noohayo 1.0', help="\t\t show program's version number and exit.")
    parser.add_argument('-n' ,'--new', const="", metavar="[name]" , nargs="?" ,help="Makes a new profile." )
    parser.add_argument('-s', '--select',const="",metavar="[name]",  nargs="?",help="Selects a [name] profile from the profiles you have, if [name] is not provided it shows you all the profiles you have." )
    parser.add_argument('-l', '--location',action="store_true",help="\t Shows you the location of the profiles." )
    
    selectedProfile =  Config().ReadConfig()
    
    args = parser.parse_args()
    if args.help :
        Help(parser._actions,des)
    elif args.new is not None:
        if args.new != "":
            Fetch.newProfile(args.new)
        else :
            print("\nProvide a name for the profile -> example : noohayo -n profile1\n")
    elif args.select is not None :
        Select(args.select,selectedProfile)
    elif args.location:
        print(f"\n{appdirs.user_data_dir(appname='noohayo', appauthor='BreakRyo')}\\Profiles \n\nNote : to view to profiles here run -> noohoyo -s\n")
    elif selectedProfile=="" :
        print("\n No profile was was selected, select one with -> noohayo -s profileName\n")
        print("\n if you didn't create a profile yet, create one with -> noohayo -n profileName\n")
    else :
        #print(f"\nProfile {selectedProfile} is printing :)" )
        General(selectedProfile)
    # 
    

if __name__ == "__main__":
    main()
