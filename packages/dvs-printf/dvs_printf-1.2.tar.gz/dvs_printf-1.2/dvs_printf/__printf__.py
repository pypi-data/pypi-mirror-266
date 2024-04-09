# Enhance your Python project's console output with stylish printing animations using the dvs_printf module.
from time import sleep
from os import get_terminal_size

ranchoice =[
    "b","c","d","e","f","g","h","i","c",
    "d","l","a","w","t","r","s","v","x",
    "z","n","o","-","p","q","r","s","t"
]
def _help():
    tem_len_line = int(get_terminal_size()[0])
    mid_len_line = int(tem_len_line/2 - 9)
    print("\n"+"="*tem_len_line+"\n"+(" "*mid_len_line)+">>> DVS_PRINTF <<<"+"\n"+"="*tem_len_line)
    for x in """\n
keywords --> printf(values, style='typing', speed=3, interval=2, stay=True)\n\n
values --> main stream input values  
        value can be any-data-Type 
        Ex. printf(str, list, [tuple, set], dict, int,...)\n\n
style --> style is different type if printing animation 
        styles, from this list each style type works 
        differently according to description below\n
        ["typing", "headline", "newsline", "mid", "gunshort", "snip",
        "left", "right", "center", "centerAC", "centerAL", "centerAR", 
        "matrix", "matrix2", "scatter", "fire", "shiver", "blink", 
        "f2b","b2f", "help"]\n
        typing   => print like typing
        headline => print headlines animation
        newsline => print running newslines animation
        mid      => print line from mid
        left     => value coming from left side of the terminal
        right    => value coming from right side of the terminal
        center   => values appear at center of the terminal
        centerAC => values arrang at center of the terminal
        centerAL => arrang list-item at center-Left on terminal
        centerAR => arrang list-item at center-Right on terminal
        gunshort => firing the words from short gun
        snip     => sniping the words from end of the terminal
        matrix   => print random words to real line
        matrix2  => print 1st word and 2nd random word and go on
        scatter  => Scatter effect for each line
        fire     => appear latters with gap creates flames effect.
        wave     => creats wave effect with each line.
        blink    => appear Blink effect from start to end.
        f2b      => typing and remove word from (back to front)
        b2f      => typing and remove word from (front to back)\n\n
speed -->  speed of printf's animation 
        defult speed is 3, from (1 to 6)\n
        1 = Very Slow  
        2 = Slow  
        3 = Mediam
        4 = Fast
        5 = Fast+
        6 = Very Fast\n\n
interval --> interval is waiting time between printing 
            of each values, (interval in second) 
            defult interval is 2, you can set from 0 to grater\n\n    
stay --> after style animation whether you want the values OR Not
        defult stay is True, can be `True or False`\n
        but some styles take No action on stay
        whether it is True OR False 
        Ex. ( typing, headline, newsline, f2b,  b2f, matrix2 )\n""":
        print(x, end="",flush=True);sleep(.002)
    print("="*tem_len_line+"\n")
    


