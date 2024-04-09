#!/usr/bin/env python

##/backupsarchivin04/check_partitions.py

import PyTangoArchiving as pta, sys, traceback
dbs = sys.argv[1:] or pta.get_hdbpp_databases()
dbs = {db:pta.api(db) for db in dbs}
for db,api in sorted(dbs.items()): 
    parts = {t:api.getTablePartitions(t) for t in api.get_data_tables()} 
    for t,ps in parts.items():
      try:
        if not ps or api.getTableRows(t)<1e6:
            continue
        dt = [p for p in ps if 'last' not in p]
        if not dt:
          p = ps[-1]
        else:
          p = dt[-1]
          dt = api.get_partition_time_by_name(p)
        if not dt or dt < pta.utils.now() + 6*30*86400:
          p += '\t%s rows at %s!!!' % (api.getTableSize(t),api.get_table_timestamp(t)[1])
          print('%20s\t%20s\t%20s' % (db,t,p))
      except:
        print(db,t,traceback.format_exc())


