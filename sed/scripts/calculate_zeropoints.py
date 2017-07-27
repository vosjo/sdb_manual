 
import pyfits

import numpy as np
import pylab as pl

from ivs.sed import builder, model
from ivs.io import ascii
from ivs.units import conversions as cv
from ivs.units import constants as cc


photbands = ['2MASS.J', '2MASS.H', '2MASS.KS']

c1, c2 = 'J', 'Ks'

reference = 'VEGA' # 'VEGA' or 'AB'

minerror = 0.01 # minimum photometric error

s_reject = 10 # reject points outside s_reject * sigma on zp

basedir = '/home/joris/Python/ivsdata/sedtables/calibrators/'

calculate = False # true to calculate synthetic photomety, false to load it.

obsfile = 'observed_2MASS.dat' # file to save/load observed data
synfile = 'synthetic_2MASS.dat' # file to save/load synthetic data

#===================================================================================
# Get all necessary data
#===================================================================================

#-- Get the reference flux
if reference == 'VEGA':
   #-- calculate Flam based on the Vega spectrum
   hdu = pyfits.open('alpha_lyr_stis_008.fits')
   wave, flux = hdu[1].data['wavelength'], hdu[1].data['flux']
   hdu.close()

else:
   #-- calculate Flam for the AB system
   wave = np.arange(3000, 9000, step=0.5)
   flux = cv.convert(cc.cc_units, 'AA/s', cc.cc) / wave**2 * 3631e-23

Flam_0 = model.synthetic_flux(wave,flux,photbands=photbands)


#-- load the calibrators
calibrators = ascii.read2array(basedir+'calspec.ident', splitchar=',', dtype=str)


def get_synthetic_photometry(calibrator):
   """
   Integrate the spectrum belonging to this calibrator and return the synthetic magnitudes
   """
    
   hdu = pyfits.open(basedir+calibrator[1])
   wave, flux = hdu[1].data['wavelength'], hdu[1].data['flux']
   hdu.close()
   
   #-- integrate the flux over the 5 pass bands.
   flam = model.synthetic_flux(wave,flux,photbands=photbands)
   
   #-- convert fluxes to magnitudes (assuming Zp=0)
   mag = -2.5 * np.log10(flam / Flam_0)
   
   #-- only return is all bands are valid
   if any(np.isnan(mag)):
      return []
   
   return mag


def get_observed_photometry(calibrator):
   """
   Load the photometry file belonging to this calibrator and return the 
   observed magnitudes
   """
   
   sed = builder.SED(calibrator[0], load_fits=False, load_hdf5=False)
   sed.load_photometry(basedir+calibrator[2])
   
   photometry, error = [], []
   for pband in photbands:
      s = np.where(sed.master['photband'] == pband)
      
      #-- only return if all photbands have values
      if len(sed.master['meas'][s]) == 0:
         return [], []
      
      #-- only return if all photbands have a real value
      if any(np.isnan(sed.master['meas'][s])):
         return [], []
      
      photometry.append(sed.master['meas'][s][0])
      
      #-- if err is nan, replace with min error
      if np.isnan(sed.master['e_meas'][s][0]):
         error.append(minerror)
      else:
         error.append(sed.master['e_meas'][s][0])
      
   return np.array(photometry), np.array(error)

if calculate:
   #-- run over all calibrators and get synthetic and observed magnitudes
   synthetic = []
   observed = []
   for i, calibrator in enumerate(calibrators):
      
      print i+1, '/', len(calibrators)
      
      syn = get_synthetic_photometry(calibrator)
      
      #-- skip calibrator if synthetic photometry can't be computed
      if len(syn) == 0:
         #print 'fail'
         continue
      
      obs, err= get_observed_photometry(calibrator)
      
      #-- skip calibrator is no photometry is available
      if len(obs) == 0:
         #print 'fail'
         continue
      
      syn = [calibrator[0]] + list(syn)
      obs = [calibrator[0]] + list(obs) +list(err)
      
      synthetic.append(tuple(syn))
      observed.append(tuple(obs))

   #-- store in easy to use recarrays
   dtype = [('name', 'a20')] + [(pb.split('.')[-1] , 'f8') for pb in photbands]
   synthetic = np.array(synthetic, dtype=dtype)

   dtype = [('name', 'a20')] + [(pb.split('.')[-1] , 'f8') for pb in photbands] +\
         [('e_'+pb.split('.')[-1] , 'f8') for pb in photbands]
   observed = np.array(observed, dtype=dtype)

   #-- write results to file
   ascii.write_array(synthetic, synfile, sep=',')
   ascii.write_array(observed, obsfile, sep=',')
   
