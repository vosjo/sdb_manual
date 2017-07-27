import pylab as pl
import numpy as np

from ivs.sed import model, filters

#-- get the binary model
model.set_defaults_multiple({'grid':'tmapsdb'}, {'grid':'kuruczsdb'})
wave, flux = model.get_table(teff1=28000, logg1=5.8, rad1=0.15, teff2=6200, logg2=4.5, rad2=1.2)

#-- plotting function
def plot_bands(bands, xlim):
   ax1 = pl.subplot(111)
   pl.plot(wave, flux, '-b')
   ax2 = ax1.twinx()
   xticks, xlabels = [], []
   for band in bands:
      w, t = filters.get_response(band)
      xlabels.append(band.split('.')[-1])
      xticks.append(filters.eff_wave(band))
      ax2.plot(w, t, '--k')

   ax1.set_xlim(xlim)
   f_ = flux[(wave>=xlim[0]) & (wave<=xlim[-1])]
   ax1.set_ylim([0.95*np.min(f_), 1.1*np.max(f_)])
   ax2.set_ylim([0, 1])

   ax3 = ax2.twiny()
   ax3.set_xlim(ax2.get_xlim())
   ax3.set_xticks(xticks)
   ax3.set_xticklabels(xlabels)

   ax1.set_xlabel('Wavelength (AA)')
   ax1.set_ylabel('Flux (erg/s/cm2/AA)')
   ax2.set_ylabel('Transmission efficiency')
    
bands = ['JOHNSON.U','JOHNSON.B','JOHNSON.V','JOHNSON.R','JOHNSON.I']
pl.figure(1, figsize=(8, 4))
pl.subplots_adjust(left=0.09, bottom=0.13, right=0.92, top=0.92)
plot_bands(bands, [3000, 13000])

bands = ['STROMGREN.B', 'STROMGREN.U', 'STROMGREN.V', 'STROMGREN.Y']
pl.figure(2, figsize=(8, 4))
pl.subplots_adjust(left=0.09, bottom=0.13, right=0.92, top=0.92)
plot_bands(bands, [3000, 6000])

bands = filters.list_response('APASS')
pl.figure(3, figsize=(8, 4))
pl.subplots_adjust(left=0.09, bottom=0.13, right=0.92, top=0.92)
plot_bands(bands, [3000, 9000])

bands = filters.list_response('2MASS')
pl.figure(4, figsize=(8, 4))
pl.subplots_adjust(left=0.09, bottom=0.13, right=0.92, top=0.92)
plot_bands(bands, [9000, 25000])

bands = ['SDSS.U', 'SDSS.G', 'SDSS.R', 'SDSS.I', 'SDSS.Z']
pl.figure(5, figsize=(8, 4))
pl.subplots_adjust(left=0.09, bottom=0.13, right=0.92, top=0.92)
plot_bands(bands, [3000, 11000])

pl.show()