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

all: test

test: clean unittests pyflakes pep8

pep8: envsetup
	bash -c "\
          source ./pygerritenv/bin/activate && \
          git ls-files | grep \"\.py$$\" | xargs pep8 --max-line-length 80"

pyflakes: envsetup
	bash -c "\
          source ./pygerritenv/bin/activate && \
          git ls-files | grep \"\.py$$\" | xargs pyflakes"

unittests: envsetup
	bash -c "\
          source ./pygerritenv/bin/activate && \
          python unittests.py"

envsetup:
	bash -c "\
          [ -e ./pygerritenv/bin/activate ] || virtualenv ./pygerritenv && \
          source ./pygerritenv/bin/activate && \
          pip install --upgrade -r requirements.txt"

clean:
	@find . -type f -name "*.pyc" -exec rm -f {} \;
	@rm -rf pygerritenv pygerrit.egg-info build dist
