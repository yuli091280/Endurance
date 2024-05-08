PYINSTALLER_ENTRY = src/rwv/main.py
EXE_NAME = Endurance
EXECUTABLE_OUT = dist/${EXE_NAME}

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
	cd docs && poetry run sphinx-apidoc -o . ../src
	cd docs && poetry run sphinx-build -b html . ./_build

docs-appmap: docs-clean-appmap
	APPMAP=true poetry run pytest test_plot_widget.py

docs-all: docs-appmap docs-build

${EXECUTABLE_OUT}: ${PYINSTALLER_ENTRY}
	poetry run pyinstaller -n ${EXE_NAME} --onefile ${PYINSTALLER_ENTRY}
