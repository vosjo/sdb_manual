 
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


============  =======
system        filters
============  =======
      TYCHO2  BT VT
       AKARI  L15 L18W L24 N160 N2 N3 N4 N60 S11 S7 S9W WIDEL WIDES
        OAO2  133 143 155 168 191 203 238 246 294 298 332 425
       SPIRE  250 350 500
   HIPPARCOS  HP
   STROMGREN  B U V Y B HBN HBW
       SLOAN  I R
        MIPS  160 24 70
        GAIA  BP G RP RVS
       ARGUE  R R8 R9
       SCUBA  350NB 450NB 450WB 750NB 850NB 850WB
       ESOIR  BRG CO H0 K0 L0 N N1 N2 N3 Q0
      ACSWFC  F435W F475W F502N F550M F555W F606W F625W F658N F660N F775W F814W F850LP
      USNOB1  B1 R1
     JOHNSON  I R U V 110 33 35 37 40 45 52 58 58P 63 72 80 86 99 B H I J K L M N R U V
       APASS  B G I R V
        APEX  LABOCA
         MSX  A B1 B2 C D E
     STISCCD  50CCD F28X50LP
    STEBBINS  B G I R U V
        WOOD  A B G H I O R T1 T2 U V Y
     LANDOLT  B2 B3 I R U V
        IRAC  36 45 58 80
        MAIA  GA GEO REO UA UEO
         TD1  1565 1965 2365 2740
      BESSEL  H J K L LPRIME M B BW I R U V
       VISIR  ARIII NEII NEII1 NEII2 PAH1 PAH2 PAH22 Q1 Q2 Q3 SIC SIV SIV1
       2MASS  H J KS
       WFCAM  H J K Y Z
       TYCHO  BT VT BT VT
      GENEVA  B B1 B2 G U V V1 B B1 B2 G U V V1
        KRON  I R
     COUSINS  I R V
     BALLOON  UV
        MOST  V
    WALRAVEN  B L U V W
CAMELOT-SDSS  G I R U Z
         DDO  35 38 41 42 45 48 51
       PLAVI  NIR SWIR VIS
      NICMOS  F110W F160W F187W F190N F205W F222M
        IRAS  F100 F12 F25 F60
    ULTRACAM  GP IP RP UP ZP
  SUPRIMECAM  B GP IC IP NB711 NB816 NB921 RC RP V ZP
       BRITE  B R
       GALEX  FUV NUV
        SDSS  G I R U Z G GP I IP R RP U UP Z ZP
        WISE  W1 W2 W3 W4
     BESSELL  B BW I R U V
        UVEX  G HA I R U
        PACS  B G R
        SAAO  35 38 41 42 45 48 H J K L M N Q
     CAMELOT  GAMMA I R U V G I R U Z B U V Y IZ1 IZ2
       DENIS  I J KS
     GENEVA2  B B1 B2 G U V V1
         ANS  15N 15W 18 22 25 33
       IPHAS  HA IP RP
     EEV4280  CCD
      NARROW  HA
       COROT  EXO SIS
     VILNIUS  P S U V X Y Z
  CAMELOT-BR  GAMMA
       DIRBE  F100 F12 F140 F1_25 F240 F25 F2_2 F3_5 F4_9 F60
============  =======


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