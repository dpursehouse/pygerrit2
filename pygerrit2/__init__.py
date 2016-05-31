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


def from_json(json_data, key):
    """ Helper method to extract values from JSON data.

    :arg dict json_data: The JSON data
    :arg str key: Key to get data for.

    :Returns: The value of `key` from `json_data`, or None if `json_data`
        does not contain `key`.

    """
    if key in json_data:
        return json_data[key]
    return None


def escape_string(string):
    """ Escape a string for use in Gerrit commands.

    :arg str string: The string to escape.

    :returns: The string with necessary escapes and surrounding double quotes
        so that it can be passed to any of the Gerrit commands that require
        double-quoted strings.

    """

    result = string
    result = result.replace('\\', '\\\\')
    result = result.replace('"', '\\"')
    return '"' + result + '"'


class GerritReviewMessageFormatter(object):

    """ Helper class to format review messages that are sent to Gerrit.

    :arg str header: (optional) If specified, will be prepended as the first
        paragraph of the output message.
    :arg str footer: (optional) If specified, will be appended as the last
        paragraph of the output message.

    """

    def __init__(self, header=None, footer=None):
        self.paragraphs = []
        if header:
            self.header = header.strip()
        else:
            self.header = ""
        if footer:
            self.footer = footer.strip()
        else:
            self.footer = ""

    def append(self, data):
        """ Append the given `data` to the output.

        :arg data: If a list, it is formatted as a bullet list with each
            entry in the list being a separate bullet.  Otherwise if it is a
            string, the string is added as a paragraph.

        :raises: ValueError if `data` is not a list or a string.

        """
        if not data:
            return

        if isinstance(data, list):
            # First we need to clean up the data.
            #
            # Gerrit creates new bullet items when it gets newline characters
            # within a bullet list paragraph, so unless we remove the newlines
            # from the texts the resulting bullet list will contain multiple
            # bullets and look crappy.
            #
            # We add the '*' character on the beginning of each bullet text in
            # the next step, so we strip off any existing leading '*' that the
            # caller has added, and then strip off any leading or trailing
            # whitespace.
            _items = [x.replace("\n", " ").strip().lstrip('*').strip()
                      for x in data]

            # Create the bullet list only with the items that still have any
            # text in them after cleaning up.
            _paragraph = "\n".join(["* %s" % x for x in _items if x])
            if _paragraph:
                self.paragraphs.append(_paragraph)
        elif isinstance(data, str):
            _paragraph = data.strip()
            if _paragraph:
                self.paragraphs.append(_paragraph)
        else:
            raise ValueError('Data must be a list or a string')

    def is_empty(self):
        """ Check if the formatter is empty.

        :Returns: True if empty, i.e. no paragraphs have been added.

        """
        return not self.paragraphs

    def format(self):
        """ Format the message parts to a string.

        :Returns: A string of all the message parts separated into paragraphs,
            with header and footer paragraphs if they were specified in the
            constructor.

        """
        message = ""
        if self.paragraphs:
            if self.header:
                message += (self.header + '\n\n')
            message += "\n\n".join(self.paragraphs)
            if self.footer:
                message += ('\n\n' + self.footer)
        return message
