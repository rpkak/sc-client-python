BUILDOPTS  ?=
PYTHON     ?= python3
PIP        ?= $(PYTHON) -m pip
BUILD      ?= $(PYTHON) -m build 

added_files = $(wildcard *.egg-info/* dist/*)

.PHONY: all
all: clean dependencies build

.PHONY: clean
clean:
	rm -frv $(added_files)

.PHONY: dependencies
dependencies:
	$(PIP) install -U pip twine build

.PHONY: build
build:
	$(BUILD) $(BUILDOPTS)
