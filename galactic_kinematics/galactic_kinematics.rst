 
Galactic Kinematics
===================

Galaxtic space velocity
-----------------------

Based on the radial velocity, the location, the proper motion and the distance to the sun the velocity of a star around the galactic center can be calculated. This velocity is expressed in three components U, V and W in units of km/s. The components are defind as:

   - U: positive in the direction of the Galactic Center
   - V: positive in the direction of the Galactic rotation
   - W: positive in the direction of the North Galactic Pole
   
.. warning::

   While the definition of V and W is standard, U is sometime positive towards the center, while in other cases it is positive towards the anti-center. 

To calculate the space velocity based on the propper motion, location, radial velocity and distance you can use the script below which is based on the method described by `Johnson & Soderblom (1987) <http://adsabs.harvard.edu/abs/1987AJ.....93..864J>`_.

.. code-block:: python

   import numpy as np
   
   ra, dec = None, None     # RA and Dec in degrees
   pmra, pmdec = None, None # propper motion  in mas/yr
   d = None                 # distance in parsec
   vrad = None              # radial velocity in km/s

   plx = 1e3 / d # parallax in mas

   cosd = np.cos(np.radians(dec))
   sind = np.sin(np.radians(dec))
   cosa = np.cos(np.radians(ra))
   sina = np.sin(np.radians(ra))

   k = 4.74047     #Equivalent of 1 A.U/yr in km/s   
   A_G = np.array( [ [ 0.0548755604, +0.4941094279, -0.8676661490],  
                   [ 0.8734370902, -0.4448296300, -0.1980763734], 
                   [ 0.4838350155,  0.7469822445, +0.4559837762] ]).T

   vec1 = vrad
   vec2 = k * pmra / plx
   vec3 = k * pmdec / plx

   u = ( A_G[0,0]*cosa*cosd+A_G[0,1]*sina*cosd+A_G[0,2]*sind)*vec1+ \
      (-A_G[0,0]*sina     +A_G[0,1]*cosa                   )*vec2+ \
      (-A_G[0,0]*cosa*sind-A_G[0,1]*sina*sind+A_G[0,2]*cosd)*vec3
   v = ( A_G[1,0]*cosa*cosd+A_G[1,1]*sina*cosd+A_G[1,2]*sind)*vec1+ \
      (-A_G[1,0]*sina     +A_G[1,1]*cosa                   )*vec2+ \
      (-A_G[1,0]*cosa*sind-A_G[1,1]*sina*sind+A_G[1,2]*cosd)*vec3
   w = ( A_G[2,0]*cosa*cosd+A_G[2,1]*sina*cosd+A_G[2,2]*sind)*vec1+ \
      (-A_G[2,0]*sina     +A_G[2,1]*cosa                   )*vec2+ \
      (-A_G[2,0]*cosa*sind-A_G[2,1]*sina*sind+A_G[2,2]*cosd)*vec3
   
   u = -u # U in Johnson & Soderblom is defined as positive outwards, so we switch here.
   
Local standard of rest
^^^^^^^^^^^^^^^^^^^^^^

As all of the properties (radial velocity, proper motion and distance) used to calculate U,V and W are measured with respect to the velocity of the Sun, the space velocity determined is the velocity of the star with respect to the Sun. This reference frame is also called the local standard of rest (LSR). To calculate the Galactic space velocity with respect to the center of the Galaxy, you need to subtract the velocity of the LSR. Different authors have derived the space velocity of the LSR based on the movements of nearby stars using different samples. There is a reasonable agreement in U and W between studies, but the values found for V can vary significantly as the determination of this velocity component is very dependent on the kinematical model used.

