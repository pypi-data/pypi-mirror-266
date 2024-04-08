import os
import appdirs
import json



class Config :


    def __init__(self):
        self.data_dir = appdirs.user_data_dir(appname='noohayo', appauthor='BreakRyo')

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.data_dir+"\\Profiles", exist_ok=True)
        if not os.path.exists(f"{self.data_dir}\\config.json"):
            conData = {"profile":""}
            f = open(f"{self.data_dir}\\config.json",'w')
            json.dump(conData, f, indent=4)
        


    def CreatProfile(self,fileContent, name) :
        logo = """色1                    .....                止              
色1              :=+*#########*+=:             止           
色1             =#################+            止           
色1         ::. +###**+==-==++*###* .::         止          
色1       =####*:=+.           .=+:*####+        止         
色1     .*#####+:   色2   :*#*-    色1  :=#####*:  止             
色1    .*####*:    色2  =#######=   色1   .*####*.  止            
色1    *####*   色2 .==-:*##+##*--==. 色1   *####*  止            
色1   -#####. 色2 +*####*:+# *+:+####*+ 色1 .#####=  止           
色1   +####+  色2 *####==+:-:-:+==####*. 色1 +####*  止           
色1   *####=  色2 .#####+- *## -+*####.  色1 =#####  止           
色1   +####+  色2  .--===+:::-.+===--.  色1  +####+  止           
色1    :=++=-  色2  -####-=# #=-####-  色1  :=++=-  止            
色1      :+*#   色2 .*###### ######*. 色1   **+-    止            
色1     :####*.  色2 +#####* +#####*  色1 .*####-   止            
色1     .*#####=.  ..         ..  .=#####*.         止
色1       =######+-.           .-+######+.       止  
色1        .+#######*+==+ +==+*#######+:          止    
色1          .-*########* *########*=.        止        
色1             .:=+*#*+. .=*#*+=:.          止          

"""
        data = {
            "MyComputer": fileContent.split('\n'),
            "customLeftMargin" : 60,
            "colors" : ["#aab7b8", "#7b7d7d"],
            "logoColors" : ["#212425","#5b6366"],
            "palette" : ["#212425","#3f4447","#5b6366","#323739","#0b0c0c"]
        }
        
        profiles_path = self.data_dir+"\\Profiles"

        file = open(f"{profiles_path}\\{name}",'w', encoding="utf-8")
        json.dump(data, file, ensure_ascii=False, indent=4)
        open(f"{self.data_dir}\\Profiles\\{name.split('.')[0]}.txt",'w',encoding="utf-8").write(logo)

    
    def GetProfiles(self) :

        profiles = os.listdir(f"{self.data_dir}\\profiles\\")
        return profiles
    
    def ReadConfig(self):
        return json.load(open(f"{self.data_dir}\\config.json",'r'))['profile']
    
    def EditConfig(self,newProfile):
        con = json.load(open(f"{self.data_dir}\\config.json",'r'))
        con['profile'] = newProfile
        json.dump(con,open(f"{self.data_dir}\\config.json",'w'), indent=4)
        

