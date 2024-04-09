import PyTangoArchiving as pta, fandango as fn, PyTangoArchiving.hdbpp.maintenance as ptam
import traceback

#dbs = ['hdbacc','hdbct','hdbdi','hdbpc','hdbrf','hdbvc']

def check_and_recover_attributes(schema,read=True,recover=False, period=-4*3600, attributes=[]):
    db = pta.api(schema) if fn.isString(schema) else schema
    attrs = attributes or db.get_attributes()
    act = [a for a in attrs if db.get_attribute_archiver(a)]
    aper = [a for a in attrs if db.get_periodic_attribute_archiver(a)]
    aev = [a for a in attrs if db.get_attribute_subscriber(a)]
    both = [a for a in attrs if a in aper and a in aev]
    
    print('Checking %s, %d attributes in database, %d active, %d periodic,'
          ' %d subscribed, %d both' % (db, len(attrs),len(act),len(aper),len(aev),len(both)))
    
    if read:
        reads = {}
        times = {}
        for a in attrs:
            t0 = fn.now()
            v = fn.read_attribute(a)
            reads[a],times[a] = v,fn.now()-t0
        
        noread = [a for a in reads if reads[a] is None]
        slow = [a for a in aper if times[a] > 0.1]
        noact = [a for a in reads if a not in noread and a not in act]
    
        print('%d not readable, %d are slow, %d disabled' % (len(noread),len(slow),len(noact)))
    else:
        reads = times = dict((k,0 if k in act else None) for k in attrs)
    
    last_vals = db.load_last_values(act)
    notup = [a for a,v in last_vals.items() if reads[a] is not None and (not v or v[0] < fn.now()-abs(period))]
    novals = [a for a in last_vals if db.is_attribute_archived(a) and not last_vals[a] and reads[a] is not None]
    if read:
        noevs = [a for a in aev if not fn.check_attribute_events(a)]
    else:
        noevs = []
    noevsnoper = [a for a in noevs if a not in aper]
    nones = [a for a,v in last_vals.items() if a not in notup and v and v[1] is None and reads[a] is not None]
    
    lost = []
    for a in notup:
        try:
            if ((reads[a] is not None if not fn.isSequence(reads[a]) else len(reads[a])) 
                and (not last_vals[a] or reads[a]!=last_vals[a][1])):
                lost.append(a)
        except Exception as e:
            print(a,reads[a],last_vals[a],e)
            lost.append(a)
            
    print('%d not updated, %d with no values, %d not sending events, '
          '%d not events nor polling, %d updated with None instead of value' 
          % (len(notup),len(novals),len(noevs),len(noevsnoper),len(nones)))
    
    recattrs = sorted(set(lost+novals))
    recper = [a for a in recattrs if a in aper]
    recevs = [a for a in recattrs if a in aev and a not in noevs]
    
    print('%d attributes should be recoverable, %d periodic, %d subscribed' 
          % (len(recattrs), len(recper), len(recevs)))
    
    if recover:
        print('Recovering %d event-based attributes' % len(recevs))
        db.restart_attributes(recevs)
        
    if recover:
        print('Recovering %d periodic attributes' % len(recper))
        recperslow = [a for a in recper if a in slow]
        print('%d attributes are too slow to be periodic archived: %s' % (
            len(recperslow),recperslow))
        devs = sorted(set(db.get_periodic_attribute_archiver(a) for a in recper))
        print('%d periodic archivers will be restarted: %s' % (len(devs),devs))
        astor = fn.Astor(devs)
        astor.stop_servers()
        astor.start_servers()
    
    result = fn.Struct()
    result.update(dict((k,v) for k,v in locals().items() if isinstance(v,(list,dict))))
    return result


