PYINSTALLER_ENTRY = src/pyqt_test/main.py
EXECUTABLE_OUT = dist/main

.PHONY: build clean

build: ${EXECUTABLE_OUT}

clean:
	rm -rf build dist

${EXECUTABLE_OUT}: ${PYINSTALLER_ENTRY}
	poetry run pyinstaller ${PYINSTALLER_ENTRY}