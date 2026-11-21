"""Extract public input subsets without job names/users. Takes the three original archives and API JSON."""
import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
from statistics import median, quantiles
import sqlite3
import tarfile
import tempfile
import zipfile

DST=Path(__file__).parent
T0=int(datetime(2022,3,7,tzinfo=timezone.utc).timestamp())
T1=T0+7*86400
def dump(name,head,records):
    with (DST/name).open('w',newline='') as stream:
        wr=csv.writer(stream);wr.writerow(head);wr.writerows(records)
def gethash(path,algo):
    dg=hashlib.new(algo)
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20), b''): dg.update(block)
    return dg.hexdigest()

def extract(schedules,meters,reservations,grid):
    assert gethash(schedules,'md5')=='5af5ae243a29c4890c40c03d6e90b3d1'
    assert gethash(meters,'md5')=='aef9f5dd6d941a497200c6f42f2320c1'
    jobs=[]
    with open(schedules) as fs:
        for row in csv.DictReader(fs):
            if not all(row[k] for k in ('Start','End','AllocNodes','Elapsed')): continue
            s,e=int(float(row['Start'])),int(float(row['End']))
            n=int(row['AllocNodes'])
            if e>T0 and s<T1+7200 and n>0 and e>s:
                assert e-s==float(row['Elapsed'])
                jobs.append((s,e,n))
    dump('archer2_allocations.csv',['start_epoch_utc','end_epoch_utc','nodes'],sorted(jobs))
    with tarfile.open(meters) as archive:
        name='HPC-JEEP_WP1_data/ARCHER2/raw_data/2022-03_scua_sacct.dat.gz'
        gz=gzip.GzipFile(fileobj=archive.extractfile(name))
        vals=[]
        total=0
        for ln in io.TextIOWrapper(gz):
            a=ln.strip().split('::')
            if len(a)!=10 or a[6]!='COMPLETED':continue
            total+=1
            if not a[3].isdigit() or not a[5].isdigit() or not a[7].isdigit():continue
            ns,sec,j=map(int,(a[3],a[5],a[7]))
            if min(ns,sec,j)>0: vals.append(j/(ns*sec))
    qs=quantiles(vals,n=4,method='inclusive')
    dump('archer2_meter_calibration.csv',['completed_steps','positive_measured_steps','q25_W_per_node','median_W_per_node','q75_W_per_node'],[(total,len(vals),*qs)])
    with zipfile.ZipFile(reservations) as z,tempfile.TemporaryDirectory() as directory:
        file=Path(directory)/'g.sqlite'
        file.write_bytes(z.read('Grid5000.sqlite'))
        with sqlite3.connect(file) as conn:
            rows=conn.execute('select j.SubmitTime,j.WaitTime,j.RunTime,r.StartTime,r.StopTime from Jobs_Reservation r JOIN Jobs j ON r.JobID=j.JobID').fetchall()
    usable=[(s+w,r,st,en) for s,w,r,st,en in rows if r>0 and st>0 and en>=st]
    dump('reservation_audit.csv',['linked_reservations','usable_windows','equal_elapsed_to_window','observed_start_matches','at_least_30min_spare'],
         [(len(rows),len(usable),sum(r==en-st for _,r,st,en in usable),sum(start==st for start,_,st,_ in usable),sum(en-st-r>=1800 for _,r,st,en in usable))])
    raw=json.load(open(grid))['data']
    out=[]
    for r in raw:
        a=r['intensity']; stamp=int(datetime.fromisoformat(r['from']).timestamp())
        assert a['actual'] is not None and a['forecast'] is not None
        out.append((stamp,a['actual'],a['forecast']))
    dump('gb_intensity.csv',['from_epoch_utc','actual_gCO2_per_kWh','archived_forecast_gCO2_per_kWh'],out)
    print(len(jobs),len(out),total,len(vals),qs,len(usable))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for a in ('schedules','meters','reservations','grid'):parser.add_argument(a)
    parser.add_argument('--repeat',action='store_true',help='Extract March 14–20 to repeat_week/')
    args=vars(parser.parse_args())
    if args.pop('repeat'):
        T0+=7*86400;T1+=7*86400;DST=DST/'repeat_week';DST.mkdir(exist_ok=True)
    extract(**args)
