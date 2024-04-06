import re
import os, sh
import shutil
import subprocess
import colorama as ca
from tqdm import tqdm
import platform
import pandas as pd
import numpy as np
import glob
from xml.etree import ElementTree as et
import xarray as xr
import xesmf as xe


def p_header(text):
    print(ca.Fore.CYAN + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def p_hint(text):
    print(ca.Fore.LIGHTBLACK_EX + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def p_success(text):
    print(ca.Fore.GREEN + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def p_fail(text):
    print(ca.Fore.RED + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def p_warning(text):
    print(ca.Fore.YELLOW + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def s_header(text):
    return ca.Fore.CYAN + ca.Style.BRIGHT + text + ca.Style.RESET_ALL

def s_hint(text):
    return ca.Fore.LIGHTBLACK_EX + ca.Style.BRIGHT + text + ca.Style.RESET_ALL

def s_success(text):
    return ca.Fore.GREEN + ca.Style.BRIGHT + text + ca.Style.RESET_ALL

def s_fail(text):
    return ca.Fore.RED + ca.Style.BRIGHT + text + ca.Style.RESET_ALL

def s_warning(text):
    return ca.Fore.YELLOW + ca.Style.BRIGHT + text + ca.Style.RESET_ALL

def replace_str(fpath, d):
    ''' Replace the string in a given text file according
    to the dictionary `d`
    '''
    with open(fpath, 'r') as f:
        text = f.read()
        for k, v in d.items():
            search_text = k
            replace_text = v
            text = text.replace(search_text, replace_text)

    with open(fpath, 'w') as f:
        f.write(text)

def run_shell(cmd, timeout=None):
    print(f'CMD >>> {cmd}')
    try:
        subprocess.run(cmd, timeout=timeout, shell=True)
    except:
        pass

def svn_export(url, fpath=None):
    if fpath is None:
        fpath = os.path.basename(url)

    if os.path.exists(fpath): os.remove(fpath)
    run_shell(f'svn export {url} {fpath}')
    return fpath

def copy(src, dst=None):
    if dst is None:
        dst = os.path.basename(src)

    dst = os.path.abspath(dst)
    sh.cp(src, dst)
    return dst

def exec_script(fpath, args=None, timeout=None, chmod_add_x=False):
    if chmod_add_x:
        run_shell(f'chmod +x {fpath}')

    if args is None:
        cmd = fpath
    else:
        cmd = f'{fpath} {args}'

    run_shell(cmd, timeout=timeout)

def make_pbs(fpath=None, cmd=None, args=None, name='test', pbs_fname=None, queue=None, select=1, ncpus=36, mpiprocs=36, mem=64, walltime='06:00:00', account=None,
             lines_before='', lines_after=''):

    if account is None:
        raise ValueError('account must be specified')

    if cmd is None:
        if args is None:
            cmd = fpath
        else:
            cmd = f'{fpath} {args}'

    if pbs_fname is None:
        pbs_fname = f'pbs_{name}.zsh'

    hostname = platform.node()
    if hostname[:7] == 'derecho':
        if queue is None: queue = 'main'
    elif hostname[:8] == 'cheyenne':
        if queue is None: queue = 'regular'
    elif hostname[:6] == 'casper':
        if queue is None: queue = 'regular'

    with open(pbs_fname, 'w') as f:
            f.write(f'''#!/bin/zsh
#PBS -N {name}
#PBS -q {queue}
#PBS -l select={select}:ncpus={ncpus}:mpiprocs={mpiprocs}:mem={mem}GB
#PBS -l walltime={walltime}
#PBS -A {account}

{lines_before}
{cmd}
{lines_after}
                ''')

    p_success(f'>>> {pbs_fname} created')

def qsub_script(fpath, mach=None, args=None, name='test', queue=None, select=1, ncpus=36, mpiprocs=36, mem=64, walltime='06:00:00', account=None,
                lines_before='', lines_after='', chmod_add_x=False):
    if chmod_add_x:
        run_shell(f'chmod +x {fpath}')

    if account is None:
        raise ValueError('account must be specified')

    make_pbs(fpath, args=args, name=name, queue=queue, select=select, ncpus=ncpus, mpiprocs=mpiprocs, mem=mem, walltime=walltime, account=account,
             lines_before=lines_before, lines_after=lines_after)

    if mach is not None:
        cmd = f'qsub @{mach} pbs_{name}.zsh'
    else:
        cmd = f'qsub pbs_{name}.zsh'

    run_shell(cmd)
    
def qcmd_script(fpath, mach=None, args=None, name='test', queue=None, select=1, ncpus=36, mpiprocs=36, mem=64, walltime='06:00:00', account=None, chmod_add_x=False, **env_vars):
    if chmod_add_x:
        run_shell(f'chmod +x {fpath}')

    if account is None:
        raise ValueError('account must be specified')

    env_str = ''
    for k, v in env_vars.items():
        env_str += f'{k}="{v},"'

    if args is None:
        cmd = fpath
    else:
        cmd = f'{fpath} {args}'

    hostname = platform.node()
    if hostname[:7] == 'derecho':
        if queue is None: queue = 'main'
    elif hostname[:8] == 'cheyenne':
        if queue is None: queue = 'regular'

    l1 = f'select={select}:ncpus={ncpus}:mpiprocs={mpiprocs}:mem={mem}GB'
    l2 = f'walltime={walltime}'

    if mach is not None:
        exe = f'qcmd @{mach}'
    else:
        exe = 'qcmd'

    run_shell(f'{exe} -N {name} -q {queue} -l {l1} -l {l2}  -A {account} -- {cmd}')

def write_file(fname, content=None, mode='w'):
    if content is None:
        raise ValueError('Please assign the value for `content`.')

    with open(fname, mode) as f:
        f.write(f'''{content}''')


def merge_summaries(paths, save_path=None):
    dfs = []
    for path in paths:
        dfs.append(pd.read_csv(path, index_col=0))

    df = pd.concat(dfs, axis=1)

    if save_path is not None:
        df.to_csv(save_path)
        p_success(f'>>> Summary report saved to: {os.path.abspath(save_path)}')

    return df

def wildcard_paths(path_with_wildcard):
    paths = sorted(glob.glob(path_with_wildcard))
    return paths

def parse_xml(fpath, key):
    tree = et.parse(fpath)
    root = tree.getroot()
    d = {}
    for item in root.iter('entry'):
        if item.attrib['id'] == key:
            d[key] = item.attrib['value']

    return d

def parse_nml(fpath, key):
    d = {}
    with open(fpath, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if key in line and key == line.split('=')[0].strip():
            d[key] = line.split('=')[-1].strip().split('\n')[0]

    return d

def jupyter_server(port=None, qsub=False, name='JupyterLab', queue=None, select=1, ncpus=36, mpiprocs=36, mem=64, walltime='06:00:00', account=None):
    port = 8000 if port is None else port
    cmd = f'jupyter lab --no-browser --port={port}'

    if qsub:
        hostname = platform.node()
        if hostname[:7] == 'derecho':
            if queue is None: queue = 'main'
        elif hostname[:8] == 'cheyenne':
            if queue is None: queue = 'regular'
        l1 = f'select={select}:ncpus={ncpus}:mpiprocs={mpiprocs}:mem={mem}GB'
        l2 = f'walltime={walltime}'

        run_shell(f'qcmd -N {name} -q {queue} -l {l1} -l {l2}  -A {account} -- {cmd}')
    else:
        run_shell(cmd)

def monthly2annual(ds):
    month_length = ds.time.dt.days_in_month
    wgts_mon = month_length.groupby('time.year') / month_length.groupby('time.year').mean()
    ds_ann = (ds * wgts_mon).groupby('time.year').mean('time')
    return ds_ann.rename({'year':'time'})

def monthly2season(ds):
    month_length = ds.time.dt.days_in_month
    wgts = month_length.groupby('time.season') / month_length.groupby('time.season').mean()
    ds_season = (ds * wgts).groupby('time.season').mean('time')
    return ds_season

def regrid_cam_se(dataset, weight_file):
    """
    Regrid CAM-SE output using an existing ESMF weights file.

    Parameters
    ----------
    dataset: xarray.Dataset
        Input dataset to be regridded. Must have the `ncol` dimension.
    weight_file: str or Path
        Path to existing ESMF weights file

    Returns
    -------
    regridded
        xarray.Dataset after regridding.
    """
    assert isinstance(dataset, xr.Dataset)
    weights = xr.open_dataset(weight_file)

    # input variable shape
    in_shape = weights.src_grid_dims.load().data

    # Since xESMF expects 2D vars, we'll insert a dummy dimension of size-1
    if len(in_shape) == 1:
        in_shape = [1, in_shape.item()]

    # output variable shapew
    out_shape = weights.dst_grid_dims.load().data.tolist()[::-1]

    print(f"Regridding from {in_shape} to {out_shape}")

    # Insert dummy dimension
    vars_with_ncol = [name for name in dataset.variables if "ncol" in dataset[name].dims]
    updated = dataset.copy().update(
        dataset[vars_with_ncol].transpose(..., "ncol").expand_dims("dummy", axis=-2)
    )

    # construct a regridder
    # use empty variables to tell xesmf the right shape
    # https://github.com/pangeo-data/xESMF/issues/202
    dummy_in = xr.Dataset(
        {
            "lat": ("lat", np.empty((in_shape[0],))),
            "lon": ("lon", np.empty((in_shape[1],))),
        }
    )
    dummy_out = xr.Dataset(
        {
            "lat": ("lat", weights.yc_b.data.reshape(out_shape)[:, 0]),
            "lon": ("lon", weights.xc_b.data.reshape(out_shape)[0, :]),
        }
    )

    regridder = xe.Regridder(
        dummy_in,
        dummy_out,
        weights=weight_file,
        method="test",
        reuse_weights=True,
        periodic=True,
    )

    # Actually regrid, after renaming
    regridded = regridder(updated.rename({"dummy": "lat", "ncol": "lon"}))

    # merge back any variables that didn't have the ncol dimension
    # And so were not regridded
    return xr.merge([dataset.drop_vars(regridded.variables), regridded])