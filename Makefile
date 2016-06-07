# The MIT License
#
# Copyright 2013 Sony Mobile Communications. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

PWD := $(shell pwd)
VERSION := $(shell git describe)

VIRTUALENV := $(shell which virtualenv)
ifeq ($(wildcard $(VIRTUALENV)),)
  $(error virtualenv must be available)
endif

PIP := $(shell which pip)
ifeq ($(wildcard $(PIP)),)
  $(error pip must be available)
endif

REQUIRED_VIRTUALENV ?= 1.10
VIRTUALENV_OK := $(shell expr `virtualenv --version | \
    cut -f2 -d' '` \>= $(REQUIRED_VIRTUALENV))

all: test

test: clean unittests pyflakes pep8 pep257

docs: html

sdist: valid-virtualenv test
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          python setup.py sdist"

ddist: sdist docs
	bash -c "\
          cd docs/_build/html && \
          zip -r $(PWD)/dist/pygerrit2-$(VERSION)-api-documentation.zip . && \
          cd $(PWD)"

valid-virtualenv:
ifeq ($(VIRTUALENV_OK),0)
  $(error virtualenv version $(REQUIRED_VIRTUALENV) or higher is needed)
endif

html: sphinx
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          export PYTHONPATH=$(PWD) && \
          cd docs && \
          make html && \
          cd $(PWD)"

sphinx: docenvsetup
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          sphinx-apidoc \
              -V \"$(VERSION)\" \
              -R \"$(VERSION)\" \
              -H \"Pygerrit2\" \
              -A \"David Pursehouse\" \
              --full \
              --force \
              -o docs pygerrit2"

pep257: testenvsetup
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          git ls-files | grep \"\.py$$\" | xargs pep257"

pep8: testenvsetup
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          git ls-files | grep \"\.py$$\" | xargs flake8 --max-line-length 80"

pyflakes: testenvsetup
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          git ls-files | grep \"\.py$$\" | xargs pyflakes"

unittests: testenvsetup
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          python unittests.py"

testenvsetup: envsetup
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          pip install --upgrade -r test_requirements.txt"

docenvsetup: envsetup
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          pip install --upgrade -r doc_requirements.txt"

envsetup: envinit
	bash -c "\
          source ./pygerrit2env/bin/activate && \
          pip install --upgrade -r requirements.txt"

envinit:
	bash -c "[ -e ./pygerrit2env/bin/activate ] || virtualenv --system-site-packages ./pygerrit2env"

clean:
	@find . -type f -name "*.pyc" -exec rm -f {} \;
	@rm -rf pygerrit2env pygerrit2.egg-info build dist docs
