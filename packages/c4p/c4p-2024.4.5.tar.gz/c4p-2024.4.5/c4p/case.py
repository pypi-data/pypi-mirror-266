import os
import shutil
from datetime import date
import platform
import pandas as pd

from . import utils
from .rof import ROF
from .ocn import OCN
from .lnd import LND
from .atm import ATM
from .mapping import Mapping

cwd = os.path.dirname(__file__)

class PaleoSetup:
    def __init__(self, casename=None, work_dirpath=None, account=None, netcdf_lib_path=None, netcdf_inc_path=None, clean_old=False):
        self.casename = casename
        self.account = account
        self.work_dirpath = work_dirpath

        hostname = platform.node()
        if hostname[:7] == 'derecho':
            self.hostname = 'derecho'
        elif hostname[:8] == 'cheyenne':
            self.hostname = 'cheyenne'
        elif hostname[:6] == 'casper':
            self.hostname = 'casper'
        else:
            utils.p_warning(f'Unknown hostname: {hostname}')

        if netcdf_lib_path is None:
            if self.hostname == 'derecho':
                self.netcdf_lib_path = '/glade/u/apps/derecho/23.06/spack/opt/spack/netcdf/4.9.2/oneapi/2023.0.0/iijr/lib'
            elif self.hostname == 'cheyenne':
                self.netcdf_lib_path = '/glade/u/apps/ch/opt/netcdf/4.8.1/intel/19.1.1/lib'

        if netcdf_inc_path is None:
            if self.hostname == 'derecho':
                self.netcdf_inc_path = '/glade/u/apps/derecho/23.06/spack/opt/spack/netcdf/4.9.2/oneapi/2023.0.0/iijr/include'
            elif self.hostname == 'cheyenne':
                self.netcdf_inc_path = '/glade/u/apps/ch/opt/netcdf/4.8.1/intel/19.1.1/include'

        if clean_old:
            shutil.rmtree(work_dirpath) if os.path.exists(work_dirpath) else None

        if not os.path.exists(work_dirpath):
            os.makedirs(work_dirpath, exist_ok=True)
            utils.p_success(f'>>> {work_dirpath} created')

        os.chdir(work_dirpath)
        utils.p_success(f'>>> Current directory switched to: {work_dirpath}')

    def mapping(self, atm_grid, ocn_grid, rof_grid, gen_cesm_maps_script=None, gen_esmf_map_script=None, gen_domain_exe=None):
        return Mapping(
            atm_grid=atm_grid, ocn_grid=ocn_grid, rof_grid=rof_grid,
            gen_cesm_maps_script=gen_cesm_maps_script,
            gen_esmf_map_script=gen_esmf_map_script,
            gen_domain_exe=gen_domain_exe, **self.__dict__,
        )

    def setup_rof(self):
        return ROF(**self.__dict__)

    def setup_ocn(self):
        return OCN(**self.__dict__)

    def setup_lnd(self):
        return LND(**self.__dict__)

    def setup_atm(self):
        return ATM(**self.__dict__)

