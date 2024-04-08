class Colorer :
    def ColorText(text, color , withEscape):
        
        color_code = f"\033[38;2;{int(color[1:3], 16)};{int(color[3:5], 16)};{int(color[5:], 16)}m"
        
        reset_code = "\033[0m"
        answer = f"{color_code}{text}{reset_code}" if withEscape else f"{color_code}{text}"
        return answer
    
    def ColorBackground(text, color, withEscape) :
        

        color_code = f"\033[48;2;{int(color[1:3], 16)};{int(color[3:5], 16)};{int(color[5:], 16)}m"
        
        reset_code = "\033[0m"
        answer = f"{color_code}{text}{reset_code}" if withEscape else f"{color_code}{text}"
        return answer
    