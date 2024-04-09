#!/usr/bin/env python

import sys, pickle, os, re, traceback
import PyTangoArchiving as pta
import fandango as fn
from fandango.functional import *

__doc__ = USAGE = """
Usage:
    check_archiving_schema schema [period=] [ti=] [values=] [--export]
    
    or
    
    check_archiving_schema schema [action=start_devices]
    
    or just save to pickle file
    
    check_archiving_schema schema action=save filename=/tmp/schema.pck

"""

def check_table_stats(api, tables=None, n=100, stop = 0, period = 90*86400):
    """ 
    Usage:
    stats = check_table_stats(pta.api('hdbvc'))
    In [44]: sorted([(v.querytime,k,api.get_last_partition(k),api.getPartitionSize(k,api.get_last_partition(k))/1e9) for k,v in stats.items()])[-10:]
    Out[44]: 
    [(0.838482141494751, 'att_scalar_devboolean_rw', 'sbw20220201', 0.00661082),
    (3.4906461238861084, 'att_scalar_devboolean_ro', 'sbr20220201', 0.155190924),
    (4.710180044174194, 'att_scalar_devshort_rw', 'shw20220201', 0.225972352),
    (8.115447044372559, 'att_array_devdouble_ro', 'adr20220201', 34.397814775),
    (11.272470951080322, 'att_scalar_devlong_ro', 'slr20220201', 1.345685536),
    (12.805779933929443, 'att_scalar_devshort_ro', 'shr20220201', 0.951104612),
    (15.820309162139893, 'att_scalar_devstate_ro', 'str20220201', 0.62807808),
    (18.66020393371582, 'att_array_devboolean_ro', 'abr20220201', 0.358075216),
    (21.042890071868896, 'att_array_devstring_ro', 'asr20220201', 1.028261416),
    (99.29140996932983, 'att_scalar_devdouble_ro', 'sdr20220201', 11.82627616)] <<<< wtf!!
    """
    stats = {}
    tables = fn.toList(tables or api.get_data_tables())
    for t in tables:
        t0 = fn.now()
        stats[t] = fn.Struct()
        stats[t].attrs = api.get_attributes_by_table(t)
        stats[t].failed = {}
        stats[t].vals = {}
        for a in stats[t].attrs:
            try:
                stats[t].vals[a] = api.get_last_attribute_values(
                                        a, n, epoch=stop, period=period)
            except Exception as e:
                stats[t].failed[a] = str(e)

        stats[t].rows = api.getTableRows(t)
        stats[t].size = api.getTableSize(t)
        stats[t].nattrs = len(stats[t].attrs)
        stats[t].rowsize = stats[t].rows and stats[t].size/stats[t].rows
        stats[t].rowsperattr = stats[t].nattrs and stats[t].rows/len(stats[t].attrs)
        stats[t].sizeperattr = stats[t].nattrs and stats[t].size/len(stats[t].attrs)
        stats[t].lasttime = stats[t].nattrs and max(api.attributes[a].last_date for a in stats[t].attrs)
        stats[t].querytime = fn.now()-t0
        
    return stats

