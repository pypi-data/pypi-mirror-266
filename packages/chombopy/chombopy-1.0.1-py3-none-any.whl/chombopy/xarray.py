import xarray as xr
from chombopy.plotting import PltFile
import numpy as np
from shapely.ops import cascaded_union
from shapely.geometry import Polygon
import geopandas as gpd
import math
from itertools import product
import matplotlib as mpl
import logging
import warnings
import matplotlib.cm as cm
import matplotlib.pyplot as plt

LOGGER = logging.getLogger(__name__)


def get_chombo_box_extent(box, space_dim):
    """

    Parse box extents from Chombo HDF5 files into low and high limits

    Parameters
    ----------
    box : List
        Chombo HDF5 format box limits,
        e.g. [x_lo, y_lo, x_hi, y_hi] = [0,0,1,1]

    space_dim : int
        Number of spatial dimensions

    Returns
    -------
    lo, hi : List
        Low and high limits, [x_lo, y_lo, ...], [x_hi, y_hi, ...]
        e.g [0,0], [1,1]

    """
    lo = [box[i] for i in range(space_dim)]
    hi = [box[i] for i in range(space_dim, 2 * space_dim)]
    return lo, hi


@xr.register_dataarray_accessor("amr")
class AMRDataArray(object):
    def __init__(self, xr_obj: xr.DataArray):
        self.obj = xr_obj

    def convert_names(self, level):
        data = self.obj
        keys = [data.name]
        return convert_names(self.obj, level, keys)

    # def remove_amr_indicators(self, level):
    #     data = self.obj
    #     keys = [data.name]
    #     return remove_amr_indicators(self.obj, level, keys)


@xr.register_dataset_accessor("amr")
class AMRDataset(object):
    def __init__(self, xr_obj: xr.Dataset):
        self.obj = xr_obj

    @property
    def num_levels(self):
        return self.obj.attrs["num_levels"]

    @property
    def space_dim(self):
        return self.obj.attrs["SpaceDim"]

    def get_dx(self, level):
        return self.obj.attrs["dx"][level]

    def get_ref_ratio(self, level):
        return self.obj.attrs["ref_ratio"][level]

    def get_components(self):
        return self.obj.attrs["components"]

    def get_boxes(self, level):
        return self.obj.attrs["boxes"][level]

    def get_dims(self):
        return self.obj.attrs["dims"]

    def get_amr_data(self, component, levels=None, valid_only=True):
        """
        Get dataset with all data for a component across all levels

        Parameters
        ----------
        component : str

        Returns
        -------
        amr_data : List[xarray.DataArray]
        """

        if levels is None:
            levels = self.get_levels()

        ds_levs = [
            self.get_level_data(component, level, valid_only)
            for level in levels
        ]

        return ds_levs

    def get_transect(self, component, transect, levels=None):
        if levels is None:
            levels = self.get_levels()

        x = xr.DataArray(transect["x"], dims="z")
        y = xr.DataArray(transect["y"], dims="z")
        d_0 = np.array([transect["x"][0], transect["y"][0]])

        ds_levs = self.get_amr_data(component, levels, valid_only=False)

        ds_transects = []
        for level in levels:
            level_transect = ds_levs[level].interp(x=x, y=y).drop(("i", "j"))

            # Get transect coords as (x,y) pairs and compute distance along line
            transect_coords = np.array([level_transect.coords["x"], level_transect.coords["y"]]).transpose()
            dist = [np.linalg.norm(d-d_0) for d in transect_coords]
            level_transect.coords["z"] = dist

            ds_transects.append(level_transect)

        merged = xr.merge(ds_transects, compat='override')

        return merged[component]


    def get_grid(self, level, coords, mesh=True):
        grids = {}
        dx = self.get_dx(level)
        coords_to_process = [c for c in self.obj.coords if convert_name(str(c), level) in coords]
        for dir in coords_to_process:
            x_i = np.array(self.obj.coords[dir])

            if mesh:
                x_i = np.append(x_i, [x_i[-1] + dx]) - dx / 2

            grids[convert_name(str(dir), level)] = x_i

        return grids

    def get_mesh_grid(self, level, coords=("x", "y", "z")):
        return self.get_grid(level, coords, mesh=True)

    def get_node_grid(self, level, coords=("x", "y", "z")):
        return self.get_grid(level, coords, mesh=False)

    def get_valid_volume(self, level):
        data = self.get_level_data(self.get_components()[0], level, valid_only=True)
        valid_cells = np.count_nonzero(~np.isnan(data))
        cell_vol = pow(self.get_dx(level), self.space_dim)
        return valid_cells * cell_vol

    def amr_mean(self, component, levels=None):
        if levels is None:
            levels = self.get_levels()

        amr_data = self.get_amr_data(component, levels, valid_only=True)
        means = np.array([d.mean() for d in amr_data])
        vols = np.array([self.get_valid_volume(level) for level in levels])

        return np.sum(vols*means)/np.sum(vols)

    def amr_max(self, component, levels=None):
        if levels is None:
            levels = self.get_levels()

        amr_data = self.get_amr_data(component, levels, valid_only=True)
        return max([d.max() for d in amr_data])

    def amr_min(self, component, levels=None):
        if levels is None:
            levels = self.get_levels()

        amr_data = self.get_amr_data(component, levels, valid_only=True)
        return min([d.min() for d in amr_data])

    def amr_norm(self, component, levels=None):
        if levels is None:
            levels = self.get_levels()

        return mpl.colors.Normalize(vmax=self.amr_max(component, levels), vmin=self.amr_min(component, levels))


    def get_outline(self, level):
        polygons = []
        for box in self.get_boxes(level):
            lo_indices, hi_indices = get_chombo_box_extent(box, self.space_dim)

            # 0.5 offset because cell centred
            lo_vals = [self.get_dx(level) * (0.5 + i) for i in lo_indices]
            hi_vals = [self.get_dx(level) * (0.5 + i) for i in hi_indices]

            end_points = [
                [lo_vals[i] - self.get_dx(level) / 2, hi_vals[i] + self.get_dx(level) / 2]
                for i in range(self.space_dim)
            ]

            # Construct vertices in n dimensions
            polygon_vertices_auto = list(product(*end_points))
            x = [p[0] for p in polygon_vertices_auto]
            y = [p[1] for p in polygon_vertices_auto]
            centroid = (
                sum(x) / len(polygon_vertices_auto),
                sum(y) / len(polygon_vertices_auto),
            )
            polygon_vertices_auto = sorted(
                polygon_vertices_auto,
                key=lambda x: math.atan2(x[1] - centroid[1], x[0] - centroid[0]),
            )

            poly = Polygon(polygon_vertices_auto)
            if poly.is_valid:
                polygons.append(poly)

        level_outline = gpd.GeoSeries(cascaded_union(polygons))

        return level_outline

    def get_all_outlines(self):
        return [self.get_outline(level) for level in self.get_levels()]

    def get_levels(self):
        return np.arange(0, self.num_levels)

    def get_level_data(self, component, level, valid_only=False):
        level_data = self.obj[get_comp_lev_str(component, level)]
        level_data = level_data.amr.convert_names(level)

        if valid_only and level < self.num_levels - 1:
            fine_level = self.obj[get_comp_lev_str(component, level+1)].amr.convert_names(level+1)

            # fine_level = fine_level.convert_names(fine_level, level+1)

            coarsen_dims = {}
            for dir in ("x", "y", "z")[0:self.space_dim]:
                coarsen_dims[dir] = self.get_ref_ratio(level)

            # Ignore warning from computing mean of a slice full of NaN values
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                coarsened_fine = fine_level.coarsen(coarsen_dims).mean()

            coarse_nans = level_data.copy(deep=True) * float("NaN")
            coarsened_fine = coarsened_fine.combine_first(coarse_nans)

            # NaN values are those which aren't covered on the finer level
            isnan = np.isnan(coarsened_fine)
            level_data = level_data.where(isnan)

        return level_data

    def plot(self, component, levels=None):
        if levels is None:
            levels = self.get_levels()

        if self.space_dim == 3:
            LOGGER.warning("Can't plot 3D data yet")

        dims = self.get_dims()

        fig = plt.figure()
        ax = plt.gca()

        for level in levels:
            coords = self.get_mesh_grid(level)
            ax.pcolormesh(coords[dims[0]], coords[dims[1]],
                          self.get_level_data(component, level),
                          norm=self.amr_norm(component))

            if level > 0:
                colors = [[1, 0, 0, 1.0], [0, 1, 0, 1.0], [0, 0, 1, 1.0]]
                outline = self.get_outline(level)
                outline.plot(ax=ax, edgecolor=colors[level-1], facecolor=[1, 1, 1, 0],
                             linewidth=3.0)

        ax.set_xlabel(dims[0])
        ax.set_ylabel(dims[1])

        cbar = fig.colorbar(cm.ScalarMappable(norm=self.amr_norm(component), cmap='viridis'), ax=ax)
        cbar.ax.set_ylabel(component)

        return fig, ax

    def convert_names(self):
        data = self.obj
        level = data.coords["level"]
        keys = list(data.keys())
        return convert_names(self.obj, level, keys)