else:
   #-- load results from file
   dtype = [('name', 'a20')] + [(pb.split('.')[-1] , 'f8') for pb in photbands]
   synthetic = ascii.read2recarray(synfile, splitchar=',', dtype=dtype)
   dtype = [('name', 'a20')] + [(pb.split('.')[-1] , 'f8') for pb in photbands] +\
         [('e_'+pb.split('.')[-1] , 'f8') for pb in photbands]
   observed = ascii.read2recarray(obsfile, splitchar=',', dtype=dtype)


#-- add some minimal error is non is given observationaly
for band in ['e_'+pb.split('.')[-1] for pb in photbands]:
   observed[band] = np.where(observed[band]<=minerror, minerror, observed[band])

#===================================================================================
# Zero point calculation and plotting
#===================================================================================

def fit_zp(ax, band, c1, c2):
   """
   Get the zeropoint and plot the results
   """
   
   def mc(color, syn, obs, err):
      #-- Use MC simulation to get zero points and error
      zp, slope = [], []
      for i in range(1024):
         #-- add normal noise comparable with error
         obs_ = err * np.random.normal(len(obs)) + obs
         
         #-- calculate zp
         zp.append( np.average( syn - obs_ , weights=1./err ) )
         
         #-- calculate the slope
         coef = np.polyfit(color, syn - obs_, 1, w=1./err)
         slope.append(coef[0])
      
      #-- error and exact value for zp
      e_zp = np.std(zp)
      zp = np.average( syn - obs , weights=1./err )
      
      #-- error and exact value for slope
      coef = np.polyfit(color, syn - obs , 1, w=1./err)
      e_slope = np.std(slope)
      slope = coef[0]
      
      return zp, e_zp, slope, e_slope
   
   #-- Get the zero point and slope
   color = synthetic[c1]-synthetic[c2]
   
   syn = synthetic[band]
   obs = observed[band]
   err = observed['e_'+band]
   #err = 0.02*np.ones_like(syn)
   
   zp, e_zp, slope, e_slope = mc(color, syn, obs, err)
   
   #-- remove all points that have zero points above 3 sigma from the average
   #   and recalculate zero point and slope without outliers
   s = np.where(abs(syn - obs - zp) < s_reject*e_zp)
   
   color, syn, obs, err = color[s], syn[s], obs[s], err[s]
   
   zp, e_zp, slope, e_slope = mc(color, syn, obs, err)
   
   
   #-- get the linear fit for plotting
   coef = np.polyfit(color, syn - obs , 1, w=1./err)
   
   x = pl.linspace(np.min(color), np.max(color))
   y = np.polyval(coef, x)
   y1 = np.polyval([slope-e_slope, coef[1]], x)
   y2 = np.polyval([slope+e_slope, coef[1]], x)
   
   #-- plot
   pl.errorbar(color, 
               syn-obs, 
               yerr=err, ls='', marker='o')
   
   pl.plot(x, y, '-r')
   pl.plot(x, y1, '--r')
   pl.plot(x, y2, '--r')
   
   pl.axhline(y=zp, color='k', ls='--')
   
   
   pl.text(0.02, 0.98, "slope = {:0.2f} +- {:0.2f}".format(slope, e_slope),
           va='top', color='r', transform=ax.transAxes)
   
   pl.text(0.98, 0.98, "Average = {:0.3f} +- {:0.3f}".format(zp, e_zp), 
           va='top', ha='right', color='k', transform=ax.transAxes)
   
   pl.text(0.02, 0.02, "accepted = {:0.0f}   rejected = {:0.0f}".format(len(syn), 
                                                         len(synthetic) - len(syn) ),
           color='r', transform=ax.transAxes)
   
   pl.xlabel(c1+' - '+c2)
   pl.ylabel('syn - obs (mag)')
   pl.title("{} : Zp = {:0.3f} +- {:0.3f}".format(band, zp, e_zp))



pl.figure(1, figsize=(12, 5))
bands = [pb.split('.')[-1]  for pb in photbands]
for i, b in enumerate(bands):
   ax = pl.subplot(1, len(bands), i+1)
   fit_zp(ax, b, c1, c2)
pl.tight_layout()
pl.show()