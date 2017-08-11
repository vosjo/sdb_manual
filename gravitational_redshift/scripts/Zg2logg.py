import numpy as np
from ivs.units import constants, conversions

def get_error(sample, mean):
    
    sl = sample[sample <= mean]
    su = sample[sample >= mean]
    
    el = np.sqrt( np.sum( (sl - mean)**2 ) / (len(sl) - 1) ) / 2.
    eu = np.sqrt( np.sum( (su - mean)**2 ) / (len(su) - 1) ) / 2.
    
    return el, eu

def calc_gr(loggms, M1, M2, dv):
    
    G = constants.GG_cgs
    c = constants.cc_cgs
    Msol = constants.Msol_cgs
    
    gr_ms = 10**loggms/c * np.sqrt(G * M1 * Msol / 10**loggms)
    gr_ms = conversions.convert('cm s-1','km s-1',gr_ms) 

    gr_tot = gr_ms + dv

    gr = conversions.convert('km s-1','cm s-1',gr_tot)
    loggsdb = np.log10(gr**2 * c**2 / (G * M2 * Msol))
    
    return loggsdb

def calc_gr_mc(loggms, M1, M2, dv, n):
    
    loggsdb = calc_gr(loggms[0], M1[0], M2[0], dv[0])
    
    loggms = np.random.normal(loggms[0], loggms[1], n)
    M1 = np.random.normal(M1[0], M1[1], n)
    M2 = np.random.normal(M2[0], M2[1], n)
    dv = np.random.normal(dv[0], dv[1], n)
    
    loggsdbe = calc_gr(loggms, M1, M2, dv)
    el, eu = get_error(loggsdbe, loggsdb)
    
    return loggsdb, el, eu
      
if __name__ == "__main__":
    
    #BD-29.3070
    loggms = (4.32, 0.5)
    M1 = (1.19, 0.09)
    M2 = (0.47, 0.05)
    dv = (0.73, 1.46)
    
    #BD+34.1543
    loggms = (4.18, 0.40)
    M1 = (0.82, 0.07)
    M2 = (0.47, 0.05)
    dv = (1.01, 0.52)
    
    #Feige87
    loggms = (4.36, 0.42)
    M1 = (0.86, 0.07)
    M2 = (0.47, 0.05)
    dv = (1.34, 0.51)
    
    # HE0430-2457
    loggms = (4.50, 0.40)
    M1 = (0.73, 0.12)
    M2 = (0.18, 0.05)
    dv = (2.009, 0.25)

    n = 10000
    
    logg, el, eu = calc_gr_mc(loggms, M1, M2, dv, n)
    
    print 'logg sdB: %0.3f - %0.3f + %0.3f'%(logg, el, eu)


    


