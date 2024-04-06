import os
import pickle
import xarray as xr
import numpy as np
import pandas as pd
try:
    import pygplates
except:
    print('c4p warning: `pygplates` is not installed properly')
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

from . import utils

cwd = os.path.dirname(__file__)

class Rotation:
    def __init__(self, ds, lat_dn='nlat', lon_dn='nlon', lat_vn='TLAT', lon_vn='TLONG', rotation_file=None, polygon_file=None):
        self.ds = ds
        self.lat_dn = lat_dn
        self.lon_dn = lon_dn
        self.lat_vn = lat_vn
        self.lon_vn = lon_vn
        self.rotation_file = os.path.join(cwd, 'src/rotation/Muller2019-Young2019-Cao2020_CombinedRotations.rot') if rotation_file is None else rotation_file
        self.polygon_file = os.path.join(cwd, 'src/rotation/Global_EarthByte_GPlates_PresentDay_StaticPlatePolygons.gpmlz') if polygon_file is None else polygon_file

        self.lats = self.ds[self.lat_vn]
        self.lons = self.ds[self.lon_vn]
        if len(self.lats.shape) == 1:
            self.lons, self.lats = np.meshgrid(self.lons, self.lats)  # 1D -> 2D lats and lons
            
        if np.max(self.ds[self.lon_vn]) > 180:
            self.lons = (self.ds[self.lon_vn] + 180) % 360 - 180  # lon: (0, 360) -> (-180, 180)


    def recon(self, vn, t_ma=15):
        if not isinstance(vn, (list, tuple)):
            vn = [vn]
        
        self.vn = vn

        pt_features = []
        values_flat = []
        varnames = []
        for v in self.vn:
            if len(self.ds[v].dims) == 3:
                value_flat = self.ds[v].data.reshape(self.ds[v].shape[0], -1)
                for k in range(value_flat.shape[0]):
                    values_flat.append(value_flat[k])
                    varnames.append(f'{v}_{k}')
            elif len(self.ds[v].dims) == 2:
                value_flat = self.ds[v].data.flatten()
                values_flat.append(value_flat)
                varnames.append(v)
            else:
                raise ValueError(f'Cannot handle the case: len(self.ds[{v}].dims) = {len(self.ds[v].dims)}')

        values_flat = np.array(values_flat)
        
        for i, (lat, lon) in enumerate(zip(self.lats.data.flatten(), self.lons.data.flatten())):
            pt_feature = pygplates.Feature()
            pt_feature.set_geometry(pygplates.PointOnSphere(lat, lon))   # Note: we specify latitude first here! 
            for k in range(values_flat.shape[0]):
                pt_feature.set_shapefile_attribute(varnames[k], values_flat[k, i])
            pt_features.append(pt_feature)

        pt_features_cc = pygplates.partition_into_plates(
            self.polygon_file, self.rotation_file, 
            pt_features, properties_to_copy=[pygplates.PartitionProperty.reconstruction_plate_id],
        )

        recons = []
        pygplates.reconstruct(pt_features_cc, self.rotation_file, recons, t_ma)

        df = pd.DataFrame(index=range(len(recons)), columns=['pr_lat', 'pr_lon', 're_lat', 're_lon', *varnames])
        df['pr_lat'] =  [r.get_present_day_geometry().to_lat_lon()[0] for r in recons]
        df['pr_lon'] =  [r.get_present_day_geometry().to_lat_lon()[1] for r in recons]
        df['re_lat'] =  [r.get_reconstructed_geometry().to_lat_lon()[0] for r in recons]
        df['re_lon'] =  [r.get_reconstructed_geometry().to_lat_lon()[1] for r in recons]
        for v in varnames:
            df[v] = [r.get_feature().get_shapefile_attribute(v) for r in recons]

        self.df = df
        self.varnames = varnames
        utils.p_success('>>> Rotation.df created')
        utils.p_success('>>> Rotation.varnames created')

    def regrid(self, method='linear'):
        regrid_res = griddata((self.df['re_lat'], self.df['re_lon']), self.df[self.varnames], (self.lats.data, self.lons.data), method=method).reshape((len(self.ds[self.lat_dn]), len(self.ds[self.lon_dn]), -1))
        self.regrid_res = np.moveaxis(regrid_res, -1, 0)
        utils.p_success('>>> Rotation.regrid_res created')

        self.ds_rotate = xr.Dataset()
        k = 0
        for i, v in enumerate(self.vn):
            da_recon = self.ds[v].copy()
            if len(self.ds[v].dims) == 3:
                nz = self.ds[v].shape[0]
                da_recon.values = self.regrid_res[k:k+nz]
                k += nz
            elif len(self.ds[v].dims) == 2:
                da_recon.values = self.regrid_res[k]
                k += 1
            else:
                raise ValueError(f'Cannot handle the case: len(self.ds[{v}].dims) = {len(self.ds[v].dims)}')
            
            self.ds_rotate[v] = da_recon

        utils.p_success('>>> Rotation.ds_rotate created')

    def plot(self, vn, level=0, figsize=[8, 8]):
        fig, ax = plt.subplots(2, 1, figsize=figsize)

        if len(self.ds[vn].dims) == 2:
            self.ds[vn].plot(ax=ax[0])
            ax[0].set_title('Before Rotation')

            self.ds_rotate[vn].plot(ax=ax[1])
            ax[1].set_title('After Rotation')
        else:
            self.ds[vn][level].plot(ax=ax[0])
            ax[0].set_title('Before Rotation')

            self.ds_rotate[vn][level].plot(ax=ax[1])
            ax[1].set_title('After Rotation')

        fig.tight_layout()

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        