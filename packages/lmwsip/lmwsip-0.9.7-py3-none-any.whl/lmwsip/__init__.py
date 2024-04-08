"""Module to support the LmwSip class

See: LmwSip"""

import socket
import ssl
import select
import time
import re
import logging
from datetime import datetime, timedelta
from dateutil import tz

""" Version info changed by git hook """
__version__ = '0.9.7'

class LmwSip:
    """Class to connect to the LMW Standard Interface prototcol (sip)
    
This class iplement connection to the Rijkswaterstaat Meetnet
Water (LMW) with the Standard Interface Protocol using the
Rijkswaterstaat Meetnet Infrastructuur (RMI).

https://waterberichtgeving.rws.nl/water-en-weer/metingen

Support for:
    ti
    cmd(wn, vw, as)

lmwParameters:
 - Type: WN, VW, AS
 - Array size: [1-201]
 - Periode: 1, 10
"""

    lmwParameters = {
        'Tm02_MV': ('VW', 1, 0),
        'xH1': ('WN', 1, 1),
        'HH1S': ('WN', 1, 1),
        'SRV1': ('WN', 1, 1),
        'TL1': ('WN', 1, 1),
        'SRV1w1': ('WN', 1, 1),
        'SRV1w2': ('WN', 1, 1),
        'SRV1w3': ('WN', 1, 1),
        'xTL1': ('WN', 1, 1),
        'DO1': ('WN', 1, 1),
        'SSV1': ('WN', 1, 1),
        'SSV1w3G': ('WN', 1, 1),
        'SSV1w3': ('WN', 1, 1),
        'SSV1w2G': ('WN', 1, 1),
        'SSV1w2': ('WN', 1, 1),
        'SSV1w1G': ('WN', 1, 1),
        'H1Z': ('WN', 1, 1),
        'SSV1w1': ('WN', 1, 1),
        'H1': ('WN', 1, 1),
        'bSSVG1': ('WN', 1, 1),
        'xWS1': ('WN', 1, 1),
        'HG1Z': ('WN', 1, 1),
        'WS1': ('WN', 1, 1),
        'HG1': ('WN', 1, 1),
        'WR1': ('WN', 1, 1),
        'ZA1': ('WN', 1, 1),
        'ZM1': ('WN', 1, 1),
        'H1RC': ('WN', 1, 1),
        'bSRV1': ('WN', 1, 1),
        'bSSV1': ('WN', 1, 1),
        'xWR1': ('WN', 1, 1),
        'THmax': ('WN', 1, 10),
        'Th0_B4': ('WN', 1, 10),
        'Th0': ('WN', 1, 10),
        'Th0_G1': ('WN', 1, 10),
        'Th0_B3': ('WN', 1, 10),
        'Th0_G10': ('WN', 1, 10),
        'Th010': ('WN', 51, 10),
        'Th0_G7': ('WN', 1, 10),
        'Th0_B0': ('WN', 1, 10),
        'Th0_G6': ('WN', 1, 10),
        'Th0_G2': ('WN', 1, 10),
        'Th0_G3': ('WN', 1, 10),
        'Th0_B2': ('WN', 1, 10),
        'Th0_B1': ('WN', 1, 10),
        'Th0_G5': ('WN', 1, 10),
        'Th0_G4': ('WN', 1, 10),
        'Th0_G8': ('WN', 1, 10),
        'Th0_G9': ('WN', 1, 10),
        'TW10S': ('WN', 1, 10),
        'U10': ('WN', 1, 10),
        'UUR10': ('WN', 1, 10),
        'Th3V': ('VW', 1, 10),
        'V10': ('WN', 1, 10),
        'V10S': ('WN', 1, 10),
        'WC10': ('WN', 1, 10),
        'WC10MXS3': ('WN', 1, 10),
        'WC10V': ('VW', 1, 10),
        'TW10': ('WN', 1, 10),
        'Tm_10_M': ('WN', 1, 10),
        'Tmax': ('WN', 1, 10),
        'Th3': ('WN', 1, 10),
        'Tm_10': ('WN', 1, 10),
        'TL10': ('WN', 1, 10),
        'TL10MNM1': ('WN', 1, 10),
        'TL10MXM1': ('WN', 1, 10),
        'Tm02': ('WN', 1, 10),
        'Tm02V': ('VW', 1, 10),
        'Tm02V_M': ('VW', 1, 10),
        'Tm02_M': ('WN', 1, 10),
        'WDG10': ('WN', 1, 10),
        'TH1d3': ('WN', 1, 10),
        'S0bh_G10': ('WN', 1, 10),
        'SPGH': ('WN', 1, 10),
        'SPGT': ('WN', 1, 10),
        'SRV10': ('WN', 1, 10),
        'SRV10m': ('WN', 50, 10),
        'SRV10STD': ('WN', 1, 10),
        'SRV10V': ('VW', 1, 10),
        'SRV10w1': ('WN', 1, 10),
        'SRV10w2': ('WN', 1, 10),
        'SRV10w3': ('WN', 1, 10),
        'SS10': ('WN', 1, 10),
        'SH10': ('WN', 1, 10),
        'SG10': ('WN', 1, 10),
        'SEC10': ('WN', 1, 10),
        'S0bh_G2': ('WN', 1, 10),
        'S0bh_G3': ('WN', 1, 10),
        'S0bh_G4': ('WN', 1, 10),
        'S0bh_G5': ('WN', 1, 10),
        'S0bh_G6': ('WN', 1, 10),
        'S0bh_G7': ('WN', 1, 10),
        'S0bh_G8': ('WN', 1, 10),
        'S0bh_G9': ('WN', 1, 10),
        'SAL10': ('WN', 1, 10),
        'SD10': ('WN', 1, 10),
        'SSG10': ('WN', 1, 10),
        'SSV10': ('WN', 1, 10),
        'SSV10A': ('AS', 1, 10),
        'T10': ('WN', 1, 10),
        'T1d3': ('WN', 1, 10),
        'T1d3V': ('VW', 1, 10),
        'TD10': ('WN', 1, 10),
        'TD10M1': ('WN', 1, 10),
        'TE0': ('WN', 1, 10),
        'TE1': ('WN', 1, 10),
        'TE1_M': ('WN', 1, 10),
        'TE2': ('WN', 1, 10),
        'TE3': ('WN', 1, 10),
        'Stat10Sm': ('WN', 50, 10),
        'Stat10S': ('WN', 1, 10),
        'ST10': ('WN', 1, 10),
        'SSV10m': ('WN', 50, 10),
        'SSV10V': ('VW', 1, 10),
        'SSV10w1': ('WN', 1, 10),
        'SSV10w1G': ('WN', 1, 10),
        'SSV10w2': ('WN', 1, 10),
        'SSV10w2G': ('WN', 1, 10),
        'SSV10w3': ('WN', 1, 10),
        'SSV10w3G': ('WN', 1, 10),
        'SSVG10': ('WN', 1, 10),
        'SSVG10V': ('VW', 1, 10),
        'TE3V': ('VW', 1, 10),
        'xP10': ('WN', 1, 10),
        'xSS10': ('WN', 1, 10),
        'xSSV10': ('WN', 1, 10),
        'xT1d3': ('WN', 1, 10),
        'xTD10': ('WN', 1, 10),
        'xTD10M1': ('WN', 1, 10),
        'xTE1': ('WN', 1, 10),
        'xTE2': ('WN', 1, 10),
        'xTE3': ('WN', 1, 10),
        'xTH1d3': ('WN', 1, 10),
        'xTHmax': ('WN', 1, 10),
        'xTh0': ('WN', 1, 10),
        'xSRV10': ('WN', 1, 10),
        'xSPGT': ('WN', 1, 10),
        'xSPGH': ('WN', 1, 10),
        'xPC10': ('WN', 1, 10),
        'xPH': ('WN', 1, 10),
        'xPH10': ('WN', 1, 10),
        'xPQFE10': ('WN', 1, 10),
        'xPQFF10': ('WN', 1, 10),
        'xPQNH10': ('WN', 1, 10),
        'xQ10': ('WN', 1, 10),
        'xQ10B': ('VW', 1, 10),
        'xR10': ('WN', 1, 10),
        'xRS10': ('WN', 1, 10),
        'xSH10P': ('WN', 1, 10),
        'xTh3': ('WN', 1, 10),
        'xTL10': ('WN', 1, 10),
        'xWR10': ('WN', 1, 10),
        'xWR10STD': ('WN', 1, 10),
        'xWS10': ('WN', 1, 10),
        'xWS10MX': ('WN', 1, 10),
        'xWS10MXS': ('WN', 1, 10),
        'xWS10STD': ('WN', 1, 10),
        'xWS10XS1': ('WN', 1, 10),
        'xZM10': ('WN', 1, 10),
        'ZA10': ('WN', 1, 10),
        'ZM10': ('WN', 1, 10),
        'ZMT10': ('WN', 1, 10),
        'xWC10MXS': ('WN', 1, 10),
        'xWC10': ('WN', 1, 10),
        'xVE10s': ('WN', 1, 10),
        'xTL10MNM': ('WN', 1, 10),
        'xTL10MXM': ('WN', 1, 10),
        'xTm02': ('WN', 1, 10),
        'xTmax': ('WN', 1, 10),
        'xTm_10': ('WN', 1, 10),
        'xTT10P': ('WN', 1, 10),
        'xTW10': ('WN', 1, 10),
        'xU10': ('WN', 1, 10),
        'xV10': ('WN', 1, 10),
        'xVE10': ('WN', 1, 10),
        'xVE10S': ('WN', 1, 10),
        'ZV10S': ('WN', 1, 10),
        'WI': ('BL', 8, 10),
        'xBS10S': ('WN', 1, 10),
        'xBS1S': ('WN', 1, 1),
        'xBS10s': ('WN', 1, 10),
        'xC10P': ('WN', 1, 10),
        'xCHL10': ('WN', 1, 10),
        'xCL10': ('WN', 1, 10),
        'xCzz10': ('WN', 51, 10),
        'xCzz5': ('WN', 25, 10),
        'xD10': ('WN', 1, 10),
        'xDO10': ('WN', 1, 10),
        'xDO10P': ('WN', 1, 10),
        'xFp': ('WN', 1, 10),
        'xBM10s': ('WN', 1, 10),
        'xBM10S': ('WN', 1, 10),
        'xAV10_H': ('WN', 1, 10),
        'WNR10': ('WN', 1, 10),
        'WR10': ('WN', 1, 10),
        'WR10STD': ('WN', 1, 10),
        'WR10V': ('VW', 1, 10),
        'WS10': ('WN', 1, 10),
        'WS10MX10': ('WN', 1, 10),
        'WS10MXS3': ('WN', 1, 10),
        'WS10STD': ('WN', 1, 10),
        'WS10V': ('VW', 1, 10),
        'xAG': ('WN', 1, 10),
        'xANT10': ('WN', 1, 10),
        'xGE10': ('WN', 1, 10),
        'xGGH': ('WN', 1, 10),
        'xHS7': ('WN', 1, 10),
        'xHTE3': ('WN', 1, 10),
        'xKH10B': ('VW', 1, 10),
        'xM0': ('WN', 1, 10),
        'xNdlr_H': ('WN', 1, 10),
        'xNd_z': ('WN', 1, 10),
        'xNgd_zP': ('WN', 1, 10),
        'xNI10': ('WN', 1, 10),
        'xNi_z': ('WN', 1, 10),
        'xNu_z': ('WN', 1, 10),
        'xNv_z': ('WN', 1, 10),
        'xHmax': ('WN', 1, 10),
        'xHm0': ('WN', 1, 10),
        'xHHR10': ('WN', 1, 10),
        'xGGT': ('WN', 1, 10),
        'xH10': ('WN', 1, 10),
        'xH10BV': ('VW', 1, 10),
        'xH10R': ('WN', 1, 10),
        'xH10Z': ('WN', 1, 10),
        'xH1d10': ('WN', 1, 10),
        'xH1d3': ('WN', 1, 10),
        'xH1d50': ('WN', 1, 10),
        'xHCM': ('WN', 1, 10),
        'xHH10': ('WN', 1, 10),
        'xHH10R': ('WN', 1, 10),
        'xNwt_zP': ('WN', 1, 10),
        'G1_B0': ('WN', 1, 10),
        'G2_B0': ('WN', 1, 10),
        'G2_B1': ('WN', 1, 10),
        'G2_B2': ('WN', 1, 10),
        'G2_B3': ('WN', 1, 10),
        'G2_B4': ('WN', 1, 10),
        'G2_G1': ('WN', 1, 10),
        'G2_G10': ('WN', 1, 10),
        'G2_G2': ('WN', 1, 10),
        'G2_G3': ('WN', 1, 10),
        'G2_G4': ('WN', 1, 10),
        'G2_G5': ('WN', 1, 10),
        'G1_G9': ('WN', 1, 10),
        'G1_G8': ('WN', 1, 10),
        'G1_G7': ('WN', 1, 10),
        'G1_B1': ('WN', 1, 10),
        'G1_B2': ('WN', 1, 10),
        'G1_B3': ('WN', 1, 10),
        'G1_B4': ('WN', 1, 10),
        'G1_G1': ('WN', 1, 10),
        'G1_G10': ('WN', 1, 10),
        'G1_G2': ('WN', 1, 10),
        'G1_G3': ('WN', 1, 10),
        'G1_G4': ('WN', 1, 10),
        'G1_G5': ('WN', 1, 10),
        'G1_G6': ('WN', 1, 10),
        'G2_G6': ('WN', 1, 10),
        'G2_G7': ('WN', 1, 10),
        'G2_G8': ('WN', 1, 10),
        'GK': ('BL', 11, 10),
        'GKZ': ('BL', 11, 10),
        'GO': ('BL', 70, 10),
        'GO_H': ('BL', 35, 10),
        'GO_L': ('BL', 35, 10),
        'GR': ('BL', 107, 10),
        'GRZ': ('BL', 107, 10),
        'GW': ('BL', 6, 10),
        'H10': ('WN', 1, 10),
        'H10A': ('AS', 1, 10),
        'H10RC': ('WN', 1, 10),
        'GH_M': ('BL', 27, 10),
        'GHZ': ('BL', 128, 10),
        'GHRZ': ('BL', 78, 10),
        'G2_G9': ('WN', 1, 10),
        'GB': ('BL', 35, 10),
        'GE10': ('WN', 1, 10),
        'GE10S': ('WN', 1, 10),
        'GGH': ('WN', 1, 10),
        'GGT': ('WN', 1, 10),
        'GH': ('BL', 27, 10),
        'GH2': ('BL', 27, 10),
        'GHC': ('BL', 76, 10),
        'GHC_M': ('BL', 126, 10),
        'GHR': ('BL', 128, 10),
        'H10V': ('VW', 1, 10),
        'AB': ('BL', 256, 10),
        'bSSV10': ('WN', 1, 10),
        'bSSVG10': ('WN', 1, 10),
        'C10P': ('WN', 1, 10),
        'C110S': ('WN', 1, 10),
        'C210S': ('WN', 1, 10),
        'C310S': ('WN', 1, 10),
        'CHL10': ('WN', 1, 10),
        'CL10': ('WN', 1, 10),
        'Cor10': ('WN', 1, 10),
        'Cor10m': ('WN', 50, 10),
        'CX10S': ('WN', 1, 10),
        'bSRV10': ('WN', 1, 10),
        'bQ10': ('WN', 1, 10),
        'bH10': ('WN', 1, 10),
        'AG': ('WN', 1, 10),
        'AL': ('BL', 35, 10),
        'AV10_H': ('WN', 1, 10),
        'AV10_R': ('WN', 1, 10),
        'BCor10': ('WN', 1, 10),
        'BEcho10': ('WN', 1, 10),
        'BH10': ('WN', 1, 10),
        'BNgd10P': ('WN', 1, 10),
        'BSRV10': ('WN', 1, 10),
        'BSSV10': ('WN', 1, 10),
        'BT10': ('WN', 1, 10),
        'Czz10': ('WN', 51, 10),
        'Czz10_M': ('WN', 101, 10),
        'Czz5': ('WN', 25, 10),
        'Fm01_G1': ('WN', 1, 10),
        'Fm01_G10': ('WN', 1, 10),
        'Fm01_G2': ('WN', 1, 10),
        'Fm01_G3': ('WN', 1, 10),
        'Fm01_G4': ('WN', 1, 10),
        'Fm01_G5': ('WN', 1, 10),
        'Fm01_G6': ('WN', 1, 10),
        'Fm01_G7': ('WN', 1, 10),
        'Fm01_G8': ('WN', 1, 10),
        'Fm01_G9': ('WN', 1, 10),
        'Fp': ('WN', 1, 10),
        'Fm01_B4': ('WN', 1, 10),
        'Fm01_B3': ('WN', 1, 10),
        'Fm01_B2': ('WN', 1, 10),
        'D10': ('WN', 1, 10),
        'D10S': ('WN', 1, 10),
        'DH10': ('WN', 1, 10),
        'DL_index': ('WN', 1, 10),
        'DO10': ('WN', 1, 10),
        'DO10P': ('WN', 1, 10),
        'DT10': ('WN', 1, 10),
        'Echo10': ('WN', 1, 10),
        'Echo10m': ('WN', 50, 10),
        'Fm01_B0': ('WN', 1, 10),
        'Fm01_B1': ('WN', 1, 10),
        'Fp_M': ('WN', 1, 10),
        'H10Z': ('WN', 1, 10),
        'ND10': ('WN', 1, 10),
        'Ndlr_H': ('WN', 1, 10),
        'Ndlr_R': ('WN', 1, 10),
        'Nd_x': ('WN', 1, 10),
        'Nd_y': ('WN', 1, 10),
        'Nd_z': ('WN', 1, 10),
        'Ngd10P': ('WN', 1, 10),
        'Ngd10Pm': ('WN', 50, 10),
        'Ngd_xP': ('WN', 1, 10),
        'Ngd_yP': ('WN', 1, 10),
        'Ngd_zP': ('WN', 1, 10),
        'NI10': ('WN', 1, 10),
        'Ni_x': ('WN', 1, 10),
        'Ndfe_G9': ('WN', 1, 10),
        'Ndfe_G8': ('WN', 1, 10),
        'Ndfe_G7': ('WN', 1, 10),
        'Ndfe_B0': ('WN', 1, 10),
        'Ndfe_B1': ('WN', 1, 10),
        'Ndfe_B2': ('WN', 1, 10),
        'Ndfe_B3': ('WN', 1, 10),
        'Ndfe_B4': ('WN', 1, 10),
        'Ndfe_G1': ('WN', 1, 10),
        'Ndfe_G10': ('WN', 1, 10),
        'Ndfe_G2': ('WN', 1, 10),
        'Ndfe_G3': ('WN', 1, 10),
        'Ndfe_G4': ('WN', 1, 10),
        'Ndfe_G5': ('WN', 1, 10),
        'Ndfe_G6': ('WN', 1, 10),
        'Ni_y': ('WN', 1, 10),
        'Ni_z': ('WN', 1, 10),
        'PQFF10': ('WN', 1, 10),
        'PQNH10': ('WN', 1, 10),
        'PW10': ('WN', 1, 10),
        'Q10': ('WN', 1, 10),
        'Q10V': ('VW', 1, 10),
        'S0bh': ('WN', 1, 10),
        'S0bh10': ('WN', 51, 10),
        'S0bh_B0': ('WN', 1, 10),
        'S0bh_B1': ('WN', 1, 10),
        'S0bh_B2': ('WN', 1, 10),
        'S0bh_B3': ('WN', 1, 10),
        'S0bh_B4': ('WN', 1, 10),
        'PQFE10': ('WN', 1, 10),
        'PH': ('WN', 1, 10),
        'PC10': ('WN', 1, 10),
        'NtrackS': ('WN', 1, 10),
        'Nu_x': ('WN', 1, 10),
        'Nu_y': ('WN', 1, 10),
        'Nu_z': ('WN', 1, 10),
        'Nv_x': ('WN', 1, 10),
        'Nv_y': ('WN', 1, 10),
        'Nv_z': ('WN', 1, 10),
        'Nwt_zP': ('WN', 1, 10),
        'NzoekS': ('WN', 1, 10),
        'OL10S': ('WN', 1, 10),
        'OT10': ('WN', 1, 10),
        'P10': ('WN', 1, 10),
        'S0bh_G1': ('WN', 1, 10),
        'H10ZV': ('VW', 1, 10),
        'Hm0_B2': ('WN', 1, 10),
        'Hm0_B3': ('WN', 1, 10),
        'Hm0_B4': ('WN', 1, 10),
        'Hm0_G1': ('WN', 1, 10),
        'Hm0_G10': ('WN', 1, 10),
        'Hm0_G2': ('WN', 1, 10),
        'Hm0_G4': ('WN', 1, 10),
        'Hm0_G5': ('WN', 1, 10),
        'Hm0_G6': ('WN', 1, 10),
        'Hm0_G7': ('WN', 1, 10),
        'Hm0_G8': ('WN', 1, 10),
        'Hm0_G9': ('WN', 1, 10),
        'Hm0_B1': ('WN', 1, 10),
        'Hm0_B0': ('WN', 1, 10),
        'Hm0V': ('VW', 1, 10),
        'H1d10': ('WN', 1, 10),
        'H1d3': ('WN', 1, 10),
        'H1d3V': ('VW', 1, 10),
        'H1d50': ('WN', 1, 10),
        'Hb10': ('WN', 1, 10),
        'HCM': ('WN', 1, 10),
        'HG10': ('WN', 1, 10),
        'HG10Z': ('WN', 1, 10),
        'HH10': ('WN', 1, 10),
        'HH10S': ('WN', 1, 10),
        'HMR': ('BL', 159, 10),
        'Hm0': ('WN', 1, 10),
        'Hm0_M': ('WN', 1, 10),
        'Hmax': ('WN', 1, 10),
        'HS7': ('WN', 1, 10),
        'LG10': ('WN', 48, 10),
        'LGK10V': ('VW', 1, 10),
        'LGNf_z': ('WN', 1, 10),
        'LGNik_z': ('WN', 1, 10),
        'LGNvd_z': ('WN', 1, 10),
        'LGNv_z': ('WN', 1, 10),
        'M0': ('WN', 1, 10),
        'M0_M': ('WN', 1, 10),
        'MDG10': ('WN', 1, 10),
        'MIN10': ('WN', 1, 10),
        'MNR10': ('WN', 1, 10),
        'L10': ('WN', 1, 10),
        'KT10P': ('WN', 1, 10),
        'HTE3': ('WN', 1, 10),
        'Hm0_G3': ('WN', 1, 10),
        'NB10S': ('WN', 1, 10),
        'HTE3V': ('VW', 1, 10),
        'I10': ('WN', 1, 10),
        'JNR10': ('WN', 1, 10),
        'IL10P': ('WN', 1, 10),
        'JDG10': ('WN', 1, 10),
        'xQ30': ('WN', 1, 30),
        'xNI30': ('WN', 1, 30),
        'xH30': ('WN', 1, 30),
        'xH30R': ('WN', 1, 30),
        'xH60': ('WN', 1, 60),
        'xNI60': ('WN', 1, 60),
        'xQ60': ('WN', 1, 60),
        'xH60R': ('WN', 1, 60),
        'QfQStt10': ('WN', 1, 10),
        'QfQTr10': ('WN', 1, 10),
        'QfQSt10': ('WN', 1, 10),
        'QfHYS10': ('WN', 1, 10),
        'QfQSy10': ('WN', 1, 10)
    }

    def __init__(self, user=None, password=None,
            host="sip-lmw.rws.nl", port=443, meetnet="LMW", ssl = True,
            check_ssl = True, timeout = 10, log = None, cleartelnet = False,
            reconnecttime=540, idlereconnect=45):
        """LmwSip(user, password, [host], [port], [meetnet], [ssl], [check_ssl], [timeout], [log])

user(optinal): Lmw user name
password(optional): Lmw password
host(optional): Default sip-lmw.rws.nl
port(optional): Default 443
meetnet(optional): Default LMW
ssl(optional): Default true
check_ssl(optional): Default true
timeout(optional): Default 10
log(optional): Default None
cleartelnet(optional): Default False
reconnecttime(optional): Default 540

Opens the connection and logs in.
"""
        self.user          = user
        self.password      = password
        self.host          = host
        self.port          = port
        self.meetnet       = meetnet
        self.ssl           = ssl
        self.check_ssl     = check_ssl
        self.timeout       = timeout
        self.cleartelnet   = cleartelnet
        self.reconnecttime = 0
        self.idlereconnect = 0
        self._connecttime  = time.time()
        self._idletime     = time.time()

        self._socket       = None
        if (log != None):
            self.log = log
        else:
            try:
                self.log = logging.getLogger("lmwsip")
                self.log.debug("LmwSip.init: Start log")
            except Exception as e:
                print("Logger failed: %s" % e)
        self.log.debug("LmwSip.init(%s, **********, %s, %s, %s, %s, %s, %s, %s, %s, %s)" %
                          (user, host, port, meetnet, ssl, check_ssl, timeout,
                           cleartelnet, reconnecttime, idlereconnect))
        if (self.host != None):
            self.connect()
            if (self.user != None):
                self.login()
                self.reconnecttime = reconnecttime
                self.idlereconnect = idlereconnect

    def period(self, parameter):
        if parameter in self.lmwParameters:
            return(self.lmwParameters[parameter][2])
        else:
           raise LmwParmWarn(parameter)
           return(None)

    def lasttime(self, parameter):
        #
        # Find the last valid 10 minute window.
        # The measurement of 12:00 is avaiable at 12:05:30.
        # Before 12:05:30 we should use 11:50:00.
        #
        # At 12:05:29 we substract 15:29 from the time!
        #
        # Also note that we use GMT. So we should add one hour
        # because we use GMT +1 (MET, UTC-1)
        #
        now=time.time()
        period = self.period(parameter)
        if (period == 10):
            dt = now%600
            if (dt < 330):
                now = 3000 + now - dt
            else:
                now = 3600 + now - dt
        elif (period == 1):
            #
            # e.g. H1 use 30 seconds to calculate the time.
            #
            dt = now%60
            if (dt < 30):
                now = 3540 + now - dt
            else:
                now = 3600 + now - dt
        else:
           # At the moment no support for parameters other than 1 or 10 minutes.
           raise LmwParmWarn(parameter)
        time_of_day=time.strftime("%H:%M", time.gmtime(now))
        return { "day": time.strftime("%d-%m-%Y", time.gmtime(now)),
                 "time_of_day": time.strftime("%H:%M", time.gmtime(now)) }

    def connect(self):
        """Setup the network connection

connects to lmw with tcp using the values of the object creation.
"""
        try:
            self._tcp         = socket.create_connection((self.host, self.port))
            self._connecttime = time.time()
        except Exception as e:
            self.log.error("LmwSip.connect(%s, %s) failed: %s",
                               self.host, self.port, e)  
            raise LmwSipConnectError("LmwSip.connect: Socket create failed")
        if (self.ssl):
            try:
                self._context = ssl.create_default_context()
                self._context.check_hostname = self.check_ssl
                self._ssl     = self._context.wrap_socket(self._tcp,
                                                  server_hostname=self.host)
                self._socket = self._ssl
            except Exception as e:
                self.log.error("LmwSip.connect setup ssl failed:\n%s", e)
                raise LmwSipConnectError("LmwSip.connect: setup ssl failed")
        else:
            self._socket = self._tcp
        self._socket.settimeout(self.timeout)

    def closesocket(self):
        """Closes the socket and set the socket to None. Doesn't logout"""

        try:
            self.log.debug("LmwSip.closesocket")
            self._socket.close()
        except Exception as e:
            pass
        self._socket = None

    def send(self, sipcmd):
        """Send a sip command to the server

send a sip command to the server
"""
        self._idletime = time.time()
        if self._socket != None:
            try:
                logcmd = sipcmd.strip('\r')
                if re.match("^LI", logcmd, re.IGNORECASE):
                    logcmd = re.sub(",.*", ", ******", logcmd)
                self.log.debug("LmwSip.send(%s)" % logcmd)
                self._socket.sendall(sipcmd.encode('ascii'))
            except Exception as e:
                self.log.error("LmwSip.send(%s) failed: %s" % (sipcmd, e))
                self.closesocket()
                raise LmwSipConnectError("LmwSip.send: Socket connection lost")
        else:
            self.log.warning("LmwSip.send: No connection")

    def telnetheader(self, header):
        a = b'\xff\xfd\x01\xff\xfd\x03\xff\xfd\x00\xff\xfc\x01\xff\xfb\x00'
        self.log.debug("LmwSip.telnetheader(%s) --> %s" % (header, a))
        try:
            self._socket.sendall(a)
        except Exception as e:
            self.log.error("LmwSip.telnetheader(%s) --> %s failed: %s" % (header, a, e))
            self.closesocket()
            raise LmwSipConnectError("LmwSip.telnetheader: Socket connection lost")

    def recv(self):
        """Recieve the results

recieve a answer from the sip server
"""
        c = 0
        bytebuf=b''
        stringbuf=""
        while (self._socket != None) and (stringbuf.find("\r") == -1) and (c < 3):
            try:
                self.log.debug("LmwSip.recv: %s: Waiting for data" % self.cleartelnet);
                bytebuf = self._socket.recv(4096)
                if (len(bytebuf) == 0):
                    c+=1
                    self.log.debug("recv: bytebuf: %s" % bytebuf)
                if self.cleartelnet:
                    if bytebuf[0] == 255:
                        bytebuf = b''
            except Exception as e:
                self.log.error("SipLmw.recv: socket timeout: %s", e)
                self.closesocket()
                raise LmwSipConnectError("LmwSip.recv: No data recieved")
            try:
                stringbuf += bytebuf.decode('utf-8')
                self.log.debug("recv: stringbuf: %s" % stringbuf)
            except Exception as e:
                self.log.error("SipLmw.recv: decode error: %s", e)
                self.closesocket()
                raise LmwSipDecodeError("LmwSip.recv: decode error", bytebuf)
        if (c>=3) and (len(stringbuf) == 0):
            self.log.warning("LmwSip.recv: No data recieved")
            self.closesocket()
            raise LmwSipConnectError("LmwSip.recv: socket close")
        elif self._socket == None:
            self.log.warning("LmwSip.recv: No connection")
        elif len(stringbuf) == 0:
            self.log.warning("LmwSip.recv: No data")
        elif stringbuf[0] != '!':
            self.log.warning("LmwSip.recv: Sip error: %s" % stringbuf.strip('\r'))
        else:
            self.log.debug("LmwSip.recv: result: %s" % stringbuf.strip('\r'))
        return(stringbuf)

    def login(self):
        """Login the sip server

Login lmw using the object creation user, password.
Raises a LmwLoginFailure exception on failure
"""
        li="LI " + self.user + ","  + self.password + "\r"
        #
        # TODO: Check connect
        #
        # Don't use: sendrecv with reconnect check!
        #
        self.send(li)
        d = self.recv()
        if (d[0] != '!'):
            self.closesocket()
            raise LmwLoginFailure(self.user, d)

    def reconnect(self):
        self.logout()
        time.sleep(1)
        self.connect()
        self.login()

    def reconnectcheck(self):
        """Check if we need to reconnect.

Checks if a reconnect is nessecery.

There are two timeouts:
    The maxium connect time (reconnecttime)
    The maxium idle time (idlereconnect)
"""
        ct = time.time() - self._connecttime
        if (self.reconnecttime > 0) and (ct > self.reconnecttime):
            self.log.debug("LmwSip.reconnectcheck: reconnect after %i seconds" % ct)
            self.reconnect()
        it = time.time() - self._idletime
        if (self.idlereconnect > 0) and (it > self.idlereconnect):
            self.log.debug("LmwSip.reconnectcheck: idle reconnect after %i seconds" % it)
            self.reconnect()

    def sendrecv(self, cmd):
        """Send a a command and recieve the result.

send the command and recieve the answer. 
retry on socket failure.
"""
        c = 0
        ret = ""
        self.reconnectcheck()
        while (ret == "") and (c < 3):
            if (self._socket == None):
                time.sleep(10)
                self.log.warning("LmwSip.sendrecv: reconnect")
                self.connect()
                self.login()
            try:
                self.send(cmd)
                ret = self.recv()
            except LmwSipConnectError as e:
                if (self.user != None):
                    self.connect()
                    self.login()
                    c+=1
                    ret=""
                else:
                    c=3
                    raise(e)
        return(ret)

    def ti(self):
        """Recieve the time from the sipserver.

Request the time from lmw and returns the string.

Raises a LmwCmdWarn of failure
"""
        ti="TI " + self.meetnet + "\r"
        d = self.sendrecv(ti)
        return (d[2:-1])

    def cmd(self, process, location, parameter, time_delta, day,
                                                time_of_day, cmd_type="DATA"):
        """Create a sip command from the paramters

Send a cmd to LMW and returns the lmw string

    process:      <WN|VW|AS>
    location:     <lmw location (e.g. HOEK)>
    parameter:    <lmw parameter (e.g. H10)>
    time_delta:   <Time windows (max 23:59, e.g. +01:00>
    day:          <Date>
    time_of_day:  <Time>
    cmd_type:     [DATA|DATB|OORS|OORB|""]

Example:
    lmw.cmd("WN", "HOEK", "H10", "+01:00", "13-08-2018", "16:00")

Returns:
    The LMW answer string
"""
        if (process == "AS"):
            data=""
        else:
            data="," + cmd_type

        cmdstr=process + " " + self.meetnet + "," + location + "," + \
               parameter + "," + time_delta + "," + day + "," + \
               time_of_day + data + "\r" 

        d = self.sendrecv(cmdstr)
        if (d[0] != '!'):
            raise LmwCmdWarn(cmdstr, d)
        return (d[2:-1])

    def cmdWrite(self, process, location, parameter, time_delta, day,
                 time_of_day, values):
        """Write data to LMW

    process:      <WNT|VWT|AST>
    location:     <lmw location (e.g. HOEK)>
    parameter:    <lmw parameter (e.g. H10)>
    time_delta:   <Time windows (max 23:59, e.g. +01:00>
    day:          <Date>
    time_of_day:  <Time>
    data:         Values to be writen (e.g. 33/10;35/10).

Example:
    lmw.cmd("WNT", "HOEK", "H10", "+00:20", "13-08-2018", "16:00", "33/10;35/10")

Returns:
    The LMW answer string
"""
        cmdstr=process + " " + self.meetnet + "," + location + "," + \
               parameter + "," + time_delta + "," + day + "," + \
               time_of_day + values + "\r" 
        d = self.sendrecv(cmdstr)
        if (d[0] != '!'):
            raise LmwCmdWarn(cmdstr, d)
        return (d[2:-1])

    def valueStr(self, process, location, parameter, day = None,
                    time_of_day = None):
        """Get string of values from sip

Parameters:
    process:      <WN|VW|AS>
    location:     <lmw location (e.g. HOEK)>
    parameter:    <lmw parameter (e.g. H10)>
    day:          [date = now()]
    time_of_day:  [time = now()]

The default returns the last value string including quality.

Example:
    lmw.data_string("WN", "HOEK", "H10")
 
Returns a single string value with quality
"""
        if (day == None or time_of_day == None):
            last = self.lasttime(parameter)
            if (day==None):
                day=last["day"]
            if (time_of_day==None):
                time_of_day=last["time_of_day"]
        return(self.cmd(process, location, parameter, "+00:00", day,
                       time_of_day, "DATA"))

    def value(self, process, location, parameter, day = None,
                    time_of_day = None):
        """Get one value from sip

Parameters:
    process:      <WN|VW|AS>
    location:     <lmw location (e.g. HOEK)>
    parameter:    <lmw parameter (e.g. H10)>
    day:          [date = now()]
    time_of_day:  [time = now()]

The default returns the last value.

Example:
    lmw.data_string("WN", "HOEK", "H10")
 
Returns a single string value or None
"""
        res = self.valueStr(process, location, parameter, day, time_of_day)
        value=re.sub("/.*$", "", res)
        if (value == "99999"):
            value=""
        elif (value == "-999999999"):
            value=""
        #
        # We should check the "kwaliteit"
        #
        return(value)

    def _lmwdelta_(self, window):
        h = 24*window.days + window.seconds // 3600
        m = (window.seconds % 3600)//60
        return("+%02i:%02i" % (h, m))

    def _roundtime_(self, time, delta):
        # Todo check: delta != 1 en delta != 10
        if time.microsecond != 0:
            time += timedelta(microseconds=1000000-time.microsecond)
        if time.second != 0:
            time += timedelta(seconds=60-time.second)
        if (delta == timedelta(minutes=10)) and (time.minute % 10 != 0):
                time += timedelta(minutes=(10-time.minute%10))
        return(time)

    def timeSerie(self, process, location, parameter,
                        startTime, endTime, cmd_type="DATB"):
        """Get a python data structure with the results.

Parameters:
    process:      <WN|VW|AS>
    location:     <lmw location (e.g. HOEK)>
    parameter:    <lmw parameter (e.g. H10)>
    startTime:    Start time (datetime)
    endTime:      End time (datetime)
    cmd_type:     [DATA|DATB]

startTime is rounded up to the next measurement time.
So 12:00:00.000001 --> 12:00:10.00.0

The times should have correct timezone information. Otherwise local timezone
is assumed. Timezones are converted to 'GMT+1' for the sip commands.

Example:
    lmw.data_string("WN", "HOEK", "H10", ...)
 
Returns a LmwtimeSerie object

Errors:
    startTime > endTime
    endTime - startTime > 24 hour
    now - startTime < 30 days
"""
        try:
           delta = timedelta(minutes=self.period(parameter))
        except Exception as e:
            delta = timedelta(minutes=10)
            raise(e)

        startTime = self._roundtime_(startTime.astimezone(tz.gettz('GMT+1')), delta)
        endTime   = endTime.astimezone(tz.gettz('GMT+1'))

        if startTime > endTime:
            self.log.warning("starttime > endtime: %s > %s", startTime, endTime)
            raise sipTimeSeriesError(startTime, endTime,
                                     "starttime > endtime")

        if datetime.now(tz=tz.gettz('GMT+1')) - startTime > timedelta(days=30): 
            self.log.warning("now() - starttime > 30 days: %s", startTime)
            raise sipTimeSeriesError(startTime, endTime,
                                     "now - starttime > 30 days")

        self.log.debug("LmwSip.timeSerie: startTime: %s" % startTime)
        self.log.debug("LmwSip.timeSerie: endTime: %s" % endTime)

        if process == "VW":
            cmd_type="DATA"

        res = lmwTimeSerie(startTime, delta, "")

        while startTime <= endTime:
            if endTime - startTime > timedelta(days=1):
                window = timedelta(days=1) - delta
            else:
                window = endTime-startTime
            values = self.cmd(process, location, parameter,
                              self._lmwdelta_(window),
                              startTime.strftime("%d-%m-%Y"),
                              startTime.strftime("%H:%M"),
                              cmd_type)
            res.addvalues(startTime, values)
            startTime += window + delta
            
        return(res)

    def logout(self):
        """Logut of the sip server,

Logs of
"""
        self.send("LO\r")
        self.closesocket()