+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
| Reference                                                                         |   Source                          | U (km/s)      | V (km/s)     | W (km/s)     |
+===================================================================================+===================================+===============+==============+==============+
|`Annie et al. (2017) <http://adsabs.harvard.edu/abs/2017A%26A...605A...1R>`_       |    RAVE DR4 & GAIA                |  13.2 ± 1.3   |  0.9 ± 0.2   |   7.1 ± 0.2  |
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Bobylev & Bajkova (2016) <http://adsabs.harvard.edu/abs/2016AstL...42...90B>`_    |    RAVE DR4                       |  9.12 ± 0.10  |  20.8 ± 0.1  |   7.66 ± 0.08|
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Sharma et al. (2014) <http://adsabs.harvard.edu/abs/2014ApJ...793...51S>`_        |    RAVE DR4                       |  10.96 ± 0.14 |  7.53 ± 0.16 |   7.54 ± 0.09|
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Coskunoglu et al. (2011)  <http://adsabs.harvard.edu/abs/2011MNRAS.412.1237C>`_   |    RAVE DR3                       |  8.50 ± 0.29  |  13.38 ± 0.43|   6.49 ± 0.26|
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Bobylev & Bajkova (2010)  <http://adsabs.harvard.edu/abs/2010MNRAS.408.1788B>`_   |    Masers                         |  5.5 ± 2.2    |  11.0 ± 1.7  |   8.5 ± 1.2  |
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Breddels et al. (2010)    <http://adsabs.harvard.edu/abs/2010A%26A...511A..90B>`_ |    RAVE DR2                       |  12.0 ± 0.6   |  20.4 ± 0.5  |   7.8 ± 0.3  |
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Schönrich et al. (2010)   <http://adsabs.harvard.edu/abs/2010MNRAS.403.1829S>`_   |    Hipparcos                      |  11.10 ± 0.72 |  12.24 ± 0.47|   7.25 ± 0.36|
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Francis & Anderson (2009) <http://adsabs.harvard.edu/abs/2009NewA...14..615F>`_   |    Hipparcos                      |  7.5 ± 1.0    |  13.5 ± 0.3  |   6.8 ± 0.1  |
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Veltz et al. (2008)       <http://adsabs.harvard.edu/abs/2008A%26A...480..753V>`_ |    RAVE DR1                       |  8.5 ± 0.3    |  /           |   11.1 ± 1.0 |
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Bobylev & Bajkova (2007) <http://adsabs.harvard.edu/abs/2007ARep...51..372B>`_    |    F and G dwarfs                 |  8.7 ± 0.5    |  6.2 ± 2.2   |   7.2 ± 0.8  |
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Piskunov et al. (2006)   <http://adsabs.harvard.edu/abs/2006A%26A...445..545P>`_  |    Open clusters                  |  9.44 ± 1.14  |  11.90 ± 0.72|   7.20 ± 0.42|
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Mignard (2000)           <http://adsabs.harvard.edu/abs/2000A%26A...354..522M>`_  |    K0−K5                          |  9.88         |  14.19       |   7.76       |
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Dehnen & Binney (1998)   <http://adsabs.harvard.edu/abs/1998MNRAS.298..387D>`_    |    Hipparcos, dmax = 100 pc       |  10.00 ± 0.36 |  5.25 ± 0.62 |   7.17 ± 0.38|
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+
|`Binney et al. (1997)     <http://adsabs.harvard.edu/abs/1997ESASP.402..473B>`_    |   Stars near South Celestial Pole |  11 ± 0.6     |  5.3 ± 1.7   |   7.0 ± 0.6  |
+-----------------------------------------------------------------------------------+-----------------------------------+---------------+--------------+--------------+

.. note::

   The local standard of rest is not exactly the motion of the Sun, but the mean motion of the material in the Milky Way in the neighbourhood of the sun. It is defined as the rest frame of a star at the location of the Sun that would be on a circular orbit in the gravitational potential of the Galaxy.

Where U,V and W are in all cases defined as above, with U positive towards the Galactic center. Table is taken from `Coskunoglu et al. (2011)  <http://adsabs.harvard.edu/abs/2011MNRAS.412.1237C>`_ and updated with more recent data. The LSR of Dehnen & Binney (1998) is still widely used. 

Population membership
---------------------