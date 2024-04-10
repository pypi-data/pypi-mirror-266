import colorama as ca
import requests
from tqdm import tqdm
import numpy as np

def p_header(text):
    # return cprint(text, 'cyan', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.CYAN + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_hint(text):
    # return cprint(text, 'grey', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.LIGHTBLACK_EX + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_success(text):
    # return cprint(text, 'green', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.GREEN + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_fail(text):
    # return cprint(text, 'red', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.RED + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_warning(text):
    # return cprint(text, 'yellow', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.YELLOW + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def augknt(knots, degree):
    """Augment knots to meet boundary conditions

    Python version of MATLAB's augknt().
    @author: brews (https://github.com/brews)
    """
    heads = [knots[0]] * degree
    tails = [knots[-1]] * degree
    return np.concatenate([heads, knots, tails])

def download(url: str, fname: str, chunk_size=1024, show_bar=True):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    if show_bar:
        with open(fname, 'wb') as file, tqdm(
            desc='Fetching data',
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in resp.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                bar.update(size)
    else:
        with open(fname, 'wb') as file:
            for data in resp.iter_content(chunk_size=chunk_size):
                size = file.write(data)

data_url_dict = {
    'TEX_forward_SST_params_standard': 'https://raw.githubusercontent.com/jesstierney/BAYSPAR/master/ModelOutput/Output_SpatAg_SST/params_standard.mat',
    'TEX_forward_subT_params_standard': 'https://raw.githubusercontent.com/jesstierney/BAYSPAR/master/ModelOutput/Output_SpatAg_subT/params_standard.mat',
    'TEX_forward_SST_params_analog': 'https://raw.githubusercontent.com/jesstierney/BAYSPAR/master/ModelOutput/Output_SpatAg_SST/params_analog.mat',
    'TEX_forward_subT_params_analog': 'https://raw.githubusercontent.com/jesstierney/BAYSPAR/master/ModelOutput/Output_SpatAg_subT/params_analog.mat',
    'TEX_forward_SST_Data_Input': 'https://raw.githubusercontent.com/jesstierney/BAYSPAR/master/ModelOutput/Data_Input_SpatAg_SST.mat',
    'TEX_forward_subT_Data_Input': 'https://raw.githubusercontent.com/jesstierney/BAYSPAR/master/ModelOutput/Data_Input_SpatAg_subT.mat',
    'UK_bayes_posterior': 'https://raw.githubusercontent.com/jesstierney/BAYSPLINE/master/bayes_posterior_v2.mat',
}

