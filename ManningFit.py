import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

data = pd.read_csv('MinnesotaJordan.tsv', sep='\t')

# To metric
data['Q'] /= 3.28**3
data['Stage'] /= 3.28

b = 70. # meters
S = 1E-4

def _manning(h, n, k_Qbank, P_Qbank, stage_depth_Q_offset, h_bank):
    """
    Returns discharge given flow depth, 
    * h: Input. Stage.
    * n: Manning's n
    * k_Qbank, P_Qbank: Power-law fititng parameters for floodplain hypsometry,
                        thereby controlling flow depth beyond the channel, that 
                        also fold in the value of Manning's n and slope
                        (k_Qbank) and the 2/3 exponent to h (P_Qbank)
    * stage_depth_Q_offset: Q(h=0), meant to solve for the offset between
                            bed elevation and flow stage
    * h_bank: Streambank elevation. This might be known a priori, but it can
              also be solved here as a function of the inflection in the
              rating-curve data
    """
    Q_ch = b * h**(5/3.) * S**(1/2.) / n
    _ob = (h > h_bank)
    Q_fp = _ob * k_Qbank * (h-h_bank)**(P_Qbank * _ob)
    return Q_ch + Q_fp + stage_depth_Q_offset

popt, pcov = curve_fit( _manning, data['Stage'], data['Q'] )

flow_params = { "Manning's n": [popt[0]],
                "Overbank flow coefficient": [popt[1]],
                "Overbank flow power-law exponent": [popt[2]]
              }

outparams = pd.DataFrame.from_dict(flow_params)

_h = np.arange(0.,10.1, 0.1)
plt.plot(data['Stage'], data['Q'], 'k.')
plt.plot(_h, _manning(_h, *popt))
b *= 2
plt.plot(_h, _manning(_h, *popt))

