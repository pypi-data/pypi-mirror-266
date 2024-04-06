import os, glob
import numpy as np
from IPython.display import display, Image, IFrame
from datetime import date
import xarray as xr

from . import utils

cwd = os.path.dirname(__file__)

class ATM:
    def __init__(self, grids_dirpath=None, gen_esmf_map_script=None, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.grids_dirpath='/glade/p/cesmdata/inputdata/share/scripgrids' if grids_dirpath is None else grids_dirpath
        self.gen_esmf_map_script=os.path.join(cwd, './src/rof/create_ESMF_map.sh') if gen_esmf_map_script is None else gen_esmf_map_script
        self.configs = {}

        for k, v in self.__dict__.items():
            utils.p_success(f'>>> ATM.{k}: {v}')

    def gen_topo(self, path_topo, path_mk_10min_topo_ncl=os.path.join(cwd, './src/atm/mk_10min_definesurf_input_paleo.ncl')):
        utils.p_header('>>> Create a 10min topographic file ...')
        fpath_ncl = utils.copy(path_mk_10min_topo_ncl, 'mk_ocninput.ncl')
        utils.replace_str(
            fpath_ncl,
            {
                '<casename>': self.casename,
                '<directory_with_topo-bath_file>': os.path.dirname(path_topo),
                '<topo-bath_file>': os.path.basename(path_topo),
            },
        )
        utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load ncl && ncl {fpath_ncl}', timeout=3)

    def regrid_topo(self, src_grid, dst_grid, src_topo, dst_topo):
        src_grid_name, src_scrip  = list(src_grid.keys())[0], list(src_grid.values())[0]
        dst_grid_name, dst_scrip  = list(dst_grid.keys())[0], list(dst_grid.values())[0]
        utils.p_header(f'>>> Generate mapping from {src_grid_name} to {dst_grid_name} ...')
        utils.exec_script(
            self.gen_esmf_map_script,
            args=f'-fsrc {src_scrip} -nsrc {src_grid_name} -fdst {dst_scrip} -ndst {dst_grid_name} -map blin',
        )
        meta_date=date.today().strftime('%y%m%d')
        utils.p_header(f'>>> Interpolate data from {src_grid_name} to {dst_grid_name} ...')
        utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load nco && ncremap -t 1 -m ./map_{src_grid_name}_TO_{dst_grid_name}_blin.{meta_date}.nc {src_topo} {dst_topo}')
        

    def gen_boundary(self):
        utils.p_header('>>> Create boundary dataset for topography fields ...')
        # TODO
        # Step 29, 30

    def gen_solar_forcing(self):
        utils.p_header('>>> Create solar forcing file ...')
        # TODO
        # Step 31

    def gen_aerosol(self):
        utils.p_header('>>> Customize aerosol settings ...')
        # TODO
        # Step 32

    def interpic(self, template, input_field, output_field, exe_path=os.path.join(cwd, './src/interpic/interpic_atm')):
        utils.p_header('>>> Interpolate the input atmosphere IC based on the given template ...')
        fpath_exe = utils.copy(exe_path, 'interpic_atm')
        utils.exec_script(fpath_exe, args=f'-t {template} {input_field} {output_field}')
