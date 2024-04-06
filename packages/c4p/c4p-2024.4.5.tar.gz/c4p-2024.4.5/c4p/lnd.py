import os, glob
import numpy as np
from IPython.display import display, Image, IFrame
from datetime import date
import xarray as xr

from . import utils

cwd = os.path.dirname(__file__)

class LND:
    def __init__(self, grids_dirpath=None, path_create_ESMF_map_sh=None, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.grids_dirpath='/glade/p/cesmdata/inputdata/share/scripgrids' if grids_dirpath is None else grids_dirpath
        self.path_create_ESMF_map_sh=os.path.join(cwd, './src/rof/create_ESMF_map.sh') if path_create_ESMF_map_sh is None else path_create_ESMF_map_sh
        self.configs = {}

        for k, v in self.__dict__.items():
            utils.p_success(f'>>> LND.{k}: {v}')

    def prep_topo(self, path_topo, res='2x2', path_create_topo_ncl=None):
        # Step 19
        utils.p_header('>>> Prep topo file at proper resolution ...')
        self.res = res
        utils.p_success(f'>>> LND.res = "{res}"')

        if path_create_topo_ncl is None:
            path_create_topo_ncl = os.path.join(cwd, f'./src/rof/create-topo_{res}deg.ncl')

        fpath = utils.copy(path_create_topo_ncl)
        utils.replace_str(
            fpath,
            {
                '<casename>': self.casename,
                '<input_topo-bath_filename>': path_topo,
            },
        )
        utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load ncl && ncl {fpath}', timeout=3)

    def gen_rawdata(self, lsm_path, topo_path=None, topo_vn='topo', lsm_vn='pft', org_vn='z_ORGANIC',
            path_csh=os.path.join(cwd, './src/lnd/run_paleo_mkraw_cesm1_template.csh'),
            path_f90=os.path.join(cwd, './src/lnd/paleo_mkraw_cesm1_sed.F90'),
            path_makefile=os.path.join(cwd, './src/lnd/Makefile'),
            path_soi='/glade/p/cesmdata/cseg/inputdata/lnd/clm2/rawdata/mksrf_soitex.10level.c010119.nc',
            path_org=os.path.join(cwd, './src/lnd/mksrf_zon_organic.10level.nc'),
            **qsub_kws,
            ):
        utils.p_header('>>> Generate land surface data ...')
        fpath_csh = utils.copy(path_csh, 'run_paleo_mkraw_cesm1.csh')
        fpath_f90 = utils.copy(path_f90, 'paleo_mkraw_cesm1_sed.F90')

        if topo_path is None:
            topo_path = f'./topo.{self.res}deg.{self.casename}.nc'

        utils.replace_str(
            fpath_csh,
            {
                '<casename>': self.casename,
                '<lsm_file>': os.path.abspath(lsm_path),
                '<topo-bath_file>': os.path.abspath(topo_path),
                'set INPUT_SOI_DATA = /glade/p/cesmdata/cseg/inputdata/lnd/clm2/rawdata/mksrf_soitex.10level.c010119.nc': 'set INPUT_SOI_DATA = mksrf_soi.nc',
                'set INPUT_ORG_DATA = mksrf_zon_organic.10level.nc': 'set INPUT_ORG_DATA = mksrf_org.nc',
            },
        )

        if self.res == '0.5x0.5':
            nlat, nlon = 360, 720
        elif self.res == '1x1':
            nlat, nlon = 180, 360
        elif self.res == '2x2':
            nlat, nlon = 90, 180

        utils.replace_str(
            fpath_f90,
            {
                'integer, parameter :: nlon = 180': f'integer, parameter :: nlon = {nlon}', 
                'integer, parameter :: nlat = 90': f'integer, parameter :: nlat = {nlat}', 
                "call wrap_inq_varid (ncid_sur_i, 'SUR', sur_id   )": f"call wrap_inq_varid (ncid_sur_i, '{lsm_vn}', sur_id)",
                "call wrap_inq_varid (ncid_top_i, 'topo', top_id   )": f"call wrap_inq_varid (ncid_top_i, '{topo_vn}', top_id)",
                "call wrap_inq_varid (ncid_organic, 'z_ORGANIC', z_organic_id   )": f"call wrap_inq_varid (ncid_organic, '{org_vn}', z_organic_id)",
            },
        )

        utils.copy(path_makefile)
        utils.copy(path_org, 'mksrf_org.nc')
        utils.copy(path_soi, 'mksrf_soi.nc')
        utils.run_shell(f'chmod +x {fpath_csh}')
        utils.qsub_script(
            fpath_csh,
            name='paleo_mkraw_cesm1', account=self.account, **qsub_kws,
        )

    def gen_scrip(self, lanwat_file, path_ncl=os.path.join(cwd, './src/lnd/mkscripgrid_template.ncl')):
        utils.p_header('>>> Create the SCRIP grid ...')
        fpath_ncl = utils.copy(path_ncl, 'mkscripgrid.ncl')
        utils.replace_str(
            fpath_ncl,
            {
                '<casename>': self.casename,
                '<lanwat_file>': lanwat_file,
            },
        )
        utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load ncl && ncl {fpath_ncl}', timeout=3)
    
    def gen_mapping(self, lnd_grid, atm_grid, path_sh=os.path.join(cwd, './src/cime_mapping/create_ESMF_map.sh'), **qsub_kws):
        utils.p_header('>>> Create the mapping file ...')
        fpath_sh = utils.copy(path_sh)
        utils.p_header(f'>>> Creating river->atmosphere(land) mapping files')
        atm_grid_name, atm_scrip  = list(atm_grid.keys())[0], list(atm_grid.values())[0]
        lnd_grid_name, lnd_scrip  = list(lnd_grid.keys())[0], list(lnd_grid.values())[0]
        utils.qsub_script(
            fpath_sh,
            args=f'-fsrc {lnd_scrip} -nsrc {lnd_grid_name} -fdst {atm_scrip} -ndst {atm_grid_name} -map aave',
            name='mapping_lnd2atm', account=self.account, **qsub_kws,
        )
    
    def gen_surfdata(self, mapping_file, out_res,
                   mksrf_files_date=None,
                   mksrf_landuse_file=None,
                   mksrf_lai_file=None,
                   mksrf_soicol_file=None,
                   mksrf_soitex_file=None,
                   mksrf_organic_file=None,
                   mksrf_lanwat_file=None,
                   mksrf_fmax_file=None,
                   mksrf_glacier_file=None,
                   mksrf_vocef_file=None,
                   mksrf_topo_file=None,
                   mksrf_urban_file=None,
                   path_exe=None,
                   path_namelist=os.path.join(cwd, './src/lnd/mksurfdata_map.namelist.paleo')):
        utils.p_header('>>> Complete the land surface dataset ...')
        path_exe=os.path.join(cwd, f'./src/lnd/mksurfdata_map_src/mksurfdata_map_{self.hostname}') if path_exe is None else path_exe
        fpath_exe = utils.copy(path_exe)
        utils.run_shell(f'chmod +x {fpath_exe}')
        fpath_namelist = utils.copy(path_namelist)

        if mksrf_files_date is not None:
            mksrf_landuse_file=f'mksrf_landuse_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_lai_file=f'mksrf_lai_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_soicol_file=f'mksrf_soicol_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_soitex_file=f'mksrf_soitex_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_organic_file=f'mksrf_organic_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_lanwat_file=f'mksrf_lanwat_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_fmax_file=f'mksrf_fmax_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_glacier_file=f'mksrf_glacier_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_vocef_file=f'mksrf_vocef_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_topo_file=f'mksrf_topo_{self.casename}.c{mksrf_files_date}.nc'
            mksrf_urban_file=f'mksrf_urban_{self.casename}.c{mksrf_files_date}.nc'
            
        date_today = date.today().strftime('%y%m%d')
        utils.replace_str(
            fpath_namelist,
            {
                '<mapping_file>': mapping_file,
                '<mksrf_landuse_file>': mksrf_landuse_file,
                '<mksrf_lai_file>': mksrf_lai_file,
                '<mksrf_soicol_file>': mksrf_soicol_file,
                '<mksrf_soitex_file>': mksrf_soitex_file,
                '<mksrf_organic_file>': mksrf_organic_file,
                '<mksrf_lanwat_file>': mksrf_lanwat_file,
                '<mksrf_fmax_file>': mksrf_fmax_file,
                '<mksrf_glacier_file>': mksrf_glacier_file,
                '<mksrf_vocef_file>': mksrf_vocef_file,
                '<mksrf_topo_file>': mksrf_topo_file,
                '<mksrf_urban_file>': mksrf_urban_file,
                '<out_res>': out_res,
                '<casename>': self.casename,
                '<date>': date_today,
            },
        )
        utils.exec_script(fpath_exe, args=f'< {fpath_namelist}')

    def interpic(self, template, input_field, output_fname=None, exe_path=os.path.join(cwd, './src/interpic/interpic_lnd')):
        utils.p_header('>>> Interpolate the input land surface data based on the given template ...')
        fpath_exe = utils.copy(exe_path, 'interpic_lnd')
        if output_fname is None: output_fname = os.path.basename(input_field)
        fpath_out = utils.copy(template, output_fname)
        utils.exec_script(fpath_exe, args=f'-i {input_field} -o {fpath_out}')

    def clean(self):
        utils.run_shell(f'rm -rf PET*.Log *paleo_mkraw* Makefile pathnames.sed mksrf_org.nc mksrf_soi.nc core mkscripgrid.ncl create-topo_*deg.ncl pbs_mapping_lnd2atm.zsh mapping_lnd2atm.*')
        