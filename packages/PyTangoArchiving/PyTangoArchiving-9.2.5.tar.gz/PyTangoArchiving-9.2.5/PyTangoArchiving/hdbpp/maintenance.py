import sys, traceback, datetime
import fandango as fn
import PyTangoArchiving as pta
from fandango.db import FriendlyDB
import fandango.threads as ft
from fandango import time2str, str2time

__doc__ = """
To create new partitions from shell just do:

python /usr/lib/python2.7/dist-packages/PyTangoArchiving/hdbpp/maintenance.py create_db_partitions hdbpp 36 $(fandango "time2str(now()+365*86400,'%Y-%m-01')") do_it=True

"""

"""
In [1]: import PyTangoArchiving as pta

In [4]: hdbpp = pta.api('hdbpp')
HDBpp(): Loading from Schemas

In [5]: partitions = pta.dbs.get_partitions_from_query(hdbpp,'select * from %s'%table)

In [6]: partitions
Out[6]: 'afw20171201,afw20180101,afw20180201,afw20180301,afw20180401,afw20180501,afw20180601,afw20180701,afw20180801,afw20180901,afw20181001,afw20181101,afw20181201,afw20190101,afw20190201,afw20190301'

In [7]: partitions = 'afw20180301,afw20180401,afw20180501,afw20180601,afw20180701,afw20180801,afw20180901,afw20181001,afw20181101,afw20181201,afw20190101,afw20190201,afw20190301'

In [8]: hdbpp.Query('alter table %s optimize partition %s' % (table,partitions))
Out[8]: [('hdbpp.att_array_devfloat_rw', 'optimize', 'status', 'OK')]

"""

CURR_YEAR = fn.time2str().split('-')[0]

def get_all_partitions(api):
    if fn.isString(api): api = pta.api(api)
    partitions = dict((t,
        dict((p,api.getPartitionSize(t,p)) for p in api.getTablePartitions(t)))
        for t in api.getTables())
    return partitions

def get_attributes_row_counts(db,attrs='*',start=0, stop=0,
                              partition='',limit=0):
    """
    DUPLICATED BY HDBPP.get_attribute_rows !!!
    
    It will return matching $attrs that recorded more than $limit values in 
    the $start-$stop period::
    
      countsrf = get_attributes_row_counts('hdbrf',start=-3*86400,limit=20000)
      
    """
    db = pta.api(db) if fn.isString(db) else db
    if fn.isString(attrs):
        attrs = [a for a in db.get_attributes() if fn.clmatch(attrs,a)]
        
    r = {}
    for a in attrs:
        i,t,b = db.get_attr_id_type_table(a)
        q = "select count(*) from %s " % b
        if partition:
            q += "partition(%s) " % partition
        q += "where att_conf_id = %d"  % (i)
        if start and stop:
            start = start if fn.isString(start) else fn.time2str(start) 
            stop = stop if fn.isString(stop) else fn.time2str(stop)
            q += " and data_time between '%s' and '%s'" % (start,stop)
        l = db.Query(q)
        c = l[0][0] if len(l) else 0
        if c >= limit:
            r[a] = c
    return r

def get_tables_stats(dbs=None,tables=None,period=365*86400):
    """
    obtains counts and frequencies stats from all data tables from all dbs
    """
    dbs = dbs or pta.multi.get_hdbpp_databases()
    result = fn.defaultdict(fn.Struct)
    date = int(fn.clsub('[^0-9]','',fn.time2str().split()[0]))
    if period:
        date0 = int(fn.clsub('[^0-9]','',
                             fn.time2str(fn.now()-period).split()[0]))
    else:
        date0 = 0
    print(date0,date)
    for d in dbs:
        api = pta.api(d)
        dbtables = tables or api.getTables()
        for t in dbtables:
            result[(d,t)].db = d
            result[(d,t)].table = t
            result[(d,t)].partitions = [p for p in api.getTablePartitions(t)
                if date0 < fn.str2int(p) < date]
            result[(d,t)].attributes = (api.get_attributes_by_table(t) 
                if t in api.get_data_tables() else [])
            result[(d,t)].last = (api.get_last_partition(t,tref=fn.now())
                if t in api.get_data_tables() else '')
            if len(result[(d,t)].partitions) > 1:
                result[(d,t)].size = sum(api.getPartitionSize(t,p)
                                    for p in result[(d,t)].partitions)
                result[(d,t)].rows = sum(api.getPartitionRows(t,p)
                                    for p in result[(d,t)].partitions)
            else:
                result[(d,t)].size = api.getTableSize(t)
                result[(d,t)].rows = api.getTableRows(t)
                
    for k,v in result.items():
        v.partitions = len(v.partitions)
        v.attributes = len(v.attributes)
        v.attr_size = float(v.size)/v.attributes if v.attributes else 0
        v.attr_rows = float(v.rows)/v.attributes if v.attributes else 0
        v.row_size = v.size/v.rows if v.rows else 0
        v.part_size = v.size/v.partitions if v.partitions else 0
        v.row_freq = v.rows/float(period) if period else 0
        v.size_freq = v.size/float(period) if period else 0
        v.attr_freq = v.row_freq/v.attributes if v.attributes else 0
        
    return result

def get_tables_ranges(db,tables=None):
    if fn.isString(db):
        db = pta.api(db)
    tables = tables or db.get_data_tables()
    r = []
    for t in tables:
        tt = db.get_table_timestamp(t,method='max')
        if tt[0] is not None:
            mt = db.get_table_timestamp(t,method='min')
            ps = db.get_partitions_at_dates(t,mt[0],tt[0])
            if ps:
                s = fn.avg([db.getPartitionRows(t,p) for p in ps])
            else:
                s = db.getTableRows(t)
            r.append((t,mt[1].split()[0],tt[1].split()[0],s,ps[-1] if ps else None))
    return r

def check_db_partitions(api,regexp='',max_size=128*1e9/10, min_size=1e5):
    """
    year and month, strings to match on existing partitions
    e.g. '202102[0-9][0-9]' will match any partition from february

    :param api:
    :param filter:
    :return:
    """
    if fn.isString(api): api = pta.api(api)
    result = fn.Struct(db_name=api.db_name)
    type(result).__repr__ = lambda s: getattr(s,'report',
                                              'keys:%s' % str(s.keys()))
    tables = api.get_data_tables()
    sizes = dict(fn.kmap(api.getTableSize,tables))
    parts = dict(fn.kmap(api.getTablePartitions,tables))
    bigs = dict((t,max(api.getPartitionSize(t,p) for p in parts[t])) for t in tables if parts[t])
    result.wrong = dict((t,[p for p in parts[t]
        if not p.startswith(pta.hdbpp.query.partition_prefixes[t])]) for t in tables)
    
    # Partitions at "date"
    match = dict((t,[p for p in parts[t] if fn.clsearch(regexp,p)]) for t in tables)
    
    result.sizes, result.parts, result.match, result.bigs = sizes, parts, match, bigs
    
    # Tables with no partition at date
    result.miss = [t for t,ps in parts.items() if len(ps) 
                   and sizes[t]>max_size and not match[t]]
    result.noparts = [t for t in tables if sizes[t]>max_size 
                      and not len(parts[t])]
    result.toobigs = [(t,s/1e9,'G') for t,s in bigs.items() if s>max_size ]
                      #and len(match[t])<2]

    result.nolasts = [t for t in tables if len(parts[t])
        and not any(p.endswith('_last') for p in parts[t])]

    result.report = '\n'.join((
    '%s: tables that need partitioning: %s' % (result.db_name,result.noparts),
    '%s: tables with no %s partition: %s' % (result.db_name, regexp, result.miss),
    '%s: tables with too big partitions: %s' % (result.db_name, result.toobigs),
    '%s: tables with no _last partition: %s' % (result.db_name, result.nolasts),
    '%s: tables with wrong prefixes: %s' % (result.db_name,[t for t in result.wrong.items() if t[1]]),
    ))

    return result

def check_last_partitions(api,tsize=1e9):
    api = pta.api(api)
    errs = []
    for t in api.get_data_tables():
        s,ps = api.getTableSize(t),api.getTablePartitions(t)
        if s>tsize:
            if not ps:
                errs.append('%s.%s should be partitioned!: %sG' % (api.schema,t,s/1e9))
            elif ps:
                print(api.schema,t,s/1e9,ps[0],
                      api.get_last_partition(t,min_size=1e5),ps[-2:])
    print('\n'.join(sorted(errs)))

def check_partition_overlap(dbr,dbd='',min_table=1e9,min_partition=1e5):
    dbr = pta.api(dbr)
    dbd = pta.api(dbd or dbr.schema+'_r')
    for t in dbr.get_data_tables():
        s0,s1 = dbr.getTableSize(t),dbd.getTableSize(t)
        if min((s0,s1)) > min_table:
            ps = dbr.getTablePartitions(t)
            if not ps:
                print('%s should be partitioned!: %sG' % (t,s0/1e9))
            else:
                print(t,s0/1e9,dbd.schema,
                    dbd.get_last_partition(t,min_size=min_partition),
                    dbr.schema,ps[0])
                
