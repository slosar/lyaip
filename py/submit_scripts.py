#!/usr/bin/env python
from glob import glob
import os, sys

tosubmit=150
lst=glob('sh/*.sh')
for cname in lst:
    if 'test' in cname:
        continue
    name=cname.replace('sh/','')
    name=name.replace('.sh','')
    try:
        num=int(name)
    except:
        print "Not a number, name"
        continue
    done=os.path.isfile('log/%s_1.log'%name)
    if not done:
        print "submitting ", name
        os.system('qsub %s'%(cname))
        tosubmit-=1
        if (tosubmit==0):
            break
    else:
        print "skupping ",name
print "done"
