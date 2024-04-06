BUILD_DIR := build

# Builds the deployable Python artifacts
.PHONY: build
build:
	@echo "Building the package..."
	rm __init__.py
	python3 -m pip install --upgrade build && \
	  python3 -m build
	touch __init__.py

# Deploys the Python package to pip
.PHONY: deploy
deploy:
	@echo "Building the package..."
	python3 -m pip install --upgrade twine && \
	  python3 -m twine upload dist/*
