#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# ISIS-DM: the ISIS Data Model API
#
# Copyright (C) 2010 BIREME/PAHO/WHO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
import re


MAIN_SUBFIELD_KEY = '_'
SUBFIELD_MARKER_RE = re.compile(r'\^([a-z0-9])', re.IGNORECASE)
DEFAULT_ENCODING = u'utf-8'

def expand(content, subkeys=None):
    ''' Parse a field into an association list of keys and subfields

        >>> expand('zero^1one^2two^3three')
        [('_', 'zero'), ('1', 'one'), ('2', 'two'), ('3', 'three')]

    '''
    if subkeys is None:
        regex = SUBFIELD_MARKER_RE
    elif subkeys == '':
        return [(MAIN_SUBFIELD_KEY, content)]
    else:
        regex = re.compile(r'\^(['+subkeys+'])', re.IGNORECASE)
    content = content.replace('^^', '^^ ')
    parts = []
    start = 0
    key = MAIN_SUBFIELD_KEY
    while True:
        found = regex.search(content, start)
        if found is None: break
        parts.append((key, content[start:found.start()].rstrip()))
        key = found.group(1).lower()
        start = found.end()
    parts.append((key, content[start:].rstrip()))
    return parts


class CompositeString(object):
    ''' Represent an Isis field, with subfields, using
    Python native datastructures

    >>> author = CompositeString('John Tenniel^xillustrator',
    ... subkeys='x')
    >>> unicode(author)
    u'John Tenniel^xillustrator'
    '''
    
    def __init__(self, isis_raw, subkeys=None, encoding=DEFAULT_ENCODING):
        if not isinstance(isis_raw, basestring):
            raise TypeError('%r value must be unicode or str instance' % isis_raw)

        self.__isis_raw = isis_raw.decode(encoding)
        self.__expanded = expand(self.__isis_raw, subkeys)

    def __getitem__(self, key):
        for subfield in self.__expanded:
            if subfield[0] == key:
                return subfield[1]
        else:
            raise KeyError(key)

    def __iter__(self):
        return (subfield[0] for subfield in self.__expanded)

    def items(self):
        return self.__expanded

    def __unicode__(self):
        return self.__isis_raw

    def __str__(self):
        return str(self.__isis_raw)


class CompositeTuple(object):
    ''' Represent an Isis field, with subfields, using
        Python native datastructures

        >>> author = CompositeTuple( [('name','Braz, Marcelo'),('role','writer')] )
        >>> print author['name']
        Braz, Marcelo
        >>> print author['role']
        writer
        >>> author
        CompositeTuple((('name', 'Braz, Marcelo'), ('role', 'writer')))

    '''

    def __init__(self, value, subkeys=None):
        if subkeys is None:
            subkeys = [item[0] for item in value]
        composite = namedtuple('Composite', subkeys)
        try:
            value_as_dict = dict(value)
        except TypeError:
            raise TypeError('%r value must be a key-value structure' % self)
        
        try:
            self.value = composite(**value_as_dict)
        except TypeError:
            raise TypeError('%r got an unexpected keyword' % self)

    def __getitem__(self, key):
        return getattr(self.value,key)

    def __repr__(self):
        return "CompositeTuple(%s)" % str(self.items())

    def items(self):
        return tuple(zip(self.value._fields, self.value))

    def __unicode__(self):
        unicode(self.items())

    def __str__(self):
        str(self.items())


def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    test()