def recover_disabled_attributes(db,attributes=[],types=(int,float,long),do_it=False):

    db = pta.api(db) if fn.isString(db) else db
    r = fn.Struct()
    
    attrs = attributes or db.get_attributes()
    all_act = fn.join(pta.api(d).get_archived_attributes() 
        for d in pta.get_hdbpp_databases())
    

    miss = [a for a in attrs if a not in all_act]
    reads,rtimes = {},{}
    for a in miss:
        t0 = fn.now()
        reads[a] = fn.read_attribute(a)
        rtimes[a] = fn.now()-t0
    
    miss = [k for k,v in reads.items() if v is not None]
    tries = [k for k in miss if isinstance(reads[k],types)]
    evs = [k for k in tries if fn.check_attribute_events(k)]
    notype = [a for a in miss if a not in tries]
    pers = [a for a in tries if a not in evs]
    slow = [k for k in rtimes if rtimes[k]>0.25]
    
    print('%d disabled attributes, %d periodic, %d subscribed, %d do not match %s: %s' 
        % (len(miss),len(pers),len(evs),len(notype),types,notype))
    print('%d periodic attributes are too slow!: %s' % (len(slow),slow))
    pers = [a for a in pers if a not in slow]
    
    freqs = {}
    vals = {}
    for a in pers:
        vals[a] = db.get_last_attribute_values(a, n=100, 
            check_attribute=False, epoch=None, period=365*86400)
        if vals[a]:
            freqs[a] = abs(vals[a][0][0]-vals[a][-1][0])/len(vals[a])

    pollings = {}
    periods = [1, 3, 5, 10, 15, 30, 60, 90, 120, 180, 300, 600, 1200, 1800, 3600, 86400]
    for i,a in enumerate(pers):
        if a in freqs:
            l = [p for p in periods if p>=int(freqs[a])]
            pollings[a] = min(l or [86400])
            
    sets = fn.defaultdict(list)
    [sets[p].append(a) for a,p in pollings.items()]
    print('new pollings:')
    for s,l in sorted(sets.items()):
        print(s,l)

    if do_it:
        print('Recovering %d periodic attributes ...' % (len(pers)))
        [db.add_periodic_attribute(k,v*1000) for k,v in pollings.items()]
        print('Recovering %d subscribed attributes ...' % (len(evs)))
        [db.add_attribute(k,code_event=True) for k in evs]
        
    r.attrs, r.miss, r.evs, r.pers, r.slow, r.notype = attrs,miss,evs,pers,slow,notype
    r.all_act = all_act
    r.pollings, r.freqs = pollings, freqs

    return r


def recover_hdbpp_database(api):
    
    check = pta.check.check_db_schema(api,subscribe=False)
    print('>'*80)
    print('\nrecovering %d lost attributes from %s\n' % (len(check.lost),db))
    
    perlost = [a for a in check.lost if api.is_periodic_archived(a)]
    evlost = [a for a in check.lost if not api.is_periodic_archived(a)]

    errors = [a for a in evlost if api.get_attribute_errors(a)]
    recover = [a for a in errors if fn.tango.check_attribute_events(a)]

    failed = []
    for a in evlost:
        print('recovering %s' % a)
        if a in errors and a not in recover:
            print('%s not recoverable' % a)
            continue
        try:
            d = api.get_attribute_subscriber(a)
            dp = fn.get_device(d)
            dp.AttributeStop(a)
            fn.wait(0.5)
            dp.AttributeStart(a)
        except:
            failed.append(a)
            print(a,d,traceback.format_exc())

    periods = dict((a,api.get_periodic_attribute_period(a)) for a in perlost)
            
    for per in api.get_periodic_archivers():
        perattrs = api.get_periodic_archiver_attributes(per)
        if len([a for a in perattrs if a in perlost]) > 0.3*len(perattrs):
            fn.Astor(per).stop_servers()
            fn.wait(5.)
            fn.Astor(per).start_servers()
        else:
            for attr in [p for p in perattrs if p in perlost]:
                period = periods[attr]
                print('recovering %s' % attr)
                try:
                    d = api.get_periodic_attribute_archiver(attr)
                    dp = fn.get_device(d)
                    dp.AttributeRemove(attr)
                    fn.wait(.5)
                    dp.AttributeAdd([attr,str(int(period))])
                    fn.wait(.5)
                    print('%s done' % attr)
                except:
                    failed.append(attr)
                    print(attr,d,traceback.format_exc())

    print('attributes not recoverable: %s' % str([a for a in errors if a not in recover]))
    print('attributes failed: %s' % str(failed))
    
    return check

def check_all_databases():
    dbs = pta.get_hdbpp_databases()
    checks = dict((d,recover_hdbpp_database(d)) for d in dbs)
    

    
