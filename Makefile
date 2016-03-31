PACKAGE=acme_tiny
PYTHON?=python

install: clean
	$(PYTHON) setup.py sdist
	pip install dist/*

reinstall: uninstall install

uninstall:
	pip uninstall -y $(PACKAGE)

clean:
	$(PYTHON) setup.py clean --all
	rm -rf build dist MANIFEST *.egg-info
	find . -name '*.pyc' -exec rm -f {} \;
