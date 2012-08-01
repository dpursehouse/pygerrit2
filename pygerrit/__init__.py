""" Module to interface with Gerrit. """


def from_json(json_data, key):
    """ Helper method to extract values from JSON data.

    Return the value of `key` from `json_data`, or None if `json_data`
    does not contain `key`.

    """
    if key in json_data:
        return json_data[key]
    return None
