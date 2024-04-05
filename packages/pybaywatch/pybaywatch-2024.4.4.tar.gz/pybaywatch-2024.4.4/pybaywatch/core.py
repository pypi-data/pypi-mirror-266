'''
BAYWATCH in pure Python
@author: Feng Zhu (fengzhu@ucar.edu)
'''

import os
import numpy as np
import pandas as pd
import xarray as xr
from scipy.interpolate import BSpline, interp1d
from scipy.io import loadmat
from . import utils
dirpath = os.path.dirname(__file__)

def TEX_forward(lat, lon, temp, seed=2333, type='SST', nens=1000, mode='standard', tolerance=None):
    ''' TEX forward modeling based on input SST

    args:
        lat (float): latitude
        lon (float): longitude
        temp (float): temperature
        seed (int): random seed
        type (str): temperature type, must be 'SST' or 'subT'
        mode (str): calibration mode, must be 'standard' or 'analog'
        tolerance (float): search tolerance, must be provided when mode is 'analog'
        nens (int): ensemble size
    '''
    if mode not in ['standard', 'analog']:
        raise ValueError('Wrong `mode`; should be one of {"standard", "analog"}.')

    np.random.seed(seed)
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    temp = np.atleast_1d(temp)

    # download precalculated params
    params_path = os.path.join(dirpath, f'ModelOutput/Output_SpatAg_{type}/params_{mode}.mat')
    os.makedirs(os.path.dirname(params_path), exist_ok=True)
    if not os.path.exists(params_path):
        utils.download(utils.data_url_dict[f'TEX_forward_{type}_params_{mode}'], params_path)
        utils.p_success(f'>>> Downloaded file saved at: {params_path}')

    params = loadmat(params_path)
    if mode == 'standard':
        Locs_Comp = params['Locs_Comp']
        alpha_samples_comp = params['alpha_samples_comp']
        beta_samples_comp = params['beta_samples_comp']
        tau2_samples = params['tau2_samples'][0]
    elif mode == 'analog':
        alpha_samples = params['alpha_samples']
        beta_samples = params['beta_samples']
        tau2_samples = params['tau2_samples'][0]

    if mode == 'analog':
        if tolerance is None:
            raise ValueError('`tolerance` should be specified when `mode=analog`.')

        params_path = os.path.join(dirpath, f'ModelOutput/Data_Input_SpatAg_{type}.mat')
        if not os.path.exists(params_path):
            utils.download(utils.data_url_dict[f'TEX_forward_{type}_Data_Input'], params_path)
            utils.p_success(f'>>> Downloaded file saved at: {params_path}')

        data_input = loadmat(params_path)['Data_Input'][0][0]
        Locs = data_input[1]
        Inds_Stack = data_input[4][:, 0].squeeze()
        Target_Stack = data_input[5][:, 0].squeeze()
        # print(Locs.shape, Inds_Stack.shape, Target_Stack.shape)

    # searching for nearest lat/lon
    grid_half_space = 10
    if mode == 'standard':
        nloc = len(lon)
        inder_g = np.empty(nloc, dtype=int)
        for i in range(nloc):
            loc = np.where(
                (np.abs(Locs_Comp[:, 0] - lon[i]) <= grid_half_space) & (np.abs(Locs_Comp[:, 1] - lat[i]) <= grid_half_space)
            )[0][0]
            inder_g[i] = loc

        alpha_samples = alpha_samples_comp[inder_g][0]
        beta_samples = beta_samples_comp[inder_g][0]
    elif mode == 'analog':
        # find cells with modern T obs within the tolerance:
        # number of big grids:
        N_bg = len(Locs)
        # NEW: calculate mean SSTs across spatial grid cells
        spatialMean = np.empty(N_bg)
        for i in range(N_bg):
            spatialMean[i] = np.mean(Target_Stack[Inds_Stack == i+1])  # index from Matlab starts from 1

        # identify mean values within the tolerance
        inder_g = np.where(
            (spatialMean >= np.mean(temp) - tolerance) & (spatialMean <= np.mean(temp) + tolerance)
        )[0]

        if len(inder_g) == 0:
            raise ValueError('Your search tolerance is too narrow')
        else:
            alpha_samples = alpha_samples[inder_g].flatten()
            beta_samples = beta_samples[inder_g].flatten()
            tau2_samples = np.repeat(tau2_samples, len(inder_g))

    # Predict TEX86 values
    tex = np.empty((len(temp), nens))
    randind = np.random.choice(range(len(tau2_samples)), nens, replace=False)
    for i in range(nens):
        tau2 = tau2_samples[randind[i]]
        beta = beta_samples[randind[i]]
        alpha = alpha_samples[randind[i]]
        tex[:, i] = np.random.normal(temp * beta + alpha, np.sqrt(tau2))
        tex[:, i] = np.clip(tex[:, i], 0, 1)

    return tex
        

