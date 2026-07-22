# CNE-to-NMV-Character-Converter

A simple Script that converts Codename Engine Characters (`.xml`) into Nightmare Vision Characters (`.json`)

## How To Use
```bash
python convert.py --input <file_or_folder> [--output <path>] [--pixel]
```

### `--input`
Path to a single `.xml` file or a folder with multiple `.xml` files

### `--output`
Optional Value. Behavior depends on the input:

- **Input as single File:** `--output` sets the name of the resulting `.json` file.
  Use:
```bash
  python convert.py --input boyfriend.xml --output bf.json
```

- **Input as folder:** `--output` sets the destination folder where all converted `.json` files will be placed.
  Use:
```bash
  python convert.py --input characters/ --output converted/
```

If output is not provided:
- **For a single file**, the output will use a normalized version of the input file name.
- **For a folder**, converted files will be placed inside `convertedChars/` within the same input folder.

### `--pixel`
Automatically adds `-pixel` to the health icon name if isn't already there. Just a shortcut so you don't have to manually rename icons for pixel characters
Use:
```bash
python convert.py --input characters/ --pixel
```

## Important Note
This is **not a 1:1 conversion**. Codename Engine and Nightmare Vision handle camera positioning and character positioning differently, so these values may not translate perfectly. Always review the converted file in-engine and adjust if looks off
