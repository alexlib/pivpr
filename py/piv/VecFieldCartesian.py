__author__ = 'Jwely'

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

from py.utils import Timer


class VecFieldCartesian:
    """
    A cartesian vector field manager, this class can parse any v3d file (taken by
    planar PIV) into a set of velocity component matrices and coordinate mesh grids.
    This v3d format seems to be relatively common to PIV systems. Check out the v3d
    files in the `test_dataset` folder if you're unsure the format is the same.
    v3d files MUST have headers as in the example test data sets.
    """

    def __init__(self, filepath, velocity_fs=None):
        """
        All meaningful attributes of a VecField3d object are constructed upon __init__.
        The "output" attribute is the mean_set.

        :param filepath:        local filepath to a .v3d file
        :param velocity_fs:     free stream velocity, values more than 125% this value will be masked
        """

        assert filepath.endswith(".v3d"), "Input is not a valid .v3d file! filepath='{0}'".format(filepath)
        t = Timer()
        self.filepath = os.path.abspath(filepath)   # local filepath to .v3d file
        self.velocity_fs = velocity_fs              # free stream velocity associated with this file
        self.headers = None                         # list of column headers
        self.dataframe = None                       # pandas dataframe of csv like data.
        self.dims = (None, None)                    # x, y dimensions of all matrix data

        # set up empty coordinate value dictionary, (x and y are two-dimensionalized 1d vectors)
        self.x_set = None
        self.y_set = None
        self.meshgrid = {"x_mesh": None,
                         "y_mesh": None}

        self.vel_matrix = {'U': None,       # x direction velocity
                           'V': None,       # y direction velocity
                           'W': None}       # z direction velocity

        # Build up the attributes
        self._read_v3d()                    # parse the .v3d file, populates the dataframe
        self._get_meshgrid()                # populate self.dims, self.meshgrid
        self._table_to_matrix()             # populate self.mean_set
        print("loaded {0} in {1} s".format(filepath, t.finish()))


    def __getitem__(self, item):
        """ allows components of the mean_set to be accessed more simply through instance[key] """
        if item in self.vel_matrix.keys():
            return self.vel_matrix[item]

        elif item in self.meshgrid.keys():
            return self.meshgrid[item]

        else:
            raise Warning("Component {0} does not exist!".format(item))


    def _read_v3d(self):
        """ parses the .v3d file into a pandas dataframe """

        # get the header row
        with open(self.filepath, "r") as f:
            header_raw = f.next()

        # parse the header_raw string to extract list of header strings
        self.headers = header_raw.split("VARIABLES=")[1].replace('"', "").replace("\n", "").split(", ")

        # now load the rest of the file with a pandas dataframe
        self.dataframe = pd.read_csv(self.filepath, skiprows=1, names=self.headers)


    def _get_meshgrid(self):
        """
        fills the meshgrid and grabs essential dimensional information to matrisize the data
        """

        self.x_set = sorted(set(self.dataframe['X mm']))
        self.y_set = sorted(set(self.dataframe['Y mm']))
        self.dims = (len(self.y_set), len(self.x_set))

        x_mesh, y_mesh = np.meshgrid(self.x_set, self.y_set)
        self.meshgrid['x_mesh'] = x_mesh
        self.meshgrid['y_mesh'] = y_mesh


    def _table_to_matrix(self):
        """
        Fills matrix values for cartesian mesh. A little slow, but will work without any
        known information about the ordering of the input data.
        """

        # set up empty matrices
        for component in ['U', 'V', 'W']:
            self.vel_matrix[component] = np.zeros(self.dims)

        for i, row in self.dataframe.iterrows():
            x_index = self.x_set.index(row['X mm'])
            y_index = self.y_set.index(row['Y mm'])

            self.vel_matrix['U'][y_index, x_index] = row['U m/s']
            self.vel_matrix['V'][y_index, x_index] = row['V m/s']
            self.vel_matrix['W'][y_index, x_index] = row['W m/s']

        # turn the arrays into masked arrays to hide no_data and anomalously high values
        if self.velocity_fs is not None:
            high_thresh = self.velocity_fs * 1.25
        else:
            high_thresh = 100

        for component in ['U', 'V', 'W']:
            masked = np.ma.masked_array(self.vel_matrix[component], mask=self.vel_matrix[component] > high_thresh)
            self.vel_matrix[component] = masked


    def show_heatmap(self, component):
        """ prints a quick simple heads up heatmap of input component of the mean_set attribute"""
        fig, ax = plt.subplots()
        heatmap = ax.pcolor(self[component])    # see __getitem__
        plt.title(component)
        plt.show()


# testing area
if __name__ == "__main__":
    paths = [r"..\..\data_test\Ely_May28th01000.v3d",
             r"..\..\data_test\Ely_May28th01001.v3d",
             r"..\..\data_test\Ely_May28th01002.v3d",
             r"..\..\data_test\Ely_May28th01003.v3d"]

    for p in paths:
        v = VecFieldCartesian(p)

