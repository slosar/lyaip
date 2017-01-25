#!/usr/bin/env python
from glob import glob
lst=glob('301/*')
for name in lst:
    if 'html' in name:
        continue
    name=name.replace('301/','')
    f=open ('sh/%s.sh'%name,'w')
    f.write("""#!/bin/bash
# specify a jobname
#PBS -N f%s

# specify number of nodes (ppn should be 8 to reserve all cores on the node)
#PBS -l nodes=1:ppn=8

# misc other PBS settings:
#PBS -j eo
#PBS -q physics
#PBS -l walltime=99:00:00
STRIP=%s
cd /home/rcroft/frames/lyaip/
module load python27
module load python27-extras
py/process_stripe.py 301/$STRIP/1/ >log/$STRIP\_1.log 2>log/$STRIP\_1.err &
py/process_stripe.py 301/$STRIP/2/ >log/$STRIP\_2.log 2>log/$STRIP\_2.err &
py/process_stripe.py 301/$STRIP/3/ >log/$STRIP\_3.log 2>log/$STRIP\_3.err &
py/process_stripe.py 301/$STRIP/4/ >log/$STRIP\_4.log 2>log/$STRIP\_4.err &
py/process_stripe.py 301/$STRIP/5/ >log/$STRIP\_5.log 2>log/$STRIP\_5.err &
py/process_stripe.py 301/$STRIP/6/ >log/$STRIP\_6.log 2>log/$STRIP\_6.err &
wait

"""%(name,name))
    f.close()
            