def check_service(api, period=86400):
    print('Checking %s@%s database' % (api.db_name,api.host))
    attrs = api.get_attributes(active=False) #from_db
    devs = fn.defaultdict(list)
    [devs[a.rsplit('/',1)[0]].append(a) for a in attrs]
    print('%d attributes in total, read from %d devices' % (len(attrs), len(devs)))
    devsoff = [d for d in devs if not fn.check_device(d)]
    attrsoff = fn.join(devs[d] for d in devsoff)
    attrsup = [a for a in attrs if a not in attrsoff]
    print('%d devices are off with %d attributes, %d attrs are up' % (len(devsoff),len(attrsoff),len(attrsup)))
    subattrs = api.get_subscribed_attributes()
    perattrs = api.get_periodic_attributes()

    # disabled must be checked taking readability into account!
    disabled = [a for a in attrsup if not api.get_attribute_archiver(a)]
    bothattrs = [a for a in attrs if a in subattrs and a in perattrs]
    archattrsoff = [a for a in attrsoff if a in subattrs or a in perattrs]
    print('%d attrs subscribed, %d periodic, %d both, %d up and disabled, %s archived but off' % (
        len(subattrs), len(perattrs), len(bothattrs), len(disabled), len(archattrsoff)))
    evarch = api.get_subscribers()
    perarch = api.get_periodic_archivers()
    archoff = [d for d in api.dedicated if '/null' not in d and not fn.check_device(d)]
    attrarchoff = fn.join(api.dedicated[d] for d in archoff)
    hist = dict((d,fn.tango.get_property_history(d,'AttributeList')) for d in api.dedicated)
    print('%d subscribers, %d pollers, %d archivers are off: %s' % (
        len(evarch),len(perarch),len(archoff),archoff))
    removed = [a for a in disabled if a.lower() in str(hist).lower()]
    print('%d disabled attrs appear in property history' % len(removed))                                                   

    t0 = fn.now()
    reads = dict((a,fn.read_attribute(a)) for a in attrsup)  #get values per periodic archiver!
    reads = dict((k,v) for k,v in reads.items() if v is not None)
    noread = [k for k,v in reads.items() if v is None]
    print('%d/%d attributes read in %d seconds' % (len(reads),len(attrsup),fn.now()-t0)) #180s for hdbvc

    devfailed = [k for k,v in devs.items() if all(a in noread for a in v)]

    t0 = fn.now()
    tref = t0 - abs(period)
    vals = dict((a,api.get_last_attribute_values(a,n=1)) for a in reads) #get values per table! (also because arrays should be matched differently)

    #novals are attributes that have no data in period!! (but may have in the past)
    novals = [k for k,v in vals.items() if not v]
    
    """

    USE get_attr_timestamp to re-catalog those attributes as LOST!

    separate event_lost from periodic_lost

    evaluate accumulated read times per periodic archiver

    also event rates per subscribers

    """

    nones = [k for k,v in vals.items() if v and None in v and reads[k] is not None]
    tolist = lambda l: list(l) if fn.isSequence(l) else l
    lost = [k for k,v in vals.items() if v and v[0]<tref and tolist(v[1])!=tolist(reads[k])]
    stalled = [k for k,v in vals.items() if v and v[0]<tref and k not in lost]
    ok = [a for a in vals if a not in novals and a not in nones and a not in lost]
    print('%d are ok from %d attributes queried in %d seconds' % (len(ok),len(vals),fn.now()-t0)) #392s for hdbvc

    print('%d attrs have no values, %d archived None, %d are not updated, %d seem stalled' % 
        tuple(map(len,(novals,nones,lost,stalled))))

    # KNOWN ERRORS:
    # eps digital signals type mismatch 
    # tg_test / bakeout and other dummy devices
    # motors do update only when sardana is scanning ... they need periodic archive

    result = dict((k,v) for k,v in locals().items() if isinstance(v,(list,dict)))
    return result
    

def main(args=None):
    """
    see PyTangoArchiving.check.USAGE
    """
    try:
        import argparse
        parser = argparse.ArgumentParser() #usage=USAGE)
        parser.add_argument('schema')
        #parser.add_argument('--period',type=int)
        parser.add_argument('--tref',type=str,default='-43200',
            help = 'min epoch considered ok')
        parser.add_argument('--action',type=str,default='check',
            help = 'start(devices)|restart(servers)|save(values)|check(attributes)')
        parser.add_argument('--export',help = 'json|pickle',default='json')
        parser.add_argument('--values',type=str,
            help = 'values file, will be loaded by load_schema_values()')
        parser.add_argument('--restart',type=bool,
            help = 'if True, when doing a check, try to recover attributes')        
        
        try:
            args = dict(parser.parse_args().__dict__)
        except:
            sys.exit(-1)
        
        #if not args:
            #args = {}
            #assert sys.argv[2:]
            #args = fn.sysargs_to_dict(defaults=('schema','period','ti',
                #'values','action','folder'))
        #print(args)

        if args.get('action') == 'start':
            print('Call Start() for %s devices' % sys.argv[1])
            pta.api(args['schema']).start_devices(force=True)
            print('done')
            
        if args.get('action') == 'restart':
            print('Restart %s servers' % sys.argv[1])
            pta.api(args['schema']).start_servers(restart=True)
            print('done') 
            
        if args.get('action') == 'save':
            save_schema_values(args['schema'],
                    filename=args.get('filename',''),
                    folder=args.get('folder',''))
        else:
            try:
                args.pop('action')
                args = dict((k,fn.str2type(v)) for k,v in args.items() 
                            if k and v not in (False,[]))
                print(args)
                r = check_db_schema(**args)
            except:
                print(fn.except2str())

    except SystemExit:
        pass
    except:
        print(fn.except2str())
        #print(USAGE)

###############################################################################

