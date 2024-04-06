import os
import numpy as np
from IPython.display import display, Image
from datetime import date
import xarray as xr

from . import utils

cwd = os.path.dirname(__file__)

class ROF:
    def __init__(self, grids_dirpath=None, path_create_ESMF_map_sh=None, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.grids_dirpath='/glade/p/cesmdata/inputdata/share/scripgrids' if grids_dirpath is None else grids_dirpath
        self.path_create_ESMF_map_sh=os.path.join(cwd, './src/rof/create_ESMF_map.sh') if path_create_ESMF_map_sh is None else path_create_ESMF_map_sh

        for k, v in self.__dict__.items():
            utils.p_success(f'>>> ROF.{k}: {v}')
        
    def prep_topo(self, path_topo, res='1x1', path_create_topo_ncl=None):
        # Step 19
        utils.p_header('>>> Prep topo file at proper resolution ...')
        self.topo_path = path_topo
        utils.p_success(f'>>> ROF.topo_path = "{path_topo}"')

        if path_create_topo_ncl is None:
            path_create_topo_ncl = os.path.join(cwd, f'./src/rof/create-topo_{res}deg.ncl')

        fpath = utils.copy(path_create_topo_ncl)
        utils.replace_str(
            fpath,
            {
                '<casename>': self.casename,
                '<input_topo-bath_filename>': self.topo_path,
            },
        )
        utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load ncl && ncl {fpath}', timeout=3)

    def gen_rof(self,
            path_rdirc_template_csh=os.path.join(cwd, './src/rof/rdirc_template.csh'),
            path_topo2rdirc_sed_f90=os.path.join(cwd, './src/rof/topo2rdirc_sed.F90'),
            path_Makefile=os.path.join(cwd, './src/rof/Makefile'),
        ):
        # Step 20
        utils.p_header('>>> Generate runoff data from topo inputs ...')
        fpath_new = utils.copy(path_rdirc_template_csh, f'./rdirc_{self.casename}.csh')
        utils.replace_str(
            fpath_new,
            {
                '<casename>': self.casename,
                '<path/topography-bathymetry_file>': f'topo.1x1deg.{self.casename}.nc',
            },
        )

        fpath = utils.copy(path_topo2rdirc_sed_f90)
        utils.replace_str(
            fpath,
            {
                'pause': 'WRITE(*, *)',  # to avoid the prompts
            },
        )

        fpath = utils.copy(path_Makefile)
        utils.replace_str(
            fpath,
            {
                'LIB_NETCDF = -L/glade/apps/opt/netcdf/4.2/intel/default/lib -lnetcdf': f'LIB_NETCDF = -L{self.netcdf_lib_path} -lnetcdff',
                'INC_NETCDF = -I/glade/apps/opt/netcdf/4.2/intel/default/include': f'INC_NETCDF = -I{self.netcdf_inc_path}',
            },
        )
        utils.run_shell(f'chmod +x {fpath_new}')
        utils.exec_script(fpath_new)

    def plot_rof(self,
            path_plotrdirc_csh=os.path.join(cwd, './src/rof/plotrdirc.csh'),
            path_plotrdirc_ncl=os.path.join(cwd, './src/rof/plot_rdirc.ncl'),
        ):
        # Step 21
        utils.p_header('>>> Plot runoff ...')
        fpath = utils.copy(path_plotrdirc_csh)
        utils.replace_str(
            fpath,
            {
                '<casename>': self.casename,
                '<topography-bathymetry_file>': os.path.basename(self.topo_path),
            },
        )
        utils.copy(path_plotrdirc_ncl)
        utils.run_shell(f'chmod +x {fpath}')
        utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load ncl && {fpath}', timeout=3)
        display(
            Image(f'./rdirc_{os.path.basename(self.topo_path)}.png')
        )

    def rof2nc(self, input=None, output=None, res='1x1',
                  meta_user='Feng Zhu', meta_date=date.today().strftime('%Y%m%d')):
        input = f'fort.13_{self.casename}' if input is None else input
        output = f'rdirc.{res}.{self.casename}.nc' if output is None else output
        # Step 24
        utils.p_header(f'>>> Convert runoff file [{input}] to netcdf file [{output}] ...')

        with open(input, 'r') as f:
            data = np.loadtxt(f)

        rtm_lat = data[:, 0]
        rtm_lon = data[:, 1]
        rdir = data[:, 2]

        if res == '0.5x0.5':
            im0 = 720
            jm0 = 360
        elif res == '1x1':
            im0 = 360
            jm0 = 180
        elif res == '2x2':
            im0 = 180
            jm0 = 90

        # Create xarray dataset
        ds = xr.Dataset()

        ds['RTM_FLOW_DIRECTION'] = (['nj', 'ni'], rdir.reshape(jm0, im0))
        ds['xc'] = (['nj', 'ni'], rtm_lon.reshape(jm0, im0))
        ds['yc'] = (['nj', 'ni'], rtm_lat.reshape(jm0, im0))

        ds['RTM_FLOW_DIRECTION'].attrs['long_name'] = 'RTM flow direction'
        ds['RTM_FLOW_DIRECTION'].attrs['units'] = 'unitless'
        ds['RTM_FLOW_DIRECTION'].attrs['mode'] = 'time-invariant'
        ds['RTM_FLOW_DIRECTION'].attrs['comment'] = 'N,NE,E,SE,S,SW,W,NW = 1,2,3,4,5,6,7,8'

        ds['xc'].attrs['long_name'] = 'longitude of grid cell center'
        ds['xc'].attrs['units'] = 'degrees_east'
        ds['xc'].attrs['mode'] = 'time-invariant'

        ds['yc'].attrs['long_name'] = 'latitude of grid cell center'
        ds['yc'].attrs['units'] = 'degrees_north'
        ds['yc'].attrs['mode'] = 'time-invariant'

        ds.attrs['title'] = 'River Transport Model (RTM) flow directions'
        ds.attrs['conventions'] = 'CF-1.0'
        ds.attrs['SVD_ID'] = 'none'
        ds.attrs['SVN_URL'] = 'none'
        ds.attrs['history'] = f'created by {meta_user} {meta_date}'
        ds.attrs['source'] = input

        # Save dataset to netCDF file
        ds.to_netcdf(output)

    def rof2ocn_p1(self, ocn_scrp_path,
            path_runoff_map=os.path.join(cwd, './src/rof/runoff_map_1deg'),
            path_runoff_map_template_nml=os.path.join(cwd, './src/rof/runoff_map.1x1.template.nml'),
            meta_date=date.today().strftime('%Y%m%d'),
            ocnres=None,
        ):
        # Step 25
        utils.p_header('>>> Create runoff to ocean mapping file (part 1) ...')
        os.environ['ESMFBIN_PATH'] = self.esmfbin_path
        ocnres = f'gx1{self.casename}' if ocnres is None else ocnres
        fpath = utils.copy(path_runoff_map)
        fpath_new = utils.copy(path_runoff_map_template_nml,  f'./runoff_map.1x1.{self.casename}.nml')
        utils.replace_str(
            fpath_new,
            {
                '<casename>': self.casename,
                './<SCRIP_mapping_file>': ocn_scrp_path,
                '<ocnres>': ocnres,
                '<date>': meta_date,
            },
        )
        utils.run_shell(f'ln -s {fpath_new} ./runoff_map.nml')
        utils.exec_script(fpath)
        self.ocn_scrp_path = ocn_scrp_path

    def rof2ocn_p2(self, fsrc_fname='1x1d.nc'):
        # Step 26
        utils.p_header('>>> Create runoff to ocean mapping file (part 2) ...')
        fpath = utils.copy(self.path_create_ESMF_map_sh)
        ocnres = f'gx1{self.casename}'
        fsrc = os.path.join(self.grids_dirpath, fsrc_fname)
        fdst = self.ocn_scrp_path
        utils.exec_script(fpath, args=f'-fsrc {fsrc} -nsrc r1_nomask -fdst {fdst} -ndst {ocnres} -map aave')

    def rof2lnd(self, fsrc_fname='fv1.9x2.5_141008.nc', fdst_fname='1x1d_lonshift.nc'):
        # Step 27
        utils.p_header('>>> Create runoff to land mapping files - needed if rof at 1deg rather than 0.5 deg ...')
        fpath = utils.copy(self.path_create_ESMF_map_sh)
        fsrc = os.path.join(self.grids_dirpath, fsrc_fname)
        fdst = os.path.join(self.grids_dirpath, fdst_fname)
        utils.exec_script(fpath, args=f'-fsrc {fsrc} -nsrc r19_nomask -fdst {fdst} -ndst r1x1 -map aave')

    def lnd2rof(self, fsrc_fname='1x1d_lonshift.nc', fdst_fname='fv1.9x2.5_141008.nc'):
        # Step 27
        utils.p_header('>>> Create land to runoff mapping files - needed if rof at 1deg rather than 0.5 deg ...')
        fpath = utils.copy(self.path_create_ESMF_map_sh)
        fsrc = os.path.join(self.grids_dirpath, fsrc_fname)
        fdst = os.path.join(self.grids_dirpath, fdst_fname)
        utils.exec_script(fpath, args=f'-fsrc {fsrc} -nsrc r19_nomask -fdst {fdst} -ndst r1x1 -map aave')

    def gen_rmap(self, ocn_grid, rdirc_grid=None, rof_grid_name=None, res='1deg', qsub=True, rdirc_ascii=None, **qsub_kws):
        if rdirc_grid is not None:
            rof_grid_name, rdirc_ascii = list(rdirc_grid.keys())[0], list(rdirc_grid.values())[0]

        rdirc_ascii = f'fort.13_{self.casename}' if rdirc_ascii is None else rdirc_ascii
        rof2ocn_exe = os.path.join(cwd, f'./src/rof/runoff_map_{res}')
        utils.p_header(f'>>> Creating ROF2OCN_RMAP file')
        ocn_grid_name, ocn_scrip  = list(ocn_grid.keys())[0], list(ocn_grid.values())[0]
        date_today = date.today().strftime('%y%m%d')
        fpath = utils.copy(rof2ocn_exe)
        utils.write_file(f'runoff_map.nml', f'''
        &input_nml
         gridtype     = 'rtm'
         file_roff    = '{rdirc_ascii}'
         file_ocn     = '{ocn_scrip}'
         file_nn      = 'map_{rof_grid_name}_to_{ocn_grid_name}_nn.{date_today}.nc'
         file_smooth  = 'map_{rof_grid_name}_to_{ocn_grid_name}_sm_e1000r300.{date_today}.nc'
         file_new     = 'map_{rof_grid_name}_to_{ocn_grid_name}_nnsm_e1000r300.{date_today}.nc'
         title        = 'runoff map: {rof_grid_name} -> {ocn_grid_name}, nearest neighbor and smoothed'
         eFold        = 1000000.0
         rMax         =  300000.0
         step1 = .true.
         step2 = .true.
         step3 = .true.
        /
        ''')
        utils.run_shell(f'chmod +x {fpath}')
        if qsub:
            utils.qsub_script(f'{fpath} < runoff_map.nml', name='gen_rmap', account=self.account, **qsub_kws)
        else:
            utils.exec_script(f'{fpath} < runoff_map.nml')

    def clean(self):
        utils.run_shell(f'rm -rf fort.*_{self.casename} *.F90 *.ncl gen_rmap* Makefile *.sed *.zsh *.csh runoff_map* topo*')