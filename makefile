PYINSTALLER_ENTRY = src/rwv/main.py
EXECUTABLE_OUT = dist/main

.PHONY: build clean

build: ${EXECUTABLE_OUT}

clean:
	rm -rf build dist

docs-clean:
	rm -rf docs/_build
	rm -f docs/rwv.rst
	rm -f docs/rwv.ui.rst

docs-clean-appmap:
	rm -rf tmp

docs-build: docs-clean
	cd docs && sphinx-apidoc -o . ../src
	cd docs && sphinx-build -b html . ./_build

docs-appmap: docs-clean-appmap
	APPMAP=true poetry run pytest test_plot_widget.py

docs-all: docs-appmap docs-build

${EXECUTABLE_OUT}: ${PYINSTALLER_ENTRY}
	poetry run pyinstaller ${PYINSTALLER_ENTRY}
