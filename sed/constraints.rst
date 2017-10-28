 
Constraints
===========

Mass-ratio in binary fits
-------------------------

In a binary fit it is possible to use the mass ratio obtained from a radial velocity study to constrain the models. The synthetic mass ratio of the models can be derived from their parameters.

The mass (M) of a star can be linked to it's radius (R) and surface gravity (g) using the gravitational constant (G):

.. math::
   R = \sqrt{ \frac{G\,M}{g} } \rightarrow M = \frac{R^2\,g}{G}
   
In the cgs system these have the folowing units [M] = g, [R] = cm, [g] = cm s-2 and the gravitation constant is G = 6.67384e-08 cm3 g-1 s-2

The mass-ratio (q) is then given by:

.. math::
   q = \frac{M_2}{M_1} = \frac{R_2^2\,g_2}{R_1^2\,g_1} = \frac{R_2^2\, 10^{logg_2}}{R_1^2\, 10^{logg_1}}
   
Where the gravitational constant cancels out, and the units of R don't matter (but are solar radii in the SED fitting code). The SED fitting code also uses the log of the surface gravity, where the surface gravity itself is expresed in cgs units. 