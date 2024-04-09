#!/usr/bin/env python

import sys, PyTangoArchiving as pta, fandango as fn

__doc__ = """
# check_db_growth.py [-h] [--table=regexp] [databases]
"""

opts,args = [],[]
[(opts if _.startswith('-') else args).append(_) for _ in sys.argv[1:]]
opts = {s[0]:s[-1] for o in opts for s in o.strip('-').split('=')}

if 'h' in opts or 'help' in opts:
    print(__doc__)
    sys.exit(0)

args = args or pta.get_hdbpp_databases()
regexp = opts.get('table','*')

for disk in fn.shell_command('ls /dev/sd*').split():
    usage = fn.linos.get_disk_usage(disk)
    if usage > 0.6:
        print('%s usage: %1.2f %%' % (disk,usage))


def trace(label,data,unit='G',factor=1e9):
    data = data/factor
    if data > 1.:
        print('\t{}: {:.2f} {}'.format(label,data,  unit))
  
dbs = {db:pta.api(db) for db in (args or pta.get_hdbpp_databases())}
print('')
for db,api in dbs.items():
    print('Database: %s' % api)
    trace('db size',api.getDbSize())

months = fn.defaultdict(float)
sizes = fn.defaultdict(float)

for db,api in dbs.items():
    tables = [_ for _ in api.get_data_tables() if fn.clmatch(regexp,_)]
    for t in tables:
        sizes[db+'.'+t] += api.getTableSize(t)
        for p in api.getTablePartitions(t):
            d = api.get_partition_time_by_name(p)
            d = fn.time2str(d).rsplit('-',1)[0]
            months[d] += api.getPartitionSize(t,p)

print('\nTable Sizes:')
sizes = sorted(sizes.items(),key=lambda k:k[1])
if len(sizes)>20:
    print('\t...')
for t,s in sizes[-20:]:
    s > 1e9 and trace(db+'.'+t,s)

print('\nMonthly grow:')

for m,s in sorted(months.items()):
    trace(m,s)
    
trace('\nTotal size',sum(v.getDbSize() for v in dbs.values()))
trace('\nPartitions size',sum(months.values()))
print('')