class CESMCase: 
    def __init__(self,
        account=None, casename=None, codebase=None,
        res=None, mach=None, compset=None,
        case_root=None, output_root=None, clean_old=False,
        notebook_dirpath=None,
    ):
        self.account = account
        self.casename = casename
        self.res = res
        self.mach = 'derecho' if mach is None else mach
        self.compset = compset
        self.codebase = codebase
        self.case_dirpath = os.path.join(case_root, casename)
        self.output_root = output_root
        self.output_dirpath = os.path.join(output_root, casename)
        self.notebook_dirpath = os.getcwd()

        for k, v in self.__dict__.items():
            utils.p_success(f'>>> CESMCase.{k}: {v}')

        if clean_old:
            shutil.rmtree(self.case_dirpath) if os.path.exists(self.case_dirpath) else None
            shutil.rmtree(self.output_dirpath) if os.path.exists(self.output_dirpath) else None

    def create(self, run_unsupported=False, path_fix='cime'):
        if path_fix == 'cime':
            cmd = f'{self.codebase}/cime/scripts/create_newcase --case {self.case_dirpath} --res {self.res} --compset {self.compset} --mach {self.mach} --output-root {self.output_root}'
        else:
            cmd = f'{self.codebase}/scripts/create_newcase --case {self.case_dirpath} --res {self.res} --compset {self.compset} --mach {self.mach} --output-root {self.output_root}'
        if run_unsupported:
            cmd += ' --run-unsupported'

        os.environ['PROJECT'] = self.account
        utils.run_shell(cmd)

        os.chdir(self.case_dirpath)
        utils.p_success(f'>>> Current directory switched to: {self.case_dirpath}')

    def xmlquery(self, string):
        utils.run_shell(f'./xmlquery -p {string}')

    def xmlchange(self, modification_dict):
        for k, v in modification_dict.items():
            utils.run_shell(f'./xmlchange {k}={v}')

    def setup(self):
        utils.run_shell('./case.setup')

    def build(self, clean=False, **qcmd_kws):
        cmd = './case.build'
        if clean:
            cmd += ' --clean'
            utils.run_shell(cmd)
        else:
            utils.qcmd_script(cmd, account=self.account, **qcmd_kws)

    def submit(self):
        utils.run_shell('./case.submit')

    def preview_run(self):
        utils.run_shell('./preview_run')

    def preview_namelists(self):
        utils.run_shell('./preview_namelists')

    def write_file(self, fname, content=None, mode='w'):
        utils.write_file(fname=fname, content=content, mode=mode)

    def set_paths(self, atm_domain=None, lnd_domain=None, ocn_domain=None, ice_domain=None,
                  atm2ocn_fmap=None, atm2ocn_smap=None, atm2ocn_vmap=None,
                  ocn2atm_fmap=None, ocn2atm_smap=None,
                  lnd2rof_fmap=None,
                  rof2lnd_fmap=None,
                  rof2ocn_fmap=None, rof2ocn_rmap=None):
        if atm_domain is not None: self.xmlchange({'ATM_DOMAIN_PATH': os.path.dirname(atm_domain), 'ATM_DOMAIN_FILE': os.path.basename(atm_domain)})
        if lnd_domain is not None: self.xmlchange({'LND_DOMAIN_PATH': os.path.dirname(lnd_domain), 'LND_DOMAIN_FILE': os.path.basename(lnd_domain)})
        if ocn_domain is not None: self.xmlchange({'OCN_DOMAIN_PATH': os.path.dirname(ocn_domain), 'OCN_DOMAIN_FILE': os.path.basename(ocn_domain)})
        if ice_domain is not None: self.xmlchange({'ICE_DOMAIN_PATH': os.path.dirname(ice_domain), 'ICE_DOMAIN_FILE': os.path.basename(ice_domain)})
        if atm2ocn_fmap is not None: self.xmlchange({'ATM2OCN_FMAPNAME': atm2ocn_fmap})
        if atm2ocn_smap is not None: self.xmlchange({'ATM2OCN_SMAPNAME': atm2ocn_smap})
        if atm2ocn_vmap is not None: self.xmlchange({'ATM2OCN_VMAPNAME': atm2ocn_vmap})
        if ocn2atm_fmap is not None: self.xmlchange({'OCN2ATM_FMAPNAME': ocn2atm_fmap})
        if ocn2atm_smap is not None: self.xmlchange({'OCN2ATM_SMAPNAME': ocn2atm_smap})
        if lnd2rof_fmap is not None: self.xmlchange({'LND2ROF_FMAPNAME': lnd2rof_fmap})
        if rof2lnd_fmap is not None: self.xmlchange({'ROF2LND_FMAPNAME': rof2lnd_fmap})
        if rof2ocn_fmap is not None: self.xmlchange({'ROF2OCN_FMAPNAME': rof2ocn_fmap})
        if rof2ocn_rmap is not None: self.xmlchange({'ROF2OCN_RMAPNAME': rof2ocn_rmap})

    def replace_file(self, fname, path):
        utils.copy(path, os.path.join(self.case_dirpath, fname))
        utils.p_success(f'>>> {fname} replaced with: {path}')


    def add_mod(self, component, mod_path):
        target_dir = os.path.join(self.case_dirpath, 'SourceMods', f'src.{component}')
        utils.copy(mod_path, target_dir)
        utils.p_success(f'>>> Copy {mod_path} to: {target_dir}')

    def summary(self, exp_id=None, save_path=None,
                atm_nml=['co2vmr', 'cldfrc_rhminl', 'micro_mg_dcs', 'dust_emis_fact'],
                pop_nml=['dt_count'],
                ):
        exp_id = '001' if exp_id is None else exp_id

        # basics
        df = pd.DataFrame.from_dict(self.__dict__, orient='index', columns=[exp_id])

        # paths for mapping and domain files
        path_env_run_xml = os.path.join(self.case_dirpath, 'env_run.xml') 
        for entry in ['atm_domain', 'lnd_domain', 'ocn_domain', 'ice_domain']:
            path_tmp = utils.parse_xml(path_env_run_xml, f'{str.upper(entry)}_PATH')
            file_tmp = utils.parse_xml(path_env_run_xml, f'{str.upper(entry)}_FILE')
            df.loc[entry] = os.path.join(list(path_tmp.values())[0], list(file_tmp.values())[0])

        for entry in ['atm2ocn_fmap', 'atm2ocn_smap', 'atm2ocn_vmap',
                      'ocn2atm_fmap', 'ocn2atm_smap',
                      'lnd2rof_fmap',
                      'rof2lnd_fmap', 'rof2ocn_fmap', 'rof2ocn_rmap']:
            path_tmp = utils.parse_xml(path_env_run_xml, f'{str.upper(entry)}NAME')
            df.loc[entry] = list(path_tmp.values())[0]

        # namelists
        path_nml = os.path.join(self.case_dirpath, 'CaseDocs/atm_in') 
        for entry in atm_nml:
            df.loc[f'atm: {entry}'] = utils.parse_nml(path_nml, entry)[entry]

        path_nml = os.path.join(self.case_dirpath, 'CaseDocs/pop_in') 
        for entry in pop_nml:
            df.loc[f'pop: {entry}'] = utils.parse_nml(path_nml, entry)[entry]
                    

        save_path = os.path.join(self.notebook_dirpath, f'summary_{exp_id}.csv') if save_path is None else save_path
        df.to_csv(save_path)
        utils.p_success(f'>>> Summary report saved to: {os.path.abspath(save_path)}')

        return df