def purge_partitions(api, date, do_it=False):
    """ 
    it will drop all partitions prior to date 
    """
    api = pta.api(api)
    for t in api.get_data_tables():
        for p in api.getTablePartitions(t):
            if api.get_partition_time_by_name(p) < fn.str2time(date):
                q = 'alter table %s drop partition %s' % (t,p)
                print(q)
                if do_it:
                    api.Query(q)
    if not do_it:
        print('dry run, no queries executed')

def decimate_value_list(values,period=None,max_period=3600,method=None,
        N=1080, debug=False, abs_change=1e-11, rel_change=5e-4,
        generator=False):
    """
    used by decimate_into_new_table

    values must be a sorted (time,...) array 
        [(float_time,value,date,quality)]
    periods in seconds
    it will be decimated in N equal time intervals if period not given
    if method is not provided, only the first value of each interval will be kept
    if method is given, it will be applied to buffer to choose the value to keep
    first value of buffer will always be the last value kept
    """
    ## THIS METHOD IS A SIMPLIFICATION OF fandango.arrays.filter_array!
    # it allows rows to be as long as needed (if [0]=time and [1]=value)
    # (just check which is faster)
        
    if not len(values):
        return []
    
    if not period:
        tmin,tmax = (values[0][0],values[-1][0])
        period = float(tmax-tmin)/N
        
    if isinstance(method,(str,basestring)):
        method = {'max':max,'min':min,'avg':fn.avg,
                    'first':fn.first,'last':fn.last,
                    'peak':fn.peak,'maxmin':fn.peak,
                    }.get(method,None)        

    if debug:
        print('decimate_value_list(%s)' % 
            str((len(values),period,max_period,method,N)))
    
    def genx(values):
        last_i, last_v = 0, None
        valid, prev = False, None
        maxpeak, minpeak = None, None
        isfloat = None
        last_t = 0 if not method or not values else values[0][0]
        
        for i,v in enumerate(values):
            # valid flag is used to mark the interval as containing data
            # if all values are None, method() will not be executed
            # it is cleared every time a value is returned
            if v[1] is not None:
                valid = True
                if isfloat is None:
                    isfloat = isinstance(v[1],float)
                    maxpeak, minpeak = v[1], v[1]

            tdiff = v[0] - last_t
            if tdiff >= 0.99*period:
                change = False
                
                # Method will be applied to values in last_t - period interval
                if method is not None and i > last_i+1:
                    # Do not insert values earlier than they are
                    tt = v[0] #fn.avg((last_t or v[0],v[0]))
                    if valid:
                        w = method(t[1] for t in values[last_i:i] 
                                   if t[1] is not None)
                    else:
                        w = None
                else:
                    tt,w = v[0],v[1] #it simply gets the last value in interval
                    
                if not isfloat or None in (w,last_v):
                    change = (w != last_v)
                else:
                    if w > maxpeak:
                        change, maxpeak = True , w
                        #if debug: print(w,last_v,maxpeak,'maxpeak')
                    elif w < minpeak:
                        change, minpeak = True, w
                        #if debug: print(w,last_v,minpeak,'minpeak')
                    else:
                        vdiff = abs(w-last_v)
                        delta = rel_change*min((w,last_v))
                        change = vdiff > abs_change or vdiff > delta
                        #if change and debug: print(w,last_v,vdiff,delta,'delta')

                # Store data (if relevant)
                if (change or tdiff>=max_period):
                    # if not interpolating, yield previous value
                    if prev and method is None and prev[0] > (last_t + period):
                        yield tuple(prev)
                    yield tuple(z for s in ((tt,w),v[2:]) for z in s)
                    last_i,last_t,last_v,valid = i,v[0],w,False
                
                prev = v

    if not generator:
        result = list(genx(values))
        if debug:
            print('%d => %d' % (len(values),len(result))) 
            
    return result
    
def decimate_table_inline(db, table, attributes = [], 
                   start = 0, stop = -1, partition = '', 
                   trange = 3, fmargin = 1):
    """
    BAD! Use decimate_into_new_db/table instead!

    @TODO
    This method decimates the table inline using MOD by int_time
    
    This is inefficient with MyISAM
    """
    db = pta.api(db) if fn.isString(db) else db
    l,_ = db.getLogLevel(),db.setLogLevel('DEBUG')
    t0 = fn.now()
    
    int_time = 'int_time' in db.getTableCols(t)
    
    where = 'partition(%s)'%partition if partition else ''
    where += " where "
    if attributes:
        where += " att_conf_id in (%s) and " % (','.join(attributes))
        
    if start!=0 or stop!=-1 or not partition:
        if int_time:
            s = start if start>0 else fn.now()-start
            e = stop if stop>0 else fn.now()-stop
            dates += " int_time between %s and %s "
        else:
            s, e = fn.time2str(start), fn.time2str(stop)
    
    hours = [t0+i*3600 for i in range(24*30)]
    days = [t0+i*86400 for i in range(30)]
    dvalues = {}
    q = ("select count(*) from %s where att_conf_id = %d "
        "and data_time between '%s' and '%s'")
    for d in days:
        s = fn.time2str(d)
        q = hdbpp.Query(q%(table,att_id,s,fn.time2str(d+86400))
                        +" and (data_time %% 5) < 2;")
        
    sorted(values.items())
    3600/5
    for h in hours:
        s = fn.time2str(h)
        q = hdbpp.Query("select count(*) from att_scalar_devdouble_ro "
            "where att_conf_id = 1 and data_time between '%s' and '%s' "
            "and (data_time %% 5) < 2;"%(s,fn.time2str(h+3600)))
        
    
    ## Get Bigger ID's in table
    # MariaDB [hdbpp_r]> select att_conf_id, count(*) as COUNT 
    # from att_scalar_devdouble_ro partition(sdr20180601) 
    # group by att_conf_id HAVING COUNT > 864000 order by COUNT;
    
    #MariaDB [hdbpp_r]> select att_conf_id, count(*) as COUNT from att_scalar_devdouble_ro partition(sdr20180601) group by att_conf_id HAVING COUNT > 864000 order by COUNT;
    #+-------------+----------+
    #| att_conf_id | COUNT    |
    #+-------------+----------+
    #|          99 |  1756407 |
    #|         967 |  1855757 |
    #|         963 |  1877412 |
    #|         966 |  1917039 |
    #|         961 |  1921648 |
    #|         964 |  1956849 |
    #|         975 |  1989966 |
    #|        1035 |  1989980 |
    #|        1024 |  1990009 |
    #|        1023 |  1990068 |
    #|         962 |  2211943 |
    #|         968 |  2659039 |
    #|         969 |  2659042 |
    #|        1005 |  2754352 |
    #|        1006 |  2754378 |
    #|        1029 |  2755194 |
    #|        1007 |  2755194 |
    #|         985 |  2797790 |
    #|        1019 |  2797801 |
    #|          97 |  3782196 |
    #|        1014 |  4054545 |
    #|         992 |  4054548 |
    #|        1015 |  4077444 |
    #|         997 |  4077526 |
    #|         974 |  4174792 |
    #|        1012 |  4174847 |
    #|        1013 |  4266515 |
    #|         986 |  4266653 |
    #|           1 |  8070710 |
    #|         982 |  8456059 |
    #|         981 |  8456105 |
    #|         996 |  9815756 |
    #|        1018 |  9815768 |
    #|        1037 | 10138245 |
    #|        1032 | 10138463 |
    #|           5 | 12769963 |
    #|           6 | 12881867 |
    #+-------------+----------+
    #37 rows in set (2 min 37.02 sec)

    """
    drop table tmpdata;
    set maxcount : = 864000;
    
    create temporary table tmpdata (attid int(10), rcount int(20));
    
    insert into tmpdata select att_conf_id, count(*) as COUNT 
        from att_scalar_devdouble_ro partition(sdr20180501) 
        group by att_conf_id order by COUNT;
        
    delete from att_scalar_devdouble_ro partition(sdr20180501) 
        where att_conf_id in (select attid from tmpdata where rcount > @maxcount)
        and CAST(UNIX_TIMESTAMP(data_time) AS INT)%3 > 0;
        
    select att_conf_id, count(*) as COUNT 
        from att_scalar_devdouble_ro partition(sdr20180501) 
        group by att_conf_id order by COUNT;
        
    select att_conf_id, count(*) as COUNT 
        from att_scalar_devdouble_ro partition(sdr20180501) 
        group by att_conf_id order by COUNT HAVING COUNT > @maxcount;
        
    set attid := (select attid from tmpdata order by count desc limit 1);
    select * from tmpdata where attid = @attid;
    select att_conf_id, data_time, count(*) as COUNT 
        from att_scalar_devdouble_ro partition(sdr20180501) 
        where att_conf_id = @attid group by att_conf_id, 
        CAST((UNIX_TIMESTAMP(data_time)/(86400)) AS INTEGER) 
        order by att_conf_id,data_time;
    """
    
    ## Get N rows per day
    # select data_time, count(*) as COUNT from att_scalar_devdouble_ro 
    # partition(sdr20180501) where att_conf_id = 1013 group by 
    # CAST((UNIX_TIMESTAMP(data_time)/86400) AS INTEGER) order by data_time;
    
    # MariaDB [hdbpp_r]> delete from att_scalar_devdouble_ro 
    # partition(sdr20180501) where att_conf_id = 6 
    # and CAST(UNIX_TIMESTAMP(data_time) AS INTEGER)%3 > 0; 
        
    q = 'repair table %s' + ('partition(%s)'%partition if partition else '')
    api.Query(q)
    print('decimate(%s, %s) took %f seconds' % (table,partition,fn.now()-t0))
    db.setLogLevel(l)
    return