def check_archiving_schema(
        schema='hdb',
        attributes=[],values={},
        ti = None,
        period = 7200,
        old_period=24*3600*90,\
        exclude=['*/waveid','*/wavename','*/elotech-*'],
        use_index = True,
        loads = True,
        action=False,
        trace=True,
        export=None,
        n = 1):
    
    raise Exception('deprecated!, use check_db_schema')

    ti = fn.now() if ti is None else str2time(ti) if isString(ti) else ti
    api = pta.api(schema)
    is_hpp = isinstance(api,pta.HDBpp)
    attributes = list(attributes)
    values = dict(values)
    
    check = dict()
    old_period = 24*3600*old_period if old_period < 1000 \
        else (24*old_period if old_period<3600 else old_period)
    
    allattrs = api.get_attributes() if hasattr(api,'get_attributes') \
        else api.keys()
    print('%s contains %d attributes' % (schema,len(allattrs)))
    
    if attributes:
        if fn.isString(attributes) and fn.isRegexp(attributes):
            tattrs = [a for a in allattrs if clsearch(attributes,a)]
        else:
            attributes = map(fn.tango.get_normal_name,fn.toList(attributes))
            tattrs = [a for a in allattrs 
                      if fn.tango.get_normal_name(a) in allattrs]
            
    else:
        tattrs = allattrs
    
    excluded = [a for a in tattrs if any(fn.clmatch(e,a) for e in exclude)]
    tattrs = [a for a in tattrs if a not in excluded]
    
    print('%d attributes to check' % len(tattrs))
    if not len(tattrs):
        return 
    
    if excluded:
        print('\t%d attributes excluded' % len(excluded))
    
    archived = {}
    for a in tattrs:
        if hasattr(api,'get_attribute_archiver'):
            arch = api.get_attribute_archiver(a) 
        else:
            arch = api[a].archiver
        if arch: 
            archived[a] = arch
  
    print('\t%d attributes are archived' % len(archived))
    
    ###########################################################################

    values = load_schema_values(schema,attributes,values,n)
    
    ###########################################################################    
    
    #Getting Tango devices currently not running
    alldevs = set(t.rsplit('/',1)[0] for t in tattrs)
    #tdevs = filter(fn.check_device,alldevs)
    #nodevs = [fn.tango.get_normal_name(d) for d in alldevs if d not in tdevs]
    #if nodevs:
        #print('\t%d devices are not running' % len(nodevs))
        
    archs = sorted(set(archived.values()))
    if loads:
        astor = fn.Astor()
        astor.load_from_devs_list(archs)
        loads = fn.defaultdict(list)
        for k,s in astor.items():
            for d in s.get_device_list():
                d = fn.tango.get_normal_name(d)
                for a in archived:
                    if fn.tango.get_normal_name(archived[a]) == d:
                        loads[k].append(a)
        for k,s in sorted(loads.items()):
            print('\t%s archives %d attrs (last at %s)' 
                % (k,len(s),fn.time2str(max(values[a][0] 
                    for a in loads[k] if values[a]))))
    
    noarchs = [fn.tango.get_normal_name(d) for d in archs 
               if not fn.check_device(d)]
    if noarchs:
        print('\t%d archivers are not running: %s' % (len(noarchs),noarchs))
    
    ###########################################################################
    
    now = fn.now()
    result = fn.Struct()
    times = [t[0] for t in values.values() if t]
    futures = [t for t in times if t>now]
    times = [t for t in times if t<now]
    tmiss = []
    tfutures = [k for k,v in values.items() if v and v[0] in futures]
    tmin,tmax = min(times),max(times)
    print('\toldest update was %s' % time2str(tmin))
    print('\tnewest update was %s' % time2str(tmax))
    if futures:
        print('\t%d attributes have values in the future!' % len(futures))

    tnovals = [a for a in archived if not values.get(a,None)]
    if tnovals:
        print('\t%d archived attributes have no values' % len(tnovals))    
    try:
        tmiss = [a for a,v in values.items() if v 
                 and old_period < v[0] < ti-period and a not in archived]
    except:
        print(fn.first(values.items()))
    if tmiss:
        print('\t%d/%d attrs with values are not archived anymore' % 
              (len(tmiss),len(tattrs)))
        
    result.Excluded = excluded
    result.Schema = schema
    result.All = tattrs
    result.Archived = values   
        
    result.NoValues = tnovals
    result.MissingOrRemoved = tmiss        
    
    result.TMin = tmin
    result.TMax = tmax
    result.Futures = tfutures    
        
    tup = sorted(a for a in values if values[a] and values[a][0] > ti-period)
    tok = [a for a in tup if values[a][1] not in (None,[])]
    print('\n%d/%d archived attributes are updated since %s - %s' 
          % (len(tup),len(archived),ti,period))
    print('%d archived attributes are fully ok\n' % (len(tok)))

    tnotup = sorted(a for a in values if values[a] and values[a][0] < ti-period)
    print('\t%d archived attrs are not updated' % len(tnotup))    
    tupnoread = [a for a in tup if values[a][1] is None 
                 and fn.read_attribute(a) is None]
    
    reads = dict((a,fn.read_attribute(a)) for a in tnotup)
    tnotupread = [a for a in tnotup if reads[a] is not None]
    print('\t%d not updated attrs are readable (Lost)' % len(tnotupread))    
    print('\t%d of them are not floats' 
          % len([t for t in tnotupread if not isinstance(reads[t],float)]))
    print('\t%d of them are states' 
          % len([t for t in tnotupread if t.lower().endswith('/state')]))
    print('\t%d of them seem motors' 
          % len([t for t in tnotupread if t.lower().endswith('/position')]))
    
    tnotupevs = [a for a in tnotupread 
        if fn.tango.check_attribute_events(a,min_tango_version=800))]
    print('\t%d not updated attrs are readable and have events (LostEvents)' 
          % len(tnotupevs))    
    
    tnotupnotread = [a for a in tnotup if a not in tnotupread]
    print('\t%d not updated attrs are not readable' % len(tnotupnotread))
    
    result.Lost = tnotupread
    result.LostEvents = tnotupevs    
    
    losts = (tnotupevs if is_hpp else tnotupread)
    
    diffs = dict()
    for a in losts:
        try:
            v,vv = values.get(a,(None,))[1],reads[a]
            if fn.isSequence(v): v = fn.toList(v)
            if fn.isSequence(vv): vv = fn.toList(vv)
            diffs[a] = v!=vv
            if fn.isSequence(diffs[a]):
                diffs[a] = any(diffs[a])
            else:
                diffs[a] = bool(diffs[a])
        except:
            diffs[a] = None
            
    differ = [a for a in losts if diffs[a]] #is True]
    print('\t%d/%d not updated attrs have also wrong values!!!' 
          % (len(differ),len(losts)))     
    result.LostDiff = differ    
        
    print('\n')
    fams = fn.defaultdict(list)
    for a in tnotupread:
        fams['/'.join(a.split('/')[-4:-2])].append(a)
    for f in sorted(fams):
        print('\t%s: %d attrs not updated' % (f,len(fams[f])))
        
    print('-'*80)
    rd = pta.Reader()
    only = [a for a in tnotupread if len(rd.is_attribute_archived(a))==1]
    print('\t%d/%d not updated attrs are archived only in %s' 
          % (len(only),len(losts),schema))
    print()   
    print('-'*80)        
    archs = sorted(set(archived.values()))
    astor = fn.Astor()
    astor.load_from_devs_list(archs)
    badloads = fn.defaultdict(list)
    for k,s in astor.items():
        for d in s.get_device_list():
            d = fn.tango.get_normal_name(d)
            for a in losts:
                try:
                    if fn.tango.get_normal_name(archived[a]) == d:
                        badloads[k].append(a)
                except:
                    traceback.print_exc()
                    
    for k,s in sorted(badloads.items()):
        if len(s):
            t = loads and len(loads[k]) or len(s)
            print('\t%s archives %d/%d lost attributes (%f)'%
                  (k,len(s),t,float(len(s))/t))
        
    print('\t%d updated attrs are not readable' % len(tupnoread))    
    
    result.ArchivedAndReadable = tok
    result.Updated = tup
    result.NotUpdated = tnotup
    result.Unreadable = tnotupnotread
    #result.DeviceNotRunning = nodevs
    result.ArchiverNotRunning = noarchs

    result.LostFamilies = fams
    

    # Tnones is for readable attributes not being archived
    tnones = [a for a in archived if (
        a not in values or values[a] and values[a][1] in (None,[]))
        and a not in tupnoread and a not in tnotupread]
    tupnones = [a for a in tnones if a in tup]

    if tupnones:
        print('\t%d archived readable attrs record empty values' % len(tupnones))
        
    result.Nones = tnones
    
    if 0:
        
        get_ratio = lambda a,b:float(len(a))/float(len(b))
        
        #result.ArchRatio = get_ratio([t for t in readarch if t not in tnotup],readarch)
        #result.ReadRatio = get_ratio(result.Readable,tattrs)
        #result.LostRatio = get_ratio([a for a in tread if a in tnotup],tread)
        #result.MissRatio = get_ratio([a for a in tread if a not in tarch],tread)
        #result.OkRatio = 1.0-result.LostRatio-result.MissRatio
        
        #result.Summary = '\n'.join((
            #('Checking archiving of %s attributes'%(len(attributes) if attributes else schema))
            #,('%d attributes in %s, %d are currently active'%(len(api),schema,len(tarch)))
            #,('%d devices with %d archived attributes are not running'%(len(nodevs),len([a for a in api if a.rsplit('/',1) in nodevs])))
            #,('%d archived attributes (%2.1f %%) are unreadable! (check and remove)'%(len(tnoread),1e2*get_ratio(tnoread,tarch)))
            #,('%d readable attributes are not archived'%(len(tmiss)))
            #,('%d attributes (readable or not) are updated (%2.1f %% of all readables)'%(len(tok),1e2*result.OkRatio))
            #,('-'*80)
            #,('%d archived attributes (readable or not) are not updated!'%len(tnotup))
            #,('%d archived and readable attributes are not updated! (check and restart?)'%len(treadnotup))
            #,('-'*80)
            #,('%d readable attributes have been removed in the last %d days!'%(len(removed),old_period/(24*3600)))
            #,('%d readable scalar attributes are not being archived (not needed anymore?)'%len(tmscalar))
            #,('%d readable array attributes are not being archived (Ok)'%len(tmarray))
            #,('%d readable array attributes are archived (Expensive)'%len(tarray))
            #,('')))
        
        #if trace: print(result.Summary)
        #print('%d readable lost,Ok = %2.1f%%, %2.1f %% over all Readables (%2.1f %% of total)'%\
            #(len(treadnotup),1e2*result.ArchRatio,1e2*result.OkRatio,1e2*result.ReadRatio))

    if action:
        if action == 'start_devices':
            print('Executing action %s' % action)
            api.start_devices()
            
        if action == 'restart_all':
            print('Executing action %s' % action)
            devs = api.get_archivers()
            astor = fn.Astor()
            print('Restarting %d devs:' % (len(devs),devs))
            astor.load_from_devs_list(devs)
            astor.stop_servers()
            fn.wait(10.)
            astor.start_servers()
            
        #print('NO ACTIONS ARE GONNA BE EXECUTED, AS THESE ARE ONLY 
        # RECOMMENDATIONS')
        #print("""
        #api = PyTangoArchiving.HDBpp(schema)
        #api.start_devices()
        
        #or  
            
        #api = PyTangoArchiving.ArchivingAPI('%s')
        #lostdevs = sorted(set(api[a].archiver for a in result.NotUpdated))
        #print(lostdevs)
        #if lostdevs < a_reasonable_number:
          #astor = fn.Astor()
          #astor.load_from_devs_list(lostdevs)
          #astor.stop_servers()
          #fn.time.sleep(10.)
          #astor.start_servers()
        #"""%schema)
        
    print('\nfinished in %d seconds\n\n'%(fn.now()-ti))
    
    if export is not None:
        if export is True:
            export = 'txt'
        for x in (export.split(',') if isString(export) else export):
            if x in ('json','pck','pickle','txt'):
                x = '/tmp/%s.%s' % (schema,x)
            print('Saving %s file with keys:\n%s' % (x,result.keys()))
            if 'json' in x:
                fn.dict2json(result.dict(),x)
            else:
                f = open(x,'w')
                if 'pck' in x or 'pickle' in x:
                    pickle.dump(result.dict(),f)
                else:
                    f.write(fn.dict2str(result.dict()))
                f.close()        
        
    return result 

