import json
from noohayo.scripts.Colorer import Colorer
import appdirs

def General(profile) :

    #logo = open("assets/odaSmall.txt",'r').readlines()
    
    data_dir = appdirs.user_data_dir(appname='noohayo', appauthor='BreakRyo')
    jsonFile = json.load(open(f"{data_dir}\\Profiles\\{profile}.json", 'r'))
    myComputer = jsonFile['MyComputer']
    numberOfLines = len(myComputer)
    mcColors = jsonFile['colors']
    mcColors = [Colorer.ColorText("",c,False) for c in mcColors]

    for mcX in range(len(mcColors)):
        for mxY in range(len(myComputer)):
            myComputer[mxY] = myComputer[mxY].replace(f"濶ｲ{mcX+1}",mcColors[mcX])
            myComputer[mxY] = myComputer[mxY].replace(f"豁｢","\033[0m")


    logoColors = []
    palette = jsonFile['palette']
    leftMargin = jsonFile['customLeftMargin']
    palette = [Colorer.ColorBackground("",x,False) for x in palette]
    logo = open(f"{data_dir}\\Profiles\\{profile}.txt", 'r').readlines()
    logo = [x.replace(f"\n", "\033[0m") for x in logo]



    numberOfLines = len(logo) if len(logo) > numberOfLines else numberOfLines
    logoColors = jsonFile['logoColors']
    logoColors = [Colorer.ColorText("",c,False) for c in logoColors]
    unlogo = logo.copy()
    if len(logoColors)>0 :
        for lc in range(len(logoColors)) :
            for l in range(len(logo)) :
                #   色 = 濶ｲ , 止 = 豁｢ 
                unlogo[l] = unlogo[l].replace(f"濶ｲ{lc+1}","")
                logo[l] = logo[l].replace(f"濶ｲ{lc+1}", logoColors[lc])
                if lc==0 :
                    unlogo[l] = unlogo[l].replace(f"豁｢","")
                    logo[l] = logo[l].replace(f"豁｢", "\033[0m")
                        
        
    

    biggest  = int(max([len(x) for x in unlogo]))

    biggest = int(max([biggest,leftMargin]))
    
    
    missingLines = len(logo) - len(myComputer)
    
    smc = int(missingLines/2)
    if smc<1 :
        numberOfLines+=5
    for index in range(0,numberOfLines):
        if index < len(logo) :
            addSpace = " "*(biggest-len(unlogo[index]))
            print(f"{logo[index]}{addSpace}",end='')
        elif index>len(logo)-1:
            print(" "*biggest, end='')

        # prints mycomputer
        customCondition = (index < len(myComputer)+smc  if smc>0 else index < len(myComputer))
        customPalCon = (index==len(myComputer)+smc+1 if smc>0 else index==len(myComputer)+1)
        if index >= smc and  customCondition:
            info = myComputer[index-smc] if smc>0 else myComputer[index]
            

            print(info,end='')

        elif customPalCon :
            col = "".join([f"{x}  " for x in palette])
            print(col+"\033[0m",end='')
        
        print()
  