def decimate_into_new_db(db_in, db_out, min_period = 3, min_array_period = 10,
                         max_period = 3600, begin=None, end=None,
                         tables = None, method=None, 
                         attributes = None,
                         remove_nones=True,
                         server_dec = True, 
                         insert = True,
                         bunch=86400/4,
                         use_files=True,
                         force_interval=False,
                         tmpdir='/tmp/',debug=False,
                         disable_keys=True):
    """
    force_interval: if False, interval for query will depend on the gaps to 
      fill between the 2 databases. If True, it will attach to arguments.
    """
    t00 = fn.now()
    if tables is None:
        tables = db_in.get_data_tables() #pta.hdbpp.query.partition_prefixes.keys()

    done = []
    for i,table in enumerate(sorted(tables)):
        print('%s decimating table %s.%s (%d/%d)' 
              % (fn.time2str(),db_in.db_name,table,i+1,len(tables)))
    
        begin = fn.str2time(begin) if fn.isString(begin) else begin
        end = fn.str2time(end) if fn.isString(end) else end
        
        tbegin = get_last_value_in_table(db_out,table,ignore_errors=True)[0]
        if not tbegin:
            tbegin = get_first_value_in_table(db_in,table,ignore_errors=True)[0]
        print(begin,tbegin)
        if force_interval:
            tbegin = begin
        elif begin is not None:
            tbegin = max((begin,tbegin)) #Query may start later

        tend = get_last_value_in_table(db_in,table,ignore_errors=True)[0]
        print(end,tend)
        if force_interval:
            tend = end
        elif end is not None:
            tend = min((end,tend)) #Query may finish earlier
        if tend is None:
            tend = tbegin
        print(end,tend)
            
        print('%s, syncing %s,%s to %s,%s' % (table,
            tbegin,fn.time2str(tbegin),tend,fn.time2str(tend)))

        if tend and tbegin and tend-tbegin < 600:
            db_out.warning('%s Tables already synchronized' % table)
            continue

        if 'array' in table:
            period = min_array_period
        else:
            period = min_period
        
        try:
            if disable_keys:
                db_out.warning('Disabling keys on %s' % table)
                db_out.Query("ALTER TABLE `%s` DISABLE KEYS;" % table)

            try:
                decimate_into_new_table(db_in,db_out,table,
                    tbegin,tend,min_period=period, max_period = max_period,
                    method = method,remove_nones = remove_nones,
                    server_dec = server_dec, bunch = bunch,
                    use_files = use_files, attributes = attributes,
                    tmpdir = tmpdir, insert = insert, debug = debug)
                done.append(table)
            except:
                print(fn.time2str())
                traceback.print_exc()                
                
            finally:
                if disable_keys:
                    db_out.warning('Reenabling keys on %s' % table)
                    db_out.Query("ALTER TABLE `%s` ENABLE KEYS;" % table)

        except:
            print(fn.time2str())
            traceback.print_exc()
            
    print('decimate_into_new_db(%s,%s,%s,%s) took %s seconds' % (
        db_in,db_out,begin,end,fn.now()-t00))
    return done

def decimate_into_new_table(db_in, db_out, table, start, stop, ntable='', 
        min_period=1, max_period=3600, bunch=86400/4, suffix='_dec',
        drop=False, method=None, 
        remove_nones=True, attributes = None,
        server_dec=True, insert=True, use_files=True, use_process=True,
        tmpdir='/tmp/',
        debug=False,
        ):
    """
    decimate by distinct value, or by fix period
    accept a min_resolution argument
    do selects in bunches 6 hours
    db_in is the origin database; db_out is where decimated data will be stored
    if db_in == db_out; then a temporary table with suffix is created

    bunch: queries will be split in bunch intervals
    """
    t0 = fn.now()

    if (db_in.host,db_in.db_name) != (db_out.host,db_out.db_name):
        suffix = ''
    if not ntable:
        ntable = table+suffix
    l = db_in.getLogLevel()
    nattrs = len(db_in.get_attributes_by_table(table))
    
    if fn.isString(start):
        date0,date1 = start,stop
        start,stop = fn.str2time(start),fn.str2time(stop)
    else:
        date0,date1 = fn.time2str(start),fn.time2str(stop)
        
    db_in.setLogLevel('INFO')
    db_out.setLogLevel('INFO')               
        
    print('decimate_into_new_table(%s.%s => %s@%s.%s, %s to %s): periods (%s,%s)' % 
        (db_in.db_name,table,db_out.db_name,db_out.host,ntable,date0,date1,
         min_period,max_period))
    try:
        cpart = (db_in.get_partitions_at_dates(table,start) or [None])[0]
        print('%s.%s.%s size = %s' % 
              (db_in,table,cpart,db.getPartitionSize(table,cpart)))
    except: 
        cpart = None
        
    # BUNCHING PROCEDURE!
    if stop-start > bunch:
        # Decimation done in separate processes to not overload memory
        # at the end, it returns values
        i = 0
        rs = (0,0,0,0,0) if insert else [] #tquery, tdec, tinsert, len(data), len(dec)
        nb = bunch
        while start < stop and start < fn.now():
            rstop = start+nb #rstop = min((start+nb,stop))
            r = ft.SubprocessMethod(decimate_into_new_table, db_in, db_out, table,
                start = start,stop = rstop, attributes = attributes,
                ntable=ntable, min_period=min_period, max_period=max_period,
                bunch=bunch, suffix=suffix, drop=drop, method=method,
                server_dec=server_dec,insert=insert,use_process=False,
                sp_timeout=3*3600,
                )
            start+=nb
            i+=nb/bunch            
            tquery,tdec,tinsert,ldata,ldec = rs
            print('%s.%s[%s] => %s.%s[%s] (tquery=%s,tdec=%s,tinsert=%s)' % (
                db_in.db_name,table,ldata,db_out.db_name,ntable,ldec,
                    tquery,tdec,tinsert))        

            if not len(rs):
                nb = bunch*10
            else:
                nb = bunch
                if insert:
                    rs = tuple(map(sum,zip(rs,r)))
                else:
                    rs.extend(rs)                

        if insert:
            tquery,tdec,tinsert,ldata,ldec = rs
            print('%s.%s[%s] => %s.%s[%s] (tquery=%s,tdec=%s,tinsert=%s)' % (
                db_in.db_name,table,ldata,db_out.db_name,ntable,ldec,
                    tquery,tdec,tinsert))        

        return rs  
    
    ###########################################################################
    # PROCESS OF DECIMATION FOR EACH INDIVIDUAL BUNCH:
    ###########################################################################
    
    tables = db_out.getTables()
    
    if drop:
        db_out.Query('drop table if exists %s' % ntable)
    
    # Create Table if it doesn't exist
    if ntable not in tables:
        code = db_in.getTableCreator(table)
        qi = code.split('/')[0].replace(table,ntable)
        try:
            db_out.Query(qi)
        except Exception as e:
            db_in.warning('Unable to create table %s' % ntable)
            print(e)

    # Create partitions if they doesn't exist
    pass

    try:
        # Create Indexes if they doesn't exit
        add_int_time_column(db_out, table)
    except:
        traceback.print_exc()

    ###########################################################################
    # Getting the data
    
    t0 = fn.now()
    db_in.info('Get %s values between %s and %s server_dec=(%s,%s)' 
               % (table, date0, date1, server_dec, method))
    aggr = 'value_r'
    if server_dec:
        if method in (max,'max'): aggr = 'max(value_r)'
        elif method in (min,'min'): aggr = 'min(value_r)'
        elif method in (fn.arrays.average,'avg'): aggr = 'avg(value_r)'

    what = ("att_conf_id,data_time,%s,quality"%aggr).split(',')
    # converting  times on mysql as python seems to be very bad at
    # converting datetime types
    float_time = "CAST(UNIX_TIMESTAMP(data_time) AS DOUBLE)"
    what.append(float_time)
    array = 'idx' in db_in.getTableCols(table)
    if array:
        what.extend('idx,dim_x_r,dim_y_r'.split(','))
        
    #-------------------------------------------------------------------------   
    attrs = db_in.get_attributes_by_table(table)
    attrs = attrs if not attributes else [a for a in attrs if a in attributes]
    ids = [db_in.get_attr_id_type_table(a)[0] for a in attrs]
    data = []
    #  QUERYING THE DATA PER ATTRIBUTE IS MUUUUUCH FASTER!
    for i,a in enumerate(attrs):
        q = db_in.get_attribute_values_query(a,
            what = ','.join(what),
            where = '',
            start_date = start,
            stop_date = stop,
            decimate = min_period if server_dec else 0,
            )
        
        if not i%10:
            db_in.info(q)
        else:
            db_in.debug(q)

        if use_process:
            dd = ft.SubprocessMethod(db_in.Query,q,sp_timeout=1800)
        else:
            dd = db_in.Query(q)
        db_in.debug('%s values [%d] (%2.3f values/second)' 
                % (fn.tango.get_normal_name(a),len(dd),len(dd)/(stop-start)))
        data.extend(dd)

    ldata = len(data)
    tquery = fn.now()-t0

    ###########################################################################
    # Decimating
    
    t0 = fn.now()
    
    # Splitting data into attr or (attr,idx) lists
    # Creating empty dictionaries to store decimated data
    data_ids = fn.defaultdict(lambda:fn.defaultdict(list))
    # i,j : att_id, idx
    
    # Do not remove nones when using server-side decimation!
    tlimit = fn.now()+86400
    db_in.info('data[0]: %s' % fn.shortstr(len(data) and data[0]))
    
    if 'array' in table or not server_dec or remove_nones:
        # Nones are inserted only if using server_decimation on scalars
        if array:
            [data_ids[aid][idx].append((t,v,d,q,x,y)) for aid,d,v,q,t,idx,x,y in data if v is not None
             and 1e9 < t < tlimit];
        else:
            [data_ids[aid][None].append((t,v,d,q)) for aid,d,v,q,t in data if v is not None
             and 1e9 < t < tlimit];
    else:
        if array:
            [data_ids[aid][idx].append((t,v,d,q,x,y)) for aid,d,v,q,t,idx,x,y in data
             and 1e9 < t < tlimit];
        else:
            [data_ids[aid][None].append((t,v,d,q)) for aid,d,v,q,t in data
             and 1e9 < t < tlimit];
            
    db_in.info('Decimating %s[%s] %d values, period = (%s,%s,[%s]), '
               'server_dec = %s, remove_nones = %s, method = %s' % 
               (table,len(data_ids),len(data),min_period,max_period,
                bunch,server_dec,remove_nones,method))            
       
    if debug:
        print(fn.shortstr(data))
        print(fn.shortstr(data_ids))

    data_dec = {}  
    for i,tt in enumerate(data_ids.items()):
        kk,vv = tt
        data_dec[kk] = {}
        for k,v in vv.items():
            # Values need to be ALWAYS! decimated, because server_dec only
            # eliminates higher frequencies
            if kk == fn.first(data_ids.keys()):
                print(kk,k,v and v[0])#len(v))
            
            #if server_dec: # and int(server_dec) == int(min_period):
                #data_dec[kk][k] = v
            #else:
            data_dec[kk][k] = decimate_value_list(v,
                period=min_period, max_period=max_period, 
                method=method, #if not server_dec else None,
                debug = debug or not i%10)
            
            if debug or not i%10:
                print('%s[%d] => %s' % (kk,len(v),len(data_dec[kk][k])))
                if kk == fn.first(data_ids.keys()):
                    print(kk,k,fn.first(data_dec[kk][k],None))
    
    if data_dec.values() and fn.first(data_dec.values()).values():
        db_in.info('data_dec[0][0]: %s' 
                   % fn.shortstr(fn.first(fn.first(data_dec.values()).values())))
            
    if array:
        # TODO: idx should go before value_r!!!
        #data_all = sorted((d,aid,v,q,idx,x,y) for aid in data_dec
        data_all = sorted((aid,idx,d,v,q,x,y) for aid in data_dec 
            for idx in data_dec[aid] for t,v,d,q,x,y in data_dec[aid][idx])
    else:
        #data_all = sorted((d,i,v,q) for i in data_dec for t,v,d,q in data_dec[i][None])
        data_all = sorted((i,d,v,q) for i in data_dec for t,v,d,q in data_dec[i][None])
            
    tdec = fn.now()-t0
    ldec = len(data_all)
    t0 = fn.now()
    
    if insert:
        if use_files:
            db_in.info('insert using tmp files ...')
            filename = tmpdir+'/%s.%s.bulk' % (db_out.db_name,ntable)
            columns = 'att_conf_id'
            if array:
                columns += ',idx'
            columns += ',data_time,value_r,quality'
            if array: 
                columns += ',dim_x_r,dim_y_r'
                if ntable.endswith('_rw'):
                    columns += ',dim_x_w,dim_y_w'
            insert_into_csv_file(data_all,columns,ntable,filename)
            r = load_from_csv_file(db_out,ntable,columns,filename)
            if debug:
                for l in r:
                    print(l)
        elif use_process:
            db_in.info('insert using subprocess ...')
            r = ft.SubprocessMethod(
                insert_into_new_table,db_out,ntable,data_all
                ,sp_timeout = 1800)
        else:
            r = insert_into_new_table(db_out,ntable,data_all)
            
    tinsert = fn.now()-t0
    
    print('\n%s.%s[%s] => %s.%s[%s] (tquery=%s,tdec=%s,tinsert=%s)\n' % (
        db_in.db_name,table,len(data),db_out.db_name,ntable,ldec,
            tquery,tdec,tinsert))
    
    if debug:
        try:
            cpart = (db_out.get_partitions_at_dates(ntable,start) or [None])[0]
            r = db_out.getPartitionSize(ntable,cpart)
            print('%s.%s.%s new size = %s' % 
                (db_out,ntable,cpart,r))
            q = 'select count(*) from %s where data_time between '\
                '"%s" and "%s"' % (ntable,fn.time2str(start),fn.time2str(stop))
            print(q)
            print(db_out.Query(q))    
        except: 
            if debug:
                traceback.print_exc()
            cpart = None    
            r = 0            
    
    if insert:
        return tquery,tdec,tinsert,len(data),ldec
    else:
        return data_all
    
def insert_into_csv_file(data, columns, table, filename):
    print('insert_into_csv_file(%s,%s,%s,%s)'%(fn.shortstr(data),columns,table,filename))
    t0 = fn.now()
    if fn.isString(columns):
        columns = columns.split(',')

    str_cols = [i for i,c in enumerate(columns) if 'data_time' in c 
                or ('value' in c and 'str' in table)]

    r = 0
    try:
        f = open(filename,'w')
        #f.write(','.join(columns) + '\n')
        
        for t in data:
            l = []
            for i,c in enumerate(columns):
                if i>=len(t):
                    l.append('"0"')
                else:
                    v = str(t[i])
                    #if v is None or i not in str_cols:
                        #l.append(str(v))
                    #else:
                    if 'str' in table and 'value' in c:
                        v = v.replace('"','').replace("'",'').replace(' ','_')[:80]

                    if c == 'data_time':
                        v = v.replace(' ','T')
                        
                    if v == 'None':
                        v = 'NULL'
                        
                    l.append('"%s"' % v)
            f.write(','.join(l) + '\n')
            r+=1
    except:
        traceback.print_exc()
    finally:
        f.close()
        
    tinsert = fn.now() - t0
    print('%d/%d values written to %s in %f seconds' % (r,len(data),filename,tinsert))
    return len(data),tinsert


def load_from_csv_file(api, table, columns, filename):
    print('load_from_csv_file(%s,%s,%s,%s)'%(api,table,columns,filename))
    if fn.isString(api): api = pta.api(api)
    if fn.isSequence(columns):
        columns = ','.join(columns)
    q = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY ',' "\
            "ENCLOSED BY '\"' (%s);" % (filename,table,columns)
    r = api.Query(q)
    return q,r,filename
    
                
                
            #if array:
                #d,i,v,q,j,x,y = t
            #else:
                #d,i,v,q = t

            #if 'string' in ntable and v is not None:
                #v = v.replace('"','').replace("'",'')[:80]
                #if '"' in v:
                    #v = "'%s'" % v
                #else:
                    #v = '"%s"' % v

            #if array:
                #if ntable.endswith('_rw'):
                    #s = "('%s',%s,%s,%s,%s,%s,%s,0,0)"%(d,i,v,q,j,x,y)
                #else:
                    #s = "('%s',%s,%s,%s,%s,%s,%s)"%(d,i,v,q,j,x,y)
            #else:
                #s = "('%s',%s,%s,%s)"%(d,i,v,q)

            #svals.append(s.replace('None','NULL'))

                #db_out.Query(qi % (ntable,','.join(svals)))        


