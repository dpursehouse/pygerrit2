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

FILES := $(shell git ls-files | grep py$$)

test: clean pyflakes pep8 pydocstyle unittests livetests

sdist: test
	pipenv run python setup.py sdist

pydocstyle: testenvsetup
	pipenv run pydocstyle $(FILES)

pep8: testenvsetup
	pipenv run flake8 $(FILES) --max-line-length 88

pyflakes: testenvsetup
	pipenv run pyflakes $(FILES)

black-check: testenvsetup
	pipenv run black --check $(FILES)

black-format: testenvsetup
	pipenv run black $(FILES)

unittests: testenvsetup
	pipenv run pytest -sv unittests.py

livetests: testenvsetup
	pipenv run pytest -sv livetests.py

testenvsetup:
	pipenv install --dev

clean:
	@find . -type f -name "*.pyc" -exec rm -f {} \;
	@rm -rf pygerrit2env pygerrit2.egg-info build dist