def load_schema_values(schema, attributes=None, values=None, n=1, tref=None):
    
    api = schema if not isString(schema) else pta.api(schema)
    
    if isString(values) and values.endswith('.pck'):
        print('\nLoading last values from %s file\n' % values)
        import pickle
        values = pickle.load(open(values))
        
    elif isString(values) and values.endswith('.json'):
        print('\nLoading last values from %s file\n' % values)
        values = fn.json2dict(values)        

    elif values is None: #if not use_index or is_hpp:

        print('\nGetting last values ...\n')
        if n==1 and not isinstance(api,pta.HDBpp):
            ups = api.db.get_table_updates()
            values = dict((k,(ups[api[k].table],None)) for k in attributes)
        else:
            value = {}
            values = dict((a,api.load_last_values(a,n=n,tref=tref,brief=True))
                          for a in attributes)
            
    values = values.get('values',values)
    err = 0
    for k,v in values.items():
        # each value can be either a tuple (t,v), a list of t,v values or None
        # what should be returned is an attribute:[[t0,v0],...] list (even if n=1)
        try:
            if isinstance(v,dict): 
                v = fn.first(v.values())
            if isSequence(v):
                if not len(v):
                   v = [] if n>1 else None
                elif not isSequence(v[0]):
                   v = [v]
            if v is not None and len(v) and len(v[0]) and not isNumber(v[0][0]):
                v = [[date2time(t[0])]+t[1:] for t in v]
            values[k] = v
        except:
            if not err:
                traceback.print_exc()
                err = 1
            #print('unable to parse %s: %s' % (k,v))
    
    print('%d values obtained' % len(values))
    
    return values
    

