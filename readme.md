# Race Walking Visualization Tool

A pyqt-6 GUI app to visualize various data pertaining to race walking from a sqlite database.

## Features

- Graphing LOC (lost of contact) data
- Inspect various data points on the graph for more info
- Export graph as either jpeg and pdf

## Setup

Make sure you have python3.11 installed, then:

On Windows, download and install the [Qt6](https://www.qt.io/download) runtime library

On Linux, do `sudo apt update && sudo apt install qt6-base-dev`

then do these for python dependencies:

- `pip install poetry`
- `poetry install`

## Running the project

- get in the shell by `poetry shell`
- run the program with `rwv`

## Building the project

This is for packaging, you can run the project without building

`make clean build`

## Generating documentation

### Generating HTML documentation

1. `make docs-build`
2. It will generate a website in docs/_build

### Generating sequence diagram

1. `make docs-appmap`
2. It will generate in tmp/appmap/pytest
3. Open the generated file in the [VS Code Appmap extension](https://marketplace.visualstudio.com/items?itemName=appland.appmap).
   1. There might be multiple generated. The only one 
   that works will be the only one that matters
4. Export to .svg

### Generate both the HTML docs and sequence diagrams

1. `make docs-all`
