 
Photometric passbands 
=====================


Available response functions
----------------------------

To print a list of all available systems:

.. code-block:: python
   
   responses = list_response()
   systems = set([response.split('.')[0] for response in responses])
   for system in systems:
      bands = [band.split('.')[-1] for band in filters.list_response(name=system)]
      temp = "*{:>17s}: " + " ".join(["{}" for b in bands])
      print temp.format(system, *bands)


Transmission curves of some of the most commonly used systems plotted over a spectrum of an sdB+F type binary. The code to make these plots: :download:`scripts/plot_response_curves.py`.

APASS 
^^^^^
   
.. image:: images/filters_apass.png
   :width: 60em

JOHNSON 
^^^^^^^
   
.. image:: images/filters_johnson.png
   :width: 60em

SDSS 
^^^^
   
.. image:: images/filters_sdss.png
   :width: 60em
   
STROMGREN
^^^^^^^^^
   
.. image:: images/filters_stromgren.png
   :width: 60em   

2MASS
^^^^^
   
.. image:: images/filters_2mass.png
   :width: 60em 

Defining a new filter
---------------------

You can add custom filters on the fly using L{add_custom_filter}. In this
example we add a weird-looking filter and check the definition of Flambda and
Fnu and its relation to the effective wavelength of a passband:

Prerequisites: some modules that come in handy:

.. code-block:: python

   from ivs.sigproc import funclib
   from ivs.sed import model
   from ivs.units import conversions

First, we'll define a double peakd Gaussian profile on the wavelength grid of
the WISE.W3 response curve:

.. code-block:: python

   wave = get_response('WISE.W3')[0]
   trans = funclib.evaluate('gauss',wave,[1.5,76000.,10000.,0.])
   trans+= funclib.evaluate('gauss',wave,[1.0,160000.,25000.,0.])

This is what it looks like:

.. code-block:: python

   p = pl.figure()
   p = pl.plot(wave/1e4,trans,'k-')
   p = pl.xlabel("Wavelength [micron]")
   p = pl.ylabel("Transmission [arbitrary units]")



We can add this filter to the list of predefined filters in the following way
(for the doctests to work, we have to do a little work around and call
filters via that module, this is not needed in a normal workflow):

.. code-block:: python

   model.filters.add_custom_filter(wave,trans,photband='LAMBDA.CCD',type='CCD')
   model.filters.add_custom_filter(wave,trans,photband='LAMBDA.BOL',type='BOL')

Note that we add the filter twice, once assuming that it is mounted on a
bolometer, and once on a CCD device. We'll call the filter C{LAMBDA.CCD} and
C{LAMBDA.BOL}. From now on, they are available within functions as L{get_info}
and L{get_response}. For example, what is the effective (actually pivot)
wavelength?

.. code-block:: python

   effwave_ccd = model.filters.eff_wave('LAMBDA.CCD')
   effwave_bol = model.filters.eff_wave('LAMBDA.BOL')


Let's do some synthetic photometry now. Suppose we have a black body atmosphere:

.. code-block:: python

   bb = model.blackbody(wave,5777.)

We now calculate the synthetic flux, assuming the CCD and BOL device. We
compute the synthetic flux both in Flambda and Fnu:

.. code-block:: python

   flam_ccd,flam_bol = model.synthetic_flux(wave,bb,['LAMBDA.CCD','LAMBDA.BOL'])
   fnu_ccd,fnu_bol = model.synthetic_flux(wave,bb,['LAMBDA.CCD','LAMBDA.BOL'],units=['FNU','FNU'])

You can see that the fluxes can be quite different when you assume photon or
energy counting devices!

Can we now readily convert Flambda to Fnu with assuming the pivot wavelength?

.. code-block:: python

   fnu_fromflam_ccd = conversions.convert('erg/s/cm2/AA','erg/s/cm2/Hz',flam_ccd,wave=(effwave_ccd,'A'))
   fnu_fromflam_bol = conversions.convert('erg/s/cm2/AA','erg/s/cm2/Hz',flam_bol,wave=(effwave_bol,'A'))

Which is equivalent with:

.. code-block:: python

   fnu_fromflam_ccd = conversions.convert('erg/s/cm2/AA','erg/s/cm2/Hz',flam_ccd,photband='LAMBDA.CCD')
   fnu_fromflam_bol = conversions.convert('erg/s/cm2/AA','erg/s/cm2/Hz',flam_bol,photband='LAMBDA.BOL')

Apparently, with the definition of pivot wavelength, you can safely convert from
Fnu to Flambda


Temporarily modifying an existing filter
----------------------------------------

Under usual conditions, you are prohibited from overwriting an existing predefined
response curve. That is, if you try to L{add_custom_filter} with a C{photband}
that already exists as a file, a C{ValueError} will be raised (this is not the
case for a custom defined filter, which you can overwrite without problems!).
If, for testing purposes, you want to use another definition of a predefined
response curve, you need to set C{force=True} in L{add_custom_filter}, and then
call

.. code-block:: python

   set_prefer_file(False)

To reset and use the original definitions again, do

.. code-block:: python

   set_prefer_file(True)

Adding filters permanently
--------------------------

Add a new response curve file to the ivs/sed/filters directory. The file should
contain two columns, the first column is the wavelength in angstrom, the second
column is the transmission curve. The units of the later are not important.

Then, call L{update_info}. The contents of C{zeropoints.dat} will automatically
be updated. Make sure to add any additional information on the new filters
manually in that file (e.g. is t a CCD or bolometer, what are the zeropoint
magnitudes etc).