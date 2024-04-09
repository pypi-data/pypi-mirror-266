import h5py
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot
import re
import os
import socket
import math
import logging
import xarray as xr
from shapely.ops import unary_union
from shapely.geometry import Polygon
import geopandas as gpd
from chombopy.inputs import read_inputs
from itertools import product

LOGGER = logging.getLogger(__name__)

# TODO: Fix: AMR plotting is broken at the moment


class PltFile:
    """
    Class to represent a Chombo plot file.

    Attributes
    ----------
    is_plot_file : bool
    defined : bool
    data_loaded : bool
    ds_levels : List[xarray.DataSet]
    iteration : int
    max_level : int
    num_levels : int
    num_comps : int
    space_dim : int
    comp_names : List[str]
    levels : List[dict]
        Information about each level
    time : float
    frame : int
    prob_domain : List[int]
        Base level number of cells in each dimension
    domain_size : List[float]
        Domain extent in each dimension
    level_outlines : List[geopandas.GeoSeries]
        Outline of the level extent on each level
    inputs : dict
        Input parameters
    filename : str
    plot_prefix : str
    python_index_ordering : bool
    indices : dict
        Indices for filtering data, e.g. dict(y=slice(0,3), x=slice(2,5))
    reflect : bool
    """

    NUM_COMPS = "num_comps"
    DATA = "data"
    DX = "dx"
    DT = "dt"
    REF_RATIO = "ref_ratio"
    BOXES = "boxes"
    PREFIX_FORMAT = r"([^\d\/]*)(\d+)\.\dd\.hdf5"

    # List of names for each direction to be used later
    INDEX_COORDS_NAMES = ("i", "j", "k", "l", "m")  # add more here if more dimensions

    indices = None
    reflect = None
    is_plot_file = False
    defined = False
    data_loaded = False
    ds_levels = []
    iteration = -1
    max_level = -1
    num_levels = -1
    num_comps = -1
    space_dim = -1
    comp_names = []
    levels = []
    time = -1
    frame = -1
    prob_domain = None
    domain_size = []
    level_outlines = []
    domain_size = None
    inputs = None
    filename = ""
    data = {}
    plot_prefix = ""
    python_index_ordering = True

    def __init__(self, filename, load_data=True, inputs_file="inputs"):
        self.filename = filename

        # Now read all the component names
        if not os.path.exists(self.filename):
            LOGGER.info('PltFile: file does not exist "%s"' % self.filename)
            return

        # Get the plot prefix and frame number assuming a format
        m = re.search(self.PREFIX_FORMAT, self.filename)

        if m and m.groups() and len(m.groups()) == 2:
            self.plot_prefix = m.group(1)
            self.frame = int(m.group(2))
        else:
            self.plot_prefix = None
            self.frame = -1

        # get inputs
        output_folder = os.path.abspath(os.path.join(self.filename, ".."))
        inputs_file_loc = os.path.join(output_folder, inputs_file)
        if os.path.exists(inputs_file_loc):
            self.inputs = read_inputs(inputs_file_loc)
        else:
            LOGGER.info("Cannot find inputs file %s" % inputs_file_loc)
            self.inputs = None

        self.defined = True

        if load_data:
            self.load_data()

    def __repr__(self):
        return "<PltFile object for %s>" % self.filename

    def unload_data(self):
        """
        Delete existing data (e.g. to save memory)
        """
        self.ds_levels = []
        self.data_loaded = False

    def load_data(self, zero_x=False):
        """
        Load the data for this plotfile.

        Parameters
        ----------
        zero_x : bool, optional
            Whether to shift the axes so that the bottom corner is at :math:`x=0`

        """

        if self.data_loaded:
            return

        LOGGER.info("Loading %s" % self.filename)
        h5_file = h5py.File(self.filename, "r")

        chombo_group = h5_file["Chombo_global"]
        global_attrs = chombo_group.attrs

        attrs = h5_file.attrs

        self.time = attrs["time"]
        self.iteration = int(attrs["iteration"])
        self.max_level = int(attrs["max_level"])
        self.num_levels = int(attrs["num_levels"])
        self.num_comps = int(attrs["num_components"])
        self.space_dim = int(global_attrs["SpaceDim"])

        # Now read all the component names
        self.comp_names = []

        for i in range(0, self.num_comps):
            name = attrs["component_" + str(i)]
            name = name.decode("UTF-8")
            self.comp_names.append(name)

        ds_levels = []

        self.levels = [{}] * self.num_levels
        self.level_outlines = []
        for level in range(0, self.num_levels):
            level_group = h5_file["level_" + str(level)]

            # Data is stored differently in plot files and chk files
            # much of what follows will be different as a result
            if "data:datatype=0" in list(level_group.keys()):
                self.is_plot_file = True

            group_atts = level_group.attrs
            boxes = level_group["boxes"]
            lev_dx = group_atts["dx"]
            self.levels[level] = {
                self.DX: lev_dx,
                self.DT: group_atts["dt"],
                self.REF_RATIO: group_atts["ref_ratio"],
                self.BOXES: list(boxes),
            }

            # Some attributes on level 0 apply to whole hierarchy
            if level == 0:
                self.time = group_atts["time"]

                self.prob_domain = group_atts["prob_domain"]

                self.domain_size = [
                    self.prob_domain[i] * self.levels[level][self.DX]
                    for i in range(0, len(self.prob_domain))
                ]

                # Moving to N-dimensions
                for i in range(self.space_dim, self.space_dim + self.space_dim):
                    self.domain_size[i] = self.domain_size[i] + lev_dx

            # Create a box which spans the whole domain
            # Initialise with a box spanning the whole domain, then add data where it exists
            # Important to do it like this for refined levels, where the whole domain isn't covered with data
            size = []
            for i in range(self.space_dim):
                lev_dom_box_dir = np.arange(
                    self.domain_size[i] + lev_dx / 2,
                    self.domain_size[i + self.space_dim] - lev_dx / 2,
                    lev_dx,
                )
                size.append(lev_dom_box_dir.size)

            blank_data = np.empty(tuple(size))
            blank_data[:] = np.nan

            # Create an empty dataset which spans entire domain, which we will use as a template for loading data into
            coords = {}
            box_size = ()
            for d in range(self.space_dim):
                coords_dir = np.arange(
                    self.prob_domain[d], self.prob_domain[self.space_dim + d] + 1
                )
                coords[self.INDEX_COORDS_NAMES[d]] = coords_dir
                box_size = box_size + (coords_dir.size,)  # append to tuple of sizes

            blank_data = np.empty(box_size)
            ds_dom_box = xr.Dataset({}, coords=coords)

            # Use indexes rather than x, y for now - then convert to x,y later
            # this is to avoid issues with floating point arithmetic when merging datasets
            # (we can end up trying to merge datasets where x coordinates differ by ~ 10^{-10}, creating nonsense)

            # Create empty datasets spanning entire domain for each component
            for comp_name in self.comp_names:
                extended_coords = coords
                extended_coords["level"] = np.array(level)
                dims = self.INDEX_COORDS_NAMES[: self.space_dim]
                # dims = dims[::-1]  # reverse list so we have k, j, i etc
                ds_dom_box[comp_name] = xr.DataArray(
                    blank_data, dims=dims, coords=extended_coords  # dims=['j', 'i'],
                )

            ds_boxes = [ds_dom_box]

            # Get level outlines
            boxes = self.levels[level][self.BOXES]
            polygons = []
            for box in boxes:
                lo_indices, hi_indices = self.get_indices(box)

                # 0.5 because cell centred
                lo_vals = [lev_dx * (0.5 + i) for i in lo_indices]
                hi_vals = [lev_dx * (0.5 + i) for i in hi_indices]

                end_points = [
                    [lo_vals[i] - lev_dx / 2, hi_vals[i] + lev_dx / 2]
                    for i in range(self.space_dim)
                ]

                # For plotting level outlines

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

            level_outline = gpd.GeoSeries(unary_union(polygons))
            self.level_outlines.append(level_outline)

            # Data is sorted by box and by component, so need to know total number of components
            num_comps = len(self.comp_names)

            # Now get the  data for each field, on each level
            if self.is_plot_file:

                # For plt files, data is sorted by box then by component

                data = level_group["data:datatype=0"]

                data_unshaped = data[()]

                offset = 0

                for box in self.levels[level][self.BOXES]:
                    lo_indices = [box[i] for i in range(self.space_dim)]
                    hi_indices = [
                        box[i] for i in range(self.space_dim, 2 * self.space_dim)
                    ]

                    n_cells_dir = [
                        hi_indices[d] + 1 - lo_indices[d] for d in range(self.space_dim)
                    ]

                    num_box_cells = np.prod(
                        n_cells_dir
                    )  # effectively nx * ny * nz * ...
                    num_cells = (
                        num_box_cells * num_comps
                    )  # also multiply by number of components

                    # Now split into individual components
                    # data contains all fields on this level, sort into individual fields
                    comp_offset_start = 0

                    coords = self.get_coordinates(lo_indices, hi_indices)

                    # Blank dataset for this box, which each component will be added to
                    ds_box = xr.Dataset({}, coords=coords)

                    for comp_name in self.comp_names:
                        # LOGGER.info('Num cells in a box: ' + str(num_box_cells))
                        comp_offset_finish = comp_offset_start + num_box_cells

                        indices = [
                            offset + comp_offset_start,
                            offset + comp_offset_finish,
                        ]

                        comp_offset_start = comp_offset_finish

                        ds_box[comp_name] = self.get_box_comp_data(
                            data_unshaped,
                            level,
                            indices,
                            comp_name,
                            n_cells_dir,
                            coords,
                        )

                    # Move onto next box
                    offset = offset + num_cells

                    ds_boxes.append(ds_box)

            else:

                # For chk files, data is sorted by component then by box
                # Loop over components and get data for that component from each box

                box_offset_scalar = 0

                for box in self.levels[level][self.BOXES]:
                    lo_indices, hi_indices = self.get_indices(box)

                    n_cells_dir = [
                        hi_indices[d] + 1 - lo_indices[d] for d in range(self.space_dim)
                    ]

                    num_box_cells = np.prod(
                        n_cells_dir
                    )  # effectively nx * ny * nz * ...

                    # Now split into individual components
                    # data contains all fields on this level, sort into individual fields

                    coords = self.get_coordinates(lo_indices, hi_indices)

                    # Blank dataset for this box, which each component will be added to
                    ds_box = xr.Dataset({}, coords=coords)

                    for comp_name in self.comp_names:
                        component = 0

                        # Need to get data differently if this is a vector
                        is_vector = (
                            comp_name[0] == "x"
                            or comp_name[0] == "y"
                            or comp_name[0] == "z"
                            and sum([comp_name[1:] in x for x in self.comp_names])
                            == self.space_dim
                        )
                        if is_vector:
                            if comp_name[0] == "x":
                                component = 0
                            elif comp_name[0] == "y":
                                component = 1
                            elif comp_name[0] == "z":
                                component = 2

                            # Hardwired to 2D for now
                            num_comps = self.space_dim

                            # This is the data for this component in all boxes
                            data = level_group[comp_name[1:] + ":datatype=0"]
                        else:
                            data = level_group[comp_name + ":datatype=0"]
                            component = 0

                            num_comps = 1

                        data_unshaped = data[()]

                        component_offset = 0  # this is just 0 because we only get data for this component

                        # For vectors, we may have an offset?
                        if num_comps > 1:
                            component_offset = component * num_box_cells

                        # start_index = component_offset + box_offset
                        start_index = box_offset_scalar * num_comps + component_offset
                        end_index = start_index + num_box_cells

                        indices = [start_index, end_index]

                        # comp_offset_start = comp_offset_finish

                        ds_box[comp_name] = self.get_box_comp_data(
                            data_unshaped,
                            level,
                            indices,
                            comp_name,
                            n_cells_dir,
                            coords,
                        )

                    # Move onto next box
                    box_offset_scalar = box_offset_scalar + num_box_cells

                    ds_boxes.append(ds_box)

            # Update will replace in place
            first_box = 1
            ds_level = ds_boxes[first_box]
            for b in ds_boxes[first_box + 1 :]:
                ds_level = ds_level.combine_first(b)

            # Create x,y,z, coordinates
            x_y_coords_names = ["x", "y", "z"]

            for d in range(self.space_dim):
                # Factor of 0.5 accounts for cell centering
                ds_level.coords[x_y_coords_names[d]] = (
                    ds_level.coords[self.INDEX_COORDS_NAMES[d]] + 0.5
                ) * lev_dx

            if zero_x:
                ds_level.coords["x"] = ds_level.coords["x"] - min(ds_level.coords["x"])

            # Swap i,j,k to x,y,z coordinates
            for d in range(self.space_dim):
                ds_level = ds_level.swap_dims(
                    {self.INDEX_COORDS_NAMES[d]: x_y_coords_names[d]}
                )

            # TODO: should level be an attribute or co-ordinate? need to try with actual AMR data
            ds_level.attrs["level"] = level

            ds_levels.append(ds_level)

        self.ds_levels = ds_levels

        h5_file.close()

        self.data_loaded = True

    def get_coordinates(self, lo, hi):
        """

        Get coordinates in index space given the low and high box limits

        Parameters
        ----------
        lo : tuple
            Lower limits of the domain in each dimension e.g. (0, 0).
        hi : tuple
            Upper limits of the domain in each dimension e.g. (5, 5).

        Returns
        -------
        coordinates : dict
            coordinates (in index space) in each dimension
            e.g. {'i': numpy.array([0,1,2,3,4,5]), 'j': numpy.array([0,1,2,3,4])}

        """
        coordinates = {}
        for d in range(self.space_dim):
            coords_dir = np.arange(lo[d], hi[d] + 1)
            coordinates[self.INDEX_COORDS_NAMES[d]] = coords_dir

        return coordinates

    def get_box_comp_data(
        self, data_unshaped, level, indices, comp_name, n_cells_dir, coords
    ):
        """

        Parse a list of data values from a Chombo HDF5 file into structured data

        Parameters
        ----------
        data_unshaped : numpy.array
            1D list of data values
        level : int
            Level of refinement data is from
        indices : tuple
            Upper and lower limits to sample from `data_unshaped`
        comp_name : str
            Name of the field this data represents
        n_cells_dir : tuple
            Number of cells in each spatial dimension i.e. (Nx, Ny, Nz)
        coords : dict
            Coordinates in each spatial dimension,
            e.g. {'i': [0,1,2,3], 'j': [0,1,2,3]}

        Returns
        -------
        xarray.DataArray
            Structured data

        """
        data_box_comp = data_unshaped[indices[0] : indices[1]]

        if len(data_box_comp) == 0:
            LOGGER.warning("No data in box")

        # Chombo data is indexed in reverse (i.e. data[k, j, i]), so whilst we have n_cells_dir = [Nx, Ny, Nz],
        # we need to reshape according to [Nz, Ny, Nx] before then transposing to get
        # an array which is indexed as data[i, j, k]
        # reshaped_data = data_box_comp.reshape(tuple(n_cells_dir))
        reshaped_data = data_box_comp.reshape(tuple(n_cells_dir[::-1]))
        reshaped_data = reshaped_data.transpose()

        # I think we only need to transpose in 3D
        # if self.space_dim == 3: #  or self.space_dim == 2
        #     reshaped_data = reshaped_data.transpose()
        reshaped_data = np.array(reshaped_data)

        # Check if scalar or vector
        trimmed_comp_names = [n[1:] for n in self.comp_names]
        field_type = "scalar"
        if comp_name[0] in ("x", "y", "z") and comp_name[1:] in trimmed_comp_names:
            field_type = "vector"

        dim_list = self.INDEX_COORDS_NAMES[: self.space_dim]
        extended_coords = coords
        extended_coords["level"] = level

        # If for some reason the data isn't in the right shape, try transposing
        if not reshaped_data.shape[0] == len(extended_coords[dim_list[0]]):
            LOGGER.warning("Reshaped data inconsistent with coordinates")
            reshaped_data = reshaped_data.transpose()

        xarr_component_box = xr.DataArray(
            reshaped_data,
            dims=dim_list,  # ['j', 'i'],
            coords=extended_coords,  # {'i': i_box, 'j': j_box, 'level': level},
            attrs={"field_type": field_type},
        )

        return xarr_component_box

    def get_indices(self, box):
        """

        Parse box extents from Chombo HDF5 files into low and high limits

        Parameters
        ----------
        box : list
            Chombo HDF5 format box limits,
            e.g. [x_lo, y_lo, x_hi, y_hi] = [0,0,1,1]

        Returns
        -------
        lo, hi : list
            Low and high limits, [x_lo, y_lo, ...], [x_hi, y_hi, ...]
            e.g [0,0], [1,1]

        """
        lo = [box[i] for i in range(self.space_dim)]
        hi = [box[i] for i in range(self.space_dim, 2 * self.space_dim)]
        return lo, hi

    def get_level_data(self, field, level=0, valid_only=False):
        """
        Get data for some field on a particular level of refinement.

        Parameters
        ----------
        field : str
            The field/component name to get data for
        level : int
            The level of refinement to get data on
        valid_only : bool
            Whether to set covered (not valid) regions to NaN. Covered regions are those
            which are covered by finer levels.

        Returns
        -------
        data : xarray.DataArray
            Data for the specified field on the given level.

        """
        if len(self.comp_names) == 0:
            LOGGER.info(
                "No data loaded, perhaps you meant to call PltFile.load_data() first? "
            )

        if not self.data_loaded:
            LOGGER.info("Data not loaded")
            return

        available_comps = list(self.ds_levels[0].keys())

        if field not in available_comps:
            LOGGER.info("Field: %s not found. The following fields do exist: " % field)
            LOGGER.info(available_comps)
            return

        ds_lev = self.ds_levels[level]

        ld = ds_lev[field]

        # Set covered cells to NaN
        # This is really slow, I'm sure there's a faster way
        if valid_only and level < self.num_levels - 1:
            ref_ratio = self.levels[level][self.REF_RATIO]
            fine_level = self.ds_levels[level + 1][field].copy(deep=True)

            coarsened_fine = fine_level.coarsen(x=ref_ratio, y=ref_ratio).mean()

            coarse_nans = ld.copy(deep=True) * float("NaN")
            coarsened_fine = coarsened_fine.combine_first(coarse_nans)

            # NaN values are those which aren't covered on the finer level
            isnan = np.isnan(coarsened_fine)
            ld = ld.where(isnan)

        # By default, swap to python indexing
        if self.python_index_ordering:
            if self.space_dim == 3:
                ld = ld.transpose("z", "y", "x")
            elif self.space_dim == 2:
                ld = ld.transpose("y", "x")

        ld = self.scale_slice_transform(ld)

        # If this is the x-component of a vector, and we're reflecting, we need to also make the field negative
        if self.reflect:
            if self.should_negate_field_upon_reflection(field):
                ld = -ld

        return ld

    @staticmethod
    def get_mesh_grid_n(arr, grow=0):
        """

        Parameters
        ----------
        arr : xarray.DataArray
            Data Array for some field, which must contain coordinates
        grow : int
            Number of grid cells to extend grid by in each dimension

        Returns
        -------
        x, y : numpy.array
            coordinates in x and y directions

        """
        x = np.array(arr.coords["x"])
        y = np.array(arr.coords["y"])

        x_min = x[0]
        x_max = x[-1]
        y_min = y[0]
        y_max = y[-1]

        nx = len(x) + grow
        ny = len(y) + grow

        x = np.linspace(x_min, x_max, nx)
        y = np.linspace(y_min, y_max, ny)

        return x, y

    def get_rotate_dims(self, rotate_dims):
        """
        Backward compatibility fix. Originally user had to ask to rotate dimensions to match
        python indexing. We now do this by default.

        Parameters
        ----------
        rotate_dims : bool
            Whether to transpose the spatial dimensions.

        Returns
        -------
        rotate_dims : bool
            Backwards compatible option for whether to transpose spatial dimensions.

        """
        if self.python_index_ordering:
            rotate_dims = not rotate_dims

        return rotate_dims

    def get_mesh_grid_for_level(self, level=0, grow=False):
        """
        Gets the coordinates for the given DataArray as numpy arrays

        Parameters
        ----------
        arr : xarray.DataArray
            DataArray (including coordinates) to get coordinates for
        grow : bool
            Whether to grow the domain by :math:`\Delta x/2` in each direction to extend to the edges of the domain

        Returns
        -------
        x, y : numpy.array
            Coordinates in x and y directions.
        """

        arr = self.get_level_data(self.comp_names[0], level=level)
        return PltFile.get_mesh_grid_xarray(arr, grow)

    @staticmethod
    def get_mesh_grid_xarray(arr, grow=False):
        """
        Gets the coordinates for the given DataArray as numpy arrays

        Parameters
        ----------
        arr : xarray.DataArray
            DataArray (including coordinates) to get coordinates for
        grow : bool
            Whether to grow the domain by :math:`\Delta x/2` in each direction to extend to the edges of the domain

        Returns
        -------
        x, y : numpy.array
            Coordinates in x and y directions.
        """

        x = np.array(arr.coords["x"])
        y = np.array(arr.coords["y"])

        dx = float(x[1] - x[0])
        dy = float(y[1] - y[0])

        if grow:
            x = np.append(x, [float(x[-1]) + dx])
            y = np.append(y, [float(y[-1]) + dy])

            x = x - dx / 2
            y = y - dx / 2

        return x, y

    def get_mesh_grid(self, rotate_dims=False, extend_grid=True, level=0):
        """
        Returns coordinate grids in each dimension

        Parameters
        ----------
        rotate_dims : bool, optional
            Whether to transpose the grids
        extend_grid : bool, optional
            Whether to extend the grid by :math:`\Delta x/2` in each dimension to cover the domain edges,
            rather than stopping at the center of the cells on the edge of the domain.
        level : int
            level of refinement

        Returns
        -------
        x, y, z : numpy.mgrid
            Grid in each dimension
        """

        rotate_dims = self.get_rotate_dims(rotate_dims)

        field = self.get_level_data(self.comp_names[0], level=level)

        x_coords = np.array(field.coords["x"])
        y_coords = np.array(field.coords["y"])

        dx = np.abs(x_coords[1] - x_coords[0])

        if extend_grid:
            extend = dx / 2
        else:
            extend = 0

        y, x = np.mgrid[
            slice(min(x_coords) - extend, max(x_coords) + extend, dx),
            slice(min(y_coords) - extend, max(y_coords) + extend, dx),
        ]

        if self.space_dim == 3:

            dir_strings = ["x", "y", "z"]
            dir_extents = []
            for i in range(0, self.space_dim):
                dir_coords = np.array(field.coords[dir_strings[i]])
                dir_extents.append((min(dir_coords) - extend, max(dir_coords) + extend))

            # grid_size = field_array.shape
            # if extend_grid:
            #     grid_size = grid_size + (1, 1, 1)

            # coord_max = [(grid_size[i]) * dx for i in range(0, self.space_dim)]
            # coords_min = [dx/2-extend] * self.space_dim
            # grid_spacing = [coord_max[i] / grid_size[i] for i in range(0, self.space_dim)]
            grid_spacing = dx
            grids = np.mgrid[
                [
                    slice(
                        dir_extents[i][0],
                        dir_extents[i][1] + grid_spacing,
                        grid_spacing,
                    )
                    for i in range(0, self.space_dim)
                ]
            ]

            x = grids[0]
            y = grids[1]
            z = grids[2]

            if rotate_dims:
                x = x.transpose()
                y = y.transpose()
                z = z.transpose()

            z = self.scale_slice_transform(z)
            x = self.scale_slice_transform(x, no_reflect=True)
            y = self.scale_slice_transform(y, no_reflect=True)

            return x, y, z

        else:
            if rotate_dims:
                y_new = x.transpose()
                x_new = y.transpose()

                x = x_new
                y = y_new

            return x, y

    def get_data(self, var_name, rotate_dims=False):
        """

        Get data for some field, added for legacy support

        Parameters
        ----------
        var_name : str
            Field to get data for
        rotate_dims : bool, optional
            Whether to transpose the field to match expected alignment of axis

        Returns
        -------
        data : numpy.array
            Data values for given field

        """
        rotate_dims = self.get_rotate_dims(rotate_dims)

        data = self.get_level_data(var_name)

        if data is None:
            return None

        data = np.array(data)

        if rotate_dims:
            data = data.transpose()

        return data

    def should_negate_field_upon_reflection(self, field):
        """
        Override to change the sign of certain fields upon reflection given their name.

        Parameters
        ----------
        field : str
            Name of field

        Returns
        -------
        negate_field : bool
            Whether to change the sign of the field upon reflection

        """
        return False

    def scale_slice_transform(self, data, no_reflect=False):
        """
        Perform transformations on the dataset.

        Parameters
        ----------
        data : xarray.DataArray
            data to be transformed
        no_reflect : bool
            Whether to override the pre-defined choices to reflect data or not in this transformation

        Returns
        -------
        data : xarray.DataArray
            Transformed data

        """
        if self.indices:
            data = data[self.indices]

        if self.reflect and not no_reflect:
            # flip will change both the data values and the x coordinate
            data = np.flip(data, 0)

            # reset the x coordinate
            data = data.assign_coords(x=np.flip(data.coords["x"]))

        return data

    def plot_field(self, field):
        """
        Plot the field using matplotlib and some default options.

        Parameters
        ----------
        field : str
            Field name to plot
        """
        self.load_data()

        cmap = pyplot.get_cmap("PiYG")

        ld = self.get_level_data(field, 0)
        x, y = self.get_mesh_grid()
        img = pyplot.pcolormesh(x, y, ld, cmap=cmap)

        # make a color bar
        pyplot.colorbar(img, cmap=cmap, label="")

        pyplot.xlabel("$x$")
        pyplot.xlabel("$z$")

    def plot_outlines(self, ax, colors=None):
        """

        Plot all level outlines (except level 0)

        Parameters
        ----------
        ax : matplotlib.axes
            Axes to plot onto
        colors :  list, optional
            List of colours to plot on each level, from which the relevant colour for the required level is sampled.
        """
        for level in self.get_levels()[1:]:
            self.plot_outline(ax, level, colors)

    def plot_outline(self, ax, level, colors=None):
        """

        Plot level outline for a particular color

        Parameters
        ----------
        ax : matplotlib.axes
            Axes to plot onto
        level : int
            Level outline to plot
        colors :  list, optional
            List of colours to plot on each level, from which the relevant colour for the required level is sampled.
        """
        # Default colors
        if not colors:
            colors = [[0, 0, 0, 1.0], [1, 0, 0, 1.0], [0, 1, 0, 1.0], [0, 0, 1, 1.0]]

        ec = colors[level][:]

        outline = self.level_outlines[level]

        outline = outline.scale(0.99, 0.99)
        outline.plot(ax=ax, edgecolor=ec, facecolor=[1, 1, 1, 0], linewidth=3.0)

    def set_scale_slice_transform(self, indices, reflect=False):
        """
        Describe how to extract data.

        Parameters
        ----------
        indices : dict
            indices to take, e.g. dict(y=slice(0,3), x=slice(2,5))
        reflect : bool
        """
        self.indices = indices
        self.reflect = reflect

    def reset_scale_slice_transform(self):
        """
        Reset transform settings to their initial value (none)
        """
        self.indices = None
        self.reflect = None

    def get_levels(self):
        """
        Get list of levels in this dataset

        Returns
        -------
        levels : list
            list of levels e.g. [0,1,2]
        """
        return np.arange(0, self.num_levels)

    def get_norm(self, field, levels=None):
        """
        Compute min and max values of field across the AMR hierarchy
        
        Parameters
        ----------
        field : str
            Field name
        levels : list, optional
            List of levels to consider e.g. [0,1]

        Returns
        -------
        norm : matplotlib.colors.Normalize
            Normalize object with min and max values defined

        """
        if levels is None:
            levels = self.get_levels()

        min_val = self.get_level_data(field, level=levels[0]).min()
        max_val = self.get_level_data(field, level=levels[0]).max()

        for level in levels[1:]:
            min_val = min(min_val, self.get_level_data(field, level).min())
            max_val = max(max_val, self.get_level_data(field, level).max())

        return mpl.colors.Normalize(vmin=min_val, vmax=max_val)


def setup_mpl_latex(font_size=9, linewidth=1):
    """
    Setup matplotlib for plotting with latex styles.
    """

    # Need the mathsrfs package for \mathscr if text.usetex = True
    params = {
        "text.latex.preamble": [
            "\\usepackage{gensymb}",
            "\\usepackage{mathrsfs}",
            "\\usepackage{amsmath}",
        ],
        "axes.labelsize": font_size,
        "axes.titlesize": font_size,
        "legend.fontsize": font_size,
        "xtick.labelsize": font_size,
        "ytick.labelsize": font_size,
        "font.size": font_size,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "lines.markersize": 3,
        "lines.linewidth": linewidth,
        "text.usetex": True,
        "font.family": "serif",
        "backend": "ps",
    }

    if "osx" in socket.gethostname():
        params["pgf.texsystem"] = "pdflatex"
        os.environ["PATH"] = (
            os.environ["PATH"] + ":/Library/TeX/texbin/:/usr/local/bin/"
        )

    mpl.rcParams.update(params)
