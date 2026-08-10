#A Janky GUI :)
import os
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from tkinter import *
from tkinter import filedialog

DEFAULTS = {
    "x": 0,
    "y": 0,
    "camx": 0,
    "camy": 0,
    "scale": 1,
    "icon": "face",
    "color": "#000000",
    "holdTime": 4,
    "fps": 24,
}

def checkType(input):
    if input.is_file():
        return "file"
    elif input.is_dir():
        return "folder"
    else:
        return "NONE"

def getFolderContent(folder):
    thingie = Path(folder)
    filesArray = []
    for file in thingie.iterdir():
        if file.is_file() and file.suffix == ".xml":
            filesArray.append(file)

    return filesArray


def hexToInt(hex):
    hex = hex.strip().lstrip("#")

    if len(hex) == 6:
        hex = "FF" + hex

    value = int(hex, 16)

    if value >= 0x80000000:
        value -= 0x100000000

    return value

def getIndices(value):
    if not value:
        return []

    result = []
    for part in value.split(","):
        part = part.strip()
        if ".." in part:
            start, end = part.split("..")
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(part))
    return result

#from Boyfriend Standing to boyfriend-standing
def normalizeName(name):
    return name.strip().lower().replace(" ", "-")

def getBoolean(value):
    if isinstance(value, bool):
        return value

    return value.strip().lower() == "true"
    
def convert(file, input, output, pixel):
    tree = ET.parse(file)
    root = tree.getroot()
    attrib = root.attrib

    scale = float(attrib.get("scale", DEFAULTS["scale"]))
    
    x = int(float(attrib.get("x", DEFAULTS["x"])) * scale)
    y = int(float(attrib.get("y", DEFAULTS["y"])) * scale)

    flip_x = getBoolean(attrib.get("flipX", False))

    is_player = getBoolean(attrib.get("isPlayer", False))

    cam_x = float(attrib.get("camx", DEFAULTS["camx"]))
    cam_y = float(attrib.get("camy", DEFAULTS["camy"]))
    if is_player:
        cam_x = cam_x * -1

    icon = attrib.get("icon", DEFAULTS["icon"])
    if pixel and not icon.endswith("-pixel"):
        icon = icon + "-pixel"

    #in CNE is antialiasing, while in NMV is no antialiasing, so we need to invert the value
    antialiasing = getBoolean(attrib.get("antialiasing", True))
    no_antialiasing = not antialiasing

    hold_time = float(attrib.get("holdTime", DEFAULTS["holdTime"]))


    fallback_sprite = os.path.splitext(os.path.basename(file))[0]
    sprite = attrib.get("sprite", fallback_sprite)

    #Gets the anims
    animations = []
    for anim_node in root.findall("anim"):
        a = anim_node.attrib

        animData = {
            "loop": getBoolean(a.get("loop", False)),
            "offsets": [float(a.get("x", 0)), float(a.get("y", 0)) ],
            "anim": a.get("name", a.get("anim")),
            "fps": int(a.get("fps", DEFAULTS["fps"])),
            "name": a.get("anim", a.get("name")),
            "indices": getIndices(a.get("indices")),
        }

        animations.append(animData)

    return{
        "animations": animations,

        "no_antialiasing": no_antialiasing,
        "image": f"characters/{sprite}",
        "position": [x, y],
        "dance_every": 2,
        "gameover_initial_sound": None,
        "scalableOffsets": False,
        "healthicon": icon,
        "gameover_character": None,
        "vslice_sustains": True,
        "flip_x": flip_x,
        "healthbar_colour": hexToInt(attrib.get("color", DEFAULTS["color"])),
        "camera_position": [cam_x, cam_y],
        "gameover_loop_sound": None,    
        "sing_duration": hold_time,
        "scale": scale,
        "_editor_isPlayer": is_player
    }

def makeJson(file, input, output, pixel : bool):
    input_file = Path(file)

    if output and checkType(Path(output)) == "file":
        output_file = Path(output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        if output:
            out_dir = Path(output)
        elif checkType(Path(input)) == "folder":
            out_dir = Path(input) / "convertedChars"
        else:
            out_dir = input_file.parent

        out_dir.mkdir(parents=True, exist_ok=True)
        output_file = out_dir / (normalizeName(input_file.stem) + ".json")

    content = convert(file, input, output, pixel)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4)
    

def dircheck(is_folder : bool):#Grab & Read Directory For Appending XMLs
    global selected_input
    global files
    files = []
    num_c = 0 #Count of XMLs

    if is_folder:
        selected_input = filedialog.askdirectory()
        files = getFolderContent(selected_input)
    else:
        selected_input = filedialog.askopenfilename(
            title= "Open Character File",
            initialdir= "/",
            filetypes= [("XML Files", "*.xml")]
        )
        if not selected_input == "":
            files.append(selected_input)
        
    fileselect.config(fg="blue") #Visual Stuff
    f_l.set(selected_input + " | ")
    num_c += len(files)
    f_n.set(f"{num_c} : Characters Selected")
    visual_dirscroll()

def dir_ouput():
    global selected_output
    selected_output = filedialog.askdirectory()

def convertcheck(): #Check if file is selected
    pixel = is_pixel.get()
    if selected_input == "":
        fileselect.config(fg="red")
        f_l.set("MUST SELECT A DIRECTORY ")
        return
            
    for file in files:
        makeJson(file, selected_input, selected_output, pixel )

def visual_dirscroll():
    txt = f_l.get()[1:] + f_l.get()[0]
    f_l.set(txt)
    root.after(200, visual_dirscroll)
    
root = Tk()

selected_input = ""
selected_output = ""
is_pixel = BooleanVar(value= False)

f_l = StringVar() #Display Directory/FileDirectory
f_l.set("None")
f_n = StringVar() #Number of XMLs in Directory
f_n.set("")

root.title("CNE to NMV Convert")
root.geometry("300x300")
root.resizable(False, False)

frameb = Frame(root,
               pady= 20)

frameconv = Frame(root,
               pady= 20)

fileselect = Label(root, 
                   textvariable = f_l, 
                   fg="blue",
                   bg="lightgray",
                   pady= 10, 
                   width= 30,
                   font= ("Comic Sans MS", 12))
numberselect = Label(root, 
                   textvariable = f_n, 
                   fg="blue",
                   font= ("Comic Sans MS", 10, "bold"))

bdir = Button(frameb,
              text= "Select Directory", 
              command=lambda: dircheck(True))

fdir = Button(frameb,text= "Select File", 
              command=lambda: dircheck(False))

odir = Button(root,text= "Select Output ", 
              command=dir_ouput)

bconvert = Button(frameconv,text = "Convert",
                   command=convertcheck)

pixelbox = Checkbutton(frameconv, text = "Pixel",
                        variable=is_pixel)


fileselect.pack()
numberselect.pack()
bdir.pack(side= "left")
fdir.pack(side= "left")
bconvert.pack(side= "left")
pixelbox.pack(side= "left")
frameb.pack()
odir.pack()
frameconv.pack()
root.mainloop()