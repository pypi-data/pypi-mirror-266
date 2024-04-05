'''
Wrappers for BAYWATCH in Matlab
@author: Feng Zhu (fengzhu@ucar.edu)
'''

import os
import numpy as np
import oct2py
from . import utils
dirpath = os.path.dirname(__file__)

def TEX_forward_M(lat, lon, temp, seed=2333, type='SST', mode='standard', tolerance=None):
    ''' Wrapper for TEX_forward in Matlab

    args:
        lat (float): latitude
        lon (float): longitude
        temp (float): temperature
        seed (int): random seed
        type (str): temperature type, must be 'SST' or 'subT'
        mode (str): calibration mode, must be 'standard' or 'analog'
        tolerance (float): search tolerance, must be provided when mode is 'analog'
    '''
    # download precalculated params
    params_path = os.path.join(dirpath, f'ModelOutput/Output_SpatAg_{type}/params_{mode}.mat')
    os.makedirs(os.path.dirname(params_path), exist_ok=True)
    if not os.path.exists(params_path):
        utils.download(utils.data_url_dict[f'TEX_forward_{type}_params_{mode}'], params_path)
        utils.p_success(f'>>> Downloaded file saved at: {params_path}')

    if mode == 'analog':
        if tolerance is None:
            raise ValueError('`tolerance` should be specified when `mode=analog`.')

        params_path = os.path.join(dirpath, f'ModelOutput/Data_Input_SpatAg_{type}.mat')
        if not os.path.exists(params_path):
            utils.download(utils.data_url_dict[f'TEX_forward_{type}_Data_Input'], params_path)
            utils.p_success(f'>>> Downloaded file saved at: {params_path}')

    # call the forward function
    oc = oct2py.Oct2Py(temp_dir=dirpath)
    oc.addpath(dirpath)
    oc.eval(f"rng({seed})")
    res = oc.feval('TEX_forward', lat, lon, temp, type, mode, tolerance)
    oc.exit()
    return res


def UK_forward_M(sst, seed=2333):
    ''' Wrapper for UK_forward in Matlab

    args:
        sst (array): sea-surface temperature
        seed (int): random seed
    '''
    # TODO: augknt, spmak, fnxtr, fnval functions not available
    # call the forward function
    oc = oct2py.Oct2Py(temp_dir=dirpath)
    oc.addpath(dirpath)
    oc.eval(f"rng({seed})")
    res = oc.feval('UK_forward', sst)
    oc.exit()
    return res

def d18Oc_forward_M(sst, d18Osw, species='all', seed=2333):
    ''' Wrapper for bayfox_forward in Matlab

    Args:
        sst (array): the SST vector
        d18Osw (array): the sea-water d18O vector
        species (str): the foram species; can be one of the below
            'bulloides' = G. bulloides
            'incompta' = N. incompta
            'pachy' = N. pachyderma
            'ruber' = G. ruber
            'sacculifer' = T. sacculifer
            'all' = use the pooled annual (non-species specific) model
            'all_sea' = use the pooled seasonal (non-species specific) model
        
        seed (int): random seed
    '''
    # call the forward function
    oc = oct2py.Oct2Py(temp_dir=dirpath)
    oc.addpath(dirpath)
    oc.eval(f"rng({seed})")
    res = oc.feval('bayfox_forward', sst, d18Osw, species)
    oc.exit()
    return res

def MBT_forward_M(temp, seed=2333, type='T0', archive='lake'):
    ''' Wrapper for baymbt_forward in Matlab

    args:
        temp (float): temperature
        seed (int): random seed
        type (str): temperature type, must be 'T0' or 'T'
        archive (str): archive type, must be 'lake' or 'soil'
    '''
    # call the forward function
    oc = oct2py.Oct2Py(temp_dir=dirpath)
    oc.addpath(dirpath)
    oc.eval(f"rng({seed})")
    res = oc.feval('baymbt_forward', temp, archive, type)
    oc.exit()
    return res

def MgCa_forward_M(age, temp, omega, salinity, pH, clean, species, sw=2, H=1, seed=2333):
    # call the forward function
    oc = oct2py.Oct2Py(temp_dir=dirpath)
    oc.addpath(dirpath)
    oc.eval(f"rng({seed})")
    res = oc.feval('baymag_forward_ln', age, temp, omega, salinity, pH, clean, species, sw, H)
    oc.exit()
    return res