CheckState = fn.Struct(
    ON = 0, # archived
    OFF = 1, # not archived
    OK = 2, # device up and running, values updated
    NO_READ = 3, # device not running
    STALL = 4, # value not changing
    NO_EVENTS = 5, # not sending events
    LOST = 6, # value changed, but not updated in db
    UNK = 7, # value cannot be evaluated
    WRONG = 8, # types dont match
    )

def check_attribute_exists(model):
    model = fn.tango.parse_tango_model(model)
    alldevs = fn.tango.get_all_devices()
    device = fn.tango.get_normal_name(model.device)
    if device not in alldevs:
        return False
    #alldevs = fn.tango.get_all_devices(exported=True)
    #if not device in alldevs:
        #return True
    if not fn.tango.check_device(device):
        return True
    return bool(fn.find_attributes(model.normalname))

def check_db_schema(schema, attributes = None, values = None,
                    tref = -12*3600, n = 1, filters = '*', export = 'json',
                    restart = False, subscribe = False):
    """
    tref is the time that is considered updated (e.g. now()-86400)
    n is used to consider multiple values
    
    attrs: all attributes in db
    on: archived
    off: in db but not currently archived
    ok: updated   
    
    known error causes (attrs not lost but not updated):
    
    nok: attributes are not currently readable
    noevs: attributes not sending events
    novals: attributes never recorded a value
    stall: not updated, but current value matches archiving
    lost: not updated, and values doesn't match with current
    """
    
    t0 = fn.now()
    if hasattr(schema,'schema'):
        api,schema = schema,schema.schema
    else:
        api = pta.api(schema)

    r = fn.Struct(schema=schema,api=api)    
    if isString(tref): 
        tref = fn.str2time(tref)
    r.tref = fn.now()+tref if tref < 0 else tref
    r.attrs = [a for a in (attributes or api.get_attributes())
                if fn.clmatch(filters,a)]
    r.summary = ('check_db_schema(%s,attrs[%s],tref="%s",export as %s)' 
          % (schema,len(r.attrs),fn.time2str(r.tref),export))
    print(r.summary)
    
    r.stopped = api.get_stopped_attributes()
    if restart: # and schema!='hdbpc':
        archs = [a for a in api.get_archivers() if not fn.check_device(a)]
        if archs:
            try:
                print('Restarting archivers: %s' % str(archs))
                astor = fn.Astor(archs)
                astor.stop_servers()
                astor.start_servers()
            except:
                traceback.print_exc()
        
        print('Restarting %d stopped attributes' % len(r.stopped))
        api.restart_attributes(r.stopped)
    
    r.on = [a for a in api.get_archived_attributes() if a in r.attrs]
    r.weird = [a for a in api.get_archived_attributes() if a not in r.attrs]
    r.off = [a for a in r.attrs if a not in r.on]
    
    r.subs = fn.defaultdict(list)
    r.pers = fn.defaultdict(list)
    # it will always return an attribute:[[val0],[val1]] dict
    r.values = load_schema_values(api,r.on,values,n,tref=tref)
    
    if schema in ('tdb','hdb'):
        [r.subs[api[k].archiver].append(k) for k in r.on]
    else:
        r.rvals = r.values
        r.freq, r.values = {}, {}
        for k,v in r.rvals.items():
            try:
                if v and len(v)>1:
                    r.freq[k] = float(len(v))/abs(v[0][0]-v[-1][0])
                else:
                    r.freq[k] = 0
                r.values[k] = v #[0] if len(v) else None
            except Exception as e:
                print(k,v)
                print(fn.except2str())
                
        for k in api.get_subscribers():
            r.subs[k] = api.get_archiver_attributes(k)
        for k in api.get_periodic_archivers():
            r.pers[k] = api.get_periodic_archiver_attributes(k)

    try:
        print(fn.first(r.values.items()))
        r.times = dict((a,(v[0][0] if v else 0)) for a,v in r.values.items())
        # Get all updated attributes
        r.ok = [a for a,v in r.times.items() if v > r.tref]
        # Try to read not-updated attributes
        r.check = dict((a,fn.check_attribute(a)
                        ) for a in r.attrs if a not in r.ok)
        #r.novals = [a for a,v in r.values.items() if not v]
        r.nok,r.stall,r.noevs,r.lost,r.novals,r.evs,r.rem,r.wrong = \
            [], [], [], [], [], {}, [], []
        # Method to compare numpy values
        
        
        
        for a,v in r.check.items():
            state = check_archived_attribute(a, v, default=CheckState.LOST, 
                cache=r, tref=r.tref, api=api,
                check_events = subscribe and not api.is_periodic_archived(a))
            {
                #CheckState.ON : r.on,
                #CheckState.OFF : r.off,
                CheckState.OK : r.ok, #Shouldn't be any ok in check list               
                CheckState.NO_READ : r.nok,
                CheckState.STALL : r.stall,
                CheckState.NO_EVENTS : r.noevs,
                CheckState.LOST : r.lost,
                CheckState.UNK : r.novals,
                CheckState.WRONG : r.wrong
            }[state].append(a)
                    
        r.ev_lost = [a for a in r.lost if api.is_attribute_subscribed(a)]
        r.per_lost = [a for a in r.lost if api.is_periodic_archived(a)]
        
        r.stop = api.get_stopped_attributes()
        r.evattrs = api.get_subscribed_attributes()        
        r.perattrs = [a for a in r.on if a in api.get_periodic_attributes()]
        r.notper = [a for a in r.on if a not in r.perattrs]
        r.not_updated = list(set(
            r.wrong + r.lost + r.stall + r.novals + r.nok + r.noevs))

        r.recover = [a for a in r.off+r.lost if a not in r.nok]
        r.rec_pers = [a for a in r.recover if a in r.noevs]
        r.rec_evs = [a for a in r.recover if a not in r.noevs]
        
                    
        # SUMMARY
        r.summary = r.summary +'\n'
        r.summary += ','.join(
            """on: archived
            off: not archived
            ok: updated   
            nok: not readable
            noevs: no events
            novals: no values
            stall: not changing
            lost: not updated
            """.split('\n'))+'\n'
        
        getline = lambda k,v,l: '\t%s:\t:%d\t(%s)' % (k,len(v),l)
        
        r.summary += '\n\t%s:\t:%d\tok+stall: %2.1f %%' % (
            'attrs',len(r.attrs),
            (100.*(len(r.ok)+len(r.stall))/(len(r.on) or 1e12)))
        r.summary += '\n\tsubscribed / periodic / both : %s / %s / %s' % (
            (len(r.evattrs),len(r.perattrs),len([a for a in r.perattrs if a in r.evattrs])))
        r.summary += '\n\t%d attributes updated in the last %d hours' %(
            len(r.ok),tref/3600.)

        r.summary += '\n\t%s/%s\t:\t%d/%d' % (
            'on','off (noarch)',len(r.on),len(r.off))
        r.summary += '\n\t%d attributes were stopped' % len(r.stopped)
        #if r.off > 20: r.summary+=' !!!'
        r.summary += '\n\t%s/%s\t:\t%d/%d' % (
            'wrong (type)','nok (noread)',len(r.wrong),len(r.nok))
        if (len(r.wrong)+len(r.nok)) > 10: 
            r.summary+=' !!!'
        r.summary += '\n\t%s/%s\t:\t%d/%d' % (
            'noevs','novals',len(r.noevs),len(r.novals))
        if len(r.novals) > 1: 
            r.summary+=' !!!'
        r.summary += '\n\t%s/%s\t:\t%d/%d' % (
            'lost','stall',len(r.lost),len(r.stall))    
        if len(r.lost) > 1: 
            r.summary+=' !!!'
        r.summary += '\n\t%s/%s\t:\t%d/%d' % (
            'ev_lost','per_lost',len(r.ev_lost),len(r.per_lost))        

        r.summary += '\n\trecoverable (total/evs/pers)\t:\t%s' % str(
            (len(r.recover),len(r.rec_evs),len(r.rec_pers)))
        r.summary += '\n'
            
        for d in sorted(r.subs):
            novals = [a for a in r.subs[d] if a in r.novals]   
            lost = [a for a in r.subs[d] if a in r.lost]
            if (len(novals)+len(lost)) > 2:
                r.summary += ('\n%s (all/novals/lost): %s/%s/%s' 
                    % (d,len(r.subs[d]),len(novals),len(lost)))
                
        for d in sorted(r.pers):
            novals = [a for a in r.pers[d] if a in r.novals]
            lost = [a for a in r.pers[d] if a in r.lost]
            if len(novals)+len(lost) > 2:
                r.summary += ('\n%s (all/novals/lost): %s/%s/%s' % 
                    (d,len(r.pers[d]),len(novals),len(lost)))
    
    except:
        print('Stats failed!')
        traceback.print_exc()        
        
        
    r.summary += '\nfinished in %d seconds\n\n'%(fn.now()-t0)
    print(r.summary)
    
    if restart:
        try:
            retries = sorted(set(r.ev_lost))
            print('restarting %d attributes ...\n' % len(retries))
            api.restart_attributes(retries)
        except:
            traceback.print_exc()
            
        try:
            retries = set(map(api.get_periodic_attribute_archiver,r.per_lost))
            print('restarting %d periodic archivers ...\n' % len(retries))
            fn.Astor(devs_list=sorted(retries)).restart_servers()
        except:
            traceback.print_exc()            
    
    try:
        if export not in (None,False):
            export = 'txt' if export is True else str(export)

            for x in (export.split(',')):
                for suffix in ('json','pck','pickle','txt'):
                    if suffix in x:
                        x = x if x!=suffix else '/tmp/?.%s' % (suffix)
                        x = x.replace('?',api.host+'-'+schema)
                if x in ('json','pck','pickle','txt'):
                    x = '/tmp/%s.%s' % (schema,x)
                print('Saving %s file with keys:\n%s' % (x,r.keys()))
                if 'json' in x:
                    fn.dict2json(r.dict(),x)
                else:
                    f = open(x,'w')
                    dct = r.dict()
                    dct.pop('api'),dct.pop('check')
                    if 'pck' in x or 'pickle' in x:
                        dct = fn.any2type(dct,'pickle')
                        pickle.dump(dct,f)
                    else:
                        f.write(fn.dict2str(dct))
                    f.close()     
    except:
        print('Export failed!')
        traceback.print_exc()
                
    for k,v in r.items():
        if fn.isSequence(v):
            r[k] = sorted(v)
                
    return r

