#!/usr/bin/env python
import sys
from glob import glob
import numpy as np
import healpy as hp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

Nside=2048
Npix=12*Nside**2

def filterAvg(s):
    sr=s*1.0
    Nx,Ny=s.shape
    for i in range(Nx):
        sr[i,:]-=sr[i,:].mean()
    for j in range(Ny):
        sr[:,j]-=sr[:,j].mean()
    return sr
        

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
        header,sky,ra,dec=np.load(fname)['arr_0']
        sky=filterAvg(sky)
        sky=sky.flatten()
        ra=ra.flatten()
        dec=dec.flatten()
        theta=np.pi/2-dec/180.*np.pi
        phi=ra/180.*np.pi
        ipix=hp.ang2pix(Nside,theta,phi)
        wmap+=np.bincount(ipix,minlength=Npix)
        gmap+=np.bincount(ipix,weights=sky,minlength=Npix)
        vmap[ipix]+=1
    gmap/=wmap
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