def insert_into_new_table(db_out, ntable, data_all):
    ###########################################################################    
    # Inserting into database
    
    db_out.setLogLevel('INFO')
    array = 'array' in ntable
    
    if array:
        qi = 'insert into %s (`data_time`,`att_conf_id`,`value_r`,`quality`'
        qi = qi % ntable
        if ntable.endswith('_rw'):
            qi += ',`idx`,`dim_x_r`,`dim_y_r`,`dim_x_w`,`dim_y_w`) VALUES ' #%s'
            qi += "(%s,%s,%s,%s,%s,%s,%s,0,0)" #%s,%s)'
            
        else:
            qi += ',`idx`,`dim_x_r`,`dim_y_r`) VALUES ' #%s'
            qi += "(%s,%s,%s,%s,%s,%s,%s)"

    else:
        qi += ") VALUES (%s,%s,%s,%s)" #%s'
        
    db_out.info('Inserting %d values into %s' % (len(data_all), ntable))
    while len(data_all):
        #printout every 500 bunches
        bunch_size = 200
        db_out.info('Inserting values into %s (%d pending)' 
                    % (ntable, len(data_all)))

        for j in range(500):
            if len(data_all):
                vals = [] #data_all.pop(0) for i in range(bunch_size) if len(data_all)]
                for i in range(bunch_size):
                    if len(data_all):
                        v = data_all.pop(0)
                        vals.append(v)

                if db_out.db.__module__ == 'mysql.connector.connection':
                    cursor = db_out.db.cursor(prepared=True)
                else:
                    cursor = db_out.getCursor()

                cursor.executemany(qi,vals)
                db_out.db.commit()
                cursor.close()

    return

def compare_databases(dbr,dbd=None,verbose=True,tables=None):
    """
    this method will check for the overlap between databases
    it  will compare the beginning of dbr (newer) against the end of dbd (older)
    if dbd is not specified, then it just analyzes the begin and end of dbr
    """
    dbd = dbd or dbr
    tables = fn.toList(tables or dbr.get_data_tables())
    sizes,attrs,limits,lasts,lastsize = {},{},{},{},{}

    for t in sorted(tables):
        sizes[t] = dbr.getTableSize(t)/1e9,dbd.getTableSize(t)/1e9
        limits[t] = dbr.get_table_timestamp(t,method='min'),dbd.get_table_timestamp(t,method='max')
        attrs[t] = dbr.get_attributes_by_table(t),dbd.get_attributes_by_table(t)
        try:
            p0 = fn.toList(dbr.get_partitions_at_dates(t,fn.time2str(
                limits[t][0][0])))[0]
        except:
            p0 = dbr.get_last_partition(t)
            
        lasts[t] = p0,dbd.get_last_partition(t)
        lastsize[t] = (lasts[t][0] and dbr.getPartitionSize(t,lasts[t][0])/1e9,
                lasts[t][1] and dbd.getPartitionSize(t,lasts[t][1])/1e9)
        """
        (t,dbr.get_table_timestamp(t,method='min'),dbr.getTablePartitions(t) and dbr.getPartitionSize(t,dbr.get_last_partition(t))/1e9,dbd.get_table_timestamp(t,method='max'),db
        d.getTablePartitions(t) and dbd.getPartitionSize(t,dbd.get_last_partition(t))/1e9) for t in dbr.get_data_tables()]
        """
        lasts[t] = dbr.get_last_partition(t),dbd.get_last_partition(t)
        
    if verbose:
        print('%6.4fG'%(dbr.getDbSize()/1e9) + 'vs %6.4fG'%(dbd.getDbSize()/1e9) if dbd is not dbr else '')
        xx = lambda x: (fn.isNumber(x) and '%6.4f'%float(x) or 
                    fn.isSequence(x) and str(len(x)) or
                    str(x))
        jj = lambda a,b: ('%s vs %s' % (xx(a),xx(b)) 
                      if xx(a)!=xx(b) or dbd is not dbr else xx(a))
        print('\t'.join('table file_sizes n_attrs t0_min t1_max plast0 plast1 psize0 psize1'.split()))
        
    for s,t in reversed(sorted((v,k) for k,v in sizes.items())):
        if verbose and limits[t][0][0] is not None:
            print('\t'.join(map(str,(t,
                #sizes[t][0],limits[t][0][1],lasts[t][0],lastsize[t][0],
                #sizes[t][1],limits[t][1][1],lasts[t][1],lastsize[t][1],
                jj(sizes[t][0],sizes[t][1]),jj(attrs[t][0],attrs[t][1]),
                jj(limits[t][0][1],limits[t][1][1]),
                jj(lasts[t][0],lasts[t][1]),jj(lastsize[t][0],lastsize[t][1]),
                ))))
    return {'dbs':('%s@%s'%(dbr.db_name,dbr.host),'%s@%s'%(dbd.db_name,dbd.host)),
            'sizes':sizes,'lasts':lasts,'lastsize':lastsize}
            

def copy_between_tables(api, table, source, start, stop, step = 86400):
    
    t0 = fn.now()
    
    if fn.isString(api):
        api = pta.api(api)
        
    if fn.isString(start):
        date0,date1 = start,stop
        start,stop = fn.str2time(start),fn.str2time(stop)
    else:
        date0,date1 = fn.time2str(start),fn.time2str(stop)        

    int_time = 'int_time' in api.getTableCols(table)
    q = 'insert into %s (`data_time`,`att_conf_id`,`value_r`,`quality`) ' % table
    q += 'SELECT data_time,att_conf_id,value_r,quality from %s ' % source
    
    for i in range(int(start),int(stop),86400):
        end = min((stop,i+86400))
        if int_time:
            where = 'where int_time between %d and %d order by int_time' % (i,end)
        else:
            where = 'where data_time between "%s" and "%s" order by data_time' % (
                fn.time2str(i),fn.time2str(end))
        print(q+where)
        api.Query(q+where)
        
    print(fn.now()-t0,'seconds')
    return
    

# def decimate_partition_by_modtime(api, table, partition, period = 3,
#                        min_count = 30*86400/3,
#                        check = True,
#                        start = 0, stop = 0):
#     """
#     This method uses (data_time|int_time)%period to delete all values with
#     module >= 1 only if the remaining data will be bigger than min_count.
#
#     This is as destructive and unchecked method of decimation as
#     it is to do a fixed polling; so it is usable only when data length to be kept
#     is bigger than (seconds*days/period)
#
#     A better method would be to use GROUP BY data_time DIV period; inserting
#     the data in another table, then reinserting and repartitioning. But the cost
#     in disk and time of that operation would be much bigger.
#     """
#     t0 = fn.now()
#     api = pta.api(api) if fn.isString(api) else api
#     print('%s: decimate_partition(%s, %s, %s, %s, %s), current size is %sG' % (
#         fn.time2str(), api, table, partition, period, min_count,
#         api.getPartitionSize(table, partition)/1e9))
#
#     col = 'int_time' if 'int_time' in api.getTableCols(table) else (
#             'CAST(UNIX_TIMESTAMP(data_time) AS INT)' )
#     api.Query('drop table if exists tmpdata')
#
#     api.Query("create temporary table tmpdata (attid int(10), rcount int(20));")
#     q = ("insert into tmpdata select att_conf_id, count(*) as COUNT "
#         "from %s partition(%s) " % (table,partition))
#     q += " where "+col + "%" + str(period) + " = 0 "
#     if start and stop:
#         q += " and %s between %s and %s " % (col, start, stop)
#     q += "group by att_conf_id order by COUNT;"
#     print(q)
#     api.Query(q)
#
#     ids = api.Query("select attid, rcount from tmpdata where rcount > %s order by rcount"
#                     % min_count)
#     print(ids)
#     print('%s: %d attributes have more than %d values'
#           % (fn.time2str(), len(ids), min_count))
#     if not len(ids):
#         return ids
#
#     mx = ids[-1][0]
#     print(mx)
#     try:
#         if ids:
#             print('max: %s(%s) has %d values' % (fn.tango.get_normal_name(
#                 api.get_attribute_by_ID(mx)),mx,ids[-1][1]))
#     except:
#         traceback.print_exc()
#
#     ids = ','.join(str(i[0]) for i in ids)
#     q = ("delete from %s partition(%s) " % (table,partition) +
#         "where att_conf_id in ( %s ) " % ids )
#     if start and stop:
#         q += " and %s between %s and %s " % (col, start, stop)
#     q += "and " + col + "%" + str(period) + " > 0;"
#     print(q)
#     api.Query(q)
#     print(fn.time2str() + ': values deleted, now repairing')
#
#     api.Query("alter table %s optimize partition %s" % (table, partition))
#     nc = api.getPartitionSize(table, partition)
#     print(type(nc),nc)
#     print(fn.time2str() + ': repair done, new size is %sG' % (nc/1e9))
#
#     q = "select count(*) from %s partition(%s) " % (table,partition)
#     q += " where att_conf_id = %s " % mx
#     if start and stop:
#         q += " and %s between %s and %s " % (col, start, stop)
#     nc = api.Query(q)[0][0]
#     print('%s: %s data reduced to %s' % (fn.time2str(),mx,nc))
#
#     api.Query('drop table if exists tmpdata')
#
#     return ids.split(',')


def alter_data_time(api, precision=3, do_it=True):
    r = []
    if fn.isString(api): api = pta.api(api)
    for t in api.get_data_tables():
        for f in ('data_time','recv_time','insert_time'):
            q = 'ALTER TABLE %s MODIFY %s DATETIME(%d);' % (t,f,precision)
            r.append(q)
            if do_it:
                api.Query(q)
    return r


def add_int_time_column(api, table, do_it=True):
    # Only prefixed tables will be modified
    if fn.isString(api): api = pta.api(api)
    pref = pta.hdbpp.query.partition_prefixes.get(table,None)
    r = []
    if not pref:
        print('table %s not in partition_prefixes list' % table)
        return 

    if 'int_time' not in api.getTableCols(table):
        q = ('alter table %s add column int_time INT generated always as '
                '(TO_SECONDS(data_time)-62167222800) PERSISTENT;' % table)
        print(q)
        if do_it: 
            api.Query(q)
        r.append(q)

    if not any('int_time' in idx for idx in api.getTableIndex(table).values()):
        q = 'drop index att_conf_id_data_time on %s;' % table
        print(q)
        if do_it: 
            api.Query(q)
        r.append(q)
        q = ('create index i%s on %s(att_conf_id, int_time);' % (pref,table))
        print(q)
        if do_it: 
            api.Query(q)
        r.append(q)
        
    # array index
    if 'array' in table:
        add_idx_index(api, table, do_it=do_it) #This method already checks if exists        
        
    return '\n'.join(r)

def add_idx_index(api, table, do_it=True):
    try:
        if fn.isString(api): api = pta.api(api)
        if not 'idx' in api.getTableCols(table):
            return 
        if any('idx' in ix for ix in api.getTableIndex(table).values()):
            return 
        pref = pta.hdbpp.query.partition_prefixes.get(table,None)
        if not pref:
            return
        it = 'int_time' if 'int_time' in api.getTableCols(table) else 'data_time'
        #q = ('create index ii%s on %s(att_conf_id, idx, %s)' % (pref,table,it))
        # old index (aid/time) should go first!
        q = ('create index ii%s on %s(att_conf_id, idx, %s);' % (pref,table,it))
        print(api.db_name,q)
        if do_it: 
            api.Query(q)
        return q
    except:
        traceback.print_exc()
    
from PyTangoArchiving.hdbpp.query import MIN_FILE_SIZE

def get_db_last_values_per_table(api, tables = None):
    db = pta.api(api) if fn.isString(api) else api
    tables = dict()
    for t in sorted(db.getTables()):
        if 'data_time' not in db.getTableCols(t):
            continue
        last = get_last_value_in_table(api,t)
        tables[t] = last
    return tables

def get_last_value_in_table(api, table, method='max', 
                            ignore_errors = False,
                            trace = False): #, tref = -180*86400):
    """
    DEPRECATED, USE API.get_table_timestamp instead

    Returns a tuple containing:
    the last value stored in the given table, in epoch and date format
    """
    if fn.isString(api): api = pta.api(api)
    return api.get_table_timestamp(table, method, ignore_errors=ignore_errors)

    # t0,last,size = fn.now(),0,0
    # db = pta.api(api) if fn.isString(api) else api
    # #print('get_last_value_in_table(%s, %s)' % (db.db_name, table))
    #
    # int_time = any('int_time' in v for v in db.getTableIndex(table).values())
    #
    # # If using UNIX_TIMESTAMP THE INDEXING FAILS!!
    # field = 'int_time' if int_time else 'data_time'
    # q = 'select %s(%s) from %s ' % (method,field,table)
    #
    # size = db.getTableSize(table)
    # ids = db.get_attributes_by_table(table,as_id=True)
    # r = []
    #
    # for i in ids:
    #     qi = q+' where att_conf_id=%d' % i
    #     #if tref and int_time: where += ('int_time <= %d'% (tref))
    #     rr = db.Query(qi)
    #     if trace:
    #         print('%s[%s]:%s' % (table,i,rr))
    #     r.extend(rr)
    #
    # method = {'max':max,'min':min}[method]
    # r = [db.mysqlsecs2time(l[0]) if int_time else fn.date2time(l[0])
    #      for l in r if l[0] not in (0,None)]
    # r = [l for l in r if l if (ignore_errors or 1e9<l<fn.now())]
    #
    # if len(r):
    #     last = method(r) if len(r) else 0
    #     date = fn.time2str(last)
    # else:
    #     db.warning('No values in %s' % table)
    #     last, date = None, ''
    #
    # return (last, date, size, fn.now() - t0)    t0,last,size = fn.now(),0,0
    # db = pta.api(api) if fn.isString(api) else api
    # #print('get_last_value_in_table(%s, %s)' % (db.db_name, table))
    #
    # int_time = any('int_time' in v for v in db.getTableIndex(table).values())
    #
    # # If using UNIX_TIMESTAMP THE INDEXING FAILS!!
    # field = 'int_time' if int_time else 'data_time'
    # q = 'select %s(%s) from %s ' % (method,field,table)
    #
    # size = db.getTableSize(table)
    # ids = db.get_attributes_by_table(table,as_id=True)
    # r = []
    #
    # for i in ids:
    #     qi = q+' where att_conf_id=%d' % i
    #     #if tref and int_time: where += ('int_time <= %d'% (tref))
    #     rr = db.Query(qi)
    #     if trace:
    #         print('%s[%s]:%s' % (table,i,rr))
    #     r.extend(rr)
    #
    # method = {'max':max,'min':min}[method]
    # r = [db.mysqlsecs2time(l[0]) if int_time else fn.date2time(l[0])
    #      for l in r if l[0] not in (0,None)]
    # r = [l for l in r if l if (ignore_errors or 1e9<l<fn.now())]
    #
    # if len(r):
    #     last = method(r) if len(r) else 0
    #     date = fn.time2str(last)
    # else:
    #     db.warning('No values in %s' % table)
    #     last, date = None, ''
    #
    # return (last, date, size, fn.now() - t0)

def get_first_value_in_table(api, table, ignore_errors=False):
    """
    DEPRECATED, USE API.get_table_timestamp instead
    """
    if fn.isString(api): api = pta.api(api)
    return get_last_value_in_table(api, table, method='min',ignore_errors=ignore_errors)

def delete_att_parameter_entries(api,timestamp=None):
    """
    att_parameter table tends to grow and slow down startup of archivers
    """
    api = pta.api(api) if fn.isString(api) else api
    timestamp = timestamp or fn.now()-3*30*86400
    api.Query("delete from att_parameter where insert_time < '%s'" 
              % fn.time2str(timestamp))
    api.Query("optimize table att_parameter")
    return api.getTableSize('att_parameter')

def delete_data_older_than(api, table, timestamp, doit=False, force=False):
    if fn.isString(api): api = pta.api(api)
    delete_data_out_of_time(api, table, timestamp, fn.END_OF_TIME, doit, force)

def delete_data_out_of_time(api, table, tstart=1e9, tstop=None, doit=False, force=False):
    if fn.isString(api): api = pta.api(api)
    if not doit:
        print('doit=False, nothing to be executed')
    if 'archiving04' in api.host and not force:
        raise Exception('deleting on archiving04 is not allowed'
            ' (unless forced)')

    timestamp = fn.str2time(tstart) if fn.isString(tstart) else tstart
    tstop = fn.str2time(tstop) if fn.isString(tstop) else fn.notNone(tstop,fn.now()+86400)
    query = lambda q: (api.Query(q) if doit else fn.printf(q))
    
    try:
        lg = api.getLogLevel()
        api.setLogLevel('DEBUG')
        partitions = sorted(api.getTablePartitions(table))
        for p in partitions[:]:
            t = api.get_partition_time_by_name(p)
            if t < timestamp:
                query('alter table %s drop partition %s' 
                        % (table, p))
                partitions.remove(p)
            
        cols = api.getTableCols(table)
        col = (c for c in ('int_time','data_time','time') if c in cols).__next__()
        if col != 'int_time':
            timestamp,tstop = "'%s'" % timestamp, "'%s'" % tstop
        q = 'delete from %s where %s < %s' % (table, col, timestamp)

        if tstop != fn.END_OF_TIME:
            q += " and %s < %s " % (col, tstop)
        query(q)

        if partitions:
            p = partitions[-1]
            query('alter table %s repair partition %s' % (table,p))
            query('alter table %s optimize partition %s' % (table,p))
        else:
            query('repair table %s' % table)
            query('optimize table %s' % table)
            
    finally:
        api.setLogLevel(lg)

def create_db_partitions(api, max_parts, stop_date, start_date = None, 
        do_it = False, test = False, force = True, int_time = True,
        tables = None,
        bigs = ['att_array_devdouble_ro', 'att_scalar_devdouble_ro']):
    """
    nmonths, maximum number of partitions to create
    stop_date, date of last partition
    
    do_it: if not True, nothing is executed
    test: if not True, queries to be done are printed out
    force: if True, partitions will be created even if the table is small (needed for new DBs)
    int_time: it creates and int_time column and index
    """
    if fn.isString(api): api = pta.api(api)
    tables = tables or pta.hdbpp.partition_prefixes.keys()
    for t in sorted(tables):
        try:
            parts = api.getTablePartitions(t) or []
            s = api.getTableSize(t)/1e9
            print('')
            print('%s size is %sG' % (t,s))
            print('%s last partitions: %s' % (t,parts[-3:]))
            
            if not force and (not parts or len(parts)==1):
                if s>15:
                    print('%s is not partitioned ... and it should!' % t)
                continue
            
            last = api.get_last_partition(t,tref=fn.now())
            if last and 'last' in last:
                print('%s last partition is under use! manual maintenance required!' % t)
                continue
                
            if s > 100 or t in bigs:
                print('%s is huge, %sG! 2 parts/month will be created' % (t,s))
                n = 2
            elif s < 1 and not force:
                if last is not None:
                    n = 0 #not adding new partitions, but at least adding _last
                else:
                    print('%s is too small, %sG, to be partitioned!' % (t,s))
                    continue
            else:
                n = 1
                
            if 'TO_DAYS' in api.getTableCreator(t):
                print('%s already partitioned by data_time' % t)
                int_time = False
            elif int_time:
                r = add_int_time_column(api, t, do_it=do_it)
                api.getTables(load=True)
                if not do_it and not test:
                    print(r)

            if len(parts)<2 or (api.get_partition_time_by_name(parts[-2]) < 
                        fn.str2time(stop_date)-20*86400):
                print('%s will be partitioned' % t)
                if do_it:
                    create_new_partitions(api,t,n*max_parts,partpermonth=n,
                        stop_date=stop_date,start_date=start_date,
                        int_time=int_time,do_it=True)
                elif not test:
                    print(create_new_partitions(api,t,n*max_parts,partpermonth=n,
                        stop_date=stop_date,start_date=start_date,
                        int_time=int_time))

        except Exception as e:
            traceback.print_exc()
            if test or do_it:
                raise e
    return

def create_new_partitions(api,table,nmonths,partpermonth=1,
        start_date=None,stop_date=None, int_time=False,
        add_last=True,do_it=False):
    """
    This script will create new partitions for nmonths*partpermonth
    for the given table and key
    partpermonth should be 1, 2 or 3
    start/stop dates must be strings
    start_date better to not be used, may fail
    """
    if fn.isString(api): 
        api = pta.api(api)
    if partpermonth > 3: 
        raise Exception('max partpermonth = 3')

    npartitions = nmonths*partpermonth
    tables = pta.hdbpp.query.partition_prefixes
    t = table
    pref = tables.get(t,None)
    if not pref:
        print('table %s will not be partitioned' % t)
        return []
    intcol = 'int_time'

    if 'TO_DAYS' in api.getTableCreator(table).lower():
        # already partitioned by data_time
        int_time = False
    else:
        int_time = int_time or intcol in api.getTableCols(table)
    eparts = sorted(api.getTablePartitions(t))

    if not start_date:
        nparts = [p for p in eparts if '_last' not in p]
        last = (api.get_partition_time_by_name(nparts[-1]) 
            if nparts else fn.now())
        nxt = fn.time2date(last)
        if nxt.month == 12:
            nxt = fn.str2time('%s-%s-%s' % (nxt.year+1,'01','01'))
        else:
            nxt = fn.str2time('%s-%s-%s' % (nxt.year,nxt.month+1,'01'))
        start_date = fn.time2str(nxt).split()[0]

    def inc_months(date,count):
        y,m,d = map(int,date.split('-'))
        m = m+count
        r = m%12
        if r:
            y += int(m/12)
            m = m%12
        else:
            y += int(m/12)-1
            m = 12
        return '%04d-%02d-%02d'%(y,m,d)
        
    if int_time:
        head = "ALTER TABLE %s "
        comm = "PARTITION BY RANGE(int_time) ("
        line = "PARTITION %s%s VALUES LESS THAN (TO_SECONDS('%s')-62167222800)"
    else:
        head = "ALTER TABLE %s "
        comm = "PARTITION BY RANGE(TO_DAYS(data_time)) ("
        line = "PARTITION %s%s VALUES LESS THAN (TO_DAYS('%s'))"

    lines = []

    if do_it and int_time and (api is None or not intcol in api.getTableCols(t)):
        print(int_time,api is None,intcol,api.getTableCols(t))
        raise Exception('%s.%s column do not exist!' % (t,intcol))
        #lines.append(newc%t)
        #lines.append(newi%(t,pref,t))

    lines.append(head%t)
    if not any(eparts):
        lines.append(comm)
    elif pref+'_last' in eparts and npartitions>0:
        lines.append('REORGANIZE PARTITION %s INTO (' % (pref+'_last'))
    else:
        lines.append('ADD PARTITION (')
    
    counter = 0
    #print(start_date,stop_date,nmonths)
    for i in range(0,nmonths):
        date = inc_months(start_date,i)
        end = inc_months(date,1)
        pp = pref+date.replace('-','') #prefix+date
        
        if not partpermonth:
            continue
        
        elif partpermonth == 1:
            dates = [(date,end)]
            
        elif partpermonth == 2:
            dates = [(date, date.rsplit('-',1)[0]+'-16'),
                     (date.rsplit('-',1)[0]+'-16', end)]
            
        elif partpermonth == 3:
            dates = [(date, date.rsplit('-',1)[0]+'-11'),
                (date.rsplit('-',1)[0]+'-11', date.rsplit('-',1)[0]+'-21'),
                (date.rsplit('-',1)[0]+'-21', end)]
        #print(dates)
            
        for jdate,jend in dates:
            jdate = jdate.replace('-','')
            pname = (pref+jdate)
            if not stop_date or api.get_partition_time_by_name(pname)<fn.str2time(stop_date):
                l = line%(pref,jdate,jend)
                if counter<(npartitions-1):
                    l+=','
                if not eparts or '_last' in eparts[0] or (
                        pname not in eparts and not pname < eparts[0]):
                    lines.append(l)
                counter+=1
                #print(l)

    if add_last and pref+'_last' not in eparts or 'REORGANIZE' in str(lines):
        if not lines[-1][-1] in ('(',','):
            lines[-1] += ','
        lines.append('PARTITION %s_last VALUES LESS THAN (MAXVALUE)'%pref)
    
    lines.append(');\n\n') 
    r = '\n'.join(lines)
    if do_it and (counter or ('last' in r)):
        print('Executing query .... %s' % r)
        api.Query(r)
    
    return r

def get_archiving_loads(schema,maxload=250):
    r = fn.Struct()
    if isinstance(schema,pta.hdbpp.HDBpp):
        api,r.schema = schema,schema.db_name
    else:
        api,r.schema = pta.api(schema),schema
    r.attrs = api.get_attributes()
    r.subs = api.get_subscribers()
    r.pers = api.get_periodic_archivers()
    r.evsubs = [d for d in api.get_subscribers() if 'null' not in d]
    r.nulls = [d for d in r.subs if 'null' in d]
    r.subsloads = dict((d,api.get_archiver_attributes(d)) for d in r.subs)
    r.subserrors = dict((d,api.get_archiver_errors(d)) for d in r.evsubs) 
    r.persloads = dict((d,api.get_periodic_archiver_attributes(d)) for d in r.pers)
    r.perserrors = dict((d,api.get_periodic_archiver_errors(d)) for d in r.pers)
    r.perattrs = api.get_periodic_attributes()
    r.pernoevs = [a for a in r.perattrs if not fn.tango.check_attribute_events(a)]
    r.perevs = [a for a in r.perattrs if a not in r.pernoevs]
    r.attrlists = dict((d,fn.get_device_property(d,'AttributeList'))
                                   for d in r.subs)
    r.perlists = dict((d,fn.get_device_property(d,'AttributeList'))
                                   for d in r.pers)
    r.subattrs = [a.split(';')[0] for v in r.attrlists.values() for a in v]
    r.evattrs = [a.split(';')[0] for v in r.subattrs if v not in r.pernoevs]
    r.miss = [a for a in r.attrs if a not in r.subattrs]
    r.dubs = len(r.subattrs)-len(list(set(r.subattrs)))
    r.both = r.perevs
    print('%d attributes in %s schema' % (len(r.attrs),schema))
    dbsize = api.getDbSize()
    print('DbSize: %f' % (dbsize/1e9))
    tspan = api.get_timespan()
    print('%s - %s ; %2.1f G/day' % (fn.time2str(tspan[0]),fn.time2str(tspan[1]),
        (dbsize/1e9)/((tspan[1]-tspan[0])/86400)))
    print('%d repeated attributes in archiver lists' % r.dubs)
    print('%d not on any archiver' % len(r.miss))
    print('%d on event archiving' % len(r.evattrs))
    print('%d on periodic archiving' % len(r.perattrs))
    print('%d(%d) have both' % (len(r.perattrs)-len(r.pernoevs),len(r.both)))
    print('')
    for k,v in sorted(r.subsloads.items()):
        print('%s: %d (%d errors)' % (k,len(v),len(r.subserrors.get(k,[]))))
    for k,v in sorted(r.persloads.items()):
        print('%s: %d (%d errors)' % (k,len(v),len(r.perserrors.get(k,[]))))
    return r
        
    

def redistribute_loads(schema,maxload=300,subscribers=True,periodics=True,
                       do_it=True):
    """
    It moves periodic attributes to a /null subscriber
    Then tries to balance load between archivers
    """
    if isinstance(schema,pta.hdbpp.HDBpp):
        api,schema = schema,schema.db_name
    else:
        api,schema = pta.api(schema),schema
    subs = api.get_subscribers()
    nulls = [d for d in subs if 'null' in d]
    if not nulls:
        api.add_event_subscriber('hdb++es-srv/%s-null'%api.db_name,
                                 'archiving/%s/null'%api.db_name)
    r = get_archiving_loads(schema)
    
    #subsloads = dict((d,api.get_archiver_attributes(d)) for d in subs)
    #pers = api.get_periodic_archivers()
    #persloads = dict((d,api.get_periodic_archiver_attributes(d)) for d in pers)
    #perattrs = api.get_periodic_attributes()
    #pernoevs = [a for a in perattrs if not fn.tango.check_attribute_events(a)]
    #subattrs = [a for a in api.get_attributes() if a not in perattrs]
    #attrlists = sorted(set(fn.join(fn.get_device_property(d,'AttributeList') 
                                   #for d in subs)))
    #evsubs = [d for d in api.get_subscribers() if 'null' not in d]
    
    #print('%d attributes, %d subscribed, %d periodic, %d subscribers, %d pollers' % 
          #(len(attrlists),len(subattrs),len(perattrs),len(evsubs),len(pers)))
    #print('Current loads')
    #print([(k,len(v)) for k,v in subsloads.items()])


    sublist = []
    # get generic archivers only
    for d in r.subs:
        if fn.clmatch('*([0-9]|null)$',d):
            sublist.extend(fn.get_device_property(d,'AttributeList'))
        
    nulllist = [a for a in sublist if a.split(';')[0] in r.pernoevs]
    sublist = [a for a in sublist if a.split(';')[0] not in r.pernoevs]
    
    if subscribers:
        print('Moving %d periodics to /null' % len(nulllist))
        if do_it:
            fn.tango.put_device_property('archiving/%s/null'%api.db_name,
                'AttributeList',nulllist)
        
        evsubs = [d for d in r.subs if fn.clmatch('*[0-9]$',d)]
        avgload = 1+len(sublist)/(len(evsubs))
        print('Subscriber load = %d' % avgload)
        if avgload>maxload:
            raise Exception('Load too high!, create archivers!')
        
        for i,d in enumerate(evsubs):
            attrs = sublist[i*avgload:(i+1)*avgload]
            print(d,len(attrs))
            if do_it:
                fn.tango.put_device_property(d,'AttributeList',attrs)
    
    r.nulllist = nulllist
    r.sublist = sublist
    
    if periodics:
        sublist = []
        for d in r.pers:
            sublist.extend(fn.get_device_property(d,'AttributeList'))        
        avgload = 1+len(sublist)/(len(r.pers))
        print('Periodic archiver load = %d' % avgload)
        if avgload>maxload:
            raise Exception('Load too high!, create archivers!')
        
        for i,d in enumerate(r.pers):
            attrs = sublist[i*avgload:(i+1)*avgload]
            print(d,len(attrs))
            if do_it:
                fn.tango.put_device_property(d,'AttributeList',attrs)        
    
    if not do_it:
        print('It was just a dry run, nothing done')
    return r

def rename_hdbpp_attributes(old_names, new_names, do_it=False, remove=False):
    """
    This method replaces [old_names] by [new_names] in DB and archiving devices
    
    if do_it = False (default), it is a dry-run with no real changes
    
    if remove = True, the attribute is renamed in DB and not reassigned to any archiver   
    """
    olds = [fn.tango.get_simple_name(a) for a in old_names]
    if not remove:
        for a in new_names:
            try:
                fn.tango.PyTango.AttributeProxy(a).read()
            except Exception as e:
                print('%s is not readable' % a)
                raise e
        
    # new is FQDN, while old is NOT, to maximize matching
    names = dict((fn.tango.get_full_name(n,fqdn=True),o)
                     for n,o in zip(new_names,old_names))
    dones = []
        
    # It is done iterating through DB's instead of attributes
    # to summarize device changes/restarts as much as possible.
    for schema in pta.get_hdbpp_databases(active=False):
        db = pta.api(schema)
        in_db = []
        
        for new,old in sorted(names.items()):
            
            # first, find archived devices
            #arch = [a for a in names.values() if db.is_attribute_archived(a)]
            #arch = db.is_attribute_archived(old)
            #if not arch:
                ##print('%s not archived by %s' %  (old,schema))
                #continue            
            
            old = fn.tango.get_full_name(old,fqdn=True)
            if not db.is_attribute_archived(old, active=False):
                #print('%s is not archived!, skipping' % old)
                continue
            if db.is_attribute_archived(new, active=False):
                print('%s is already archived!, skipping' % new)
                continue
            
            print('rename_hdbpp_attributes(%s,%s,%s,%s)' % (old,new,schema,do_it))
            
            # then, update the database
            aid = db.get_attribute_ID(old)
            names[new] = db.Query('select att_name from att_conf where '
                'att_conf_id = %d' % aid)[0][0]
            in_db.append(new)
            
            print('Updating %s: %s => %s' % (db,old,new))
            facility, domain, family, member, name = new.rsplit('/',4)
            q = "update att_conf set att_name = '%s' "\
                ", facility = '%s'" \
                ", domain = '%s'" \
                ", family = '%s'" \
                ", member = '%s'" \
                ", name = '%s'" \
                " where att_conf_id = %d" % (
                new,facility,domain,family,member,name,aid)
            print(q)
            if do_it:
                db.Query(q)
        
        # third, find archivers on charge
        devs = fn.find_devices('archiving/%s/*' % db.schema)
        attrlists = dict((d,fn.get_device_property(d,'AttributeList')) for d in devs)
        devs = [d for d,v in attrlists.items() 
                if any(a.lower() in str(v).lower() for a in old_names)]

        # update attributelists
        in_dev = []
        for d in devs:
            newattrs = []
            for i,l in enumerate(attrlists[d]):
                match = fn.first(
                    ((new,old) for (new,old) in names.items() 
                     if fn.clsearch('(^|/)'+fn.tango.get_simple_name(old) + '[;$]',l)), #requires old to be simple_name
                    default=None)               

                if not match:
                    ln = l
                elif remove:
                    print('Updating %s: Stop %s archiving' % (d,old))
                    ln = ''
                    in_dev.append(old)
                else:
                    new,old = match
                    old = fn.tango.get_fqdn_name(old)
                    ln = fn.clsub(old, new, l)
                    print('Updating %s: %s => %s' % (d,l,ln))
                    dones.append(new)
                    in_dev.append(old)
                if ln:
                    newattrs.append(ln)
                        
            if do_it:
                fn.put_device_property(d,'AttributeList',newattrs)

        if (in_db or in_dev) and do_it and len(devs):
            print('Restarting %s %s servers' % (schema,len(devs)))
            astor = fn.Astor(devs_list=devs)
            astor.stop_servers()
            fn.wait(3 * 3.)
            astor.start_servers()
            
            if not remove:
                print('Restarting %s %s attributes archiving' % (schema,len(in_db)))
                db.restart_attributes(in_db)
                        
    print('\nrename %d attributes: done = %s' % (len(dones),do_it))

    
def repair_attribute_type(api, attribute, do_it=False):
    tt = pta.utils.get_attribute_type_table(attribute)
    curr = api.get_table_name(attribute)
    print('repair_attribute(%s,%s,do_it=%s): %s => %s' % (
        api.db_name,attribute,do_it,curr,tt))

    aid = api.get_attr_id_type_table(attribute)
    tid = api.get_data_types()[tt.replace('att_','')]
    q = ('update att_conf set att_conf_data_type_id = %s '
        'where att_conf_id = %s' % (tid, aid[0]))
    print(q)
    if do_it:
        api.Query(q)
    return do_it


"""
cd $FOLDER
FILENAME=$SCHEMA.full.$(date +%F).dmp

echo "$(fandango time2str) Dump to $FOLDER/$FILENAME..."
mysqldump --single-transaction --force --compact --no-create-db --skip-lock-tables --quick -u manager -p $SCHEMA > $FILENAME
echo "$(fandango time2str) Compressing $FOLDER/$FILENAME"
tar zcvf $FILENAME.tgz $FILENAME
echo "$(fandango time2str) Removing $FOLDER/$FILENAME"
rm $FILENAME

"""


def main_partitioning_check(*args,**opts):
    schema = args[0]
    api = pta.api(schema)
    tables = [a for a in api.getTables() if fn.clmatch('att_(scalar|array)_',a)]
    descriptions = dict((t,api.getTableCreator(t)) for t in tables)
    partitioned = [t for t,v in descriptions.items() if 'partition' in str(v).lower()]
    print('%s: partitioned tables: %d/%d' % (schema,len(partitioned),len(tables)))
    
if __name__ == '__main__' :
    print(fn.call(locals_=locals()))
    #arg0 = fn.getitem(sys.argv,1,'help') 
    #if arg0 in 'help' or arg0 in locals():
        #r = fn.call(locals_=locals())
        #print(r)
    #else:
        #args,opts = fn.linos.sysargs_to_dict(split=True)
        #main_partitioning_check(*args,**opts)
    
