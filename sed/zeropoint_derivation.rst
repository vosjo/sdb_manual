
Calibrating Zero points 
=======================

The zero points of photometric filters can be derived from systems for which reliable flux calibrated spectroscopy is avaible. Especially in the case of all sky surveys it is not too hard to find such spectroscopy.

In this page, we will use spectra from the CALSPEC and the NGSL libraries to recalibrate the zeropoints of APASS. 

Spectral libraries
------------------

CALSPEC: `<http://www.stsci.edu/hst/observatory/crds/calspec.html>`_

NGSL: `<https://archive.stsci.edu/prepds/stisngsl/>`_

APASS
-----

APASS is the AAVSO Photometric All-Sky Survey. Its goal is to provide photometric coverage of the entire sky in 5 bands: B, V, g', r' and i', for all objects with a magnitude between 7 and 17. The current release is DR9. 

The B and V filters are Landolt B and V filters in the Vega Mag system. g', r' and i' are SDSS filters in the AB mag system. The filter database of VOSA provide transmission curves for all fiters, which we will use here.

APASS home page: `<https://www.aavso.org/apass>`_

Vizier access to data: `II/336/apass9 <http://vizier.u-strasbg.fr/viz-bin/VizieR?-source=II/336&-to=3>`_

Magnitude vs Flux
-----------------

To convert flux to magnitudes or the reverse, the zero point of the filter needs to be known. The conversion of flux the mag is given by:

.. math:: m = -2.5 \log{\left( \frac{f}{f_0} \right) } + z_p
   :label: magnitude_flux

where :math:`m` is the magnitude, :math:`f` is the flux, :math:`f_0` is the reference flux and :math:`z_p` is the zeropoint. Depending on the magnitude system in use, the reference flux can be calculated as:

.. math:: f_0(\rm Vega) = \int_{\lambda} p(\lambda)\ F_{\rm vega}\ d\lambda

.. math:: f_0(\rm AB) = \int_{\nu} p(\nu)\ 3631\ Jy\ d\nu = \int_{\lambda} p(\lambda) \frac{c}{\lambda^2}\ 3631\ Jy\ d\lambda

where :math:`p` is the transmission curve, :math:`F_{\rm vega}` is the vega flux and 3631 Jy is the constant flux density that is used as a reference in the AB mag system. This corresponds to :math:`3631 \cdot 10^{-23}` erg/s/cm2/Hz.

Zero point derivation
---------------------

If no zero points are published for a given photometric system, it is possible to derived them. To do this, you need to calculate synthetic magnitudes based on flux calibrated spectra, and compare them to actual observed magnitudes. To calculate the magnitudes from the spectra you use equation :eq:`magnitude_flux`, assuming that :math:`z_p=0`. 

The difference between the observed and the synthetic magnitude is then the zero point of that filter. By including lots of spectra, and averaging the derived zero points you can determine an accurate zeropoint as well as the expected error. The standard deviation of the zero points will also give you a reasonable guess on the reliability of the provided photometric errors. If the deviation of the zero points is larger than the errors, they are likely underestimated. 

Transmission curve correctness
------------------------------

If you have flux calibrated spectra of systems from different spectral classes, it is possible to check if the transmission curves you are using are correct. If the transmission curve is correct, the zero point should be completely independent of the spectral type. You can easily check this by plotting the derived zero points versus the color. 

Below the zero points derived for 56 systems in the 2MASS Ks are plotted versus the J - Ks color. There is a negelectable slope of -0.01 in the distribution, indicating that there is no significant variation of the zero point with spectral type. The transmission curve is thus likely correct.

.. image:: images/zero_point_2MASS_Ks.png
   :width: 50em
   
Full example
------------

Using the ivs python repository, we can derive zero points and the correlation between color and zero point using spectra from fx. CALSPEC. We assume that we have a file in which we list all systems together with the path to the spectrum, and the path to the phtometry file.

Necessary imports:

.. code-block:: python
   
   import pyfits

   import numpy as np
   import pylab as pl

   from ivs.sed import model
   from ivs.io import ascii
   from ivs.units import conversions as cv
   from ivs.units import constants as cc
   
Start with calculating the reference fluxes assuming that the B and V bands are in the Vega reference system. The flux calibrated vega spectrum (alpha_lyr_stis_008.fits) is provided by CALSPEC. The units of Flam_0 are erg/s/cm2/AA, because the flux of Vega is provided in these units.