def check_attribute_data(attribute, read = None, last = None, events = None):

    r = fn.Struct(type = None, events = events, value = read, last = last)
    r.model = fn.tango.get_fqdn_name(attribute)
    if read is None:
        r.value = fn.read_attribute(r.model)

    if r.value is not None:
        r.type = pta.utils.get_attribute_type_table(r.model)
        if events is None:
            r.events = fn.check_attribute_events(r.model, min_tango_version=800)

    rd = pta.Reader()
    r.schemas = rd.is_attribute_archived(r.model,active=False)
    if r.schemas:
        r.db = r.schemas[0]
        api = pta.api(r.db)
            
    r.table = api.get_table_name(r.model)
    if last is None:
        r.last = api.load_last_values(r.model,brief=True)
        
    r.subscriber = api.get_attribute_subscriber(r.model)
    r.periodic = api.get_periodic_attribute_archiver(r.model)
    return r

def check_archived_attribute(attribute, value = False, state = CheckState.OK, 
        default = CheckState.LOST, cache = None, tref = None, api = None,
        check_events = True):
    """
    generic method to check the state of an attribute (readability/events)
    
    value = AttrValue object returned by check_attribute
    cache = result from check_db_schema containing archived values
    
    this method will not query the database; database values should be 
    given using the chache dictionary argument
    """
    # readable and/or no reason known for archiving failure
    state = default # do not remove this line
    
    # Get current value/timestamp
    stored = cache.values.get(attribute,None) if cache else None
    if stored is not None and len(stored):
        if isSequence(stored[0]):
            stored = stored[0]
        t,v = stored[0],stored[1]
        
        if t>=tref and not isinstance(v,(type(None),Exception)):
            print('%s should not be in check list! (%s,%s)' % (attribute,t,v))
            return CheckState.OK
        
    if value is False:
        value = fn.check_attribute(attribute, brief=False)
        
    vv,t = getattr(value,'value',value),getattr(value,'time',0)
    t = t and fn.ctime2time(t)
    try:
        tvs = stored and type(vv)(stored[1])
    except:
        tvs = stored and stored[1]
    
    if isinstance(vv,(type(None),Exception)):
        # attribute is not readable
        state = CheckState.NO_READ
           
    elif (api and (pta.utils.get_attribute_type_table(attribute) != 
          api.get_table_name(attribute)) or t > fn.now()):
        state = CheckState.WRONG
        
    elif stored is None or (fn.isSequence(stored) and not len(stored)):
        # attribute never recorded data
        return CheckState.UNK        
        
    elif cache and stored and 0 < t <= stored[0]:
        # attribute timestamp doesnt change
        state = CheckState.STALL
        
    elif cache and stored and fbool(vv == tvs):
        # attribute value doesnt change
        state = CheckState.STALL
        
    elif check_events:
        # READABLE NOT STORED WILL ARRIVE HERE
        evs = fn.tango.check_attribute_events(attribute, min_tango_version=800)
        if cache:
            cache.evs[attribute] = evs
        if not evs:
            # attribute doesnt send events
            state = CheckState.NO_EVENTS
        else:
            state = default #CheckState.LOST

    return state

def check_table_data(db, att_id, table, start, stop, gap, period):
    """
    db must be a fandango.FriendlyDB object
    
    NOTE: count(*) seems to be a very unefficient method to do this!!
    
    this method will check different intervals within the table to 
    see whether there is available data or not for the attribute
    
    start/stop must be epoch times
    """
    cols = db.getTableCols(table)
    if 'att_conf_id' in cols:
        query = ("select count(*) from %s where att_conf_id = %s and "
            "data_time between " % (table, att_id))
    else:
        query = ("select count(*) from %s where "
            "time between " % (table))
    
    tend = start + period
    while tend < stop:
        tq = '"%s" and "%s"' % (fn.time2str(start),fn.time2str(tend))
        try:
            r = db.Query(query + ' ' + tq)
            print('%s:%s' % (tq, r[0][0]))
        except:
            traceback.print_exc()
            break
            print('%s: failed' % tq)
        start, tend = start+gap, tend+gap
        
    return


def save_schema_values(schema, filename='', folder=''):
    """
    This method saves all last values from a given schema into a file
    it can be called from crontab to generate daily reports
    """
    t0 = fn.now()
    print('Saving %s attribute values' % schema)
    date = fn.time2str().split()[0].replace('-','')
    filename = filename or '%s_%s_values.pck' % (schema,date)
    if folder: 
        filename = '/'.join((folder,filename))

    api = pta.api(schema)
    attrs = api.keys() if hasattr(api,'keys') else api.get_attributes()
    print('%d attributes in %s' % (len(attrs),schema))
    values = dict.fromkeys(filter(api.is_attribute_archived,attrs))
    print('%d attributes archived' % (len(values)))
    values.update((a,api.load_last_values(a)) for a in values.keys())
    pickle.dump(values,open(filename,'w'))

    print('%s written, %d seconds ellapsed' % (filename,fn.now()-t0))
    print(os.system('ls -lah %s' % filename))

##############################################################################

if __name__ == '__main__':
    
    main()
    
