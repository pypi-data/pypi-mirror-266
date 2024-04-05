import numpy 
from seidart.routines import prjrun, arraybuild, sourcefunction
from seidart.routines.definitions import *
from seidart.routines.arraybuild import getrcx
from glob2 import glob 
# Constants
prjfile = 'test_co.prj' 
rcxfile = 'receivers.xyz'
srcfile = 'sources.xyz'

# Initiate the model and domain objects
dom, mat, seis, em = prjrun.domain_initialization(prjfile)

# !!!! Meters or indices?
offsets = [3, 0, 0]
rgb = np.array([0,0,0])
xyz = rcxgen(rgb, dom, mat, filename = rcxfile)
# In this case, we want every 4 of the output xyz because when converting from
# PDF to png we doubled the points.
xyz = xyz[::4,:]
src = xyz + offsets

prjrun.status_check(
    seis, 
    mat,
    dom,
    prjfile, 
    seismic=True, 
    appendbool = True
)

prjrun.status_check(
    em, 
    mat,
    dom,
    prjfile, 
    seismic=False, 
    appendbool = True
)


# Create the source functions
st, fx, fy, fz, srcfn = sourcefunction(seis, 1e7, 'gaus1', 's')
# et, fx, fy, fz, srcfn = sourcefunction(em, 1e7, 'gaus1', 'e')

chan = 'Vz'
n = src.shape[0]
timeseries = np.zeros([int(seis.time_steps), n])
for ind in range(n):
    seis.x = src[ind, 0]
    seis.y = src[ind, 1]
    seis.z = src[ind, 2]
    prjrun.run(seis, mat, dom, seismic=True)
    source = np.array([int(seis.x), int(seis.z)])
    timeseries[:,ind] = getrcx(chan, xyz[ind,:], source, dom)
