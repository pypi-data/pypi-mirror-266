# Pickart
#### [Українська версія](README_UA.md)

Pickart - this is the file format used by the game called[Colouring art](https://github.com/AntynK/ColouringArt) for storing images.

Name 'Pickart' - comes from combination of two words ['pickle'](https://docs.python.org/3.9/library/pickle.html) and 'art'.

## About format
Root of .pickart file is Python dict serialized with [pickle](https://docs.python.org/3.9/library/pickle.html) and compressed with [gzip](https://docs.python.org/3.9/library/gzip.html).

File structure(version 1.0.0):
``` Python
{
    "info":{
        "size": (1, 1),
        "version": 1
    },
    "palette":[(red, green, blue, alpha), ...],
    "pixels": [
        [(colour_index, is_painted), ...]
    ]
}
```

`"info"` - stores image size and Pickart file version.

`"palette"` - stores colour palette. Every colour is tuple of integers. Integer value is in range from 0 to 255(including), `alpha` - optional. 

`"pixels"` - stores matrix which contain tuple with `colour_index`(int) and flag `painted`(bool). 

`colour_index` - colour index in palette if this pixel is transparent(`alpha` = 0) index becomes `None`.

`painted` - represents pixel state if false it will appear as a shade of gray otherwise like normal colour. 

Package [pickle](https://docs.python.org/3.9/library/pickle.html) has security issues game does not use standart pickle.load() instead it uses [restricted loader](https://docs.python.org/3/library/pickle.html#restricting-globals) which allows only basic types(int, str, list, dict, tuple, set). If it detects that file contains external types(any object that is imported) it will throw exception `UnpicklingError` with message `There is something strange in the file, do not trust it!`.


## Command line interface
This package allows convert .png files to .pickart and vise versa.

Command below shows all arguments:

**Windows:**
```bash
python -m pickart -h
```
**For Linux and MacOS**
```bash
python3 -m pickart -h
```

### Basic arguments
`-i "path"` - indicates the folder in which the files for conversion are located(by default 'input'). Folder must exist.

`-o "path"` - indicates the folder in which converted files will be stored(by default 'output'). May not exist.

`-m "mode"` - indicates conversion mode: 
* `to_pickart` - .png files to .pickart files.
* `to_png` - .pickart files to .png files.
