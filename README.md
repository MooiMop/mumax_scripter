# Mumax scripter

This repository showcases a collection of python scripts that can be used to script simulations in [Mumax3](https://mumax.github.io).

## Usage
- Write a simulation sequence such as in the file `Sequence_template.py`.
- Run that code using Python 3+
- Wait until the simulation is done and find your output in the `Output` folder.

## Requirements
Apart from the standard scientific packages (e.g.`numpy` and `matplotlib`), the scripts in this repository require the following python packages that can all be installed with `pip`:
```
tqdm
platform
subprocess
webbrowser
glob
pandas as pd
matplotlib.pyplot as plt
imageio
ffmpy
struct
PIL
imageio
```

## Background
The code in this repository was written as part of my [master thesis](https://hdl.handle.net/1887/3237982) at Leiden University. It has als contributed to the scientific publication by Fermin, Scheinowitz, Aarts & Lahabi [*Mesoscopic superconducting memory based on bistable magnetic textures*](https://link.aps.org/doi/10.1103/PhysRevResearch.4.033136).

