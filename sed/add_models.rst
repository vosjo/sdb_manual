 
Adding new model SEDs
=====================

File locations in the ivs library
---------------------------------

Adding a new model
------------------

Integrating a model for use in SED fitting
------------------------------------------

Before a new models can be used in the SED fitting process, it needs to be pre-integrated over all photometric pass bands that you want to use, and this for different E(B-V)s that you want to be able to reach in the fit. 

The pre-integration is necessary to speed up the fitting process, and only needs to be done once. The integrated models are stored next to the original models and can be be extended if new photometric bands need to be added.

Information on how the SED fitting works is given in an earlier section.

.. hint::

   The larger the grid (in teff, logg, ebv, photbands, ...) the easier it is to apply in different usercases, but remember, the larger the grid, the more memory it will take when interpolating in the grid, and also the longer the interpolation will take. In some cases it might make sense to calculate a small grid focused on a specific usercase so that interpolation will go fast. Especially when a lot of user interaction is expected. You can make subgrids, and when using the sed fitting tools, you can directly specify the path to this smaller grid instead of giving a grid name. 

Creating a new integrated grid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some necessary imports

.. code-block:: python
   
   import numpy as np
   from ivs.sed import creategrids
   
Set the range in E(B-V) from 0 to 0.5 in steps of 0.02, and include all photometric bands in the GALEX, APASS, 2MASS and WISE system.
   
.. code-block:: python
   
   ebvs = np.r_[0:0.5:0.02]
   responses = ['GALEX', 'APASS', '2MASS', 'WISE']
   
Set the model for which you want to create the integrated grid. In this case we want to integrated the tmap models. Then call calc_integrated_grid to do the actual work. Some keywords to take care of are:

* ebvs: the range in E(B-V)
* law: the reddening law to use for E(B-V), fx. fitzpatrick2004
* Rv: The Rv value for the reddening law
* responses: array of photometric bands to include
* update: if True, then these integrated bands will be added to an already existing file, otherwise a possible existing file will be overwritted

This function returns the filename of the integrated grid that it just created. This file will always be writted in the directory where you are running this process, regardless of where exactly your other models are. Depending on your setup, you will have to copy the new file to the directory where the IVS repository will be looking for the integrated models.

   
.. code-block:: python
   
   model.set_defaults(grid='tmap')
   ifile = creategrids.calc_integrated_grid(threads=2, ebvs=ebvs, reponses=responses,
                                    law='fitzpatrick2004', Rv=3.1, update=False)
                                    
After the integration is done, call creategrids.fix_grid() to check the results are correct and to setup the headers. This function will first create a backup of the file it is going to modify. If the modification is sucessfull, you can delete the backup.

.. code-block:: python

   creategrids.fix_grid(ifile)
   
You can now check the structure of the integrated file

.. code-block:: python

   import pyfits
   print pyfits.getheader(ifile, 1)
   
   XTENSION= 'TABLE   '           / ASCII table extension                          
   BITPIX  =                    8 / array data type                                
   NAXIS   =                    2 / number of array dimensions                     
   NAXIS1  =                  885 / length of dimension 1                          
   NAXIS2  =                 8684 / length of dimension 2                          
   PCOUNT  =                    0 / number of group parameters                     
   GCOUNT  =                    1 / number of groups                               
   TFIELDS =                   59 / number of table fields                         
   KEY     =                  0.0                                                  
   TTYPE1  = 'teff    '                                                            
   TFORM1  = 'E15.7   '                                                            
   TBCOL1  =                    1                                                  
   TTYPE2  = 'logg    '                                                            
   TFORM2  = 'E15.7   '                                                            
   TBCOL2  =                   16                                                  
   TTYPE3  = 'ebv     '                                                            
   TFORM3  = 'E15.7   '                                                            
   TBCOL3  =                   31                                                  
   TTYPE4  = 'labs    '                                                            
   TFORM4  = 'E15.7   '                                                            
   TBCOL4  =                   46                                                  
   TTYPE5  = 'GALEX.FUV'                                                           
   TFORM5  = 'E15.7   '                                                            
   TBCOL5  =                   61                                                  
   TTYPE6  = 'GALEX.NUV'                                                           
   TFORM6  = 'E15.7   '                                                            
   TBCOL6  =                   76 
   ...
   
   print pyfits.getdata(ifile, 1)['ebv']
   
   array([ 0.        ,  0.02      ,  0.04      , ...,  0.46000001,
        0.47999999,  0.5       ], dtype=float32)

      

Appending to an existing grid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use the above function with while setting update=True, and making sure the ebv range you give is the same as the already ebv range in the file. Also, the calc_integrated_grid function will only write to a local file, so you need to make sure to call the function in the same directory where the file to update is.

An alternative is to use the update_grid function. This function takes the full path to the grid to update as an argument, and will automatically add the same ebv values as are currently in the file.

For example, if we want to extend the grid we calculated above with the GAIA passbands we can do:

.. code-block:: python
   
   model.set_defaults(grid='tmap')
   responses = ['GAIA']
   update_grid(ifile,responses,threads=2)
   
Here ifile is the name of the file containing the integrated grid you want to append to. You should not need to call fixgrid after this process.