def listfunction(*values: tuple , getmat: bool | str | None = False) -> list[str]:
    """
Takes any values in tuple -> list[str] 

return list with each elements given. takes any DataType and gives `list[str]`\\
with each elements by index. for `list, tuple, dict, set` breake this kind of \\
DataSet and add Them into a list by index. 
---
## getmat: 
    matrix data modifier for `pytorch, tensorflow, numpy, pandas, list` \\
    it breaks matrices in `rows by index` and convet that in to list of string. `default getmat=False`
##### getmat = `True` or `"true"` 
    to modify coyp of data for animation if `getmat=False` \\
    it's just apply animation whitout data modification, `as normal output`
##### getmat = `"show"`
    for values `with information` about matrix 
    `<class, shape, dtype>` 
    """
    values=values[0]  
    newa_a=[]
    for value in values:
        var_type=type(value)
        if getmat:
            try:
                if "numpy" in  str(var_type):
                    newa_a.extend(
                [str(sublist.tolist()) for sublist in value.reshape(-1, value.shape[-1])]
                    )
                    if "show" in str(getmat).lower():
                        newa_a.extend([
    "<class 'numpy.ndarray'","dtype="+str(value.dtype)+" ","shape="+str(value.shape)+">"
                    ])
                    continue
                elif "tensorflow" in str(var_type):    
                    from tensorflow import reshape,shape;newa_a.extend(
                [str(sublist.numpy().tolist()) for sublist in reshape(value, [-1, shape(value)[-1]])]
                    )
                    if "show" in str(getmat).lower():newa_a.extend([
    "<class 'Tensorflow'",(str(value.dtype).replace("<","")).replace(">","") +" ","shape: "+str(value.shape)+">"
                    ])
                    continue  
                elif "torch" in str(var_type):
                    newa_a.extend(
                [str(sublist.tolist()) for sublist in value.view(-1, value.size(-1))]
                    )
                    if "show" in str(getmat).lower():newa_a.extend([
    "<class 'torch.Tensor'", " dtype="+str(value.dtype)+" "," shape="+str(value.shape)+">"
                    ])
                    continue
                elif "pandas" in str(var_type):
                    newa_a.extend(value.stack().apply(lambda x: str(x)).tolist())
                    if "show" in str(getmat).lower():
                        newa_a.extend(["<class 'pandas'"," shape="+str(value.shape)+" "+">"])
                        newa_a.extend(
    (str(value.dtypes).replace("\n","@#$@")).replace("    ",": ").split("@#$@")
                    )
                    continue
                else: 
                    if isinstance(value,list) and isinstance(value[0],list):
                        newa_a.extend(listfunction(value, getmat=getmat))
                        continue
                    elif isinstance(value,list):
                        newa_a.append(str(value).replace("\n"," "))
                        continue
            except:pass

        if var_type==dict:
            for i in value:
                newa_a.extend(f"{i}: {value[i]}".replace("\n","@#$%#$@"+" "*(len(i)+2)).split("@#$%#$@"))
        elif(var_type==list)or(var_type==tuple)or(var_type==set):newa_a.extend(listfunction(value,getmat=getmat))
        elif var_type==str:newa_a.extend(value.split("\n"))
        else:newa_a.extend(str(value).split("\n"))
    return newa_a


