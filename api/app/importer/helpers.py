import re

class Field():
    """ Represents a field with a value, basically from a text file """
    def __init__(self, content):
        self.content = content

    def group_dict(self, regex):
        """ Returns a tuple of groupdicts based on the given regex """
        ret = []
        for match in re.finditer(regex, self.content):
            if match:
                ret.append(match.groupdict())
        return tuple(ret)