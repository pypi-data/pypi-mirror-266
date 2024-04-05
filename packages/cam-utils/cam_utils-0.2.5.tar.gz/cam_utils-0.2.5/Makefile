
NAME=cam_utils
VERSION=0.2.5
PYTHON = python3



# Define targets and their dependencies
all: build upload

help: 
	@echo "make all # do build && do upload "
	@echo "make build # create de package dist/* "
	@echo "make upload # Upload dist do PyPIP "


upload:
	@echo "Start Upload dist/* to pip" 
	pip3 install twine
	twine upload dist/*

build:
	@echo "Create package pip in dist/*" 
	@echo "Compilando $(NAME):$(VERSION)"
	$(PYTHON) setup.py sdist bdist_wheel # --name=$(NAME) --version=$(VERSION)



.PHONY: all help upload build


