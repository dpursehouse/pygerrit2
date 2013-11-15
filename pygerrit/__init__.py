# The MIT License
#
# Copyright 2012 Sony Mobile Communications. All rights reserved.
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

""" Module to interface with Gerrit. """

__numversion__ = (0, 2, 2)
__version__ = '.'.join([str(num) for num in __numversion__])


def from_json(json_data, key):
    """ Helper method to extract values from JSON data.

    Return the value of `key` from `json_data`, or None if `json_data`
    does not contain `key`.

    """
    if key in json_data:
        return json_data[key]
    return None


def escape_string(string):
    """ Escape a string for use in Gerrit commands.

    Return the string with necessary escapes and surrounding double quotes
    so that it can be passed to any of the Gerrit commands that require
    double-quoted strings.

    """

    result = string
    result = result.replace('\\', '\\\\')
    result = result.replace('"', '\\"')
    return '"' + result + '"'
