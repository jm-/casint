# casint
CASIO Basic Interpreter

![Demo of input/captures/SCUM2.g1m](demo_scum2.png)

A simple interpreter for CASIO Basic using G1M files as input. Uses SDL for graphics.

## Installing

Requirements:
* Python 2
* SDL2 installation

1. Clone the repo
2. Install the requirements 

```
pip install -r requirements.txt
```

3. Install SDL2

If using Windows, it's sufficient to download a runtime binary from https://www.libsdl.org/download-2.0.php

Drop the appropriate DLL in lib/32 or lib/64.

4. Run it!
```
python run.py input/captures/SCUM2.G1M
```