def UK_forward(sst, order=2, seed=2333):
    ''' UK forward modeling based on input SST

    Args:
        sst (array): the SST vector
        params (array): the Bayesian parameters
        order (int): the BSpline order
        seed (int): random seed
    '''
    np.random.seed(seed)
    sst = np.atleast_1d(sst)
    # load posteriors for B coefficients and tau^2 variance
    params = loadmat(os.path.join(dirpath, 'params/bayes_posterior_v2.mat'))

    # NOTE: calibration is seasonal for the following regions: North Pacific (Jun-Aug),
    # North Atlantic (Aug-Oct), Mediterranean (Nov-May). If the data lie in the
    # following polygons then you should provide seasonal SSTs:

    kn = np.concatenate(([params['knots'].squeeze()[0]]*order, params['knots'].squeeze(), [params['knots'].squeeze()[-1]]*order))
    nens = params['bdraws'].shape[0]
    nobs = len(sst)
    uk = np.ndarray((nobs, nens))

    for i, bdraw in enumerate(params['bdraws']):
        # assembles the b-spline with the given knots and current coeffs
        # print(kn.shape)
        # print(np.array(bdraw).shape)
        tau2 = np.array(params['tau2'].squeeze())[i]
        bs = BSpline(kn, np.array(bdraw), k=order)

        # linearly extrapolates the spline to evaluate values at SSTs
        # outside the calibration range (0-30). w/o this, B-spline will return a NaN
        # at SSTs out of this range.

        # evaluate the mean value of the spline for your SST obs:
        mean = bs(sst)

        # draw from the distribution:
        uk[:, i] = np.random.normal(mean, np.sqrt(tau2))
        # any uk values outside 0 to 1 are forced to be in that range.
        uk[:, i] = np.clip(uk[:, i], 0, 1)

    return uk

