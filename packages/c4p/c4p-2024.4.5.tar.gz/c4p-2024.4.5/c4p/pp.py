
import os
import shutil
import copy
import subprocess
import glob
import gzip
import xarray as xr
import numpy as np
import pandas as pd
from tqdm import tqdm
import datetime
import cftime
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.colors import BoundaryNorm, Normalize
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import termcolor
import xesmf as xe
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy import util as cutil

from . import utils

# class Timeseries:
#     def __init__(self, dirpath):
#         self.dirpath = dirpath
#         utils.p_header(f'>>> Archive.dirpath: {self.dirpath}')

#     def check_timespan(self, ref_timespan, target_timespan):
#         ref_paths = glob.glob(f'{self.dirpath}/*/proc/tseries/month_1/*.{ref_timespan}.nc')
#         vn_dict = {}
#         for path in ref_paths:
#             comp = path.split('/proc/')[0].split('/')[-1]
#             vn = path.split('.')[-3]
#             if comp not in vn_dict:
#                 vn_dict[comp] = [vn]
#             else:
#                 vn_dict[comp].append(vn)

#         target_paths = glob.glob(f'{self.dirpath}/*/proc/tseries/month_1/*.{target_timespan}.nc')
#         vn_dict_check = {}
#         for path in target_paths:
#             comp = path.split('/proc/')[0].split('/')[-1]
#             vn = path.split('.')[-3]
#             if comp not in vn_dict_check:
#                 vn_dict_check[comp] = [vn]
#             else:
#                 vn_dict_check[comp].append(vn)

#         for comp in vn_dict.keys():
#             if comp not in vn_dict_check:
#                 print(f'{comp} not generated for {target_timespan}')
#             else:
#                 for vn in vn_dict[comp]:
#                     if vn not in vn_dict_check[comp]:
#                         print(f'{comp}/{vn} timeseries not generated for {target_timespan}')

#         utils.p_success('Done.')