def get_comp_lev_str(component, level):
    return component + get_lev_str(level)

def get_lev_str(level):
    return "_" + str(level)

def convert_name(name, level):
    level_str = get_lev_str(level)
    if level_str in name:
        return name.replace(level_str, "")
    else:
        return name + level_str


def convert_names(data, level, keys):
    """
    Convert from x_2 to x and from x to x_2
    Parameters
    ----------
    data :
    level :

    Returns
    -------

    """

    coords = list(data.coords)

    new_keys = []
    new_coords = []

    for k in keys:
        new_keys.append(convert_name(k, level))

    for c in coords:
        new_coords.append(convert_name(c, level))

    if type(data) == xr.Dataset:
        data = data.rename(dict(zip(keys, new_keys)))
    else:
        data = data.rename(new_keys[0])
    data = data.rename(dict(zip(coords, new_coords)))

    return data

def open_dataset(filename, inputs_file="inputs"):
    """
    Get dataset with each variable and coordinates labelled differently on each level

    Parameters
    ----------
    filename :
    inputs_file :

    Returns
    -------

    """

    pf = PltFile(filename, inputs_file=inputs_file)

    # Save as:
    # comp_i, with coords x_i, y_i for each level i

    ds_levs = []

    for level in pf.get_levels():
        ds_lev = pf.ds_levels[level]

        if pf.space_dim == 3:
            ds_lev = ds_lev.transpose("z", "y", "x")
        elif pf.space_dim == 2:
            ds_lev = ds_lev.transpose("y", "x")

        # Rename appropriately
        keys = list(ds_lev.keys())
        coords = list(ds_lev.coords)

        keys_lev = [k + get_lev_str(level) for k in keys]
        coords_lev = [c + get_lev_str(level) for c in coords]
        ds_lev = ds_lev.rename(dict(zip(keys, keys_lev)))
        ds_lev = ds_lev.rename(dict(zip(coords, coords_lev)))

        ds_lev = ds_lev.drop("level" + get_lev_str(level))

        ds_levs.append(ds_lev)

    ds = xr.merge(ds_levs)

    ds.attrs["num_levels"] = pf.num_levels
    ds.attrs["time"] = pf.time
    ds.attrs["iteration"] = pf.iteration
    ds.attrs["max_level"] = pf.max_level
    ds.attrs["num_components"] = pf.num_comps
    ds.attrs["SpaceDim"] = pf.space_dim
    ds.attrs["components"] = pf.comp_names
    ds.attrs["dims"] = ("x", "y", "z")[0:pf.space_dim]

    ds.attrs["dx"] = []
    ds.attrs["dt"] = []
    ds.attrs["ref_ratio"] = []
    ds.attrs["boxes"] = []

    for level in pf.get_levels():
        ds.attrs["boxes"].append(pf.levels[level][PltFile.BOXES])
        ds.attrs["dx"].append(pf.levels[level][PltFile.DX])
        ds.attrs["dt"].append(pf.levels[level][PltFile.DT])
        ds.attrs["ref_ratio"].append(pf.levels[level][PltFile.REF_RATIO])

    return ds


# Examples
#
# ds = open_dataset("../tests/data/plt000100.2d.hdf5")
#
# print(ds)

# print(ds.amr.num_levels)
# print(ds.amr.get_level_data("Porosity", 2))
# print(ds.amr.get_amr_data("Porosity"))
#
#
# grids = ds.amr.get_mesh_grid(1)
#
# print(grids)
#
# for level in ds.amr.get_levels():
#     print('Valid volume on level %d = %f (dx=%f)' % (level, ds.amr.get_valid_volume(level), ds.amr.get_dx(level)))
#
# print('Mean = %.4f' % ds.amr.amr_mean("Bulk concentration"))
#
#
# fig, ax = ds.amr.plot("Bulk concentration")
#
# # fig, ax = ds.amr.plot("Bulk concentration", levels=[0])
#
# y_vals = np.arange(0, 1.02, 0.02)
# x_vals = 0.5*y_vals
# transect = ds.amr.get_transect("Bulk concentration", {"x": x_vals, "y": y_vals})
#
# fig_transect = plt.figure()
#
# ax_transect = fig_transect.gca()
# ax_transect.plot(transect.coords["z"], transect)
#
#
# ax.plot(x_vals, y_vals, linestyle='--', color='white')
# plt.show()
#
#
#
