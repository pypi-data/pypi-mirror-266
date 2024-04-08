import argparse

def Help(parser,des) :
    logo = """                                           
 _____ _____ _____ _____ _____ __ __ _____ 
|   | |     |     |  |  |  _  |  |  |     |
| | | |  |  |  |  |     |     |_   _|  |  |
|_|___|_____|_____|__|__|__|__| |_| |_____|
                                           """
    print(logo)
    print(f"\n Usage : \033[38;2;70;167;226mnoohayo\033[0m [\033[38;2;232;157;30moption\033[0m]")
    print(f"\n {des}")
    print(f"\n \033[38;2;232;157;30mOptions\033[0m :\n")
    for action in parser :
        name = action.dest
        met = (f" {action.metavar}" if action.metavar is not None else "")
        print(f"\t -{name[0]}{met}, --{name}{met} \t\t {action.help}")
    print()
    

