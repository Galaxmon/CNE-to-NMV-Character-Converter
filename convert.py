import argparse
import os
import json
from pathlib import Path
import xml.etree.ElementTree as ET

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
    
def convert(file, args):
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
    if args.pixel and not icon.endswith("-pixel"):
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

def makeJson(file, args):
    input_file = Path(file)

    if args.output and checkType(Path(args.input)) == "file":
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        if args.output:
            out_dir = Path(args.output)
        elif checkType(Path(args.input)) == "folder":
            out_dir = Path(args.input) / "convertedChars"
        else:
            out_dir = input_file.parent

        out_dir.mkdir(parents=True, exist_ok=True)
        output_file = out_dir / (normalizeName(input_file.stem) + ".json")

    content = convert(file, args)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type= str)
    parser.add_argument("--output", type= str)

    #is pixel will auto add -pixel to an icon
    parser.add_argument("--pixel", action= "store_true")

    args = parser.parse_args()

    type = checkType(Path(args.input))

    files = []

    if type == "NONE":
        print("Error: THIS FILE DOESNT EXIST.")
        return
    elif type == "folder":
        files = getFolderContent(args.input)
    elif type == "file":
        files.append(args.input)

    for file in files:
        makeJson(file, args)

if __name__ == "__main__":
    main()