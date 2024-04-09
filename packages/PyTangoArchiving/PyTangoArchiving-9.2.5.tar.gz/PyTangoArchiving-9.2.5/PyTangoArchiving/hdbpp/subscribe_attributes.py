import PyTangoArchiving as pta
from fandango.tango import *

__doc__ = """
This method will add numeric attributes (scalar int/float) matching pattern,
but only if those attributes already provide events.

Usage:
  subscribe_attributes.py <schema> <pattern> <test=true|false>
  
"""

import sys, os

args = [a for a in sys.argv if '=' not in a]
schema = args[1]
pattern = args[2]

opts = dict(a.split('=',1) for a in sys.argv if '=' in a)
test = opts.get('test','True').lower()

#polling = int(opts.get('polling',0))
#abs_event = float(opts.get('abs_event',1e-12))
#rel_event = float(opts.get('rel_event',.01))

attrs = find_attributes(pattern)
print('%d attributes matching pattern' % len(attrs))

infos = dict(kmap(get_attribute_info,attrs))
print(fn.first(infos.items()))
nums = [k for k,v in infos.items() if v[0][1] == PyTango.AttrDataFormat.SCALAR
        and v[0][0] not in (CmdArgType.DevString, CmdArgType.DevEnum, CmdArgType.DevEncoded)
        and 'Array' not in str(v[0][0])]

print('%d attributes are numeric and can be added to archiving' % len(nums))
if test != 'false': 
    print('attributes NOT numeric: %s' % ','.join(
        sorted(a for a in attrs if a not in nums)))


evs = [a for a in nums if check_attribute_events(a)]
print('%d of those attributes provide events' % len(evs))

if test != 'false':
    print('attributes NOT providing events: %s' % ','.join(
        sorted(a for a in nums if a not in evs)))

if test == 'false':
    print('adding attributes to %s archiving ...' % schema)
    api = pta.api(schema)
    api.add_attributes(nums, code_event=True)
    
    