.. code-block:: python

   photbands = ['APASS.B', 'APASS.V']
   
   hdu = pyfits.open('alpha_lyr_stis_008.fits')
   wave, flux = hdu[1].data['wavelength'], hdu[1].data['flux']
   hdu.close()
   
   Flam_0 = model.synthetic_flux(wave,flux,photbands=photbands)
   

Alternatively the reference flux in the AB reference system can be calculated as:

.. code-block:: python
   
   wave = np.arange(3000, 9000, step=0.5)
   flux = cv.convert(cc.cc_units, 'AA/s', cc.cc) / wave**2 * 3631e-23 # erg/s/cm2/AA
   
   Flam_0 = model.synthetic_flux(wave, flux, photbands=['APASS.G', 'APASS.R'])
   
Load the list of calibrators, which is given in format:

<system name>, <path to spectrum>, <path to photometry file>

And define functions to calculate the synthetic photometry by integrating the spectra, and return the observed photometry.

.. code-block:: python

   calibrators = ascii.read2array('calibrators.dat', splitchar=',', dtype=str)
   
   def get_synthetic_photometry(calibrator):
      """
      Integrate the spectrum belonging to this calibrator and return the synthetic magnitudes
      """
      
      hdu = pyfits.open(calibrator[1])
      wave, flux = hdu[1].data['wavelength'], hdu[1].data['flux']
      hdu.close()
      
      #-- integrate the flux over the 5 pass bands.
      flam = model.synthetic_flux(wave,flux,photbands=photbands)
      
      #-- convert fluxes to magnitudes (assuming Zp=0)
      return -2.5 * np.log10(flam / Flam_0)
      
   
   def get_observed_photometry(calibrator):
      """
      Load the photometry file belonging to this calibrator and return the observed magnitudes
      """
      
      master = ascii.read2recarray(calibrator[2])
      
      photometry, error = [], []
      for pband in photbands:
         s = np.where(master['photband'] == pband)
         
         photometry.append(master['meas'][s][0])
         error.append(master['e_meas'][s][0])
         
      return np.array(photometry), np.array(error)
      
Now run over all systems, for each get the synthetic and observed magnitudes and store them

.. code-block:: python

   synthetic = []
   observed = []
   for calibrator in calibrators:
      
      syn = get_synthetic_photometry(calibrator)     
      obs, err= get_observed_photometry(calibrator)
      
      synthetic.append(tuple(syn))
      observed.append(tuple(list(obs) +list(err)))
      
   #-- store in easy to use recarrays
   dtype = [(pb.split('.')[-1] , 'f8') for pb in photbands]
   synthetic = np.array(synthetic, dtype=dtype)

   dtype = [(pb.split('.')[-1] , 'f8') for pb in photbands] + [('e_'+pb.split('.')[-1] , 'f8') for pb in photbands]
   observed = np.array(observed, dtype=dtype)
   
We have the synthetic and observed magnitudes, so now we can easily derive the zero points.

.. code-block:: python

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
      
      #pl.text(0.98, 0.98, "Average = {:0.3f} +- {:0.3f}".format(zp, e_zp), 
            #va='top', ha='right', color='k', transform=ax.transAxes)
      
      pl.text(0.02, 0.02, "accepted = {:0.0f}   rejected = {:0.0f}".format(len(syn), 
                                                            len(synthetic) - len(syn) ),
            color='r', transform=ax.transAxes)
      
      pl.xlabel(c1+' - '+c2)
      pl.ylabel('syn - obs')
      pl.title("{} : Zp = {:0.3f} +- {:0.3f}".format(band, zp, e_zp))
      
   pl.figure(1)
   ax = pl.subplot(1, 2, 1)
   fit_zp(ax, 'B', 'B', 'V')
   ax = pl.subplot(1, 2, 2)
   fit_zp(ax, 'v', 'B', 'V')
   
   pl.figure(2)
   ax = pl.subplot(1, 3, 1)
   fit_zp(ax, 'G', 'G', 'I')
   ax = pl.subplot(1, 3, 2)
   fit_zp(ax, 'R', 'G', 'I')
   ax = pl.subplot(1, 3, 3)
   fit_zp(ax, 'I', 'G', 'I')
   pl.show()
   
Which produced these figures:
