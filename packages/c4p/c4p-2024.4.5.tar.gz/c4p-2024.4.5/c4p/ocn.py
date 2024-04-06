import os, glob
import numpy as np
from IPython.display import display, Image, IFrame
from datetime import date
import xarray as xr

from . import utils

cwd = os.path.dirname(__file__)

class OCN:
    def __init__(self, grids_dirpath=None, path_create_ESMF_map_sh=None, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.grids_dirpath='/glade/p/cesmdata/inputdata/share/scripgrids' if grids_dirpath is None else grids_dirpath
        self.path_create_ESMF_map_sh=os.path.join(cwd, './src/rof/create_ESMF_map.sh') if path_create_ESMF_map_sh is None else path_create_ESMF_map_sh
        self.configs = {}

        for k, v in self.__dict__.items():
            utils.p_success(f'>>> OCN.{k}: {v}')

    def create_ocn_grid(self, path_topo, iter=1, lonnp=None, lonsp=None, latnp=None, latsp=None, jcon=None,
            path_vertical_grid=os.path.join(cwd, './src/ocn/gx1v6_vert_grid'),
            path_mk_grid=os.path.join(cwd, './src/ocn/mk_ocn_grid/mk_grid_1x1_template.csh'),
            path_ns_dipole_exe=os.path.join(cwd, './src/ocn/mk_ocn_grid/ns_dipole'),
            path_paleotopo_exe=os.path.join(cwd, './src/ocn/mk_ocn_grid/paleotopo'),
            path_grid_bin2nc_exe=os.path.join(cwd, './src/ocn/mk_ocn_grid/grid_bin2nc'),
        ):
        utils.p_header('>>> Create ocean grid files ...')
        for path_exe in [path_ns_dipole_exe, path_paleotopo_exe, path_grid_bin2nc_exe]:
            fpath_exe = utils.copy(path_exe)
            utils.run_shell(f'chmod +x {fpath_exe}')

        self.configs['iter'] = iter

        fpath = utils.copy(path_mk_grid, 'mk_grid.csh')
        utils.replace_str(
            fpath,
            {
                '<casename>': self.casename,
                'ITER   = 1': f'ITER = {iter}',
                '<path_to_topo_file>': os.path.dirname(path_topo),
                '<topo-bath_file>': os.path.basename(path_topo),
                '<path_to_vrtgrid_file>': os.path.dirname(path_vertical_grid),
                '<vertical_grid_file>': os.path.basename(path_vertical_grid),
            },
        )
        if lonnp is not None:
            utils.replace_str(
                fpath,
                {
                    'lonnp   =   50.': f'lonnp = {lonnp}',
                }
            )
        if latnp is not None:
            utils.replace_str(
                fpath,
                {
                    'latnp   =   75.': f'latnp = {latnp}',
                }
            )
        if lonsp is not None:
            utils.replace_str(
                fpath,
                {
                    'lonsp   =   50.': f'lonsp = {lonsp}',
                }
            )
        if latsp is not None:
            utils.replace_str(
                fpath,
                {
                    'latsp   =   -69.': f'latsp = {latsp}',
                }
            )
        if jcon is not None:
            utils.replace_str(
                fpath,
                {
                    'jcon   =   11': f'jcon = {jcon}',
                }
            )

        utils.exec_script(fpath)

    def create_scrip(self,
            path_mk_scrip=os.path.join(cwd, './src/ocn/mk_ocn_grid/mk_SCRIPgrid_template.csh'),
            path_convertPOPT_exe=os.path.join(cwd, './src/ocn/mk_ocn_grid/myconvertPOPT')
        ):
        utils.p_header('>>> Create SCRIP mapping file ...')
        fpath = utils.copy(path_mk_scrip, 'mk_scrip.csh')
        fpath_exe = utils.copy(path_convertPOPT_exe)
        utils.run_shell(f'chmod +x {fpath}')
        utils.run_shell(f'chmod +x {fpath_exe}')

        utils.replace_str(
            fpath,
            {
                'popgriddir = <workspace>': f'popgriddir = {self.work_dirpath}',
                'scripdir   = <workspace>': f'scripdir   = {self.work_dirpath}',
                '<iter>': f'{self.configs["iter"]}',
                '<gridname>': self.casename,
                '<case>': self.casename,
            },
        )
        utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load nco && {fpath}')

    def plot_reg_diag(self,
            path_plot_global_all_ncl=os.path.join(cwd, './src/ocn/mk_ocn_grid/plot_global_all.ncl'),
        ):
        utils.p_header('>>> Create regional diagnostic plots ...')
        fpath_ncl = utils.copy(path_plot_global_all_ncl)
        ocnres = f'gx1{self.casename}'
        datestr = date.today().strftime('%y%m%d')
        for pt in ['sp', 'np', 'q1', 'q2', 'q3', 'q4']:
            args = f"'space=20' 'type=\"reg\"' 'expt=\"{ocnres}\"' 'plot_type=\"{pt}\"' 'date=\"{datestr}\"'"
            utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load ncl && ncl {args} {fpath_ncl}', timeout=5)

        fig_paths = sorted(glob.glob('*.pdf'))
        for path in fig_paths:
            utils.run_shell(f'convert {path} {path}.png')
            display(Image(f'{path}.png'))

    def gen_region_mask_transports(self, iter=1,
            path_mk_ocninput_csh=os.path.join(cwd, './src/ocn/mk_ocninput/mk_ocninput_template.csh'),
            path_modregmsk_edit_f=os.path.join(cwd, './src/ocn/mk_ocninput/modregmsk_edit.f'),
        ):
        utils.p_header('>>> Generate region mask and ocean transports ...')
        fpath_csh = utils.copy(path_mk_ocninput_csh, 'mk_ocninput.csh')
        fpath_f = utils.copy(path_modregmsk_edit_f)
        utils.replace_str(
            fpath_csh,
            {
                '<casename>': self.casename,
                '<iter>': iter,
            },
        )