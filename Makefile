# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


check: python clean check-reuse build
	@echo "\n\n\n   Yay.... check succeeded :)\n\n\n"

check-reuse: clean
#reuse --suppress-deprecation lint

python: py-test py-lint

py-test:
#PYTHONPATH=python/ python3 -m pytest --log-cli-level=10 tests/
        PYTHONPATH=. tests/test-interactive.sh 1
        PYTHONPATH=. pytest tests/test-lookup.py
        PYTHONPATH=. pytest tests/test-speed.py

py-lint:
	flake8

check-py-cli:
	@echo -n "Check cli (-h): "
	@PYTHONPATH=./python python3 ./lookup_license/__main__.py -h > /dev/null
	@echo "OK"

build:
	rm -fr build
	python3 setup.py sdist
	@echo
	@echo "build ready :)"

py-release: check clean build
	@echo
	@echo "To upload: "
	@echo "twine upload --repository lookup_license --verbose  dist/*"

check-reuse: clean
	reuse --suppress-deprecation lint

lint: check-reuse py-lint

clean:
	find . -name "*~"    | xargs rm -fr
	find . -name "*.pyc" | xargs rm -fr
	find . -name ".#*" | xargs rm -fr
	rm -f .coverage
	rm -fr *.egg-info
	rm -fr *.egg*
	rm -fr dist
	rm -fr build
