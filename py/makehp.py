#!/usr/bin/env python
import sys
from glob import glob
import numpy as np
import healpy as hp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

Nside=256
Npix=12*Nside**2

def filterAvg(sky):
    tsky=np.hstack(sky).mean(axis=1)
    fsky, fwe=[],[]
    for s in sky:
        Nx,Ny=s.shape
        fwe.append(1.0/s)
        scaling=(s.mean(axis=1)/tsky).mean()
        print scaling
        fs=s*1.0-np.outer(scaling*tsky,np.ones(256))
        for i in range(Ny):
            fs[:,i]-=fs[:,i].mean()
        fsky.append(fs)

    return fsky, fwe
        

def main():
    flist=glob(sys.argv[1])
    try:
        flist=flist[:int(sys.argv[2])]
    except:
        pass

    gmap=np.zeros(Npix)
    wmap=np.zeros(Npix)
    vmap=np.zeros(Npix)
    print flist
    for i,fname in enumerate(flist):
        print "Processing ",fname, i+1,"/",len(flist)
        if "-1-" not in fname:
            continue
        headerl,skyl,ral,decl=[],[],[],[]
        for i in range(6):
            print i,
            cf=fname.replace('-1-','-%i-'%(i+1))
            cheader,csky,cra,cdec=np.load(cf)['arr_0']
            headerl.append(cheader)
            skyl.append(csky)
            ral.append(cra)
            decl.append(cdec)
        print
        skyl,weil=filterAvg(skyl)
        for sky,wei,ra,dec in zip(skyl,weil,ral,decl):
            sky=sky.flatten()
            ra=ra.flatten()
            dec=dec.flatten()
            wei=wei.flatten()
            theta=np.pi/2-dec/180.*np.pi
            phi=ra/180.*np.pi
            ipix=hp.ang2pix(Nside,theta,phi)
            wmap+=np.bincount(ipix,weights=wei,minlength=Npix)
            gmap+=np.bincount(ipix,weights=sky*wei,minlength=Npix)
            vmap[ipix]+=1
    assert(np.all(gmap[np.where(wmap==0)]==0))
    assert(len(np.where(wmap<0)[0])==0)
    mx=np.where(wmap>0)
    gmap[mx]/=wmap[mx]
    np.savez("map",(gmap, wmap, vmap))
    # plt.figure(figsize=(12,8))
    # hp.mollview(wmap)
    # plt.savefig('weights.png')
    # plt.figure(figsize=(12,8))
    # hp.mollview(vmap)
    # plt.savefig('visits.png')
    # plt.figure(figsize=(12,8))
    # hp.mollview(gmap)
    # plt.savefig('map.png')


        
if  __name__=="__main__":
    main()
