#!/usr/bin/env python
import sys
from glob import glob
from astropy.io import fits
from astropy import wcs
from scipy.interpolate import interp1d
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy.fft import rfft2, irfft2


band="g"
debug=True
maxfiles=200000

def main():
    print "------------------------"
    print "DIRECTORY:",sys.argv[1]
    print "Debug:",debug
    print "Band:",band
    print "maxfiles:",maxfiles
    flist, header, run, col = get_list(sys.argv[1])
    outroot="output/out-%s-%04d-%i-%s"%(band,run,col,header['FLAVOR']) #want to make sure we filter non-science guys out
    print "FLAVOR:", header['FLAVOR']
    print "EXP TIME:",header['EXPTIME']
    print "STRIPE:", header['STRIPE']
    print "STRIP:", header['STRIP']
    print "Working on run %i, col %i, with %i files."%(run,col,len(flist))
    ra,dec,sky=process_list(flist)
    save_results(header,ra,dec,sky,)
    print "DONE"
    print "------------------------"
        
def get_list(d):
    flist=glob(d+"/frame-"+band+"-*.fits.bz2")
    if len(flist)==0:
        print "No files"
        sys.exit(1)
    flist.sort()
    run,col=None,None
    for name in flist:
        _,_,crun,ccol,cnum=name.split("-")
        crun=int(crun)
        ccol=int(ccol)
        cnum=int(cnum[:4])
        if run is None:
            run=crun
            col=ccol
            num=cnum
        else:
            if run!=crun:
                print "Shit #1"
                sys.exit(1)
            if col!=ccol:
                print "Shit #2"
                sys.exit(1)
            if cnum!=num+1:
                print "Missing number in sequence", num, cnum
                sys.exit(1)
            num=cnum
    header=fits.open(flist[0])[0].header
    return flist[:maxfiles], header, run,col
               
def getLinCoef(vals,maxN):
    xo=vals[0]
    xk=(vals[-1]-vals[0])/(maxN-1.)
    xo=-xo/xk
    xk=1/xk
    return xo,xk

def process_list(flist):
    tsky=[]
    tra=[]
    tdec=[]
    for fname in flist:
        print "Loading ",fname
        d=fits.open(fname)
        ### GET DATA
        if (d[0].data.shape!=(1489, 2048)):
            print "Unexpected shape:", d[0].data.shape
        sky=d[2].data['ALLSKY'][0,:,:]
        ## need to take the non-repeated bit
        NX=int(sky.shape[0]*1361/1489.)
        NY=sky.shape[1]
        tsky.append(sky[:NX,:])
        # now get ra/dec coordinates
        ### Get coordinates
        #print d[2].data['XINTERP'].max(), d[2].data['YINTERP'].max()
        xo,xk=getLinCoef(d[2].data['XINTERP'][0],2048)
        yo,yk=getLinCoef(d[2].data['YINTERP'][0],1489)
        yint=interp1d(d[2].data['YINTERP'][0],np.arange(1489))
        print "Doing WCS..."
        w = wcs.WCS(d[0].header)
        pixlist=[]
        for i in range(NX):
            for j in range(NY):
                pixlist.append([xo+xk*j,yo+yk*i]) ### yes, this seems the right ordering
        pixlist=np.array(pixlist)
        world = w.wcs_pix2world(pixlist, 1)
        ra=world[:,0].reshape((NX,NY))
        dec=world[:,1].reshape((NX,NY))
        tra.append(ra)
        tdec.append(dec)
    tsky=np.vstack(tsky)
    tra=np.vstack(tra)
    tdec=np.vstack(tdec)
    return tra,tdec, tsky


def save_results(header,tra,tdec,tsky, root):
    if debug:
        plot_strip(tsky,root+'sky.png')
        plot_strip(tra,root+'ra.png')
        plot_strip(tdec,root+'dec.png')
    # now filter
    tskyf=filterAvg(tsky)
    print "done"
    if debug:
        plot_strip(tskyf,root+'skyf.png')
    np.savez(root+"data",(header,tsky,tra,tdec))
    

    
def filterFourier(s):
    Nx,Ny=s.shape
    fs=rfft2(s)
    fs[:,0]=0
    fs[0,:]=0
    return irfft2(fs)

def filterAvg(s):
    sr=s*1.0
    Nx,Ny=s.shape
    for i in range(Nx):
        sr[i,:]-=sr[i,:].mean()
    for j in range(Ny):
        sr[:,j]-=sr[:,j].mean()
    return sr
        


def plot_strip(d,fname):
    plt.figure(figsize=(16,4))
    plt.imshow(d.T,aspect='auto', interpolation='nearest')
    plt.colorbar()
    plt.savefig(fname)

if  __name__=="__main__":
    main()
