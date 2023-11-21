# stuff

## setup

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

## building the project

This is for packaging, you can run the project without building

`make clean build`
