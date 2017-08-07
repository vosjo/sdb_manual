
import pylab as pl
import numpy as np

from ivs.sed import model

def plot_grid(gridname, marker):
   teffs,loggs = model.get_grid_dimensions(grid=gridname)
   pl.plot(np.log10(teffs), loggs, marker=marker, ls='', ms=7, label=gridname)
   
   

pl.figure(1)


teffs,loggs = model.get_grid_dimensions(grid='kurucz2')
pl.plot(np.log10(teffs), loggs, 'o', mec='b', mfc='w', mew=1.5, ms=7, label='kurucz2')

teffs,loggs = model.get_grid_dimensions(grid='tmap')
pl.plot(np.log10(teffs), loggs, '+', mew=2, ms=7, label='tmap')

pl.xlabel('Effective temperature [K]')
pl.ylabel('log( Surface gravity [cm s$^{-1}$]) [dex]')
xticks = [3000,5000,7000,10000,15000,25000,35000,50000,100000]
pl.xticks([np.log10(i) for i in xticks],['%d'%(i) for i in xticks])
pl.legend(loc='upper left',prop=dict(size='small'))
pl.ylim([-0.1, 6.6])
pl.grid()
pl.gca().invert_xaxis()
pl.gca().invert_yaxis()
pl.tight_layout()

pl.savefig('../images/models_overview.png', dpi=300)

pl.show()
