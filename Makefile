# Required executables
ifeq (, $(shell which python3))
 $(error "No python3 on PATH.")
endif
ifeq (, $(shell which poetry))
 $(error "No poetry on PATH.")
endif

# Make sure we are running with an explicit encoding
export LC_ALL = C
export LANG = C.UTF-8
# Set configuration folder to venv
export PYPE_CONFIG_FOLDER = $(shell pwd)/.venv/.pype-cli
# Process variables
VERSION = $(shell python3 setup.py --version)

all: clean venv linters-diff package

venv: clean
	@echo Initialize virtualenv, i.e., install required packages etc.
	poetry install --sync

install:
	poetry install --sync

shell:
	@echo Initialize virtualenv and open a new shell using it
	poetry shell

clean:
	@echo Clean project base
	find . -type d \
	-name ".venv" -o \
	-name ".tox" -o \
	-name ".ropeproject" -o \
	-name ".mypy_cache" -o \
	-name ".pytest_cache" -o \
	-name "__pycache__" -o \
	-iname "*.egg-info" -o \
	-name "build" -o \
	-name "dist" \
	|xargs rm -rfv

linters-edit:
	@echo Run code formatting
	poetry run isort --sp .isort.cfg ark_sdk_python tests
	poetry run black --skip-string-normalization -l 140 -t py38 ark_sdk_python tests

linters-diff:
	@echo Run code formatting
	poetry run pylint --disable=R,C --rcfile .pylintrc ark_sdk_python tests
	poetry run isort --check-only --sp .isort.cfg ark_sdk_python tests
	poetry run black --check --skip-string-normalization -l 140 -t py38 ark_sdk_python tests

run:
	@echo Execute ark-sdk-python directly
	poetry run python3 -m ark

test:
	@echo Execute Tests
	poetry run pytest tests/unit

package:
	@echo Package sdk
	poetry build