class lmwTimeSerie:
    """Class for lmw results.

The result are in lmwTimeSerie.ts as array

    [ <time1>, [<value1 a, value1 b, ...], kwaliteit1, additionele kwaliteit1],
    [ <time2>, [<value2 a, value2 b, ...], kwaliteit2, additionele kwaliteit2],
    ...

Note:
    * For most measurements there is only one value (e.g H10).
    * Additionale kwaliteit is optional and may contain None.
    * Result times in UTC

"""

    def __init__(self, start, delta, values=""):
        """lmwTimeSerie init

Create a lmwTimeSerie object with:
    start:  Start time
    delta:  Period of the measurements
    values: lmw result string
"""
        self.ts    = []
        self.delta = delta
        if values != "":
            self.addvalues(start, values)

    def addvalues(self, start, values):
        """Add values

Add values to a timeserie
    start:  Start time
    delta:  Period of the measurements
    values: lmw result string

"""
        start = start.astimezone(tz.gettz('UTC'))
        for e in values.split(";"):
            v = e.split("/")
            v[0] = v[0].split(",")
            if len(v) == 2:
                v.append(None)
            self.ts.append([start, v[0], v[1], v[2]])
            start += self.delta

class sipTimeSeriesError(Exception):
    """Parameter errors for timeSeries"""
    def __init__(self, startTime, endTime, message):
        self.startTime = startTime
        self.endTime   = endTime
        self.message   = message

    def __str__(self):
        return("%s\n  starttime: %s\n  end time:  %s" %
                              (self.message, self.startTime, self.endTime))

class LmwSipConnectError(Exception):
    """Connection exceptions for LmwSip"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return(self.message)

class LmwSipDecodeError(Exception):
    """Connection exceptions for LmwSip"""

    def __init__(self, message, buf):
        self.message = message
        self.buf     = buf

    def __str__(self):
        return(self.message + ":" + buf)


class LmwLoginFailure(Exception):
    """Exception from LmwSip on login failure"""

    def __init__(self, user, message):
        self.user    = user
        self.message = message

    def __str__(self):
        return("Login with user %s failed: %s" % (self.user, self.message))

class LmwCmdWarn(Warning):
    """Exception fro LmwSip on a cmd"""
    def __init__(self, cmd, message):
        self.cmd     = cmd.replace('\r', '')
        self.message = message

    def __str__(self):
        return("Cmd %s failed: %s" %(self.cmd, self.message))

class LmwParmWarn(Warning):
    """Exception for a unknown parameter"""
    def __init__(self, parameter):
        self.parameter = parameter

    def __str__(self):
        return("Unknown parameter: %s" % parameter)