class Archive:

    def __init__(self, dirpath, comps=['atm', 'ice', 'ocn', 'rof', 'lnd']):
        self.dirpath = dirpath
        utils.p_header(f'>>> Archive.dirpath: {self.dirpath}')
        for comp in comps:
            self.__dict__[f'{comp}_paths'] = sorted(glob.glob(os.path.join(dirpath, comp, 'hist', '*')))
            utils.p_success(f'>>> Archive.{comp}_paths created')

    # def rename_timespan(self, timespan, comps=['atm', 'ice', 'ocn', 'rof', 'lnd'], rename_tag='__c4p_renamed', nworkers=None):
    #     ''' Rename the archive files within a timespan

    #     Args:
    #         timespan (tuple or list): [start_year, end_year] with elements being integers
    #     '''
    #     if nworkers is None:
    #         nworkers = threading.active_count()
    #         utils.p_header(f'nworkers = {nworkers}')

    #     start_year, end_year = timespan
    #     self.rename_tag = rename_tag

    #     def rename_path(i, path):
    #         if self.rename_tag in path:
    #             return None
    #         elif '-' in path:
    #             date_str = path.split('.')[-2]
    #             try:
    #                 year = int(date_str[:4])
    #             except:
    #                 return None

    #         if year>=start_year and year<=end_year:
    #             os.rename(path, f'{path}{self.rename_tag}')
    #             self.__dict__[f'{comp}_paths'][i] = f'{path}{self.rename_tag}'
    #             # utils.p_success(f'>>> File {i:05d}: {os.path.basename(path)} -> {os.path.basename(path)}{tag}')
            
    #     for comp in comps:
    #         with tqdm(desc=f'Processing {comp}', total=len(self.__dict__[f'{comp}_paths'])) as pbar:
    #             with ThreadPoolExecutor(nworkers) as exe:
    #                 futures = [exe.submit(rename_path, i, path) for i, path in enumerate(self.__dict__[f'{comp}_paths'])]
    #                 [pbar.update(1) for future in as_completed(futures)]

    def rm_timespan(self, timespan, comps=['atm', 'ice', 'ocn', 'rof', 'lnd'], nworkers=None, rehearsal=True):
        ''' Rename the archive files within a timespan

        Args:
            timespan (tuple or list): [start_year, end_year] with elements being integers
        '''
        if nworkers is None:
            nworkers = threading.active_count()
            utils.p_header(f'nworkers = {nworkers}')

        start_year, end_year = timespan
        year_list = []
        for y in range(start_year, end_year+1):
            year_list.append(f'{y:04d}')

        def rm_path(year, comp=None, rehearsal=True):
            if rehearsal:
                if comp is None:
                    cmd = f'ls {self.dirpath}/*/hist/*{year}-[01][0-9][-.]*'
                else:
                    cmd = f'ls {self.dirpath}/{comp}/hist/*{year}-[01][0-9][-.]*'
            else:
                if comp is None:
                    cmd = f'rm -f {self.dirpath}/*/hist/*{year}-[01][0-9][-.]*'
                else:
                    cmd = f'rm -f {self.dirpath}/{comp}/hist/*{year}-[01][0-9][-.]*'

            subprocess.run(cmd, shell=True)
            
        if comps == ['atm', 'ice', 'ocn', 'rof', 'lnd']:
            with tqdm(desc=f'Removing files for year', total=len(year_list)) as pbar:
                with ThreadPoolExecutor(nworkers) as exe:
                    futures = [exe.submit(rm_path, year, comp=None, rehearsal=rehearsal) for year in year_list]
                    [pbar.update(1) for future in as_completed(futures)]
        else:
            for comp in comps:
                utils.p_header(f'Processing {comp} ...')
                with tqdm(desc=f'Removing files for year #', total=len(year_list)) as pbar:
                    with ThreadPoolExecutor(nworkers) as exe:
                        futures = [exe.submit(rm_path, year, comp=comp, rehearsal=rehearsal) for year in year_list]
                        [pbar.update(1) for future in as_completed(futures)]

    def check_timespan(self, timespan, comps=['atm', 'ice', 'ocn', 'rof', 'lnd']):
        start_year, end_year = timespan
        date_list = []
        for y in range(start_year, end_year+1):
            for m in range(1, 13):
                date_list.append(f'{y:04d}-{m:02d}')
        
        df_comp_list = []
        for comp in comps:
            df_comp = pd.DataFrame(columns=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
            utils.p_header(f'Checking component: {comp}')
            for date in tqdm(date_list, desc='Checking dates'):
                yyyy, mm = date.split('-')
                paths = glob.glob(f'{self.dirpath}/{comp}/hist/*{date}*')

                if len(paths) < 1:
                    df_comp.loc[f'{comp}-{yyyy}', mm] = f'{date}!'
                else:
                    df_comp.loc[f'{comp}-{yyyy}', mm] = date

            df_comp_list.append(df_comp)
        
        df = pd.concat(df_comp_list)
        def style_missing(v, props=''):
            return props if '!' in v else None
        
        def remove_mark(v):
            if '!' in v:
                v = v.split('!')[0]
            return v

        df = df.style.map(style_missing, props='background-color:red;color:white').format(remove_mark)
        return df
            



    def undo_rename(self, rename_tag, comps=['atm', 'ice', 'ocn', 'rof', 'lnd'], nworkers=None):
        if nworkers is None:
            nworkers = threading.active_count()
            utils.p_header(f'nworkers = {nworkers}')

        def undo_path(i, path):
            if rename_tag in path:
                new_path = str(path)
                new_path = new_path.replace(rename_tag, '')
                os.rename(path, new_path)
                self.__dict__[f'{comp}_paths'][i] = new_path
                # utils.p_success(f'>>> File {i:05d}: {os.path.basename(path)} -> {os.path.basename(new_path)}')

        for comp in comps:
            with tqdm(desc=f'Processing {comp}', total=len(self.__dict__[f'{comp}_paths'])) as pbar:
                with ThreadPoolExecutor(nworkers) as exe:
                    futures = [exe.submit(undo_path, i, path) for i, path in enumerate(self.__dict__[f'{comp}_paths'])]
                    [pbar.update(1) for future in as_completed(futures)]
                        

    def rm_renamed(self, comps=['atm', 'ice', 'ocn', 'rof', 'lnd']):
        for comp in comps:
            for i, path in enumerate(tqdm(self.__dict__[f'{comp}_paths'], desc=f'Processing {comp}')):
                if self.rename_tag in path:
                    os.remove(path)
                    del(self.__dict__[f'{comp}_paths'][i])

    def mk_backups(self, dest=None, comps=['rest', 'logs'], nworkers=None):
        if nworkers is None:
            nworkers = threading.active_count()
            utils.p_header(f'nworkers = {nworkers}')

        if dest is None:
            dest = self.dirpath.replace('archive', 'timeseries')
            utils.p_header(f'>>> Destination: {dest}')
        
        def copy_file(src, dest):
            if not os.path.exists(dest):
                shutil.copyfile(src, dest)

        for comp in comps:
            if not os.path.exists(os.path.join(dest, comp)):
                os.mkdir(os.path.join(dest, comp))
                
            paths = sorted(glob.glob(os.path.join(self.dirpath, comp, '*')))
            with tqdm(desc=f'Processing {comp}', total=len(paths)) as pbar:
                with ThreadPoolExecutor(nworkers) as exe:
                    futures = [exe.submit(copy_file, src, os.path.join(dest, comp, os.path.basename(src))) for src in paths]
                    [pbar.update(1) for future in as_completed(futures)]


# class Archive:
    
#     def __init__(self, paths, output_dir='./output', load_num=None, settings_csv=None):
#         if load_num < 0:
#             self.paths = self.paths[load_num:]
#         else:
#             self.paths = self.paths[:load_num]
#         utils.p_header(f'>>> {len(self.paths)} Archive.paths:')
#         print(f'Start: {os.path.basename(self.paths[0])}')
#         print(f'End: {os.path.basename(self.paths[-1])}')

#         ds_all_vars = self.get_ds()
#         self.vars = list(ds_all_vars.variables)
#         utils.p_success(f'>>> Archive.vars created')
#         if 'ncol' in ds_all_vars.dims:
#             self.grid = 'SE'
#             self.grid_weight = ds_all_vars.area.fillna(0)
#             self.grid_dim = 'ncol'
#             self.lat = ds_all_vars.lat
#         elif 'lat' in ds_all_vars.dims and 'lon' in ds_all_vars.dims:
#             self.grid = 'FV'
#             self.grid_weight = ds_all_vars.gw.fillna(0)
#             self.grid_dim = ('lat', 'lon')
#             self.lat = ds_all_vars.lat
#         elif 'z_t' in ds_all_vars.dims and 'moc_z' in ds_all_vars.dims:
#             self.grid = 'OCN'
#             self.grid_weight = ds_all_vars.TAREA.fillna(0)
#             self.grid_dim = ('nlat', 'nlon')
#             self.lat = ds_all_vars.TLAT
#         elif 'ni' in ds_all_vars.dims and 'nj' in ds_all_vars.dims:
#             self.grid = 'ICE'
#             self.grid_weight = ds_all_vars.tarea.fillna(0)
#             self.grid_dim = ('ni', 'nj')
#             self.lat = ds_all_vars.TLAT
#         elif 'lndgrid' in ds_all_vars.dims:
#             self.grid = 'LND'
#             self.grid_weight = ds_all_vars.area.fillna(0)
#             self.grid_dim = ('lndgrid')
#             self.lat = ds_all_vars.lat
#         else:
#             raise ValueError('Unkonwn grid!')

#         utils.p_header(f'>>> Archive.grid: {self.grid}')

#         self.output_dir = output_dir
#         os.makedirs(self.output_dir, exist_ok=True)
#         utils.p_header(f'>>> Archive.output_dir: {self.output_dir}')

#         if settings_csv is not None:
#             settings_df = pd.read_csv(settings_csv, index_col=0)
#             self.settings_csv = settings_csv
#             self.settings_df = settings_df
#             utils.p_header(f'>>> Archive.settings_csv: {self.settings_csv}')
#             utils.p_success(f'>>> Archive.settings_df created')

#     def get_ds(self, load_num=1):
#         ''' Get a `xarray.Dataset` from a certain file
#         '''
#         with xr.open_mfdataset(self.paths[:load_num]) as ds:
#             return ds

#     def slice2series(self, vn=['TS', 'FSNT', 'FLNT', 'LWCF', 'SWCF', 'ICEFRAC', 'MOC', 'aice', 'TSA'], load_num=None, account=None, **qsub_kws):
#         if type(vn) is not list: vn = [vn]
#         vn = list(set(vn) - (set(vn) - set(self.vars)))
#         for v in vn:
#             name = f'slice2series_{v}'
#             pbs_fname = f'pbs_{name}.zsh'
#             paths = ''
#             for path in self.paths[:load_num]:
#                 paths += path
#                 paths += ' '

#             output_fpath = os.path.join(self.output_dir, f'{v}.nc')
#             if os.path.exists(output_fpath):
#                 os.remove(output_fpath)

#             cmd = f'''
# module list > /dev/null 2>&1 || source $LMOD_ROOT/lmod/init/zsh
# module --force purge
# module load ncarenv-basic/23.09 intel-classic/2023.2.1
# module load nco
# module load udunits
# ncrcat -v {v} {paths} {os.path.abspath(output_fpath)}
#             '''
#             utils.make_pbs(cmd=cmd, name=name, pbs_fname=pbs_fname, account=account, **qsub_kws)
#             utils.run_shell(f'qsub {pbs_fname}')
#             utils.p_header(f'The output will be located at: {os.path.abspath(output_fpath)}')
    
#     def clean_pbs(self):
#         utils.run_shell(f'rm -rf *slice2series*')

#     def clim(self, timeslice=None, vn=['aice'], adjust_month=True):
#         if type(vn) is not list: vn = [vn]
#         vn = list(set(vn) - (set(vn) - set(self.vars)))
#         ds = xr.Dataset()
#         for v in vn:
#             da = xr.open_dataset(os.path.join(self.output_dir, f'{v}.nc'))[v]
#             if adjust_month:
#                 da['time'] = da['time'].get_index('time') - datetime.timedelta(days=1)
#             if timeslice is not None:
#                 da_clim = da.isel(time=timeslice).groupby('time.month').mean('time')
#             else:
#                 da_clim = da.groupby('time.month').mean('time')
#             ds[v] = da_clim
#         return ds

#     def ann(self, vn=['TS', 'FSNT', 'FLNT', 'LWCF', 'SWCF', 'MOC', 'aice'], adjust_month=True):
#         if type(vn) is not list: vn = [vn]
#         vn = list(set(vn) - (set(vn) - set(self.vars)))
#         ds = xr.Dataset()
#         for v in vn:
#             da = xr.open_dataset(os.path.join(self.output_dir, f'{v}.nc'))[v]
#             if adjust_month:
#                 da['time'] = da['time'].get_index('time') - datetime.timedelta(days=1)
#             da_ann = utils.monthly2annual(da)
#             ds[v] = da_ann
#         return ds

#     def gm(self, ds):
#         ds_res = ds.weighted(self.grid_weight).mean(self.grid_dim)
#         return ds_res

#     def nhm(self, ds):
#         ds_res = ds.where(self.lat>=0).weighted(self.grid_weight).mean(self.grid_dim)
#         return ds_res

#     def shm(self, ds):
#         ds_res = ds.where(self.lat<=0).weighted(self.grid_weight).mean(self.grid_dim)
#         return ds_res

#     def calc_ts(self, vn=['GMST', 'GMRESTOM', 'GMLWCF', 'GMSWCF', 'GMTSA'], adjust_month=True):
#         if type(vn) is not list: vn = [vn]
#         vn_map = {
#             'GMST': 'TS',
#             'GMRESTOM': ('FSNT', 'FLNT'),
#             'GMLWCF': 'LWCF',
#             'GMSWCF': 'SWCF',
#             'GMTSA': 'TSA',
#         }
#         vn_raw = []
#         for v in vn_map.values():
#             if isinstance(v, (list, tuple)):
#                 vn_raw.extend(v)
#             else:
#                 vn_raw.append(v)
            
#         # remove unavailble variables
#         vn_raw = list(set(vn_raw) - (set(vn_raw) - set(self.vars)))
#         vn_new = []
#         for v in vn:
#             if isinstance(vn_map[v], (list, tuple)):
#                 if set(vn_map[v]) <= set(vn_raw):
#                     vn_new.append(v)
#             else:
#                 if vn_map[v] in set(vn_raw):
#                     vn_new.append(v)
#         vn = vn_new

#         ds = xr.Dataset()
#         for v in vn:
#             if v[:2] == 'GM':
#                 ds_raw = self.gm(self.ann(adjust_month=adjust_month, vn=vn_raw))
#             elif v[:2] == 'NH':
#                 ds_raw = self.nhm(self.ann(adjust_month=adjust_month, vn=vn_raw))
#             elif v[:2] == 'SH':
#                 ds_raw = self.shm(self.ann(adjust_month=adjust_month, vn=vn_raw))

#             if v == 'GMST' or v == 'GMTSA':
#                 ds[v] = ds_raw[vn_map[v]] - 273.15  # K -> degC
#             elif v == 'GMRESTOM':
#                 ds[v] = ds_raw[vn_map[v][0]] - ds_raw[vn_map[v][1]]
#             else:
#                 ds[v] = ds_raw[vn_map[v]]

#         self.diagnostic = ds
#         utils.p_success(f'Archive.diagnostic generated with variables: {vn}')

#     def plot_ts(self, vn=['GMST', 'GMRESTOM', 'GMLWCF', 'GMSWCF', 'GMTSA'], figsize=[10, 6], ncol=2, wspace=0.3, hspace=0.2, xlim=None, title=None,
#                         xlabel='Time [yr]', ylable_dict=None, color_dict=None, ylim_dict=None, ax=None, print_settings=True,
#                         prt_setting_list=['cldfrc_rhminl', 'micro_mg_dcs'], **plot_kws):
#         # remove unavailable variables
#         vn_new = []
#         for v in vn:
#             if v in self.diagnostic:
#                 vn_new.append(v)
#         vn = vn_new

#         if ax is None:
#             fig = plt.figure(figsize=figsize)
#             ax = {}

#         nrow = int(np.ceil(len(vn)/ncol))
#         gs = gridspec.GridSpec(nrow, ncol)
#         gs.update(wspace=wspace, hspace=hspace)

#         _ylim_dict = {
#             'GMST': (13.5, 15.5),
#             'GMRESTOM': (-1, 3),
#             'GMLWCF': (24, 26),
#             'GMSWCF': (-52, -44),
#             'GMTSA': (6, 10),
#         }
#         if ylim_dict is not None:
#             _ylim_dict.update(ylim_dict)

#         _ylb_dict = {
#             'GMST': r'GMST [$^\circ$C]',
#             'GMRESTOM': r'GMRESTOM [W/m$^2$]',
#             'GMLWCF': r'GMLWCF [W/m$^2$]',
#             'GMSWCF': r'GMSWCF [W/m$^2$]',
#             'GMTSA': r'GMTSA [$^\circ$C]',
#         }
#         if ylable_dict is not None:
#             _ylb_dict.update(ylable_dict)

#         _clr_dict = {
#             'GMST': 'tab:red',
#             'GMRESTOM': 'tab:blue',
#             'GMLWCF': 'tab:green',
#             'GMSWCF': 'tab:orange',
#             'GMTSA': 'tab:red',
#         }
#         if color_dict is not None:
#             _clr_dict.update(color_dict)

#         i = 0
#         i_row, i_col = 0, 0
#         for v in vn:
#             if 'fig' in locals():
#                 ax[v] = fig.add_subplot(gs[i_row, i_col])

#             if i_row == nrow-1:
#                 _xlb = xlabel
#             else:
#                 _xlb = None


#             if v == 'GMRESTOM':
#                 ax[v].axhline(y=0, linestyle='--', color='tab:grey')
#             elif v == 'GMLWCF':
#                 ax[v].axhline(y=25, linestyle='--', color='tab:grey')
#             elif v == 'GMSWCF':
#                 ax[v].axhline(y=-47, linestyle='--', color='tab:grey')
#             elif v == 'GMST':
#                 ax[v].axhline(y=14, linestyle='--', color='tab:grey')

#             _plot_kws = {
#                 'linewidth': 2,
#             }
#             if plot_kws is not None:
#                 _plot_kws.update(plot_kws)
            
#             ax[v].plot(self.diagnostic[v].time.values, self.diagnostic[v].values, color=_clr_dict[v], **_plot_kws)
#             if xlim is not None:
#                 ax[v].set_xlim(xlim)
#             ax[v].set_ylim(_ylim_dict[v])
#             ax[v].set_xlabel(_xlb)
#             ax[v].set_ylabel(_ylb_dict[v])

#             i += 1
#             i_col += 1

#             if i % 2 == 0:
#                 i_row += 1

#             if i_col == ncol:
#                 i_col = 0

#         if hasattr(self, 'settings_df') and print_settings:
#             settings_info = ''
#             for name in prt_setting_list:
#                 nm = f'atm: {name}'
#                 settings_info += f'{name}: {self.settings_df.loc[nm].values[0].strip()}'
#                 settings_info += ', '
#             settings_info = settings_info[:-2]

#         if 'settings_info' in locals():
#             if title is None:
#                 title = settings_info
#             else:
#                 title += f'\n{settings_info}'

#             fig.suptitle(title)

#         if 'fig' in locals():
#             return fig, ax
#         else:
#             return ax

#     def calc_amoc(self, adjust_month=True):
#         ds_raw = self.ann(adjust_month=adjust_month, vn=['MOC'])
#         ds_raw['moc_z'] = ds_raw['moc_z']/1e5  # cm -> km
#         ds_raw['moc_z'].attrs['units'] = 'km'
#         ds = xr.Dataset()

#         ds['amoc_yz'] = ds_raw['MOC'].isel(
#             transport_reg=1, moc_comp=0, time=slice(-30, None),
#         ).mean('time').where(ds_raw['MOC'].lat_aux_grid>-35)

#         ds['amoc_t'] = ds_raw['MOC'].isel(
#             transport_reg=1, moc_comp=0,
#         ).sel(
#             moc_z=slice(0.5, None), lat_aux_grid=slice(28, 90),
#         ).max(dim=('moc_z', 'lat_aux_grid'))

#         self.diagnostic = ds
#         utils.p_success(f'Archive.diagnostic generated with variables: {["amoc_t", "amoc_yz"]}')

#     def plot_amoc(self, figsize=[10, 4], ncol=2, wspace=0.3, hspace=0.2, title=None,
#                         amoc_levels=np.linspace(-24, 24, 25), xlabel_dict=None, ylable_dict=None, ax=None, print_settings=True,
#                         prt_setting_list=['cldfrc_rhminl', 'micro_mg_dcs'], amoc_t_xlim=None, amoc_t_ylim=(4, 30), **plot_kws):
#         if ax is None:
#             fig = plt.figure(figsize=figsize)
#             ax = {}

#         _xlb_dict = {
#             'amoc_yz': 'Latitude',
#             'amoc_t': 'Time [yr]',
#         }
#         if xlabel_dict is not None:
#             _xlb_dict.update(xlabel_dict)

#         _ylb_dict = {
#             'amoc_yz': 'Depth [km]',
#             'amoc_t': 'AMOC [Sv]',
#         }
#         if ylable_dict is not None:
#             _ylb_dict.update(ylable_dict)

#         gs = gridspec.GridSpec(1, ncol)
#         gs.update(wspace=wspace, hspace=hspace)

#         i = 0
#         i_row, i_col = 0, 0
#         ds = self.diagnostic
#         for v in ['amoc_t', 'amoc_yz']:
#             if 'fig' in locals():
#                 ax[v] = fig.add_subplot(gs[i_row, i_col])

#             if v == 'amoc_yz':
#                 im = ax[v].contourf(ds[v].lat_aux_grid, ds[v].moc_z, ds[v], cmap='RdBu_r', extend='both', levels=amoc_levels)
#                 ax[v].set_xticks([-30, 0, 30, 60, 90])
#                 ax[v].set_xlim([-35, 90])
#                 ax[v].invert_yaxis()
#                 ax[v].set_yticks([0, 2, 4])
#                 cbar = fig.colorbar(im, extend='both', shrink=0.9, ax=ax[v])
#                 cbar.ax.set_title('[Sv]')

#             elif v == 'amoc_t':
#                 ax[v].plot(ds[v].time, ds[v])
#                 ax[v].set_ylim(amoc_t_ylim)
#                 if amoc_t_xlim is not None:
#                     ax[v].set_xlim(amoc_t_xlim)

#             ax[v].set_xlabel(_xlb_dict[v])
#             ax[v].set_ylabel(_ylb_dict[v])
#             _plot_kws = {
#                 'linewidth': 2,
#             }
#             if plot_kws is not None:
#                 _plot_kws.update(plot_kws)

#             i += 1
#             i_col += 1

#             if i % 2 == 0:
#                 i_row += 1

#             if i_col == ncol:
#                 i_col = 0

#         if hasattr(self, 'settings_df') and print_settings:
#             settings_info = ''
#             for name in prt_setting_list:
#                 nm = f'atm: {name}'
#                 settings_info += f'{name}: {self.settings_df.loc[nm].values[0].strip()}'
#                 settings_info += ', '
#             settings_info = settings_info[:-2]

#         if 'settings_info' in locals():
#             if title is None:
#                 title = settings_info
#             else:
#                 title += f'\n{settings_info}'

#                 fig.suptitle(title)

#         if 'fig' in locals():
#             return fig, ax
#         else:
#             return ax

#     def calc_nhaice(self, vn='ICEFRAC', adjust_month=True, timeslice=None):
#         ds = xr.Dataset()
#         ds_ann = self.ann(adjust_month=adjust_month, vn=vn)
#         ds_clim = self.clim(timeslice=timeslice, vn=vn, adjust_month=adjust_month)

#         if vn == 'ICEFRAC':
#             convert_factor = 4*np.pi*6.37122**2 / self.grid_weight.sum().values  # 1e6 km^2
#         elif vn == 'aice':
#             convert_factor = 4*np.pi*6.37122**2 / self.grid_weight.sum().values / 100  # 1e6 km^2

#         ds['NHAICE'] = ds_ann[vn].where(self.lat>0).weighted(self.grid_weight).sum(self.grid_dim) * convert_factor
#         ds['clim_NHAICE'] = ds_clim[vn].where(self.lat>0).weighted(self.grid_weight).sum(self.grid_dim) * convert_factor

#         self.diagnostic = ds
#         self.diagnostic = ds
#         utils.p_success(f'Archive.diagnostic generated with variables: {["NHAICE", "clim_NHAICE"]}')

#     def plot_nhaice(self, figsize=[10, 4], ncol=2, wspace=0.3, hspace=0.2, title=None,
#                         xlabel_dict=None, ax=None, print_settings=True, nhaice_ylim=(4, 16),
#                         prt_setting_list=['cldfrc_rhminl', 'micro_mg_dcs'], **plot_kws):
#         if ax is None:
#             fig = plt.figure(figsize=figsize)
#             ax = {}

#         _xlb_dict = {
#             'clim_NHAICE': 'Month',
#             'NHAICE': 'Time [yr]',
#         }
#         if xlabel_dict is not None:
#             _xlb_dict.update(xlabel_dict)

#         gs = gridspec.GridSpec(1, ncol)
#         gs.update(wspace=wspace, hspace=hspace)

#         i = 0
#         i_row, i_col = 0, 0
#         ds = self.diagnostic
#         for v in ['NHAICE', 'clim_NHAICE']:
#             if 'fig' in locals():
#                 ax[v] = fig.add_subplot(gs[i_row, i_col])

#             if v == 'NHAICE':
#                 ax[v].plot(ds[v].time, ds[v])
#                 ax[v].set_title('NH Sea-ice Area')

#             elif v == 'clim_NHAICE':
#                 ax[v].plot(ds[v].month, ds[v])
#                 ax[v].set_xticks(list(range(1, 13)))
#                 ax[v].set_title('Annual Cycle of NH Sea-ice Area')


#             ax[v].set_ylim(nhaice_ylim)
#             ax[v].set_xlabel(_xlb_dict[v])
#             ax[v].set_ylabel(r'NHAICE [10$^6$ km$^2$]')
#             _plot_kws = {
#                 'linewidth': 2,
#             }
#             if plot_kws is not None:
#                 _plot_kws.update(plot_kws)

#             i += 1
#             i_col += 1

#             if i % 2 == 0:
#                 i_row += 1

#             if i_col == ncol:
#                 i_col = 0

#         if hasattr(self, 'settings_df') and print_settings:
#             settings_info = ''
#             for name in prt_setting_list:
#                 nm = f'atm: {name}'
#                 settings_info += f'{name}: {self.settings_df.loc[nm].values[0].strip()}'
#                 settings_info += ', '
#             settings_info = settings_info[:-2]

#         if 'settings_info' in locals():
#             if title is None:
#                 title = settings_info
#             else:
#                 title += f'\n{settings_info}'

#                 fig.suptitle(title)

#         if 'fig' in locals():
#             return fig, ax
#         else:
#             return ax

# class Archives:
#     def __init__(self, archive_dict=None):
#         self.archive_dict = archive_dict
#         for k, v in self.archive_dict.items():
#             v.name = k
    
#     def calc_ts(self):
#         for k, v in self.archive_dict.items():
#             print(f'>>> Processing {k} ...')
#             self.archive_dict[k].calc_diagnostic_atm()

#     def calc_amoc(self):
#         for k, v in self.archive_dict.items():
#             print(f'>>> Processing {k} ...')
#             self.archive_dict[k].calc_diagnostic_ocn()

#     def plot_ts(self, vn=['GMST', 'GMRESTOM', 'GMLWCF', 'GMSWCF', 'NHAICE'], figsize=[10, 6], ncol=2, wspace=0.3, hspace=0.2, xlim=(0, 100), title=None,
#                         xlabel='Time [yr]', ylable_dict=None, ylim_dict=None, ax=None, prt_setting_list=['cldfrc_rhminl', 'micro_mg_dcs'], lgd_anchor=(-1, -1.2),
#                         plot_list=None, **plot_kws):

#         if ax is None:
#             fig = plt.figure(figsize=figsize)
#             ax = {}

#         nrow = int(np.ceil(len(vn)/ncol))
#         gs = gridspec.GridSpec(nrow, ncol)
#         gs.update(wspace=wspace, hspace=hspace)

#         _ylim_dict = {
#             'GMST': (13.5, 15.5),
#             'GMRESTOM': (-1, 3),
#             'GMLWCF': (24, 26),
#             'GMSWCF': (-52, -44),
#         }
#         if ylim_dict is not None:
#             _ylim_dict.update(ylim_dict)

#         _ylb_dict = {
#             'GMST': r'GMST [$^\circ$C]',
#             'GMRESTOM': r'GMRESTOM [W/m$^2$]',
#             'GMLWCF': r'GMLWCF [W/m$^2$]',
#             'GMSWCF': r'GMSWCF [W/m$^2$]',
#         }
#         if ylable_dict is not None:
#             _ylb_dict.update(ylable_dict)

#         i = 0
#         i_row, i_col = 0, 0
#         for v in vn:
#             if 'fig' in locals():
#                 ax[v] = fig.add_subplot(gs[i_row, i_col])

#             if i_row == nrow-1:
#                 _xlb = xlabel
#             else:
#                 _xlb = None


#             if v == 'GMRESTOM':
#                 ax[v].axhline(y=0, linestyle='--', color='tab:grey')
#             elif v == 'GMLWCF':
#                 ax[v].axhline(y=25, linestyle='--', color='tab:grey')
#             elif v == 'GMSWCF':
#                 ax[v].axhline(y=-47, linestyle='--', color='tab:grey')
#             elif v == 'GMST':
#                 ax[v].axhline(y=14, linestyle='--', color='tab:grey')

#             _plot_kws = {
#                 'linewidth': 2,
#             }
#             if plot_kws is not None:
#                 _plot_kws.update(plot_kws)
            
#             if plot_list is None: plot_list = list(self.archive_dict.keys())
#             for k, ar in self.archive_dict.items():
#                 if k in plot_list:
#                     settings_info = ''
#                     for name in prt_setting_list:
#                         nm = f'atm: {name}'
#                         settings_info += f'{name}: {ar.settings_df.loc[nm].values[0].strip()}'
#                         settings_info += ', '
#                     settings_info = settings_info[:-2]

#                     ax[v].plot(ar.diagnostic[v].time.values, ar.diagnostic[v].values, label=settings_info, **_plot_kws)

#             ax[v].set_xlim(xlim)
#             ax[v].set_ylim(_ylim_dict[v])
#             ax[v].set_xlabel(_xlb)
#             ax[v].set_ylabel(_ylb_dict[v])

#             i += 1
#             i_col += 1

#             if i % 2 == 0:
#                 i_row += 1

#             if i_col == ncol:
#                 i_col = 0

#         ax[v].legend(loc='lower left', bbox_to_anchor=lgd_anchor)
#         if title is not None:
#             fig.suptitle(title)

#         if 'fig' in locals():
#             return fig, ax
#         else:
#             return ax
            
#     def calc_som_forcings(self, ds_clim, time_name='month', lat_name='TLAT', lon_name='TLONG',
#                               z_name='z_t', hblt_name='HBLT', temp_name='TEMP', salt_name='SALT',
#                               uvel_name='UVEL', vvel_name='VVEL', shf_name='SHF', qflux_name='QFLUX',
#                               anglet_name='ANGLET', region_mask_name='REGION_MASK',
#                               save_path=None, save_format='NETCDF3_CLASSIC'):
#         ''' Calculate the slab ocean forcing

#         Reference: NCL scripts by Jiang Zhu (jiangzhu@ucar.edu) at:  /glade/u/home/jiangzhu/notebooks/pop_frc_mlt.b.e21.B1850.f19_g17.PaleoCalibr.PI.02.ncl
#         '''
#         ds_clim = ds_clim.rename({time_name: 'time', 'nlat': 'nj', 'nlon': 'ni'})
#         ds_clim.coords['time'] = [cftime.DatetimeNoLeap(1,i,1,0,0,0,0, has_year_zero=True) for i in range(1, 13)]

#         hbltin = ds_clim[hblt_name]
#         hblt_avg = hbltin.mean('time')
#         hblttmp = hblt_avg.expand_dims({'time': 12})/100

#         z_t = ds_clim[z_name]
#         zint = (z_t.values[:-1] + z_t.values[1:])/2/100
#         zint = np.insert(zint, 0, 0)
#         zint = np.append(zint, 2*z_t.values[-1]/100-zint[-1])
#         dz = np.diff(zint)

#         xc = ds_clim[lon_name]
#         yc = ds_clim[lat_name]
#         nlat, nlon = xc.shape
#         ntime = 12
#         nz = len(z_t)

#         # calculate weighted T and S
#         wgt = np.empty((ntime, nz, nlat, nlon))
#         for i in range(nz):
#             dz_tmp = hblttmp.values - zint[i]
#             dz_tmp = np.where(dz_tmp < 0, np.nan, dz_tmp)
#             dz_tmp = np.where(dz_tmp > dz[i], dz[i], dz_tmp)
#             dz_tmp = dz_tmp / hblttmp
#             wgt[:,i,:,:] = dz_tmp

#         Ttmp = ds_clim[temp_name]
#         Stmp = ds_clim[salt_name]
#         Ttmp2 = Ttmp * wgt
#         Stmp2 = Stmp * wgt 

#         Tin = Ttmp2.sum(dim=z_name)
#         Sin = Stmp2.sum(dim=z_name)

#         # calculate velocities
#         Utmp = ds_clim[uvel_name][:,0,:,:]
#         Vtmp = ds_clim[vvel_name][:,0,:,:]
#         ang = ds_clim[anglet_name]

#         Utmp2 = Utmp * 0
#         Vtmp2 = Vtmp * 0

#         Utmp2[:,1:,1:] = 0.25*(Utmp[:,1:,1:] + Utmp[:,1:,:-1]+Utmp[:,:-1,1:]+Utmp[:,:-1,:-1])
#         Vtmp2[:,1:,1:] = 0.25*(Vtmp[:,1:,1:] + Vtmp[:,1:,:-1]+Vtmp[:,:-1,1:]+Vtmp[:,:-1,:-1])

#         Uin = (Utmp2*np.cos(ang) + Vtmp2*np.sin(-ang))*0.01
#         Vin = (Vtmp2*np.cos(ang) - Utmp2*np.sin(-ang))*0.01

#         # calculate ocean heat
#         shf = ds_clim[shf_name]
#         qflux = ds_clim[qflux_name]
#         rcp_sw = 1026.*3996.
#         surf = shf+qflux
#         T1 = Tin.values.copy()
#         T1[:-1] = Tin[1:]
#         T1[-1] = Tin[0]
#         T2 = Tin.values.copy()
#         T2[0] = Tin[-1]
#         T2[1:] = Tin[:-1]
#         dT = T1 - T2
#         release = rcp_sw*dT*hblttmp / (86400.*365./6.)
#         ocnheat = surf-release
            
#         # area weighted
#         tarea = ds_clim['TAREA']
#         maskt = np.ones((nlat, nlon))
#         maskt = maskt*(~np.isnan(ocnheat[0,:,:]))
#         err = np.empty(12)
#         for i in range(12):
#             oh_tmp = ocnheat.values[i].flatten()
#             oh_tmp[np.isnan(oh_tmp)] = 0
#             err[i] = np.matmul(oh_tmp,tarea.values.flatten())/np.sum(tarea.values*maskt.values)

#         glob = np.mean(err)
#         ocnheat -= glob

#         # calculate the inverse matrix
#         dhdxin = Tin * 0
#         dhdyin = Tin * 0

#         daysinmo = np.array([31.,28.,31.,30.,31.,30.,31.,31.,30.,31.,30.,31.])
#         xnp = np.copy(daysinmo)
#         xnm = np.copy(daysinmo)

#         xnm[1:] = daysinmo[1:] + daysinmo[:-1]
#         xnm[0] = daysinmo[0] + daysinmo[-1]

#         xnp[:-1] = daysinmo[1:] + daysinmo[:-1]
#         xnp[-1] = daysinmo[0] + daysinmo[-1]

#         aa = 2 * daysinmo / xnm
#         cc = 2 * daysinmo / xnp
#         a = aa / 8.
#         c = cc / 8.
#         b = 1 - a - c

#         M = [
#             [b[0], c[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, a[0]],
#             [a[1], b[1], c[1], 0, 0, 0, 0, 0, 0, 0, 0, 0],
#             [0, a[2], b[2], c[2], 0, 0, 0, 0, 0, 0, 0, 0],
#             [0, 0, a[3], b[3], c[3], 0, 0, 0, 0, 0, 0, 0],
#             [0, 0, 0, a[4], b[4], c[4], 0, 0, 0, 0, 0, 0],
#             [0, 0, 0, 0, a[5], b[5], c[5], 0, 0, 0, 0, 0],
#             [0, 0, 0, 0, 0, a[6], b[6], c[6], 0, 0, 0, 0],
#             [0, 0, 0, 0, 0, 0, a[7], b[7], c[7], 0, 0, 0],
#             [0, 0, 0, 0, 0, 0, 0, a[8], b[8], c[8], 0, 0],
#             [0, 0, 0, 0, 0, 0, 0, 0, a[9], b[9], c[9], 0],
#             [0, 0, 0, 0, 0, 0, 0, 0, 0, a[10], b[10], c[10]],
#             [c[11], 0, 0, 0, 0, 0, 0, 0, 0, 0, a[11], b[11]],
#         ]
#         invM = np.linalg.inv(M)

#         # prepare output vars
#         T = xr.full_like(Tin, 0)
#         S = xr.full_like(Sin, 0)
#         U = xr.full_like(Uin, 0)
#         V = xr.full_like(Vin, 0)
#         dhdx = xr.full_like(dhdxin, 0)
#         dhdy = xr.full_like(dhdyin, 0)
#         hblt = xr.full_like(hbltin, 0)
#         qdp = xr.full_like(shf, 0)

#         for j in range(12):
#             for i in range(12):
#                 T[j] += invM[j, i]*Tin[i]
#                 S[j] += invM[j, i]*Sin[i]
#                 U[j] += invM[j, i]*Uin[i]
#                 V[j] += invM[j, i]*Vin[i]
#                 dhdx[j] += invM[j, i]*dhdxin[i]
#                 dhdy[j] += invM[j, i]*dhdyin[i]
#                 hblt[j] += invM[j, i]*hblttmp[i]
#                 qdp[j] += invM[j, i]*ocnheat[i]

#         ds_out = xr.Dataset()
#         ds_out['time'] = ds_clim['time']
#         ds_out['time'].attrs['long_name'] = 'days since 0001-01-01 00:00:00'
#         ds_out['time'].attrs['units'] = 'observation time'
#         ds_out['time'].attrs['calendar'] = 'noleap'

#         ds_out['xc'] = xc
#         ds_out['xc'].attrs['long_name'] = 'longitude of grid cell center'
#         ds_out['xc'].attrs['units'] = 'degrees east'

#         ds_out['yc'] = yc
#         ds_out['yc'].attrs['long_name'] = 'latitude of grid cell center'
#         ds_out['yc'].attrs['units'] = 'degrees north'

#         ds_out['T'] = T.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['T'].attrs['long_name'] = 'temperature'
#         ds_out['T'].attrs['units'] = 'degC'

#         ds_out['S'] = S.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['S'].attrs['long_name'] = 'salinity'
#         ds_out['S'].attrs['units'] = 'ppt'

#         ds_out['U'] = U.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['U'].attrs['long_name'] = 'u ocean current'
#         ds_out['U'].attrs['units'] = 'm/s'

#         ds_out['V'] = V.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['V'].attrs['long_name'] = 'v ocean current'
#         ds_out['V'].attrs['units'] = 'm/s'

#         ds_out['dhdx'] = dhdx.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['dhdx'].attrs['long_name'] = 'ocean surface slope: zonal'
#         ds_out['dhdx'].attrs['units'] = 'm/m'

#         ds_out['dhdy'] = dhdy.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['dhdy'].attrs['long_name'] = 'ocean surface slope: meridional'
#         ds_out['dhdy'].attrs['units'] = 'm/m'

#         ds_out['hblt'] = hblt.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['hblt'].attrs['long_name'] = 'boundary layer depth'
#         ds_out['hblt'].attrs['units'] = 'm'

#         ds_out['qdp'] = qdp.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['qdp'].attrs['long_name'] = 'ocean heat flux convergence'
#         ds_out['qdp'].attrs['units'] = 'W/m^2'

#         ds_out['area'] = tarea
#         ds_out['area'].attrs['long_name'] = 'area of grid cell in radians squared'
#         ds_out['area'].attrs['units'] = 'area'

#         ds_out['mask'] = ds_clim[region_mask_name]
#         ds_out['mask'].attrs['long_name'] = 'domain maskr'
#         ds_out['mask'].attrs['units'] = 'unitless'

#         ds_out.attrs['title'] = 'Monthly averaged ocean forcing from POP output'
#         ds_out.attrs['conventions'] = 'CCSM data model domain description'
#         ds_out.attrs['source'] = 'cfr.gcm.GCMCase.calc_slab_ocn_forcing (https://github.com/fzhu2e/cfr)'
#         ds_out.attrs['description'] = 'Input data for DOCN7 mixed layer model'
#         ds_out.attrs['note1'] = 'fields computed from 100-yr monthly means from pop'
#         ds_out.attrs['note2'] = 'all fields interpolated to T-grid'
#         ds_out.attrs['note3'] = 'qdp is computed from depth summed ocean column'
#         ds_out.attrs['author'] = 'Feng Zhu (fengzhu@ucar.edu), Jiang Zhu (jiangzhu@ucar.edu)'
#         ds_out.attrs['calendar'] = 'standard'
#         ds_out.attrs['comment'] = 'This data is on the displaced pole grid gx1v7'
#         ds_out.attrs['creation_date'] = datetime.date.today().strftime('%m/%d/%Y')

#         if save_path is not None:
#             ds_out.to_netcdf(save_path, format=save_format)

#         return ds_out

#     def calc_cam_forcings(self, SST, aice, SST_time_name='time', SST_lat_name='TLAT', SST_lon_name='TLONG',
#                           aice_time_name='time', aice_lat_name='TLAT', aice_lon_name='TLON',
#                           save_path=None, save_format='NETCDF3_CLASSIC'):
#         ''' Calculate the forcings for CAM only simulation (F-case)

#         Note that the regridding is implemented by `pyresample` here instead of ESMF.

#         Reference: NCL scripts by Cecile Hannay (hannay@ucar.edu) at: /glade/u/home/hannay/ncl_scripts/sst/B1850_cmip6
#         '''
#         ds_out = xr.Dataset(
#             coords={
#                 'time': SST[SST_time_name],
#                 'lat': np.linspace(-89.5, 89.5, 180),
#                 'lon': np.linspace(0.5, 359.5, 360),
#             }
#         )
#         ds_out['time'].attrs['information'] = 'middle of month'
#         ds_out['time'].attrs['calendar'] = 'gregorian'
#         ds_out['time'].attrs['units'] = 'days since 0001-01-01 00:00:00'

#         ds_out['lat'].attrs['long_name'] = 'latitude'
#         ds_out['lat'].attrs['units'] = 'degrees_north'

#         ds_out['lon'].attrs['long_name'] = 'longitude'
#         ds_out['lon'].attrs['units'] = 'degrees_east'


#         SST_rgd, _, _ = regrid_field_curv_rect(
#             SST.values, SST[SST_lat_name].values, SST[SST_lon_name].values,
#             ds_out.lat.values, ds_out.lon.values)

#         aice_rgd, _, _ = regrid_field_curv_rect(
#             aice.values, aice[aice_lat_name].values, aice[aice_lon_name].values,
#             ds_out.lat.values, ds_out.lon.values)

#         ds_out['SST'] = xr.DataArray(SST_rgd, coords=ds_out.coords)
#         ds_out['SST'].attrs['long_name'] = 'Sea-Surface temperature'
#         ds_out['SST'].attrs['units']     = 'deg_C'

#         ds_out['SEAICE'] = xr.DataArray(aice_rgd*100, coords=ds_out.coords)
#         ds_out['SEAICE'].attrs['long_name'] = 'Sea Ice Concentration'
#         ds_out['SEAICE'].attrs['units']     = '%'

#         # Corrections for data consistency
#         # 1) If SST < -1.8 or ice frac >= 90%, SST = -1.8
#         mask = (ds_out['SST'] < -1.8) | (ds_out['SEAICE'] > 90)
#         ds_out['SST'].values[mask] = -1.8
#         # 2) min ice frac is 0%, max ice_frac is 100%
#         mask = ds_out['SEAICE'] < 0
#         ds_out['SEAICE'].values[mask] = 0
#         mask = ds_out['SEAICE'] > 100
#         ds_out['SEAICE'].values[mask] = 100
#         # 3) No sea ice if SST > 4.97
#         mask = ds_out['SST'] > 4.97
#         ds_out['SEAICE'].values[mask] = 0

#         ds_out['ICEFRAC'] = ds_out['SEAICE'] / 100.

#         if save_path is not None:
#             ds_out.to_netcdf(save_path, format=save_format)

#         return ds_out
        
                

# class GCMCases:
#     ''' The class for postprocessing multiple GCM simulation cases (e.g., CESM)
#     '''
#     def __init__(self, case_dict=None):
#         self.case_dict = case_dict
#         for k, v in self.case_dict.items():
#             v.name = k

#     def calc_atm_gm(self, vars=['GMST', 'GMRESTOM', 'GMLWCF', 'GMSWCF'], verbose=False):
#         for k, v in self.case_dict.items():
#             utils.p_header(f'Processing case: {k} ...')
#             v.calc_atm_gm(vars=vars, verbose=verbose)

#     def plot_ts(self, lgd_kws=None, lgd_idx=1, **plot_kws):
#         _clr_dict = {
#             'GMST': None,
#             'GMRESTOM': None,
#             'GMLWCF': None,
#             'GMSWCF': None,
#         }
#         for k, v in self.case_dict.items():
#             if 'fig' not in locals():
#                 fig, ax = v.plot_ts(color_dict=_clr_dict, label=v.name, **plot_kws)
#             else:
#                 ax = v.plot_ts(ax=ax, color_dict=_clr_dict, label=v.name, **plot_kws)

#         _lgd_kws = {
#             'frameon': False,
#             'loc': 'upper left',
#             'bbox_to_anchor': [1.1, 1],
#         }
#         if lgd_kws is not None:
#             _lgd_kws.update(lgd_kws)

#         vn = list(ax.keys())[lgd_idx]
#         ax[vn].legend(**_lgd_kws)

#         return fig, ax

            

# class GCMCase:
#     ''' The class for postprocessing a GCM simulation case (e.g., CESM)
    
#     Args:
#         dirpath (str): the directory path where the reconstruction results are stored.
#         load_num (int): the number of ensembles to load
#         verbose (bool, optional): print verbose information. Defaults to False.
#     '''

#     def __init__(self, dirpath=None, load_num=None, name=None, include_tags=[], exclude_tags=[], verbose=False):
#         self.fd = {}  # ClimateField
#         self.ts = {}  # EnsTS
#         self.name = name

#         if type(include_tags) is str:
#             include_tags = [include_tags]
#         if type(exclude_tags) is str:
#             exclude_tags = [exclude_tags]

#         if dirpath is not None:
#             fpaths = glob.glob(os.path.join(dirpath, '*.nc'))

#             self.paths = []
#             for path in fpaths:
#                 fname = os.path.basename(path)
#                 include = True

#                 for in_tag in include_tags:
#                     if in_tag not in fname:
#                         include = False

#                 for ex_tag in exclude_tags:
#                     if ex_tag in fname:
#                         include = False

#                 if include:
#                     self.paths.append(path)

#             self.paths = sorted(self.paths)
#             if load_num is not None:
#                 self.paths = self.paths[:load_num]

#         if verbose:
#             utils.p_header(f'>>> {len(self.paths)} GCMCase.paths:')
#             print(self.paths)

#     def get_ds(self, idx=0):
#         ''' Get a `xarray.Dataset` from a certain file
#         '''
#         with xr.open_dataset(self.paths[idx]) as ds:
#             return ds

#     def load(self, vars=None, time_name='time', z_name='z_t', z_val=None,
#              adjust_month=False, mode='timeslice',
#              save_dirpath=None, compress_params=None, verbose=False):
#         ''' Load variables.

#         Args:
#             vars (list): list of variable names.
#             time_name (str): the name of the time dimension.
#             z_name (str): the name of the z dimension (e.g., for ocean output).
#             z_val (float, int, list): the value(s) of the z dimension to pick (e.g., for ocean output).
#             adjust_month (bool): the current CESM version has a bug that the output
#                 has a time stamp inconsistent with the filename with 1 months off, hence
#                 requires an adjustment.
#             verbose (bool, optional): print verbose information. Defaults to False.
#         '''
#         if type(vars) is str:
#             vars = [vars]

#         if mode == 'timeslice':
#             if vars is None:
#                 raise ValueError('Should specify `vars` if mode is "timeslice".')

#             ds_list = []
#             for path in tqdm(self.paths, desc='Loading files'):
#                 with xr.open_dataset(path) as ds_tmp:
#                     ds_list.append(ds_tmp)

#             for vn in vars:
#                 utils.p_header(f'>>> Extracting {vn} ...')
#                 if z_val is None:
#                     da = xr.concat([ds[vn] for ds in ds_list], dim=time_name)
#                 else:
#                     da = xr.concat([ds[vn].sel({z_name: z_val}) for ds in ds_list], dim=time_name)

#                 if adjust_month:
#                     da[time_name] = da[time_name].get_index(time_name) - datetime.timedelta(days=1)

#                 self.fd[vn] = ClimateField(da)

#                 if save_dirpath is not None:
#                     fname = f'{vn}.nc'
#                     save_path = os.path.join(save_dirpath, fname)
#                     self.fd[vn].to_nc(save_path, compress_params=compress_params)

#                 if verbose:
#                     utils.p_success(f'>>> GCMCase.fd["{vn}"] created')

#         elif mode == 'timeseries':
#             for path in self.paths:
#                 fd_tmp = ClimateField().load_nc(path)
#                 vn = fd_tmp.da.name
#                 self.fd[vn] = fd_tmp

#             if verbose:
#                 utils.p_success(f'>>> GCMCase loaded with vars: {list(self.fd.keys())}')

#         else:
#             raise ValueError('Wrong `mode` specified! Options: "timeslice" or "timeseries".')

#     def calc_atm_gm(self, vars=['GMST', 'GMRESTOM', 'GMLWCF', 'GMSWCF'], verbose=False):

#         for vn in vars:
#             if vn == 'GMST':
#                 v = 'TS' if 'TS' in self.fd else 'TREFHT'
#                 gmst = self.fd[v].annualize().geo_mean()
#                 self.ts[vn] = gmst - 273.15

#             elif vn == 'GMRESTOM':
#                 restom = (self.fd['FSNT'] - self.fd['FLNT']).annualize().geo_mean()
#                 self.ts[vn] = restom
            
#             else:
#                 self.ts[vn] = self.fd[vn[2:]].annualize().geo_mean()

#             if verbose:
#                 utils.p_success(f'>>> GCMCase.ts["{vn}"] created')

#     def to_ds(self, mode='ts'):
#         ''' Convert to a `xarray.Dataset`
#         '''
#         da_dict = {}
#         if mode == 'fd':
#             for k, v in self.fd.items():
#                 da_dict[k] = v.da

#         elif mode == 'ts':
#             for k, v in self.ts.items():
#                 time_name = v.time.name
#                 da_dict[k] = xr.DataArray(v.value[:, 0], dims=[time_name], coords={time_name: v.time}, name=k)

#         ds = xr.Dataset(da_dict)
#         if self.name is not None:
#             ds.attrs['casename'] = self.name

#         return ds

#     def to_nc(self, path, mode='ts', verbose=True, compress_params=None):
#         ''' Output the GCM case to a netCDF file.

#         Args:
#             path (str): the path where to save
#         '''
#         _comp_params = {'zlib': True}
#         encoding_dict = {}
#         if compress_params is not None:
#             _comp_params.update(compress_params)

#         if mode == 'fd':
#             for k, v in self.fd.items():
#                 encoding_dict[k] = _comp_params

#         elif mode == 'ts':
#             for k, v in self.ts.items():
#                 encoding_dict[k] = _comp_params

#         try:
#             dirpath = os.path.dirname(path)
#             os.makedirs(dirpath, exist_ok=True)
#         except:
#             pass

#         ds = self.to_ds(mode=mode)

#         if os.path.exists(path):
#             os.remove(path)
            
#         ds.to_netcdf(path, encoding=encoding_dict)
#         if verbose: utils.p_success(f'>>> GCMCase saved to: {path}')

#     def load_nc(self, path, verbose=False):
#         case = GCMCase()
#         ds = xr.open_dataset(path)
#         if 'casename' in ds.attrs:
#             case.name = ds.attrs['casename']

#         for vn in ds.keys():
#             if vn[:2] == 'GM':
#                 case.ts[vn] = EnsTS(time=ds[vn].year, value=ds[vn].values)
#                 if verbose:
#                     utils.p_success(f'>>> GCMCase.ts["{vn}"] created')
#             else:
#                 case.fd[vn] = ClimateField(ds[vn])
#                 if verbose:
#                     utils.p_success(f'>>> GCMCase.fd["{vn}"] created')

#         return case


#     def plot_ts(self, vars=['GMST', 'GMRESTOM', 'GMLWCF', 'GMSWCF'], figsize=[10, 6], ncol=2, wspace=0.3, hspace=0.2, xlim=(0, 100), title=None,
#                     xlabel='Time [yr]', ylable_dict=None, color_dict=None, ylim_dict=None,
#                     ax=None, **plot_kws):

#         if ax is None:
#             fig = plt.figure(figsize=figsize)
#             ax = {}

#         nrow = int(np.ceil(len(vars)/ncol))
#         gs = gridspec.GridSpec(nrow, ncol)
#         gs.update(wspace=wspace, hspace=hspace)

#         _ylim_dict = {
#             'GMST': (13.5, 15.5),
#             'GMRESTOM': (-1, 3),
#             'GMLWCF': (24, 26),
#             'GMSWCF': (-54, -44),
#         }
#         if ylim_dict is not None:
#             _ylim_dict.update(ylim_dict)

#         _ylb_dict = {
#             'GMST': r'GMST [$^\circ$C]',
#             'GMRESTOM': r'GMRESTOM [W/m$^2$]',
#             'GMLWCF': r'GMLWCF [W/m$^2$]',
#             'GMSWCF': r'GMSWCF [W/m$^2$]',
#         }
#         if ylable_dict is not None:
#             _ylb_dict.update(ylable_dict)

#         _clr_dict = {
#             'GMST': 'tab:red',
#             'GMRESTOM': 'tab:blue',
#             'GMLWCF': 'tab:green',
#             'GMSWCF': 'tab:orange',
#         }
#         if color_dict is not None:
#             _clr_dict.update(color_dict)

#         i = 0
#         i_row, i_col = 0, 0
#         for k, v in self.ts.items():
#             if 'fig' in locals():
#                 ax[k] = fig.add_subplot(gs[i_row, i_col])

#             if i_row == nrow-1:
#                 _xlb = xlabel
#             else:
#                 _xlb = None


#             if k == 'GMRESTOM':
#                 ax[k].axhline(y=0, linestyle='--', color='tab:grey')
#             elif k == 'GMLWCF':
#                 ax[k].axhline(y=25, linestyle='--', color='tab:grey')
#             elif k == 'GMSWCF':
#                 ax[k].axhline(y=-47, linestyle='--', color='tab:grey')

#             _plot_kws = {
#                 'linewidth': 2,
#             }
#             if plot_kws is not None:
#                 _plot_kws.update(plot_kws)
            

#             v.plot(
#                 ax=ax[k], xlim=xlim, ylim=_ylim_dict[k],
#                 xlabel=_xlb, ylabel=_ylb_dict[k],
#                 color=_clr_dict[k], **_plot_kws,
#             )

#             i += 1
#             i_col += 1

#             if i % 2 == 0:
#                 i_row += 1

#             if i_col == ncol:
#                 i_col = 0

#         if title is not None:
#             fig.suptitle(title)

#         if 'fig' in locals():
#             return fig, ax
#         else:
#             return ax
            
#     def calc_som_forcings(self, ds_clim, time_name='month', lat_name='TLAT', lon_name='TLONG',
#                               z_name='z_t', hblt_name='HBLT', temp_name='TEMP', salt_name='SALT',
#                               uvel_name='UVEL', vvel_name='VVEL', shf_name='SHF', qflux_name='QFLUX',
#                               anglet_name='ANGLET', region_mask_name='REGION_MASK',
#                               save_path=None, save_format='NETCDF3_CLASSIC'):
#         ''' Calculate the slab ocean forcing

#         Reference: NCL scripts by Jiang Zhu (jiangzhu@ucar.edu) at:  /glade/u/home/jiangzhu/notebooks/pop_frc_mlt.b.e21.B1850.f19_g17.PaleoCalibr.PI.02.ncl
#         '''
#         ds_clim = ds_clim.rename({time_name: 'time', 'nlat': 'nj', 'nlon': 'ni'})
#         ds_clim.coords['time'] = [cftime.DatetimeNoLeap(1,i,1,0,0,0,0, has_year_zero=True) for i in range(1, 13)]

#         hbltin = ds_clim[hblt_name]
#         hblt_avg = hbltin.mean('time')
#         hblttmp = hblt_avg.expand_dims({'time': 12})/100

#         z_t = ds_clim[z_name]
#         zint = (z_t.values[:-1] + z_t.values[1:])/2/100
#         zint = np.insert(zint, 0, 0)
#         zint = np.append(zint, 2*z_t.values[-1]/100-zint[-1])
#         dz = np.diff(zint)

#         xc = ds_clim[lon_name]
#         yc = ds_clim[lat_name]
#         nlat, nlon = xc.shape
#         ntime = 12
#         nz = len(z_t)

#         # calculate weighted T and S
#         wgt = np.empty((ntime, nz, nlat, nlon))
#         for i in range(nz):
#             dz_tmp = hblttmp.values - zint[i]
#             dz_tmp = np.where(dz_tmp < 0, np.nan, dz_tmp)
#             dz_tmp = np.where(dz_tmp > dz[i], dz[i], dz_tmp)
#             dz_tmp = dz_tmp / hblttmp
#             wgt[:,i,:,:] = dz_tmp

#         Ttmp = ds_clim[temp_name]
#         Stmp = ds_clim[salt_name]
#         Ttmp2 = Ttmp * wgt
#         Stmp2 = Stmp * wgt 

#         Tin = Ttmp2.sum(dim=z_name)
#         Sin = Stmp2.sum(dim=z_name)

#         # calculate velocities
#         Utmp = ds_clim[uvel_name][:,0,:,:]
#         Vtmp = ds_clim[vvel_name][:,0,:,:]
#         ang = ds_clim[anglet_name]

#         Utmp2 = Utmp * 0
#         Vtmp2 = Vtmp * 0

#         Utmp2[:,1:,1:] = 0.25*(Utmp[:,1:,1:] + Utmp[:,1:,:-1]+Utmp[:,:-1,1:]+Utmp[:,:-1,:-1])
#         Vtmp2[:,1:,1:] = 0.25*(Vtmp[:,1:,1:] + Vtmp[:,1:,:-1]+Vtmp[:,:-1,1:]+Vtmp[:,:-1,:-1])

#         Uin = (Utmp2*np.cos(ang) + Vtmp2*np.sin(-ang))*0.01
#         Vin = (Vtmp2*np.cos(ang) - Utmp2*np.sin(-ang))*0.01

#         # calculate ocean heat
#         shf = ds_clim[shf_name]
#         qflux = ds_clim[qflux_name]
#         rcp_sw = 1026.*3996.
#         surf = shf+qflux
#         T1 = Tin.values.copy()
#         T1[:-1] = Tin[1:]
#         T1[-1] = Tin[0]
#         T2 = Tin.values.copy()
#         T2[0] = Tin[-1]
#         T2[1:] = Tin[:-1]
#         dT = T1 - T2
#         release = rcp_sw*dT*hblttmp / (86400.*365./6.)
#         ocnheat = surf-release
            
#         # area weighted
#         tarea = ds_clim['TAREA']
#         maskt = np.ones((nlat, nlon))
#         maskt = maskt*(~np.isnan(ocnheat[0,:,:]))
#         err = np.empty(12)
#         for i in range(12):
#             oh_tmp = ocnheat.values[i].flatten()
#             oh_tmp[np.isnan(oh_tmp)] = 0
#             err[i] = np.matmul(oh_tmp,tarea.values.flatten())/np.sum(tarea.values*maskt.values)

#         glob = np.mean(err)
#         ocnheat -= glob

#         # calculate the inverse matrix
#         dhdxin = Tin * 0
#         dhdyin = Tin * 0

#         daysinmo = np.array([31.,28.,31.,30.,31.,30.,31.,31.,30.,31.,30.,31.])
#         xnp = np.copy(daysinmo)
#         xnm = np.copy(daysinmo)

#         xnm[1:] = daysinmo[1:] + daysinmo[:-1]
#         xnm[0] = daysinmo[0] + daysinmo[-1]

#         xnp[:-1] = daysinmo[1:] + daysinmo[:-1]
#         xnp[-1] = daysinmo[0] + daysinmo[-1]

#         aa = 2 * daysinmo / xnm
#         cc = 2 * daysinmo / xnp
#         a = aa / 8.
#         c = cc / 8.
#         b = 1 - a - c

#         M = [
#             [b[0], c[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, a[0]],
#             [a[1], b[1], c[1], 0, 0, 0, 0, 0, 0, 0, 0, 0],
#             [0, a[2], b[2], c[2], 0, 0, 0, 0, 0, 0, 0, 0],
#             [0, 0, a[3], b[3], c[3], 0, 0, 0, 0, 0, 0, 0],
#             [0, 0, 0, a[4], b[4], c[4], 0, 0, 0, 0, 0, 0],
#             [0, 0, 0, 0, a[5], b[5], c[5], 0, 0, 0, 0, 0],
#             [0, 0, 0, 0, 0, a[6], b[6], c[6], 0, 0, 0, 0],
#             [0, 0, 0, 0, 0, 0, a[7], b[7], c[7], 0, 0, 0],
#             [0, 0, 0, 0, 0, 0, 0, a[8], b[8], c[8], 0, 0],
#             [0, 0, 0, 0, 0, 0, 0, 0, a[9], b[9], c[9], 0],
#             [0, 0, 0, 0, 0, 0, 0, 0, 0, a[10], b[10], c[10]],
#             [c[11], 0, 0, 0, 0, 0, 0, 0, 0, 0, a[11], b[11]],
#         ]
#         invM = np.linalg.inv(M)

#         # prepare output vars
#         T = xr.full_like(Tin, 0)
#         S = xr.full_like(Sin, 0)
#         U = xr.full_like(Uin, 0)
#         V = xr.full_like(Vin, 0)
#         dhdx = xr.full_like(dhdxin, 0)
#         dhdy = xr.full_like(dhdyin, 0)
#         hblt = xr.full_like(hbltin, 0)
#         qdp = xr.full_like(shf, 0)

#         for j in range(12):
#             for i in range(12):
#                 T[j] += invM[j, i]*Tin[i]
#                 S[j] += invM[j, i]*Sin[i]
#                 U[j] += invM[j, i]*Uin[i]
#                 V[j] += invM[j, i]*Vin[i]
#                 dhdx[j] += invM[j, i]*dhdxin[i]
#                 dhdy[j] += invM[j, i]*dhdyin[i]
#                 hblt[j] += invM[j, i]*hblttmp[i]
#                 qdp[j] += invM[j, i]*ocnheat[i]

#         ds_out = xr.Dataset()
#         ds_out['time'] = ds_clim['time']
#         ds_out['time'].attrs['long_name'] = 'days since 0001-01-01 00:00:00'
#         ds_out['time'].attrs['units'] = 'observation time'
#         ds_out['time'].attrs['calendar'] = 'noleap'

#         ds_out['xc'] = xc
#         ds_out['xc'].attrs['long_name'] = 'longitude of grid cell center'
#         ds_out['xc'].attrs['units'] = 'degrees east'

#         ds_out['yc'] = yc
#         ds_out['yc'].attrs['long_name'] = 'latitude of grid cell center'
#         ds_out['yc'].attrs['units'] = 'degrees north'

#         ds_out['T'] = T.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['T'].attrs['long_name'] = 'temperature'
#         ds_out['T'].attrs['units'] = 'degC'

#         ds_out['S'] = S.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['S'].attrs['long_name'] = 'salinity'
#         ds_out['S'].attrs['units'] = 'ppt'

#         ds_out['U'] = U.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['U'].attrs['long_name'] = 'u ocean current'
#         ds_out['U'].attrs['units'] = 'm/s'

#         ds_out['V'] = V.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['V'].attrs['long_name'] = 'v ocean current'
#         ds_out['V'].attrs['units'] = 'm/s'

#         ds_out['dhdx'] = dhdx.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['dhdx'].attrs['long_name'] = 'ocean surface slope: zonal'
#         ds_out['dhdx'].attrs['units'] = 'm/m'

#         ds_out['dhdy'] = dhdy.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['dhdy'].attrs['long_name'] = 'ocean surface slope: meridional'
#         ds_out['dhdy'].attrs['units'] = 'm/m'

#         ds_out['hblt'] = hblt.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['hblt'].attrs['long_name'] = 'boundary layer depth'
#         ds_out['hblt'].attrs['units'] = 'm'

#         ds_out['qdp'] = qdp.where(~np.isnan(ds_clim['TEMP'][0,0,:,:]))
#         ds_out['qdp'].attrs['long_name'] = 'ocean heat flux convergence'
#         ds_out['qdp'].attrs['units'] = 'W/m^2'

#         ds_out['area'] = tarea
#         ds_out['area'].attrs['long_name'] = 'area of grid cell in radians squared'
#         ds_out['area'].attrs['units'] = 'area'

#         ds_out['mask'] = ds_clim[region_mask_name]
#         ds_out['mask'].attrs['long_name'] = 'domain maskr'
#         ds_out['mask'].attrs['units'] = 'unitless'

#         ds_out.attrs['title'] = 'Monthly averaged ocean forcing from POP output'
#         ds_out.attrs['conventions'] = 'CCSM data model domain description'
#         ds_out.attrs['source'] = 'cfr.gcm.GCMCase.calc_slab_ocn_forcing (https://github.com/fzhu2e/cfr)'
#         ds_out.attrs['description'] = 'Input data for DOCN7 mixed layer model'
#         ds_out.attrs['note1'] = 'fields computed from 100-yr monthly means from pop'
#         ds_out.attrs['note2'] = 'all fields interpolated to T-grid'
#         ds_out.attrs['note3'] = 'qdp is computed from depth summed ocean column'
#         ds_out.attrs['author'] = 'Feng Zhu (fengzhu@ucar.edu), Jiang Zhu (jiangzhu@ucar.edu)'
#         ds_out.attrs['calendar'] = 'standard'
#         ds_out.attrs['comment'] = 'This data is on the displaced pole grid gx1v7'
#         ds_out.attrs['creation_date'] = datetime.date.today().strftime('%m/%d/%Y')

#         if save_path is not None:
#             ds_out.to_netcdf(save_path, format=save_format)

#         return ds_out

#     def calc_cam_forcings(self, SST, aice, SST_time_name='time', SST_lat_name='TLAT', SST_lon_name='TLONG',
#                           aice_time_name='time', aice_lat_name='TLAT', aice_lon_name='TLON',
#                           save_path=None, save_format='NETCDF3_CLASSIC'):
#         ''' Calculate the forcings for CAM only simulation (F-case)

#         Note that the regridding is implemented by `pyresample` here instead of ESMF.

#         Reference: NCL scripts by Cecile Hannay (hannay@ucar.edu) at: /glade/u/home/hannay/ncl_scripts/sst/B1850_cmip6
#         '''
#         ds_out = xr.Dataset(
#             coords={
#                 'time': SST[SST_time_name],
#                 'lat': np.linspace(-89.5, 89.5, 180),
#                 'lon': np.linspace(0.5, 359.5, 360),
#             }
#         )
#         ds_out['time'].attrs['information'] = 'middle of month'
#         ds_out['time'].attrs['calendar'] = 'gregorian'
#         ds_out['time'].attrs['units'] = 'days since 0001-01-01 00:00:00'

#         ds_out['lat'].attrs['long_name'] = 'latitude'
#         ds_out['lat'].attrs['units'] = 'degrees_north'

#         ds_out['lon'].attrs['long_name'] = 'longitude'
#         ds_out['lon'].attrs['units'] = 'degrees_east'


#         SST_rgd, _, _ = regrid_field_curv_rect(
#             SST.values, SST[SST_lat_name].values, SST[SST_lon_name].values,
#             ds_out.lat.values, ds_out.lon.values)

#         aice_rgd, _, _ = regrid_field_curv_rect(
#             aice.values, aice[aice_lat_name].values, aice[aice_lon_name].values,
#             ds_out.lat.values, ds_out.lon.values)

#         ds_out['SST'] = xr.DataArray(SST_rgd, coords=ds_out.coords)
#         ds_out['SST'].attrs['long_name'] = 'Sea-Surface temperature'
#         ds_out['SST'].attrs['units']     = 'deg_C'

#         ds_out['SEAICE'] = xr.DataArray(aice_rgd*100, coords=ds_out.coords)
#         ds_out['SEAICE'].attrs['long_name'] = 'Sea Ice Concentration'
#         ds_out['SEAICE'].attrs['units']     = '%'

#         # Corrections for data consistency
#         # 1) If SST < -1.8 or ice frac >= 90%, SST = -1.8
#         mask = (ds_out['SST'] < -1.8) | (ds_out['SEAICE'] > 90)
#         ds_out['SST'].values[mask] = -1.8
#         # 2) min ice frac is 0%, max ice_frac is 100%
#         mask = ds_out['SEAICE'] < 0
#         ds_out['SEAICE'].values[mask] = 0
#         mask = ds_out['SEAICE'] > 100
#         ds_out['SEAICE'].values[mask] = 100
#         # 3) No sea ice if SST > 4.97
#         mask = ds_out['SST'] > 4.97
#         ds_out['SEAICE'].values[mask] = 0

#         ds_out['ICEFRAC'] = ds_out['SEAICE'] / 100.

#         if save_path is not None:
#             ds_out.to_netcdf(save_path, format=save_format)

#         return ds_out
        
                

# class GCMCases:
#     ''' The class for postprocessing multiple GCM simulation cases (e.g., CESM)
#     '''
#     def __init__(self, case_dict=None):
#         self.case_dict = case_dict
#         for k, v in self.case_dict.items():
#             v.name = k

#     def calc_atm_gm(self, vars=['GMST', 'GMRESTOM', 'GMLWCF', 'GMSWCF'], verbose=False):
#         for k, v in self.case_dict.items():
#             utils.p_header(f'Processing case: {k} ...')
#             v.calc_atm_gm(vars=vars, verbose=verbose)

#     def plot_ts(self, lgd_kws=None, lgd_idx=1, **plot_kws):
#         _clr_dict = {
#             'GMST': None,
#             'GMRESTOM': None,
#             'GMLWCF': None,
#             'GMSWCF': None,
#         }
#         for k, v in self.case_dict.items():
#             if 'fig' not in locals():
#                 fig, ax = v.plot_ts(color_dict=_clr_dict, label=v.name, **plot_kws)
#             else:
#                 ax = v.plot_ts(ax=ax, color_dict=_clr_dict, label=v.name, **plot_kws)

#         _lgd_kws = {
#             'frameon': False,
#             'loc': 'upper left',
#             'bbox_to_anchor': [1.1, 1],
#         }
#         if lgd_kws is not None:
#             _lgd_kws.update(lgd_kws)

#         vn = list(ax.keys())[lgd_idx]
#         ax[vn].legend(**_lgd_kws)

#         return fig, ax

class PPCase:
    ''' Designed for postprocessed timeseries
    '''
    def __init__(self, root_dir, path_pattern='comp/proc/tseries/month_1/casename.mdl.h_str.vn.timespan.nc', settings_csv=None):
        self.root_dir = root_dir
        self.path_pattern = path_pattern
        utils.p_header(f'>>> Case.root_dir: {self.root_dir}')
        self.paths = glob.glob(
            os.path.join(
                self.root_dir,
                self.path_pattern \
                    .replace('comp', '**') \
                    .replace('casename', '*') \
                    .replace('mdl', '*') \
                    .replace('h_str', '*') \
                    .replace('vn', '*') \
                    .replace('timespan', '*'),
            )
        )
        self.vars_info = {}
        for path in self.paths:
            comp = path.split('/')[-5]
            mdl = path.split('.')[-5]
            h_str = path.split('.')[-4]
            vn = path.split('.')[-3]
            if vn not in self.vars_info:
                self.vars_info[vn] = (comp, mdl, h_str)

        utils.p_success(f'>>> PPCase.vars_info created')

        self.ds = xr.Dataset()
        self.diagnostics = xr.Dataset()
        self.ds.attrs = {'components': []}
        self.calc_log = {}

        if settings_csv is not None:
            settings_df = pd.read_csv(settings_csv, index_col=0)
            self.settings_csv = settings_csv
            self.settings_df = settings_df
            utils.p_header(f'>>> PPCase.settings_csv: {self.settings_csv}')
            utils.p_success(f'>>> PPCase.settings_df created')

    def check_timespan(self, ref_timespan, target_timespan):
        utils.p_header('==================================')
        utils.p_header('Checking Timespan')
        utils.p_header('----------------------------------')
        utils.p_header(f'Reference timespan: {ref_timespan}')
        utils.p_header(f'   Target timespan: {target_timespan}')
        ref_paths = glob.glob(f'{self.root_dir}/*/proc/tseries/month_1/*.{ref_timespan}.nc')
        vn_dict = {}
        for path in ref_paths:
            comp = path.split('/proc/')[0].split('/')[-1]
            vn = path.split('.')[-3]
            if comp not in vn_dict:
                vn_dict[comp] = [vn]
            else:
                vn_dict[comp].append(vn)

        target_paths = glob.glob(f'{self.root_dir}/*/proc/tseries/month_1/*.{target_timespan}.nc')
        vn_dict_check = {}
        for path in target_paths:
            comp = path.split('/proc/')[0].split('/')[-1]
            vn = path.split('.')[-3]
            if comp not in vn_dict_check:
                vn_dict_check[comp] = [vn]
            else:
                vn_dict_check[comp].append(vn)

        for comp in vn_dict.keys():
            if comp not in vn_dict_check:
                print(f'{comp} not generated for {target_timespan}')
            else:
                for vn in vn_dict[comp]:
                    if vn not in vn_dict_check[comp]:
                        print(f'{comp}/{vn} timeseries not generated for {target_timespan}')

        utils.p_success('Done.')
        utils.p_header('==================================\n')
    
    def load(self, vn, adjust_month=True, grid_weight_dict=None, lat_dict=None, lon_dict=None, load_idx=None):
        _grid_weight_dict = {
            'atm': 'area',
            'ocn': 'TAREA',
            'ice': 'tarea',
            'lnd': 'area',
        }
        if grid_weight_dict is not None:
            _grid_weight_dict.update(grid_weight_dict)

        _lat_dict = {
            'atm': 'lat',
            'ocn': 'TLAT',
            'ice': 'TLAT',
            'lnd': 'lat',
        }
        if lat_dict is not None:
            _lat_dict.update(lat_dict)

        _lon_dict = {
            'atm': 'lon',
            'ocn': 'TLONG',
            'ice': 'TLON',
            'lnd': 'lon',
        }
        if lon_dict is not None:
            _lon_dict.update(lon_dict)

        if not isinstance(vn, (list, tuple)):
            vn = [vn]

        for v in vn:
            if v in self.vars_info and v not in self.ds:
                comp, mdl, h_str = self.vars_info[v]
                paths = sorted(glob.glob(
                    os.path.join(
                        self.root_dir,
                        self.path_pattern \
                            .replace('comp', comp) \
                            .replace('casename', '*') \
                            .replace('mdl', mdl) \
                            .replace('h_str', h_str) \
                            .replace('vn', v) \
                            .replace('timespan', '*'),
                    )
                ))
                if load_idx is not None:
                    ds =  xr.open_dataset(paths[load_idx])
                else:
                    ds =  xr.open_mfdataset(paths)

                if adjust_month:
                    ds['time'] = ds['time'].get_index('time') - datetime.timedelta(days=1)

                if comp not in self.ds.attrs['components']:
                    if load_idx is not None:
                        self.ds[f'gw_{comp}'] = ds[_grid_weight_dict[comp]].fillna(0)
                    else:
                        self.ds[f'gw_{comp}'] = ds[_grid_weight_dict[comp]][0].fillna(0)

                    if comp == 'atm':
                        self.ds[f'lat_{comp}'] = ds[_lat_dict[comp]][0]
                        self.ds[f'lon_{comp}'] = ds[_lon_dict[comp]][0]
                    else:
                        self.ds[f'lat_{comp}'] = ds[_lat_dict[comp]]
                        self.ds[f'lon_{comp}'] = ds[_lon_dict[comp]]

                    self.ds.attrs['components'].append(comp)

                self.ds[v] = ds[v]
                self.ds[v].attrs['source'] = paths[load_idx] if load_idx is not None else paths
                if comp == 'atm':
                    self.ds['lat'] = ds['lat']
                    self.ds['lon'] = ds['lon']

                utils.p_success(f'>>> PPCase.ds["{v}"] created')
            elif v in ['KMT', 'z_t', 'z_w']:
                comp, mdl, h_str = self.vars_info['TEMP']
                paths = sorted(glob.glob(
                    os.path.join(
                        self.root_dir,
                        self.path_pattern \
                            .replace('comp', comp) \
                            .replace('casename', '*') \
                            .replace('mdl', mdl) \
                            .replace('h_str', h_str) \
                            .replace('vn', 'TEMP') \
                            .replace('timespan', '*'),
                    )
                ))
                with xr.open_dataset(paths[-1], decode_cf=False) as ds:
                    self.ds[v] = ds[v]
                
            elif v not in self.vars_info:
                utils.p_warning(f'>>> Variable {v} not existed')
            elif v in self.ds:
                utils.p_warning(f'>>> Variable {v} already loaded as PPCase.ds["{v}"]')

        
        
    def calc_diagnostics(self, vn, kws=None):
        kws = {} if kws is None else kws
        if not isinstance(vn, (list, tuple)):
            vn = [vn]

        for v in vn:
            if v not in self.diagnostics:
                if v not in kws:
                    kws[v] = {}
                getattr(self, f'calc_{v}')(**kws[v])

    def plot_diagnostics(self, vn=None, figsize=[20, 10], ncol=4, nrow=None, wspace=0.3, hspace=0.5, kws=None,
                         print_settings=True, prt_setting_list=['cldfrc_rhminl', 'micro_mg_dcs'], title=None):
        kws = {} if kws is None else kws

        if vn is None:
            vn = list(self.diagnostics)

        if not isinstance(vn, (list, tuple)):
            vn = [vn]

        if nrow is None:
            nrow = int(np.ceil(len(vn)/ncol))
            
        fig = plt.figure(figsize=figsize)
        ax = {}
        gs = gridspec.GridSpec(nrow, ncol)
        gs.update(wspace=wspace, hspace=hspace)

        for i, v in enumerate(vn):
            if v not in kws:
                kws[v] = {}

            ax[v] = fig.add_subplot(gs[i])
            getattr(self, f'plot_{v}')(ax=ax[v], **kws[v])

        if hasattr(self, 'settings_df') and print_settings:
            settings_info = ''
            for name in prt_setting_list:
                nm = f'atm: {name}'
                settings_info += f'{name}: {self.settings_df.loc[nm].values[0].strip()}'
                settings_info += ', '
            settings_info = settings_info[:-2]

        if 'settings_info' in locals():
            if title is None:
                title = settings_info
            else:
                title += f'\n{settings_info}'

            fig.suptitle(title, y=0.95)

        return fig, ax

    def calc_depth(self):
        self.load('KMT')
        self.load('z_t')
        self.load('TEMP', load_idx=-1)
        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = self.ds['TEMP'].TLAT
        ocn_grid['lon'] = self.ds['TEMP'].TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )

        kmt_rgd = regridder(self.ds['KMT'])
        nlat, nlon = kmt_rgd.shape
        depth = kmt_rgd.copy()
        for j in range(nlat):
            for i in range(nlon):
                k = int(np.atleast_1d(kmt_rgd[j, i])[0])
                if k == 0:
                    depth[j, i] = 0
                else:
                    depth[j, i] = self.ds['z_t'][k-1]

        self.diagnostics['depth'] = depth/1e2/1e3   # unit: m
        utils.p_success(f'>>> PPCase.diagnostics["depth"] created')

    def plot_depth(self, figsize=[8, 5], levels=np.linspace(0, 5, 51), cbar_labels=np.linspace(0, 5, 11),
                 transform=ccrs.PlateCarree(), cmap='terrain_r', extend='max',
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='Depth [km]',
                 central_longitude=180, title='Topography'):
        depth = self.diagnostics['depth']
        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        ax.set_global()
        ax.set_title(title)

        im = ax.contourf(depth.lon, depth.lat, depth, levels, transform=transform, cmap=cmap, extend=extend)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)

        return fig, ax

    def calc_IAGE_zm(self, load_idx=-1, lon_min=0, lon_max=360, lat_min=-90, lat_max=90):
        vn = 'IAGE'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        da = utils.monthly2annual(self.ds[vn])
        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = da.TLAT
        ocn_grid['lon'] = da.TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )

        da_rgd = regridder(da)
        mask_lat = (da_rgd['lat']>=lat_min) & (da_rgd['lat']<=lat_max)
        if lon_max <= 360:
            mask_lon = (da_rgd['lon']>=lon_min) & (da_rgd['lon']<=lon_max)
        else:
            mask_lon = (da_rgd['lon']>=lon_min) & (da_rgd['lon']<=360) | (da_rgd['lon']>=0) & (da_rgd['lon']<=lon_max-360)

        da_sub = da_rgd.sel({'lon': da_rgd['lon'][mask_lon], 'lat': da_rgd['lat'][mask_lat]})
        da_sub_ann = da_sub.mean('time')
        self.diagnostics['IAGE'] = da_sub_ann.copy()
        self.diagnostics['IAGE_zm'] = da_sub_ann.mean('lon')
        utils.p_success(f'>>> PPCase.diagnostics["IAGE"] created')
        utils.p_success(f'>>> PPCase.diagnostics["IAGE_zm"] created')

    def plot_IAGE_zm(self, figsize=[8, 5], cmap='GnBu', extend='max',
                     xticks=[-90, -60, -30, 0, 30, 60, 90],
                     xticklabels=['90°S', '60°S', '30°S', 'EQ', '30°N', '60°N', '90°N'],
                     yticks=np.linspace(0, 500000, 6),
                     yticklabels=np.linspace(0, 5, 6),
                     levels=np.linspace(0, 2000, 21), cbar_labels=np.linspace(0, 2000, 11),
                     cbar_orientation='vertical', cbar_shrink=1.0, cbar_pad=0.05,
                     cbar_aspect=10, cbar_title='[yrs]',
                     title='IAGE Annual & Zonal Mean',
                    ):
        fig, ax = plt.subplots(figsize=figsize)
        da = self.diagnostics['IAGE_zm']

        im = ax.contourf(da.lat, da.z_t, da, cmap=cmap, levels=levels, extend=extend)
        ax.set_facecolor('gray')
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)
        ax.invert_yaxis()
        ax.set_ylabel('Depth [km]')
        ax.set_xlabel('Latitude')
        ax.set_title(title)
        ax.grid(False)
        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad, aspect=cbar_aspect)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)
        return fig, ax

    def calc_LST(self, load_idx=-1, weight_file='/glade/u/home/fengzhu/Scripts/regrid/map_ne16np4_TO_1x1d_aave.240225.nc'):
        vn = 'TS'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        tas = utils.monthly2annual(self.ds[vn])
        tas.name = 'TS'
        tas_ds = tas.to_dataset()
        tas_ds['lat'] = self.ds['lat']
        tas_ds['lon'] = self.ds['lon']
        vn = 'LANDFRAC'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        landfrac = utils.monthly2annual(self.ds[vn])
        landfrac.name = 'LANDFRAC'
        landfrac_ds = landfrac.to_dataset()
        landfrac_ds['lat'] = self.ds['lat']
        landfrac_ds['lon'] = self.ds['lon']

        tas_rgd = utils.regrid_cam_se(tas_ds, weight_file=weight_file)['TS']
        self.diagnostics['TAS'] = tas_rgd.mean('time') - 273.15
        utils.p_success(f'>>> PPCase.diagnostics["TAS"] created')

        landfrac_rgd = utils.regrid_cam_se(landfrac_ds, weight_file=weight_file)['LANDFRAC']
        self.diagnostics['LST'] = self.diagnostics['TAS'].where(landfrac_rgd.mean('time')>0.5)
        utils.p_success(f'>>> PPCase.diagnostics["LST"] created')

    def plot_LST(self, figsize=[8, 5], levels=np.linspace(5, 35, 31), cbar_labels=np.linspace(5, 35, 7),
                 transform=ccrs.PlateCarree(), cmap='RdBu_r', extend='both', coastlinewidth=1,
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='LST [°C]',
                 central_longitude=180, title='Annual Mean LST',
                 df_proxy=None, lat_colname='lat', lon_colname='lon', lst_colname='lst',
                 site_markersize=100, site_marker='o'):
        lst = self.diagnostics['LST']
        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        ax.set_global()
        ax.set_title(title)

        im = ax.contourf(lst.lon, lst.lat, lst, levels, transform=transform, cmap=cmap, extend=extend)
        ax.contour(lst.lon, lst.lat, np.isnan(lst), levels=[0, 1], colors='k', transform=transform, linewidths=coastlinewidth)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)

        if df_proxy is not None:
            site_lons = df_proxy[lon_colname]
            site_lats = df_proxy[lat_colname]
            site_lsts = df_proxy[lst_colname]
            cmap_obj = plt.get_cmap(cmap)
            norm = BoundaryNorm(levels, ncolors=cmap_obj.N, clip=True)
            ax.scatter(site_lons, site_lats, s=site_markersize, c=site_lsts, marker=site_marker, edgecolors='k',
                       zorder=99, transform=transform, cmap=cmap, norm=norm)
            
        return fig, ax

    def calc_aice(self, load_idx=-1):
        vn = 'aice'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        aice_ann = utils.monthly2annual(self.ds[vn])
        aice_season = utils.monthly2season(self.ds[vn])
        aice_summer = aice_season.sel(season='JJA')
        aice_winter = aice_season.sel(season='DJF')

        self.load('TEMP', load_idx=load_idx)
        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = self.ds['TEMP'].TLAT
        ocn_grid['lon'] = self.ds['TEMP'].TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )

        aice_ann_rgd = regridder(aice_ann)
        aice_summer_rgd = regridder(aice_summer)
        aice_winter_rgd = regridder(aice_winter)
        self.load('KMT')

        self.diagnostics['aice_ann'] = aice_ann_rgd.mean('time')
        self.diagnostics['aice_summer'] = aice_summer_rgd
        self.diagnostics['aice_winter'] = aice_winter_rgd
        self.diagnostics['KMT'] = regridder(self.ds['KMT'])
        utils.p_success(f'>>> PPCase.diagnostics["aice_ann"] created')
        utils.p_success(f'>>> PPCase.diagnostics["aice_summer"] created')
        utils.p_success(f'>>> PPCase.diagnostics["aice_winter"] created')
        utils.p_success(f'>>> PPCase.diagnostics["KMT"] created')

    def plot_aice(self, season='ann', figsize=[8, 5], levels=np.linspace(0, 1, 11), cbar_labels=np.linspace(0, 1, 6),
                 transform=ccrs.PlateCarree(), cmap='Blues_r', extend='neither', projection='Orthographic',
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='Ice Area [%]',
                 central_longitude=180, central_latitude=90, title='Ice Area'):
        fig = plt.figure(figsize=figsize)
        if projection == 'Orthographic':
            ax = plt.subplot(projection=ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude))
        elif projection == 'Robinson':
            ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        else:
            raise ValueError('Wrong `projection` is set. Should be either `Robinson` or `Orthographic`.')
        ax.set_global()
        ax.set_title(title)

        aice = self.diagnostics[f'aice_{season}']
        # field_var_c, lon_c = cutil.add_cyclic_point(aice.fillna(0), aice.lon)
        field_var_c, lon_c = cutil.add_cyclic_point(aice, aice.lon)
        im = ax.contourf(lon_c, aice.lat, field_var_c, levels, transform=transform, cmap=cmap, extend=extend)

        kmt = self.diagnostics['KMT']
        field_var_c, lon_c = cutil.add_cyclic_point(kmt, kmt.lon)
        # ax.contour(lon_c, kmt.lat, field_var_c, levels=[0, 1], colors='k', transform=transform, linewidths=coastlinewidth, zorder=99)
        ax.contourf(lon_c, kmt.lat, field_var_c, levels=[0, 1], colors='gray', transform=transform, zorder=99)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)

        return fig, ax

    def calc_KMT(self):
        self.load('KMT')
        self.load('TEMP', load_idx=-1)
        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = self.ds['TEMP'].TLAT
        ocn_grid['lon'] = self.ds['TEMP'].TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )
        self.diagnostics['KMT'] = regridder(self.ds['KMT'])
        utils.p_success(f'>>> PPCase.diagnostics["KMT"] created')

    def plot_KMT(self, figsize=[8, 5], transform=ccrs.PlateCarree(), central_longitude=180, title=None,
                 df_proxy=None, lat_colname=None, lon_colname=None, ptype_colname=None, ms=100,
                 clr_dict=None, marker_dict=None, edgeclr='k', lgd_loc='upper right', lgd_bbox_to_anchor=(1.3, 1)):
        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        ax.set_global()
        kmt = self.diagnostics['KMT']
        field_var_c, lon_c = cutil.add_cyclic_point(kmt, kmt.lon)
        ax.contourf(lon_c, kmt.lat, field_var_c, levels=[0, 1], colors='gray', transform=transform, zorder=99)

        if df_proxy is not None:
            clr_dict = {} if clr_dict is None else clr_dict
            marker_dict = {} if marker_dict is None else marker_dict
            _clr_dict = {
                'd18O': 'tab:brown',
                'UK37': 'tab:green',
                'TEX86': 'tab:red',
                'TEX86+UK37': 'tab:purple',
                'MgCa': 'tab:orange',
                'Others': 'tab:blue'
            }
            _marker_dict = {
                'd18O': 'o',
                'UK37': '^',
                'TEX86': 'v',
                'MgCa': 's',
                'TEX86+UK37': 'P',
                'Others': '*'
            }
            _clr_dict.update(clr_dict)
            _marker_dict.update(marker_dict)
            site_ptypes = list(set(df_proxy[ptype_colname]))
            for site_ptype in site_ptypes:
                df_tmp = df_proxy[df_proxy[ptype_colname] == site_ptype]
                ax.scatter(df_tmp[lon_colname], df_tmp[lat_colname], s=ms, c=_clr_dict[site_ptype], marker=_marker_dict[site_ptype],
                           edgecolors=edgeclr, zorder=99, transform=transform, label=site_ptype)

            ax.legend(frameon=False, loc=lgd_loc, bbox_to_anchor=lgd_bbox_to_anchor)

            if title is not None:
                ax.set_title(title)

        return fig, ax

    def calc_ICEFRAC(self, load_idx=-1, weight_file='/glade/u/home/fengzhu/Scripts/regrid/map_ne16np4_TO_1x1d_aave.240225.nc'):
        vn = 'ICEFRAC'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        ICEFRAC_ann = utils.monthly2annual(self.ds[vn])
        ICEFRAC_season = utils.monthly2season(self.ds[vn])
        ICEFRAC_summer = ICEFRAC_season.sel(season='JJA')
        ICEFRAC_winter = ICEFRAC_season.sel(season='DJF')

        ICEFRAC_ann.name = 'ICEFRAC'
        ICEFRAC_ann_ds = ICEFRAC_ann.to_dataset()
        ICEFRAC_ann_ds['lat'] = self.ds['lat']
        ICEFRAC_ann_ds['lon'] = self.ds['lon']
        ICEFRAC_ann_rgd = utils.regrid_cam_se(ICEFRAC_ann_ds, weight_file=weight_file)['ICEFRAC']

        ICEFRAC_summer.name = 'ICEFRAC'
        ICEFRAC_summer_ds = ICEFRAC_summer.to_dataset()
        ICEFRAC_summer_ds['lat'] = self.ds['lat']
        ICEFRAC_summer_ds['lon'] = self.ds['lon']
        ICEFRAC_summer_rgd = utils.regrid_cam_se(ICEFRAC_summer_ds, weight_file=weight_file)['ICEFRAC']

        ICEFRAC_winter.name = 'ICEFRAC'
        ICEFRAC_winter_ds = ICEFRAC_winter.to_dataset()
        ICEFRAC_winter_ds['lat'] = self.ds['lat']
        ICEFRAC_winter_ds['lon'] = self.ds['lon']
        ICEFRAC_winter_rgd = utils.regrid_cam_se(ICEFRAC_winter_ds, weight_file=weight_file)['ICEFRAC']

        self.load('KMT')

        self.load('TEMP', load_idx=load_idx)
        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = self.ds['TEMP'].TLAT
        ocn_grid['lon'] = self.ds['TEMP'].TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )

        self.diagnostics['ICEFRAC_ann'] = ICEFRAC_ann_rgd.mean('time')
        self.diagnostics['ICEFRAC_summer'] = ICEFRAC_summer_rgd
        self.diagnostics['ICEFRAC_winter'] = ICEFRAC_winter_rgd
        self.diagnostics['KMT'] = regridder(self.ds['KMT'])
        utils.p_success(f'>>> PPCase.diagnostics["ICEFRAC_ann"] created')
        utils.p_success(f'>>> PPCase.diagnostics["ICEFRAC_summer"] created')
        utils.p_success(f'>>> PPCase.diagnostics["ICEFRAC_winter"] created')
        utils.p_success(f'>>> PPCase.diagnostics["KMT"] created')

    def plot_ICEFRAC(self, season='ann', figsize=[8, 5], levels=np.linspace(0, 1, 11), cbar_labels=np.linspace(0, 1, 6),
                 transform=ccrs.PlateCarree(), cmap='Blues_r', extend='neither', coastlinewidth=1, projection='Orthographic',
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='Ice Area [%]',
                 central_longitude=180, central_latitude=90, title='Ice Area'):
        fig = plt.figure(figsize=figsize)
        if projection == 'Orthographic':
            ax = plt.subplot(projection=ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude))
        elif projection == 'Robinson':
            ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        else:
            raise ValueError('Wrong `projection` is set. Should be either `Robinson` or `Orthographic`.')
        ax.set_global()
        ax.set_title(title)

        ICEFRAC = self.diagnostics[f'ICEFRAC_{season}']
        # field_var_c, lon_c = cutil.add_cyclic_point(ICEFRAC.fillna(0), ICEFRAC.lon)
        field_var_c, lon_c = cutil.add_cyclic_point(ICEFRAC, ICEFRAC.lon)
        im = ax.contourf(lon_c, ICEFRAC.lat, field_var_c, levels, transform=transform, cmap=cmap, extend=extend)

        kmt = self.diagnostics['KMT']
        field_var_c, lon_c = cutil.add_cyclic_point(kmt, kmt.lon)
        # ax.contour(lon_c, kmt.lat, field_var_c, levels=[0, 1], colors='k', transform=transform, linewidths=coastlinewidth, zorder=99)
        ax.contourf(lon_c, kmt.lat, field_var_c, levels=[0, 1], colors='gray', transform=transform, linewidths=coastlinewidth, zorder=99)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)

        return fig, ax

    def calc_TS(self, load_idx=-1, clim=True, weight_file='/glade/u/home/fengzhu/Scripts/regrid/map_ne16np4_TO_1x1d_aave.240225.nc'):
        vn = 'TS'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        da = utils.monthly2annual(self.ds[vn]) - 273.15
        da.name = vn
        ds = da.to_dataset()
        ds['lat'] = self.ds['lat']
        ds['lon'] = self.ds['lon']
        da_rgd = utils.regrid_cam_se(ds, weight_file=weight_file)[vn]

        if clim:
            self.diagnostics['TS'] = da_rgd.mean('time')
        else:
            self.diagnostics['TS'] = da_rgd
        utils.p_success(f'>>> PPCase.diagnostics["TS"] created')

    def plot_TS(self, clim=True, load_idx=-1, figsize=[8, 5], levels=np.linspace(5, 35, 31), cbar_labels=np.linspace(5, 35, 7),
                 transform=ccrs.PlateCarree(), cmap='RdBu_r', extend='both', coastlinewidth=0.5,
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='TS [°C]',
                 central_longitude=180, title='Annual Mean Surface Temperature'):
        if clim:
            ts = self.diagnostics['TS']
        else:
            ts = self.diagnostics['TS'][load_idx]
            
        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        ax.set_global()
        ax.set_title(title)

        im = ax.contourf(ts.lon, ts.lat, ts, levels, transform=transform, cmap=cmap, extend=extend)

        if 'KMT' not in self.diagnostics:
            self.calc_KMT()
        kmt = self.diagnostics['KMT']
        field_var_c, lon_c = cutil.add_cyclic_point(kmt, kmt.lon)
        ax.contour(lon_c, kmt.lat, field_var_c, levels=[0, 1], colors='k', transform=transform, linewidths=coastlinewidth, zorder=99)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)
            
        return fig, ax

    def calc_SSS(self, load_idx=-1, clim=True):
        vn = 'SALT'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        sss = utils.monthly2annual(self.ds[vn][:,0])
        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = sss.TLAT
        ocn_grid['lon'] = sss.TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )

        sss_rgd = regridder(sss)
        if clim:
            self.diagnostics['SSS'] = sss_rgd.mean('time')
        else:
            self.diagnostics['SSS'] = sss_rgd
        utils.p_success(f'>>> PPCase.diagnostics["SSS"] created')

    def plot_SSS(self, clim=True, load_idx=-1, figsize=[8, 5], levels=np.linspace(20, 40, 21), cbar_labels=np.linspace(20, 40, 11),
                 transform=ccrs.PlateCarree(), cmap='viridis', extend='both', coastlinewidth=1,
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='Salinity [g/kg]',
                 central_longitude=180, title='Annual Mean Sea-surface Salinity'):
        if clim:
            sss = self.diagnostics['SSS']
        else:
            sss = self.diagnostics['SSS'][load_idx]
        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        ax.set_global()
        ax.set_title(title)

        im = ax.contourf(sss.lon, sss.lat, sss, levels, transform=transform, cmap=cmap, extend=extend)
        ax.contour(sss.lon, sss.lat, np.isnan(sss), levels=[0, 1], colors='k', transform=transform, linewidths=coastlinewidth)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)

        return fig, ax

    def calc_SSd18O(self, load_idx=-1, clim=True):
        vn = 'R18O'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        d18O = utils.monthly2annual(self.ds[vn][:,0])
        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = d18O.TLAT
        ocn_grid['lon'] = d18O.TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )

        d18O_rgd = regridder(d18O)
        if clim:
            self.diagnostics['SSd18O'] = d18O_rgd.mean('time')
        else:
            self.diagnostics['SSd18O'] = d18O_rgd

        utils.p_success(f'>>> PPCase.diagnostics["SSd18O"] created')

    def plot_SSd18O(self, clim=True, load_idx=-1, figsize=[8, 5], levels=np.linspace(0.992, 1.002, 21), cbar_labels=np.linspace(0.992, 1.002, 6),
                 transform=ccrs.PlateCarree(), cmap='viridis', extend='both', coastlinewidth=1,
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='d18O [permil]',
                 central_longitude=180, title='Annual Mean Sea-surface d18O'):
        if clim:
            d18O = self.diagnostics['SSd18O']
        else:
            d18O = self.diagnostics['SSd18O'][load_idx]

        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        ax.set_global()
        ax.set_title(title)

        im = ax.contourf(d18O.lon, d18O.lat, d18O, levels, transform=transform, cmap=cmap, extend=extend)
        ax.contour(d18O.lon, d18O.lat, np.isnan(d18O), levels=[0, 1], colors='k', transform=transform, linewidths=coastlinewidth)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)

        return fig, ax


    def calc_SST(self, load_idx=-1, clim=True):
        vn = 'TEMP'
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        sst = utils.monthly2annual(self.ds[vn][:,0])
        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = sst.TLAT
        ocn_grid['lon'] = sst.TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )

        sst_rgd = regridder(sst)
        if clim:
            self.diagnostics['SST'] = sst_rgd.mean('time')
        else:
            self.diagnostics['SST'] = sst_rgd
        utils.p_success(f'>>> PPCase.diagnostics["SST"] created')

    def plot_SST(self, clim=True, load_idx=-1, figsize=[8, 5], levels=np.linspace(5, 35, 31), cbar_labels=np.linspace(5, 35, 7),
                 transform=ccrs.PlateCarree(), cmap='RdBu_r', extend='both', coastlinewidth=1,
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='SST [°C]',
                 central_longitude=180, title='Annual Mean SST',
                 df_proxy=None, lat_colname='lat', lon_colname='lon', sst_colname='sst',
                 site_markersize=100, site_marker='o'):
        if clim:
            sst = self.diagnostics['SST']
        else:
            sst = self.diagnostics['SST'][load_idx]
            
        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        ax.set_global()
        ax.set_title(title)

        im = ax.contourf(sst.lon, sst.lat, sst, levels, transform=transform, cmap=cmap, extend=extend)
        ax.contour(sst.lon, sst.lat, np.isnan(sst), levels=[0, 1], colors='k', transform=transform, linewidths=coastlinewidth)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)

        if df_proxy is not None:
            site_lons = df_proxy[lon_colname]
            site_lats = df_proxy[lat_colname]
            site_ssts = df_proxy[sst_colname]
            cmap_obj = plt.get_cmap(cmap)
            norm = BoundaryNorm(levels, ncolors=cmap_obj.N, clip=True)
            ax.scatter(site_lons, site_lats, s=site_markersize, c=site_ssts, marker=site_marker, edgecolors='k',
                       zorder=99, transform=transform, cmap=cmap, norm=norm)
            
        return fig, ax

    def calc_MLD(self, vn='XMXL', load_idx=-1, season='DJF'):
        self.load(vn, load_idx=load_idx)
        self.ds[vn].load()
        if season == 'ann':
            da = utils.monthly2annual(self.ds[vn])
        else:
            da = utils.monthly2season(self.ds[vn]).sel(season=season)

        ocn_grid = xr.Dataset()
        ocn_grid['lat'] = da.TLAT
        ocn_grid['lon'] = da.TLONG
        regridder = xe.Regridder(
            ocn_grid, xe.util.grid_global(1, 1, cf=True, lon1=360),
            method='bilinear',
            periodic=True,
        )

        da_rgd = regridder(da)
        if season == 'ann':
            self.diagnostics['MLD'] = da_rgd.mean('time')
        else:
            self.diagnostics['MLD'] = da_rgd
        utils.p_success(f'>>> PPCase.diagnostics["MLD"] created')
        
    def plot_MLD(self, figsize=[8, 5], levels=np.linspace(0, 500, 21), cbar_labels=np.linspace(0, 500, 11),
                 transform=ccrs.PlateCarree(), cmap='GnBu', extend='max', coastlinewidth=1,
                 cbar_orientation='horizontal', cbar_shrink=0.7, cbar_pad=0.1, cbar_title='MLD [m]',
                 central_longitude=-30, title='Mixed Layer Depth'):
        mld = self.diagnostics['MLD']/100
        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(projection=ccrs.Robinson(central_longitude=central_longitude))
        ax.set_global()
        ax.set_title(title)

        field_var_c, lon_c = cutil.add_cyclic_point(mld, mld.lon)
        im = ax.contourf(lon_c, mld.lat, field_var_c, levels, transform=transform, cmap=cmap, extend=extend)
        ax.contour(lon_c, mld.lat, np.isnan(field_var_c), levels=[0, 1], colors='k', transform=transform, linewidths=coastlinewidth)

        cbar = fig.colorbar(im, ax=ax, orientation=cbar_orientation, shrink=cbar_shrink, pad=cbar_pad)
        cbar.ax.set_title(cbar_title)
        cbar.set_ticks(cbar_labels)

        return fig, ax

    def calc_GMST(self):
        vn = 'TS'
        self.load(vn)
        self.ds[vn].load()
        da = utils.monthly2annual(self.ds[vn])
        da_gm = da.weighted(self.ds.gw_atm).mean(list(self.ds.gw_atm.dims))
        self.diagnostics['GMST'] = da_gm - 273.15  # K -> degC
        utils.p_success(f'>>> PPCase.diagnostics["GMST"] created')

    def plot_GMST(self, figsize=[4, 4], ylim=[13, 15], xlim=None, xlabel='Time [yr]', ylabel=r'GMST [$^\circ$C]', color='tab:red',
                  ref=14, ax=None, stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['GMST'].plot(ax=ax, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        if xlim is not None:
            ax.set_xlim(xlim)
            ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.axhline(ref, ls='--', color='tab:grey')
        ax.set_title('Gobal Mean Surface Temperature')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["GMST"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def plot_GMST_CO2(self, data_dict, figsize=[4, 4], ylim=[10, 40], xlim=None, xticks=[1, 2, 3, 6, 9, 16, 32], xlabel=r'CO2 $\times$ 284.7 [ppm]',
                      ylabel=r'GMST [$^\circ$C]', ax=None, title=None, plot_kws=None, lgd_kws=None):

        plot_kws = {} if plot_kws is None else plot_kws
        lgd_kws = {} if lgd_kws is None else lgd_kws

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        ax.set_xscale('log')
        ax.set_xlabel(xlabel, fontweight='bold')
        ax.set_ylabel(ylabel, fontweight='bold')
        ax.set_ylim(ylim)
        ax.set_xlim(xlim)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks)

        _plot_kws = {
            'ms': 10,
            'marker': 's',
        }
        _plot_kws_default = _plot_kws.copy()
        for k, v in data_dict.items():
            if k in plot_kws:
                _plot_kws.update(plot_kws[k])
            else:
                _plot_kws.update(_plot_kws_default)

            ax.plot(v['CO2'], v['GMST'], label=k, **_plot_kws)

        _lgd_kws = {
            'frameon': False,
            'bbox_to_anchor': (1, 1),
            'loc': 'upper left',
        }
        _lgd_kws.update(lgd_kws)
        ax.legend(**_lgd_kws)

        if title is not None:
            ax.set_title(title, fontweight='bold')

        if 'fig' in locals():
            return fig, ax
        else:
            return ax
        

    def calc_GMRESTOM(self):
        vn = ['FSNT', 'FLNT']
        self.load(vn)
        self.ds[vn].load()
        da = utils.monthly2annual(self.ds[vn[0]] - self.ds[vn[1]])
        da_gm = da.weighted(self.ds.gw_atm).mean(list(self.ds.gw_atm.dims))
        self.diagnostics['GMRESTOM'] = da_gm
        utils.p_success(f'>>> PPCase.diagnostics["GMRESTOM"] created')

    def plot_GMRESTOM(self, figsize=[4, 4], ylim=[-3, 3], xlim=None, xlabel='Time [yr]', ylabel=r'GMRESTOM [W/m$^2$]', color='tab:blue',
                      ref=0, ax=None, stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['GMRESTOM'].plot(ax=ax, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        if xlim is not None:
            ax.set_xlim(xlim)
            ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.axhline(ref, ls='--', color='tab:grey')
        ax.set_title('Gobal Mean Net Radiative Flux')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["GMRESTOM"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def calc_GMLWCF(self):
        vn = 'LWCF'
        self.load(vn)
        self.ds[vn].load()
        da = utils.monthly2annual(self.ds[vn])
        da_gm = da.weighted(self.ds.gw_atm).mean([d for d in self.ds[vn].dims if d!='time'])
        self.diagnostics['GMLWCF'] = da_gm
        utils.p_success(f'>>> PPCase.diagnostics["GMLWCF"] created')

    def plot_GMLWCF(self, figsize=[4, 4], ylim=[23, 27], xlim=None, xlabel='Time [yr]', ylabel=r'GMLWCF [W/m$^2$]', color='tab:green',
                    ref=25, ax=None, stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['GMLWCF'].plot(ax=ax, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        if xlim is not None:
            ax.set_xlim(xlim)
            ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.axhline(ref, ls='--', color='tab:grey')
        ax.set_title('Gobal Mean Longwave Cloud Forcing')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["GMLWCF"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def calc_GMSWCF(self):
        vn = 'SWCF'
        self.load(vn)
        self.ds[vn].load()
        da = utils.monthly2annual(self.ds[vn])
        da_gm = da.weighted(self.ds.gw_atm).mean([d for d in self.ds[vn].dims if d!='time'])
        self.diagnostics['GMSWCF'] = da_gm
        utils.p_success(f'>>> PPCase.diagnostics["GMSWCF"] created')

    def plot_GMSWCF(self, figsize=[4, 4], ylim=[-53, -45], xlim=None, xlabel='Time [yr]', ylabel=r'GMSWCF [W/m$^2$]', color='tab:orange',
                    ref=-47, ax=None, stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['GMSWCF'].plot(ax=ax, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        if xlim is not None:
            ax.set_xlim(xlim)
            ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.axhline(ref, ls='--', color='tab:grey')
        ax.set_title('Gobal Mean Shortwave Cloud Forcing')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["GMSWCF"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def calc_NHICEFRAC(self, vn='aice'):
        self.load(vn)
        self.ds[vn].load()
        da = utils.monthly2annual(self.ds[vn])

        if vn == 'ICEFRAC':
            convert_factor = 4*np.pi*6.37122**2 / self.ds.gw_atm.sum().values  # 1e6 km^2
            da_nhm = da.where(self.ds.lat_atm>0).weighted(self.ds.gw_atm).sum(list(self.ds.gw_atm.dims))
        elif vn == 'aice':
            convert_factor = 4*np.pi*6.37122**2 / self.ds.gw_ice.sum().values / 100  # 1e6 km^2
            da_nhm = da.where(self.ds.lat_ice>0).weighted(self.ds.gw_ice).sum(list(self.ds.gw_ice.dims))

        self.diagnostics['NHICEFRAC'] = da_nhm * convert_factor
        utils.p_success(f'>>> PPCase.diagnostics["NHICEFRAC"] created')

        da = self.ds[vn].groupby('time.month').mean('time')
        if vn == 'ICEFRAC':
            da_nhm = da.where(self.ds.lat_atm>0).weighted(self.ds.gw_atm).sum(list(self.ds.gw_atm.dims))
        elif vn == 'aice':
            da_nhm = da.where(self.ds.lat_ice>0).weighted(self.ds.gw_ice).sum(list(self.ds.gw_ice.dims))

        self.diagnostics['NHICEFRAC_clim'] = da_nhm * convert_factor
        utils.p_success(f'>>> PPCase.diagnostics["NHICEFRAC_clim"] created')

                
    def plot_NHICEFRAC(self, figsize=[4, 4], ylim=[4, 16], xlim=None, xlabel='Time [yr]', ylabel=r'NHICEFRAC [10$^6$ km$^2$]', color='tab:cyan', ax=None,
                       stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['NHICEFRAC'].plot(ax=ax, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        if xlim is not None:
            ax.set_xlim(xlim)
            ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.set_title('NH Ice Area')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["NHICEFRAC"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def plot_NHICEFRAC_clim(self, figsize=[4, 4], ylim=[4, 16], xlabel='Month', ylabel=r'NHICEFRAC [10$^6$ km$^2$]', color='tab:cyan', ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['NHICEFRAC_clim'].plot(ax=ax, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        ax.set_xlim(1, 12)
        ax.set_xticks(list(range(1, 13)))
        ax.set_title('Annual Cycle of NH Ice Area')

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def calc_GMSSS(self):
        vn = 'SSS'
        self.load(vn)
        self.ds[vn].load()
        da = utils.monthly2annual(self.ds[vn])
        da_gm = da.weighted(self.ds.gw_ocn).mean(list(self.ds.gw_ocn.dims))
        self.diagnostics['GMSSS'] = da_gm
        utils.p_success(f'>>> PPCase.diagnostics["GMSSS"] created')

    def plot_GMSSS(self, figsize=[4, 4], ylim=[34, 35], xlim=[0, 500], xlabel='Time [yr]', ylabel=r'Salinity [g/kg]', color='tab:orange', ax=None,
                   stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['GMSSS'].plot(ax=ax, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        ax.set_xlim(xlim)
        ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.set_title('Gobal Mean Sea Surface Salinity')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["GMSSS"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def calc_GMSSd18O(self):
        vn = 'SSR18O'
        self.load(vn)
        self.ds[vn].load()
        da = utils.monthly2annual((self.ds[vn]-1)*1e3)
        da_gm = da.weighted(self.ds.gw_ocn).mean(list(self.ds.gw_ocn.dims))
        self.diagnostics['GMSSd18O'] = da_gm
        utils.p_success(f'>>> PPCase.diagnostics["GMSSd18O"] created')

    def plot_GMSSd18O(self, figsize=[4, 4], ylim=[-0.1, 0.1], xlim=[0, 500], xlabel='Time [yr]', ylabel=r'd18Osw [‰]', color='tab:orange', ax=None,
                   stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['GMSSd18O'].plot(ax=ax, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        ax.set_xlim(xlim)
        ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.set_title('Gobal Mean Sea Surface d18O')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["GMSSd18O"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def calc_AMOC(self, timeslice=slice(-50, None), transport_reg=1):
        vn = 'MOC'
        self.load(vn)
        self.ds[vn].load()
        self.calc_log['calc_AMOC'] = {'timeslice': timeslice}
        da = utils.monthly2annual(self.ds[vn])
        da['moc_z'] = da['moc_z'] / 1e5  # cm -> km
        da['moc_z'].attrs['units'] = 'km'

        self.diagnostics['AMOC'] = da.isel(transport_reg=transport_reg, moc_comp=0).sel(moc_z=slice(0.5, None), lat_aux_grid=slice(28, 90)).max(('moc_z', 'lat_aux_grid'))
        self.diagnostics['AMOC_yz'] = da.isel(transport_reg=transport_reg, moc_comp=0, time=timeslice).mean('time')
        self.diagnostics = self.diagnostics.drop_vars('moc_components')
        utils.p_success(f'>>> PPCase.diagnostics["AMOC"] created')
        utils.p_success(f'>>> PPCase.diagnostics["AMOC_yz"] created')

    def plot_AMOC(self, figsize=[4, 4], ylim=[15, 30], xlim=[0, 500], xlabel='Time [yr]', ylabel=r'AMOC [Sv]', color='tab:blue', ax=None, stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['AMOC'].plot(ax=ax, color=color)
        ax.set_title(None)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 6))
        ax.set_xlim(xlim)
        ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.set_title('Atlantic Meridional Overturning Circulation')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["AMOC"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def plot_AMOC_yz(self, figsize=[4, 4], xlim=[-35, 90], xlabel='Latitude', ylabel='Depth [km]', amoc_levels=np.linspace(-24, 24, 25), ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        da = self.diagnostics['AMOC_yz']
        im = ax.contourf(da.lat_aux_grid, da.moc_z, da, cmap='RdBu_r', extend='both', levels=amoc_levels)
        ax.set_xticks([-30, 0, 30, 60, 90])
        ax.set_xlim(xlim)
        ax.set_title(f"AMOC_yz (last {np.abs(self.calc_log['calc_AMOC']['timeslice'].start)} yrs)")
        ax.invert_yaxis()
        ax.set_yticks([0, 2, 4])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        cbar = plt.colorbar(im, extend='both', shrink=0.9, ax=ax)
        cbar.ax.set_title('[Sv]')

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def calc_MOC_SH(self, moc_z=slice(0.5, None), transport_reg=0, load_idx=None):
        vn = 'MOC'
        if load_idx is not None:
            self.load(vn, load_idx=load_idx)
        else:
            self.load(vn)

        self.ds[vn].load()
        self.calc_log['calc_MOC_SH'] = {'moc_z': moc_z, 'transport_reg': transport_reg}
        da = utils.monthly2annual(self.ds[vn])
        da['moc_z'] = da['moc_z'] / 1e5  # cm -> km
        da['moc_z'].attrs['units'] = 'km'

        self.diagnostics['MOC_SH'] = da.isel(transport_reg=transport_reg, moc_comp=0).sel(moc_z=moc_z, lat_aux_grid=slice(-90, -28)).min(('moc_z', 'lat_aux_grid'))
        self.diagnostics['MOC_SH_yz'] = da.isel(transport_reg=transport_reg, moc_comp=0).mean('time')
        self.diagnostics = self.diagnostics.drop_vars('moc_components')
        utils.p_success(f'>>> PPCase.diagnostics["MOC_SH"] created')
        utils.p_success(f'>>> PPCase.diagnostics["MOC_SH_yz"] created')

    def plot_MOC_SH(self, figsize=[4, 4], ylim=[25, 40], xlim=None, xlabel='Time [yr]', ylabel=r'MOC [Sv]', color='tab:blue', ax=None, stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['MOC_SH'].plot(ax=ax, color=color)
        ax.set_title(None)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.set_yticks(np.linspace(ylim[0], ylim[-1], 6))
        if xlim is not None:
            ax.set_xlim(xlim)
            ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.set_title('Southern Ocean (90°S-28°S) MOC')
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["MOC_SH"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def plot_MOC_SH_yz(self, figsize=[4, 4], xlim=[-90, 35], xlabel='Latitude', ylabel='Depth [km]', amoc_levels=np.linspace(-24, 24, 25), ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        da = self.diagnostics['MOC_SH_yz']
        im = ax.contourf(da.lat_aux_grid, da.moc_z, da, cmap='RdBu_r', extend='both', levels=amoc_levels)
        ax.set_xticks([-90, -60, -30, 0, 30, 60, 90])
        ax.set_xlim(xlim)
        ax.set_title(f"MOC_SH_yz")
        ax.invert_yaxis()
        ax.set_yticks([0, 2, 4])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        cbar = plt.colorbar(im, extend='both', shrink=0.9, ax=ax)
        cbar.ax.set_title('[Sv]')

        if 'fig' in locals():
            return fig, ax
        else:
            return ax


    def calc_ENSO(self):
        vn = 'SST'
        self.load(vn)
        self.ds[vn].load()
        da_clim = self.ds[vn].groupby('time.month').mean('time')
        da_anom = self.ds[vn].groupby('time.month') - da_clim
        da = utils.monthly2annual(da_anom)
        # da = utils.monthly2annual(self.ds[vn])

        da_avg = da.where((self.ds.lat_ocn>=-5)&(self.ds.lat_ocn<=5)&(self.ds.lon_ocn>=np.mod(-170, 360))&(self.ds.lon_ocn>=np.mod(-120, 360))).weighted(
            self.ds.gw_ocn).mean(list(self.ds.gw_ocn.dims))
        self.diagnostics['ENSO'] = da_avg
        utils.p_success(f'>>> PPCase.diagnostics["ENSO"] created')

        # da_avg = da.where((self.ds.lat_ocn>=-10)&(self.ds.lat_ocn<=10)&(self.ds.lon_ocn>=np.mod(-90, 360))&(self.ds.lon_ocn>=np.mod(-80, 360))).weighted(
        #     self.ds.gw_ocn).mean(list(self.ds.gw_ocn.dims))
        # self.diagnostics['NINO1+2'] = da_avg.load()
        # utils.p_success(f'>>> PPCase.diagnostics["NINO1+2"] created')

        # da_avg = da.where((self.ds.lat_ocn>=-5)&(self.ds.lat_ocn<=5)&(self.ds.lon_ocn>=np.mod(-150, 360))&(self.ds.lon_ocn>=np.mod(-90, 360))).weighted(
        #     self.ds.gw_ocn).mean(list(self.ds.gw_ocn.dims))
        # self.diagnostics['NINO3'] = da_avg.load()
        # utils.p_success(f'>>> PPCase.diagnostics["NINO3"] created')

        # da_avg = da.where((self.ds.lat_ocn>=-5)&(self.ds.lat_ocn<=5)&(self.ds.lon_ocn>=np.mod(160, 360))&(self.ds.lon_ocn>=np.mod(-150, 360))).weighted(
        #     self.ds.gw_ocn).mean(list(self.ds.gw_ocn.dims))
        # self.diagnostics['NINO4'] = da_avg.load()
        # utils.p_success(f'>>> PPCase.diagnostics["NINO4"] created')

    def plot_ENSO(self, figsize=[4, 4], ylim=[-2, 2], xlim=None, xlabel='Time [yr]', ylabel=r'NINO3.4 [$^\circ$C]', color='tab:red', ax=None, stat_period=-50):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.diagnostics['ENSO'].plot(ax=ax, color=color)
        ax.set_title(None)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        # ax.set_yticks(np.linspace(ylim[0], ylim[-1], 5))
        if xlim is not None:
            ax.set_xlim(xlim)
            ax.set_xticks(np.linspace(xlim[0], xlim[-1], 6))
        ax.set_title('ENSO')
        # ax.text(
        #     1, 0.90,
        #     f'last {np.abs(stat_period)}-yr mean: {np.mean(self.diagnostics["ENSO"][stat_period:].values):.2f}',
        #     verticalalignment='bottom',
        #     horizontalalignment='right',
        #     transform=ax.transAxes,
        #     color=color,
        #     fontsize=15,
        # )
        ax.text(
            1, 0.90,
            f'last {np.abs(stat_period)}-yr std: {np.std(self.diagnostics["ENSO"][stat_period:].values):.2f}',
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color=color,
            fontsize=15,
        )

        if 'fig' in locals():
            return fig, ax
        else:
            return ax


# class PPCase:
#     ''' Designed for postprocessed timeseries
#     '''
#     def __init__(self, root_dir, vn=['TS', 'FSNT', 'FLNT', 'LWCF', 'SWCF', 'ICEFRAC', 'MOC'],
#                  vn_paths=None, grid_weight_dict=None, lat_dict=None, settings_csv=None, adjust_month=True):
#         self.root_dir = root_dir
#         utils.p_header(f'>>> Case.root_dir: {self.root_dir}')

#         if settings_csv is not None:
#             settings_df = pd.read_csv(settings_csv, index_col=0)
#             self.settings_csv = settings_csv
#             self.settings_df = settings_df
#             utils.p_header(f'>>> PPCase.settings_csv: {self.settings_csv}')
#             utils.p_success(f'>>> PPCase.settings_df created')

#         # settings
#         self.vn_paths = {}
#         for v in ['TS', 'FSNT', 'FLNT', 'LWCF', 'SWCF', 'ICEFRAC']:
#             self.vn_paths[v] = f'atm/proc/tseries/month_1/*cam.h0.{v}.*.nc'

#         for v in ['MOC']:
#             self.vn_paths[v] = f'ocn/proc/tseries/month_1/*pop.h.{v}.*.nc'
        
#         if vn_paths is not None:
#             self.vn_paths.update(vn_paths)

#         self.vn_component = {}
#         for v, p in self.vn_paths.items():
#             self.vn_component[v] = p.split('/')[0]

#         # load variables
#         if type(vn) is not list: vn = [vn]
#         self.vn = vn
#         utils.p_header(f'>>> Loading variables: {self.vn}')
#         self.ds = {}
#         for v in tqdm(self.vn):
#             comp = self.vn_component[v]
#             path = os.path.join(self.root_dir, self.vn_paths[v])
#             ds =  xr.open_mfdataset(path)
#             if adjust_month:
#                 ds['time'] = ds['time'].get_index('time') - datetime.timedelta(days=1)

#             if comp not in self.ds:
#                 self.ds[comp] = ds.copy()
#             else:
#                 self.ds[comp][v] = ds[v]

#         for comp in self.ds.keys():
#             utils.p_success(f'>>> Case.ds["{comp}"] created')

#         # set grid weight
#         grid_weight = {
#             'atm': 'area',
#             'ocn': 'TAREA',
#             'ice': 'tarea',
#             'lnd': 'area',
#         }
#         if grid_weight_dict is not None:
#             grid_weight.update(grid_weight_dict)

#         self.grid_weight = {}
#         for comp in self.ds.keys():
#             self.grid_weight[comp] = self.ds[comp][grid_weight[comp]][0].fillna(0)
#             utils.p_success(f'>>> Case.grid_weight["{comp}"] created')

#         # set lat
#         lat = {
#             'atm': 'lat',
#             'ocn': 'TLAT',
#             'ice': 'TLAT',
#             'lnd': 'lat',
#         }
#         if lat_dict is not None:
#             lat.update(lat_dict)

#         self.lat = {}
#         for comp in self.ds.keys():
#             self.lat[comp] = self.ds[comp][lat[comp]]
#             utils.p_success(f'>>> Case.lat["{comp}"] created')

#     def copy(self):
#         return copy.deepcopy(self)

#     def ann(self, vn=None):
#         new = self.copy()
#         for comp in self.ds.keys():
#             vn_list = list(set(self.ds[comp].variables).intersection(set(self.vn)))
#             new.ds[comp] = utils.monthly2annual(self.ds[comp][vn_list])
#         return new


#     def gm(self, vn=None):
#         new = self.copy()
#         for comp in self.ds.keys():
#             new.ds[comp] = self.ds[comp].weighted(self.grid_weight[comp]).mean([d for d in self.ds[comp].dims if d!='time'])
#         return new

#     def nhm(self, vn=None):
#         new = self.copy()
#         for comp in self.ds.keys():
#             new.ds[comp] = self.ds[comp].where(self.lat[comp]>0).weighted(self.grid_weight[comp]).mean([d for d in self.ds[comp].dims if d!='time'])
#         return new

#     def shm(self, vn=None):
#         new = self.copy()
#         for comp in self.ds.keys():
#             new.ds[comp] = self.ds[comp].where(self.lat[comp]<0).weighted(self.grid_weight[comp]).mean([d for d in self.ds[comp].dims if d!='time'])
#         return new

class Logs:
    def __init__(self, dirpath, comp='ocn', load_num=None):
        self.dirpath = dirpath
        self.paths = sorted(glob.glob(os.path.join(dirpath, f'{comp}.log.*.gz')))
        if load_num is not None:
            if load_num < 0:
                self.paths = self.paths[load_num:]
            else:
                self.paths = self.paths[:load_num]

        utils.p_header(f'>>> Logs.dirpath: {self.dirpath}')
        utils.p_header(f'>>> {len(self.paths)} Logs.paths:')
        print(f'Start: {os.path.basename(self.paths[0])}')
        print(f'End: {os.path.basename(self.paths[-1])}')

    def get_vars(self, vn=[
                    'UVEL', 'UVEL2', 'VVEL', 'VVEL2', 'TEMP', 'dTEMP_POS_2D', 'dTEMP_NEG_2D', 'SALT', 'RHO', 'RHO_VINT',
                    'RESID_T', 'RESID_S', 'SU', 'SV', 'SSH', 'SSH2', 'SHF', 'SHF_QSW', 'SFWF', 'SFWF_WRST', 'TAUX', 'TAUX2', 'TAUY',
                    'TAUY2', 'FW', 'TFW_T', 'TFW_S', 'EVAP_F', 'PREC_F', 'SNOW_F', 'MELT_F', 'ROFF_F', 'IOFF_F', 'SALT_F', 'SENH_F',
                    'LWUP_F', 'LWDN_F', 'MELTH_F', 'IFRAC', 'PREC_16O_F', 'PREC_18O_F', 'PREC_HDO_F', 'EVAP_16O_F', 'EVAP_18O_F', 'EVAP_HDO_F',
                    'MELT_16O_F', 'MELT_18O_F', 'MELT_HDO_F', 'ROFF_16O_F', 'ROFF_18O_F', 'ROFF_HDO_F', 'IOFF_16O_F', 'IOFF_18O_F', 'IOFF_HDO_F',
                    'R18O', 'FvPER_R18O', 'FvICE_R18O', 'RHDO', 'FvPER_RHDO', 'FvICE_RHDO', 'ND143', 'ND144', 'IAGE', 'QSW_HBL', 'KVMIX', 'KVMIX_M',
                    'TPOWER', 'VDC_T', 'VDC_S', 'VVC', 'KAPPA_ISOP', 'KAPPA_THIC', 'HOR_DIFF', 'DIA_DEPTH', 'TLT', 'INT_DEPTH', 'UISOP', 'VISOP',
                    'WISOP', 'ADVT_ISOP', 'ADVS_ISOP', 'VNT_ISOP', 'VNS_ISOP', 'USUBM', 'VSUBM', 'WSUBM', 'HLS_SUBM', 'ADVT_SUBM', 'ADVS_SUBM',
                    'VNT_SUBM', 'VNS_SUBM', 'HDIFT', 'HDIFS', 'WVEL', 'WVEL2', 'UET', 'VNT', 'WTT', 'UES', 'VNS', 'WTS', 'ADVT', 'ADVS', 'PV',
                    'Q', 'PD', 'QSW_HTP', 'QFLUX', 'HMXL', 'XMXL', 'TMXL', 'HBLT', 'XBLT', 'TBLT', 'BSF',
                    'NINO_1_PLUS_2', 'NINO_3', 'NINO_3_POINT_4', 'NINO_4',
                ]):

        if not isinstance(vn, (list, tuple)):
            vn = [vn]

        nf = len(self.paths)
        df_list = []
        for idx_file in range(nf):
            vars = {}
            with gzip.open(self.paths[idx_file], mode='rt') as fp:
                lines = fp.readlines()

                # find 1st timestamp
                for line in lines:
                    i = lines.index(line)
                    if line.find('This run        started from') != -1 and lines[i+1].find('date(month-day-year):') != -1:
                        start_date = lines[i+1].split(':')[-1].strip()
                        break

                mm, dd, yyyy = start_date.split('-')

                # find variable values
                for line in lines:
                    for v in vn:
                        if v not in vars:
                            vars[v] = []
                        elif line.strip().startswith(f'{v}:'):
                            val = float(line.strip().split(':')[-1])
                            vars[v].append(val)

            df_tmp = pd.DataFrame(vars)
            dates = xr.cftime_range(start=f'{yyyy}-{mm}-{dd}', freq='MS', periods=len(df_tmp), calendar='noleap')
            years = []
            months = []
            for date in dates:
                years.append(date.year)
                months.append(date.month)

            df_tmp['Year'] = years
            df_tmp['Month'] = months
            df_list.append(df_tmp)
        
        df = pd.concat(df_list, join='inner').drop_duplicates(subset=['Year', 'Month'], keep='last')
        df = df[ ['Year', 'Month'] + [ col for col in df.columns if col not in ['Year', 'Month']]]
        self.df = df
        self.df_ann = self.df.groupby(self.df.Year).mean()
        self.vn = vn

    def plot_vars(self, vn=None, annualize=True, xlim=None, unit_dict=None, clr_dict=None,
                  figsize=[20, 5], ncol=4, nrow=None, wspace=0.3, hspace=0.5, kws=None, title=None):

        kws = {} if kws is None else kws
        unit_dict = {} if unit_dict is None else unit_dict
        clr_dict = {} if clr_dict is None else clr_dict

        _unit_dict = {
            'TEMP': 'degC',
            'SALT': 'kg/kg',
            'QFLUX': 'W/m^2',
            'NINO_3_POINT_4': 'degC',
        }
        _unit_dict.update(unit_dict)

        _clr_dict = {
            'TEMP': 'tab:red',
            'SALT': 'tab:green',
            'QFLUX': 'tab:blue',
            'NINO_3_POINT_4': 'tab:orange',
        }
        _clr_dict.update(clr_dict)

        if vn is None:
            vn = self.vn

        if not isinstance(vn, (list, tuple)):
            vn = [vn]

        if nrow is None:
            nrow = int(np.ceil(len(vn)/ncol))

        if annualize:
            df_plot = self.df_ann
        else:
            df_plot = self.df
            
        fig = plt.figure(figsize=figsize)
        ax = {}
        gs = gridspec.GridSpec(nrow, ncol)
        gs.update(wspace=wspace, hspace=hspace)

        for i, v in enumerate(vn):
            if v in self.df.columns:
                if v not in kws:
                    kws[v] = {}

                ax[v] = fig.add_subplot(gs[i])

                if v in _clr_dict:
                    kws[v]['color'] = _clr_dict[v]

                if v == 'SALT':
                    ax[v].plot(df_plot.index, df_plot[v].values*1e3, **kws[v])
                else:
                    df_plot[v].plot(ax=ax[v], **kws[v])

                if v in _unit_dict:
                    ax[v].set_ylabel(f'{v} [{_unit_dict[v]}]')
                else:
                    ax[v].set_ylabel(v)

                ax[v].ticklabel_format(useOffset=False)
                if xlim is not None:
                    ax[v].set_xlim(xlim)

        if title is not None:
            fig.suptitle(title)

        return fig, ax

    
    def compare_vars(self, L_ref, vn=None, annualize=True, xlim=None, unit_dict=None, clr_dict=None,
                  figsize=[20, 5], ncol=4, nrow=None, wspace=0.3, hspace=0.5, kws=None, title=None):

        if vn is None:
            vn = self.vn

        fig, ax = self.plot_vars(vn=vn, annualize=annualize, xlim=xlim, unit_dict=unit_dict, clr_dict=clr_dict,
                                 figsize=figsize, ncol=ncol, nrow=nrow, wspace=wspace, hspace=hspace, kws=kws, title=title)

        kws = {} if kws is None else kws
        unit_dict = {} if unit_dict is None else unit_dict
        clr_dict = {} if clr_dict is None else clr_dict

        if annualize:
            df_plot = L_ref.df_ann
        else:
            df_plot = L_ref.df

        for v in vn:
            if v not in kws:
                kws[v] = {}

            if v == 'SALT':
                ax[v].plot(df_plot.index, df_plot[v].values*1e3, color='k', **kws[v])
            else:
                df_plot[v].plot(ax=ax[v], color='k', **kws[v])
        
        return fig, ax
        