def d18Oc_forward(sst, d18Osw, species='all', seed=2333):
    ''' d18Oc forward modeling based on input SST and sea-water d18O

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
    np.random.seed(seed)
    sst = np.atleast_1d(sst)
    d18Osw = np.atleast_1d(d18Osw)

    species_list = ['bulloides', 'incompta', 'pachy', 'ruber', 'sacculifer', 'all', 'all_sea']
    if species not in species_list:
        raise ValueError(f'`species` must be one of {species_list}!')

    if species == 'all':
        params = loadmat(os.path.join(dirpath, 'params/poolann_params.mat'))
        idx = 0
    elif species == 'all_sea':
        params = loadmat(os.path.join(dirpath, 'params/poolsea_params.mat'))
        idx = 0
    else:
        params = loadmat(os.path.join(dirpath, 'params/hiersea_params.mat'))
        idx = species_list.index(species)

    betaT = params['betaT'][:, idx]
    alpha = params['alpha'][:, idx]
    sigma = params['sigma'][:, idx]

    # Unit adjustment for permil VSMOW to permil VPDB.
    d18Osw_adj = d18Osw - 0.27

    # vectorized calculation of ensemble.
    mu = alpha + sst[:, np.newaxis] * betaT + d18Osw_adj[:, np.newaxis]
    d18Oc = np.random.normal(mu, sigma)

    return d18Oc

def MgCa_forward(age, sst, salinity, pH, omega, species='all', clean=1., sw=2, H=1, seed=2333):
    ''' Mg/Ca forward modeling based on input SST, salinity, pH, and water saturation state

    Args:
        age (array): the age vector in Ma
        sst (array): the SST vector
        salinity (array): the sea-water sality vector [PSU]
        omega (array): bottom water saturation sate
        pH (array): the sea-water pH vector
        species (str): the foram species; can be one of the below
            'ruber' = G. ruber
            'bulloides' = G. bulloides
            'sacculifer' = T. sacculifer
            'pachy' = N. pachyderma
            'incompta' = N. incompta
            'all' = use the pooled annual (non-species specific) model
            'all_sea' = use the pooled seasonal (non-species specific) model
        clean (float): cleaning technique; 1.: reductive, 0.: oxidative; (0, 1): a mix of cleaning methods
        sw (int): seawater correction; 
            0 = do not include a sw term
            1 = include a sw term - original values from the 2019 paper
            2 = include a sw term - v2 values incl Na/Ca (Rosenthal et al 2022) 
        H (float):  the non-linear power component of the Mg/Casw to Mg/Caforam relationship, to use in the seawater correction (1: no non-linearity)
        seed (int): random seed
    '''
    np.random.seed(seed)
    sst = np.atleast_1d(sst)
    salinity = np.atleast_1d(salinity)
    omega = omega ** -2
    omega = np.atleast_1d(omega)
    pH = np.atleast_1d(pH)

    species_list = ['ruber', 'bulloides', 'sacculifer', 'pachy', 'incompta', 'all', 'all_sea']
    species_list_model = ['ruber', 'bulloides', 'sacculifer', 'pachy']
    if species not in species_list:
        raise ValueError(f'`species` must be one of {species_list}!')

    if species == 'incompta':
        species = 'pachy'

    if species == 'all':
        params = loadmat(os.path.join(dirpath, 'params/pooled_model_params.mat'))
        idx = 0
    elif species == 'all_sea':
        params = loadmat(os.path.join(dirpath, 'params/pooled_sea_model_params.mat'))
        idx = 0
    else:
        params = loadmat(os.path.join(dirpath, 'params/species_model_params.mat'))
        idx = species_list_model.index(species)

    nobs = len(sst)

    betaT = params['betaT'].squeeze()
    betaC = params['betaC'].squeeze()
    betaO = params['betaO'].squeeze()
    betaS = params['betaS'].squeeze()
    betaP = params['betaP'].squeeze()

    # for sigma and alpha, grab the appropriate species
    sigma = params['sigma'][:,idx]
    alpha = params['alpha'][:,idx]

    nparams = len(betaT)
    if sw == 1 or sw == 2:
        if sw == 1:
            da = loadmat(os.path.join(dirpath, 'params/mgsw_iters.mat'))
        elif sw == 2:
            da = loadmat(os.path.join(dirpath, 'params/mgsw_iters_v2.mat'))
        # mg_smooth: Array of smoothed mg values
        mg_smooth = da['mg_smooth']
        # xt: Array of x-values (e.g., ages)
        xt = da['xt'].squeeze()
        # mg_mod: Modern mg value
        mg_mod = mg_smooth[0, :]

        # Interpolate mg_smooth to the given age
        # age: The age at which you want to interpolate mgsw
        mgsw_interp = interp1d(xt, mg_smooth, kind='linear', axis=0)(age)

        # Calculate the ratio to the modern value and convert to log units
        # H: Optional exponent (if provided)
        mgsw = np.log((mgsw_interp / mg_mod) ** H)
    else:
        mgsw = 0

    lmg_mean = alpha.T + sst[:, np.newaxis] * betaT.T + omega * betaO.T + salinity[:, np.newaxis] * betaS.T + (1 - clean * betaC.T) + mgsw.T
    if idx < 2:  # If you selected ruber, bulloides, or the "all" models, assume pH sensitivity
        lmg_mean += pH * betaP.T

    lmg_sig = sigma.T
    lmg = lmg_mean + np.random.randn(nobs, nparams) * lmg_sig

    return lmg

def MBT_forward(temp, archive='lake', type='T0', seed=2333):
    if archive not in ['lake', 'soil']:
        raise ValueError('Wrong `archive`; should be one of {"lake", "soil"}.')

    if type not in ['T0', 'T']:
        raise ValueError('Wrong `type`; should be one of {"T0", "T"}.')

    np.random.seed(seed)
    temp = np.atleast_1d(temp)

    if archive == 'lake':
        params = loadmat(os.path.join(dirpath, f'params/baymbt0_params_{archive}'))
    elif archive == 'soil':
        if type == 'T0':
            params = loadmat(os.path.join(dirpath, f'params/baymbt0_params_{archive}'))
        elif type == 'T':
            params = loadmat(os.path.join(dirpath, f'params/baymbt_params_{archive}'))
    
    b_draws_final = params['b_draws_final']
    tau2_draws_final = params['tau2_draws_final'][:, 0]

    nobs = len(temp)
    nens = b_draws_final.shape[0]
    mbt5me = np.empty((nobs, nens))
    for i in range(nens):
        tau2 = tau2_draws_final[i]
        beta = b_draws_final[i, 0]
        alpha = b_draws_final[i, 1]
        mbt5me[:, i] = np.random.normal(temp * beta + alpha, np.sqrt(tau2))
        mbt5me[:, i] = np.clip(mbt5me[:, i], 0, 1)

    return mbt5me