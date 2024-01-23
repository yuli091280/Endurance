# Race Walking Visualization Tool

A pyqt-6 GUI app to visualize various data pertaining to race walking from a sqlite database.

## Features

- Graphing LOC (lost of contact) data
- Inspect various data points on the graph for more info
- Export graph as either jpeg and pdf

## Setup

Make sure you have python3.11 installed, then:

On Windows, do these:

- find and install the qt6 runtime library

On Linux, do these:

- `sudo apt update && sudo apt install qt6-base-dev`

then do these for python stuff:

- `pip install poetry`
- `poetry install`

## Running the project

- get in the shell by `poetry shell`
- run the program with `rwv`

First argument to the program needs to be a db file

## Building the project

This is for packaging, you can run the project without building

`make clean build`