def printf(*values:object, 
            style:str|None='typing', 
            speed:int|None=3, 
         interval:int|None=2,  
             stay:bool|None=True,
           getmat:bool|str|None=False) -> None:
    ''' 
#### [printf](https://github.com/dhruvan-vyas/dvs_printf?tab=readme-ov-file#printf-function): prints values to a stream with animation. 
---
#### style: 
    style is defins different types of print animation. `default a "typing"`. 
[typing, headline, newsline, mid, gunshort, snip,scatter, fire, shiver, blink, \\
left, right, center, centerAC, centerAL, centerAR, matrix, matrix2, f2b,b2f, help]
#### speed:
speed is defins printf's animation speed `from 1 to 6` `default a 3`
#### interval:
waiting time between printing animation of two lines `default a 2`.\\
`(interval in second >= 0)` int | float  
#### stay:
decide after style animation whether you want the values \\
on stream OR NOT `default a True`. don't work for some styles
#### getmat: 
matrix data modifier for `pytorch, tensorflow, numpy, pandas, list` \\
for animation, `default getmat=False`, set as `True, "true", "show"`
    '''
    values=listfunction(values, getmat=getmat)
    style=str(style).lower()
    if interval<0:interval=2
    elif style in ["right","left"]:speed=(.032/speed)if(speed>=1 and speed<=6)else .016
    elif style=="gunshort":speed=(.064/speed)if(speed>=1 and speed<=6)else .016
    elif style in ["typing","headline"]:speed=(.08/speed)if(speed>=1 and speed<=6)else 0.24
    elif style=="snip":speed=(.016/speed)if(speed>=1 and speed<=6)else .008
    elif style=="scatter":speed=(.3/speed)if(speed>=1 and speed<=6)else .1
    else:
        if style=="newsline":speed=(.18/speed)if(speed>=1 and speed<=6)else .06 
        else:speed=(.16/speed)if(speed>=1 and speed<=6)else .08
        if style in ["fire","newsline","centeral","centerar"]:
            max_line_len = max(len(line) for line in values)

    print('\033[?25l', end="")
    try:
        if style=="typing":
            for x in values:
                for i in x:
                    print(i+"|\b", end="",flush=True)
                    sleep(speed)
                print(" ")
                sleep(interval)
        elif  style=="headline":
            for x in values:
                line = ""
                x = str(x)
                for y in range(0, len(x)):
                    line = line + x[y].replace("\n","")
                    print(line+"⎮",end="\r",flush=True)
                    sleep(speed)
                    print(line[:len(line)],end="\r",flush=True)
                    print(end="\x1b[2K")
                sleep(interval)
                for i in range(0, len(x)):
                    delete_last = x[:len(x)-i-1].replace("\n","")
                    print(delete_last+"|",end="\r",flush=True)
                    sleep(speed)
                    print(end="\x1b[2K")
        elif style=="newsline":
            max_line_len = 30
            for L in values:
                if len(L)>max_line_len:max_line_len=len(L)
            for value in values:
                for i in range(max_line_len+1):
                    emptyL = max_line_len-i
                    start_point = "|"
                    if i+1 > len(value):
                        start_point = " "*(i-len(value)+1) +"|"
                    print('|'+" "*(emptyL)+value[0:i+1]+start_point, end="\r" , flush=True)
                    sleep(speed)
                for i in range(1,len(value)+1):
                    end_point = "|"+value[i:len(value)]
                    end_line = max_line_len-len(value)+i+1
                    print(end_point+" "*end_line+"|", end="\r" , flush=True)
                    sleep(speed)
                    print(end="\x1b[2K")
                sleep(interval*.06)
        elif style=="mid":
            for x in values:
                x = x if len(x)%2==0 else x+" "
                lan = len(x)//2
                front,back="",""
                for i in range(lan):
                    front = x[lan-i-1]+front
                    back = back +x[lan+i]
                    print(" "*(lan-i-1)+front+back,end="\r",flush=True)
                    sleep(speed)
                print(end="\x1b[2K")
                if stay:print(x)
                sleep(interval)
        elif style=="right":
            for i in values:
                for j in range(len(i)+1):
                    temlen = get_terminal_size()[0]
                    print(i[0:j].rjust(temlen),end="\r",flush=True)
                    sleep(speed)
                sleep(interval)
                if stay:print(end="\n")
                else:
                    for j in range(len(i)+1):
                        temlen = get_terminal_size()[0]
                        print(i[0:len(i)-j].rjust(temlen),end="\r",flush=True)
                        print(end="\x1b[2K")
                        sleep(speed)
                    sleep(.4)
        elif style=="left":
            for i in values:
                for j in range(len(i)+1):
                    temlen = get_terminal_size()[0]
                    print(i[len(i)-j:j],end="\r",flush=True)
                    sleep(speed)
                sleep(interval)
                if stay:print(end="\n")
                else:
                    for j in range(len(i)+1):
                        temlen = get_terminal_size()[0]
                        print(i[j:len(i)],end="\r", flush=True)
                        print(end="\x1b[2K")
                        sleep(speed)
                    sleep(.4)
        elif style=="center":
            for i in values:
                for j in range(len(i)+1):
                    if j < len(i):endline="|"
                    else:endline=""
                    temlen = get_terminal_size()[0]
                    print((i[0:j]+endline).center(temlen),end="\r",flush=True)
                    sleep(speed)
                sleep(interval)
                if stay:print(end="\n")
                else:print(end="\x1b[2K");sleep(.4)
        elif style=="centerac":
            for i in values:
                for j in range(len(i)+1):
                    if j < len(i):endline="|"
                    else:endline=""
                    temlen = (get_terminal_size()[0]/2)-(len(i)/2) 
                    print(" "*int(temlen)+i[0:j]+endline+" "*(len(i)-j-1),end="\r",flush=True)
                    sleep(speed)
                sleep(interval)
                if stay:print(end="\n")
                else:print(end="\x1b[2K");sleep(.4)
        elif style=="centeral":
            for i in values:
                for j in range(len(i)+1):
                    if j < len(i):endline="|"
                    else:endline=""
                    temlen = get_terminal_size()[0]
                    print(" "*int(temlen/2-(max_line_len/2))+i[0:j]+endline,end="\r")
                    sleep(speed)
                sleep(interval)
                if stay:print(end="\n")
                else:print(end="\x1b[2K");sleep(.4)
        elif style=="centerar":
            for i in values:
                for j in range(len(i)+1):
                    if j < len(i):endline="|"
                    else:endline=""
                    temlen = get_terminal_size()[0]
                    print(" "*int(temlen/2+(max_line_len/2-len(i)))+i[0:j]+endline,end="\r")
                    sleep(speed)
                sleep(interval)
                if stay:print(end="\n")
                else:print(end="\x1b[2K");sleep(.4)
        elif style=="gunshort":
            for x in values:
                short=""
                len_x = len(x)
                for i in range(len_x):
                    try:
                        next_let = x[i+1] if " " != x[i+1] else "_"
                        index = x[i] if " " != x[i] else "_"
                    except:next_let=" "; index = x[len_x-1]
                    for j in range(len_x-i):
                        print(short+" "*(len_x-j-2-len(short))+index+(" "*j)+f"  <==[{next_let}]=|",end="\r")
                        sleep(speed)
                    sleep(speed)
                    short = short + x[i]
                print(end="\x1b[2K", flush=True)
                if stay:print(short);sleep(interval)
                else:print(short,end="\r");sleep(interval);print(end="\x1b[2K", flush=True)
        elif style=="snip":
            for x in values:
                short,addone="",0
                for i in range(len(x)):
                    try:next_let = x[i+1] if " " != x[i+1] else "_";index = x[i] if " " != x[i] else "_"
                    except:next_let=" ";index = x[len(x)-1]
                    temlen = get_terminal_size()[0]
                    for j in range(0,temlen-i-len(short)+addone-10):
                        print(short+" "*(temlen-j-len(short)-11)+index+" "*(j)+f" <===[{next_let}]=|",end="\r")
                        sleep(speed)
                    sleep(speed)
                    print(end="\x1b[2K")
                    addone+=1
                    short=short+x[i]
                if stay:print(x)
                else:print(x,end="\r");print(end="\x1b[2K")
                sleep(interval)
        elif style=="matrix":
            from random import choice
            for value in values:
                entry=""
                for i in range(len(value)): 
                    entry=entry+value[i] 
                    for _ in range(5):
                        nxt=""
                        for _ in range(len(value)-i-1):
                            nxt=nxt+choice(ranchoice) 
                        print(entry+nxt, end="\r")
                        sleep(speed)
                sleep(interval)
                if stay:print(end="\x1b[2K");print(value)
                else:print(value,end="\r");print(end="\x1b[2K")
        elif style=="matrix2":
            from random import randint,choice
            for ab in values:
                entry=""
                for i in range(len(ab)-1):
                    entry=entry+ab[i]
                    for _ in range(randint(5,20)):
                        print(entry+choice(ranchoice), end="\n")
                        sleep(speed)
                print(end="\x1b[2K");print(ab);sleep(interval)
        elif style == "scatter":
            from  random import sample
            ranchoice_ = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890" 
            for line in values:
                for _ in range(13):
                    scattered_line = ''.join(sample(line+ranchoice_, len(line)))
                    print(scattered_line, end="\r", flush=True)
                    sleep(speed) #.1
                print(line, end="\r")
                sleep(interval)
                if stay:print("")
                else:print(end="\x1b[2K")
        elif style == "fire":
            for line in values:
                for i in range(len(line)):
                    print(line[:i] + " " + line[i], end="\r", flush=True)
                    sleep(speed) # .06
                print(line + " " * (max_line_len-len(line[:i])),end="", flush=True)
                sleep(interval)
                if stay:print("\r")
                else:print("\r",end="\x1b[2K")
        elif style == "wave":#shiver
            for line in values:
                for i in range(len(line)):
                    print(line[:i] + line[i].swapcase() + line[i+1:], end="\r", flush=True)
                    sleep(speed) #.08
                print(line, end="\r", flush=True)
                sleep(interval)
                if stay:print()
                else:print(end="\x1b[2K")
        elif style == "blink":
            for line in values:
                for i in range(len(line)):
                    print(line[:i] + line[i].swapcase(), end="\r", flush=True)
                    sleep(speed) # .08
                print(line,end="\r",flush=True)
                sleep(interval)
                if stay:print()
                else:print(end="\x1b[2K")
        elif style=="f2b":
            for x in values:
                x = str(x)
                for y in range(0, len(x)+1):
                    print(x[:y], end="\r", flush = True)
                    sleep(speed)
                sleep(interval)
                for y in range(0, len(x)+1):
                    print(" "*y, end="\r", flush = True)
                    sleep(speed)
                print(end="\x1b[2K")
                print(end="\r")
        elif style=="b2f":
            for x in values:
                for y in range(0, len(x)+1):
                    print(x[:y], end="\r",flush=True)
                    sleep(speed)
                sleep(interval)
                for i in range(0, len(x)+1):
                    print(x[:len(x)-i], end="\r", flush=True)
                    sleep(speed)
                    print(end="\x1b[2K")
                print(end="\r")
        elif style=="help":
            _help()
            for i in values:print(i)
        else:
            print(f'''
    printf does not accepts style='{style}' as parameter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{"^"*len(style)} 
    >>> please enter name of style from the list <<<          
---------------------------------------------------------------
[typing, headline, newsline, mid, gunshort, snip, 
left, right, center, centerAC, centerAL, centerAR, matrix, 
matrix2, scatter, fire, shiver, blink, b2f,f2b, help]
        \n\n''')
            for i in values:print(i)
    except Exception as EXP:print("\n",EXP,"\n\n")
    print('\033[?25h', end="",flush=True)
    del values


