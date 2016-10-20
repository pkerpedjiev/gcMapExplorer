#!/usr/bin/env python3
#
# Author: Rajendra Kumar
#
# This file is part of gcMapExplorer
# Copyright (C) 2016  Rajendra Kumar, Ludvig Lizana, Per Stenberg
#
# gcMapExplorer is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gcMapExplorer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gcMapExplorer.  If not, see <http://www.gnu.org/licenses/>.
#
#=============================================================================

import logging
import h5py
import numpy as np

from gcMapExplorer.config import getConfig

# get configuration
config = getConfig()

from . import ccmap as cmp
from . import ccmapHelpers as cmh


class GCMAP:
    """To access Genome wide contact map.

    It is similar to :class:`ccmap.CCMAP` and contains same attributes.
    Therefore, both :class:`ccmap.CCMAP` and ``GCMAP`` can be used in same way to accesss attributes.
    It also contains additional attributes because it uses HDF5 file to read the maps on demand.

    Structure of gcmap file:

        ::

            HDF5
            │
            ├──────── chr1 ──── Attributes : ['xlabel', 'ylabel', 'compression']
            │           │
            │           ├────── 10kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 20kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 40kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 60kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 80kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 160kb ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 320kb ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 640kb ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           │
            │           ├────── 10kb-bNoData  ( 1D Numpy Array )
            │           ├────── 20kb-bNoData  ( 1D Numpy Array )
            │           ├────── 40kb-bNoData  ( 1D Numpy Array )
            │           ├────── 60kb-bNoData  ( 1D Numpy Array )
            │           ├────── 80kb-bNoData  ( 1D Numpy Array )
            │           ├────── 160kb-bNoData ( 1D Numpy Array )
            │           ├────── 320kb-bNoData ( 1D Numpy Array )
            │           └────── 640kb-bNoData ( 1D Numpy Array )
            │
            ├──────── chr2 ──── Attributes : ['xlabel', 'ylabel', 'compression']
            │           │
            │           ├────── 10kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 20kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 40kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 60kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 80kb  ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 160kb ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 320kb ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           ├────── 640kb ( 2D Numpy Array ) ─── Attributes : ['minvalue', 'maxvalue', 'xshape', 'yshape', 'binsize']
            │           │
            │           ├────── 10kb-bNoData  ( 1D Numpy Array )
            │           ├────── 20kb-bNoData  ( 1D Numpy Array )
            │           ├────── 40kb-bNoData  ( 1D Numpy Array )
            │           ├────── 60kb-bNoData  ( 1D Numpy Array )
            │           ├────── 80kb-bNoData  ( 1D Numpy Array )
            │           ├────── 160kb-bNoData ( 1D Numpy Array )
            │           ├────── 320kb-bNoData ( 1D Numpy Array )
            │           └────── 640kb-bNoData ( 1D Numpy Array )
            :
            :
            :
            └───── ...


    .. note::
        * Reading the entire map from HDF5 could be time taking for very large map. Therefore, use this class in cases like read small region of map or read only once.
        * To perform calculation, use :meth:`gcMapExplorer.lib.gcmap.loadGCMapAsCCMap` as it returns :class:`gcMapExplorer.lib.ccmap.CCMAP`.

    The class is instantiated by two methods:
        >>> ccMapObj = CCMAP(hdf5, 'chr22')    # To read chr22 vs chr22 map
        >>> ccMapObj.matrix[200:400, 200:400]  # Read region between 200 to 400 of chr22 vs chr22 map.


    Parameters
    ----------

    hdf5 : str or h5py.File
        Either gcmap file name or h5py file object, which is an entry point to HDF5 file.
    mapName : str
        Name of contact map. e.g.: ``chr1`` or ``chr2``.
    chromAtX : str
        Name of chromosome at X-axis
    chromAtY : str
        Name of chromosome at Y-axis. If ``chromAtY = None``, both x-axis and y-axis contains same chromosome and map is of 'intra' of 'cis' type.
    resolution : str
        Resolution of required map.

    Attributes
    ==========
    yticks      :   list
        Minimum and maximum locations along Y-axis. e.g. ``yticks=[0, 400000]``
    xticks      :   list
        Minimum and maximum locations along X-axis. e.g. ``xticks=[0, 400000]``
    binsize     :  int
        Resolution of data. In case of 10kb resolution, binsize is 10000.
    title       :   str
        Title of the data
    xlabel      :   str
        Title for X-axis, which is chromosome name along X-axis
    ylabel      :   str
        Title for Y-axis, which is chromosome name along Y-axis
    shape       :   tuple
        Overall shape of matrix
    minvalue    :   float
        Minimum value in matrix
    maxvalue    :   float
        Maximum value in matrix
    matrix      :   h5py.Dataset
        A HDF5 Dataset object pointing to matrix/map. `See here for more details: <http://docs.h5py.org/en/latest/high/dataset.html#dataset>`_
    bNoData     :   numpy.ndarray
        A boolean numpy array of matrix shape
    bLog        :   bool
        If values in matrix are in log
    dtype       :   str
        Data type of matrix/map
    mapType     :   str
        Type of map: ``intra`` or ``inter`` chromosomal map. If chromosome along X- and Y- axis is same, then map is intra-chromosomal,
        otherwise map is inter-chromosomal.
    hdf5        :   h5py.File
        HDF5 file object instance
    fileOpened  : bool
        Whether a file is opened inside object or a HDF5 file object is provided to object.
        When a file is opened by object, it is closed before object is destroyed.
    groupName   :   str
        Name of current contact map or group name in HDF5 file
    resolution  :   str
        Resolution of current contact map
    finestResolution    :   str
        Finest available resolution of current contact map
    binsizes    :   list
        List of binsizes available for current contact map
    mapNameList :   list
        List of all available contact maps in gcmap file


    """

    def __init__(self, hdf5, mapName=None, chromAtX=None, chromAtY=None, resolution=None):
        self.xticks = None
        self.yticks = None
        self.binsize = 0
        self.title = None
        self.xlabel = None
        self.ylabel = None
        self.shape = None
        self.bNoData = None
        self.minvalue = 9e10
        self.maxvalue = -9e10
        self.bLog = False
        self.dtype = None
        self.matrix = None
        self.mapType = None

        self.hdf5 = None
        self.fileOpened = False
        self.groupName = None
        self.resolution = None
        self.finestResolution = None
        self.binsizes = None
        self.mapNameList = None

        if isinstance(hdf5, str):
            self.hdf5 = h5py.File(hdf5)
            self.fileOpened = True
        elif isinstance(hdf5, h5py.File):
            self.hdf5 = hdf5
        else:
            raise TypeError ('{0} is not a gcmap file or h5py.File instance'.format(hdf5))

        # In case if map name is not given, load the first map
        if mapName is None and chromAtX is None and chromAtY is None:
            self.genMapNameList()
            mapName = self.mapNameList[0]

        self._setLabels(mapName, chromAtX, chromAtY)
        self._readMap(resolution=resolution)

    def __del__(self):
        if self.fileOpened:
            self.hdf5.close()

    def genMapNameList(self, sortBy='name'):
        """ Generate list of contact maps available in gcmap file

        The maps can be either sorted by name or by size.
        The listed maps are in ``GCMAP.mapNameList``.

        Parameters
        ----------
        sortBy : str
            Accepted keywords are ``name`` and ``size``.

        """
        mapList = []
        for mapName in self.hdf5.keys():
            mapList.append(mapName)

        if sortBy == 'size':
            # Get mapname and resolution of already loaded map
            oldMapName = None
            oldResolution = None
            if self.groupName is not None:
                oldMapName = self.groupName
                oldResolution = self.resolution

            # Generate list of shapes
            shapes = []
            for mapName in mapList:
                self.changeMap(mapName=mapName)
                shapes.append(max(self.shape[0], self.shape[1]))

            # Sort and store
            idx = np.argsort(shapes)
            self.mapNameList = list( np.array(mapList)[idx] )

            # Revert back to original map
            if oldMapName is not None:
                self.changeMap(mapName=oldMapName, resolution=oldResolution)

        else:
            self.mapNameList = cmh.sorted_nicely( mapList )

    def _setLabels(self, mapName, chromAtX, chromAtY):
        """ Set xlabel and ylabel
        """

        if mapName is not None:
            if mapName not in self.hdf5:
                raise cmp.MapNotFoundError(' [{0}] dataset not found in [{1}] file...'.format(mapName, self.hdf5.filename))
            self.groupName = mapName
            self.xlabel = self.hdf5[mapName].attrs['xlabel']
            self.ylabel = self.hdf5[mapName].attrs['ylabel']
        else:
            if chromAtX is not None:
                self.xlabel = chromAtX
                if chromAtY is not None:
                    self.ylabel = chromAtY
                else:
                    self.ylabel = self.xlabel
            elif chromAtY is not None:
                self.ylabel = chromAtY
                if chromAtX is not None:
                    self.xlabel = chromAtX
                else:
                    self.xlabel = self.ylabel
            else:
                raise AssertionError('Either mapName or chromAtX or chromAtY should be provided for further processing.')

            self.groupName = None
            if self.xlabel == self.ylabel:
                self.groupName = self.xlabel
            else:
                self.groupName = self.xlabel + '-' + self.ylabel

        self.mapType = None
        if self.xlabel == self.ylabel:
            self.mapType = 'intra'
        else:
            self.mapType = 'inter'

    def _readMap(self, resolution=None):
        """ Temporarily store h5py.Dataset object to GCMAP.matrix and update all attributes for given map.
        """

        if self.groupName not in self.hdf5:
            raise cmp.MapNotFoundError(' [{0}] dataset not found in [{1}] file...'.format(self.groupName, self.hdf5.filename))

        # determining finest resolution map
        self.binsizes = []
        for key in self.hdf5[self.groupName].keys():
            if 'bNoData' not in key:
                self.binsizes.append( self.hdf5[self.groupName][key].attrs['binsize'] )
        self.binsizes = sorted(self.binsizes)

        # At the start, always choose finest resolution
        self.finestResolution = cmp.binsizeToResolution(self.binsizes[0])
        if resolution is not None:
            resolutionList = list( map(cmp.binsizeToResolution, self.binsizes ) )
            if resolution in resolutionList:
                self.resolution = resolution
            else:
                raise ValueError (' "{0}" resolution not found for "{1}" in file: "{2}".'.format(resolution, self.groupName, self.hdf5.fileName ) )
        else:
            self.resolution = self.finestResolution

        self.dtype = self.hdf5[self.groupName][self.resolution].dtype

        for key in ['xlabel', 'ylabel']:
            self.__dict__[key] = self.hdf5[self.groupName].attrs[key]

        for key in ['minvalue', 'maxvalue', 'binsize']:
            self.__dict__[key] = self.hdf5[self.groupName][self.resolution].attrs[key]

        self.shape = (self.hdf5[self.groupName][self.resolution].attrs['xshape'], self.hdf5[self.groupName][self.resolution].attrs['yshape'])
        self.xticks = [0, self.shape[0]*self.binsize]
        self.yticks = [0, self.shape[1]*self.binsize]

        self.title = self.xlabel + '_vs_' + self.ylabel

        if self.resolution+'-bNoData' in self.hdf5[self.groupName]:
            self.bNoData = np.asarray( self.hdf5[self.groupName][self.resolution+'-bNoData'][:], dtype=np.bool )
        self.matrix = self.hdf5[self.groupName][self.resolution]

    def loadSmallestMap(self, resolution=None):
        """ Load smallest sized contact map

        Parameters
        ----------
        resolution : str
            Resolution to change. When it is not provided, finest resolution of smallest maps is loaded.


        """
        self.genMapNameList(sortBy='size')
        self.changeMap(mapName=self.mapNameList[0], resolution=resolution)

    def toCoarserResolution(self):
        """ Try to change contact map to next coarser resolution

        Returns
        -------
        success : bool
            If change was successfu ``True`` otherwise ``False``.

        """

        idx = self.binsizes.index(self.binsize)
        if idx == len(self.binsizes) - 1:
            return False

        self.resolution = cmp.binsizeToResolution(self.binsizes[idx+1])

        self.dtype = self.hdf5[self.groupName][self.resolution].dtype

        for key in ['minvalue', 'maxvalue', 'binsize']:
            self.__dict__[key] = self.hdf5[self.groupName][self.resolution].attrs[key]

        self.shape = (self.hdf5[self.groupName][self.resolution].attrs['xshape'], self.hdf5[self.groupName][self.resolution].attrs['yshape'])
        self.xticks = [0, self.shape[0]*self.binsize]
        self.yticks = [0, self.shape[1]*self.binsize]

        self.title = self.xlabel + '_vs_' + self.ylabel

        if self.resolution+'-bNoData' in self.hdf5[self.groupName]:
            self.bNoData = np.asarray( self.hdf5[self.groupName][self.resolution+'-bNoData'][:], dtype=np.bool )
        self.matrix = self.hdf5[self.groupName][self.resolution]

        return True

    def toFinerResolution(self):
        """ Try to change contact map to next finer resolution

        Returns
        -------
        success : bool
            If change was successfu ``True`` otherwise ``False``.

        """

        idx = self.binsizes.index(self.binsize)
        if idx == 0:
            return False

        self.resolution = cmp.binsizeToResolution(self.binsizes[idx-1])

        self.dtype = self.hdf5[self.groupName][self.resolution].dtype

        for key in ['minvalue', 'maxvalue', 'binsize']:
            self.__dict__[key] = self.hdf5[self.groupName][self.resolution].attrs[key]

        self.shape = (self.hdf5[self.groupName][self.resolution].attrs['xshape'], self.hdf5[self.groupName][self.resolution].attrs['yshape'])
        self.xticks = [0, self.shape[0]*self.binsize]
        self.yticks = [0, self.shape[1]*self.binsize]

        self.title = self.xlabel + '_vs_' + self.ylabel

        if self.resolution+'-bNoData' in self.hdf5[self.groupName]:
            self.bNoData = np.asarray( self.hdf5[self.groupName][self.resolution+'-bNoData'][:], dtype=np.bool )
        self.matrix = self.hdf5[self.groupName][self.resolution]

        return True

    def changeResolution(self, resolution):
        """ Try to change contact map of a given resolution.

        Parameters
        ----------
        resolution : str
            Resolution to change.

        Returns
        -------
        success : bool
            If change was successfu ``True`` otherwise ``False``.

        """

        self._readMap(resolution=resolution)

    def changeMap(self, mapName=None, chromAtX=None, chromAtY=None, resolution=None):
        """ Change the map from

        It can be used to change the map. For example, to access the map of 'chr20' instead of 'chr22', use this function.

        For example:
            >>> ccMapObj = CCMAP(hdf5, 'chr22')    # To read chr22 vs chr22 map
            >>> ccMapObj.matrix[200:400, 200:400]  # To access region between 200 to 400 of chr22 vs chr22 map.
            >>> ccMapObj.changeMap('chr20')        # Changed to read chr20 vs chr20 map
            >>> ccMapObj.matrix[200:400, 200:400]  # Now, to access region between 200 to 400 of chr20 vs chr20 map.


        """

        self._setLabels(mapName, chromAtX, chromAtY)
        self.matrix = None
        self._readMap(resolution=resolution)

    def get_ticks(self, binsize=None):
        """To get xticks and yticks for the matrix

        Parameters
        ----------
        binsize : int
            Number of base in each bin or pixel or box of contact map.

        Returns
        -------
        xticks  :   numpy.array
            1D array containing positions along X-axis
        yticks  :   numpy.array
            1D array containing positions along X-axis

        """
        if binsize is None:
            xticks = np.arange(self.xticks[0], self.xticks[1], self.binsize)
            yticks = np.arange(self.yticks[0], self.yticks[1], self.binsize)
        else:
            xticks = np.arange(self.xticks[0], self.xticks[1], binsize)
            yticks = np.arange(self.yticks[0], self.yticks[1], binsize)

        return xticks, yticks

    def _performDownSampling(self , level=2, method='sum'):

        # To determine output shape but it does not contain remainder regions
        # subtracted one as real data start from first index
        outShapeX = int( np.ceil(float(self.shape[1] - 1 )/level) )
        outShapeY = int( np.ceil(float(self.shape[0] - 1 )/level) )


        # To determine remainder regions(sourceMasked.max() - sourceMasked.min())
        pad_size_outer = ( outShapeY * level) - (self.shape[0] - 1)
        pad_size_inner = ( outShapeX * level) - (self.shape[1] - 1)

        # Otput shape
        outputShape = (outShapeX + 1 , outShapeY + 1)

        # New binsize
        newBinsize = self.binsize * level

        # Create and add map
        resolution = cmp.binsizeToResolution(newBinsize)

        if  self.hdf5[self.groupName].attrs['compression'] == 'lzf':
            outCmap = self.hdf5[self.groupName].create_dataset(resolution, outputShape, dtype=self.dtype, chunks=True, compression="lzf", shuffle=True)
        else:
            outCmap = self.hdf5[self.groupName].create_dataset(resolution, outputShape, dtype=self.dtype, chunks=True, compression="gzip", shuffle=True, compression_opts=4)

        try:
            # Ignore first row and column --- no data
            count = 1
            i = 1
            while i < self.shape[0]:

                # Here handles inner
                if pad_size_inner != 0:
                    zero_part = []
                    for n in range(level):
                        zero_part.append( np.zeros(pad_size_inner) )

                    # Here handles outer
                    if i+level < self.shape[0]:
                        x_padded = np.hstack( (self.matrix[i:i + level, 1:], zero_part) )
                    else:
                        x_padded = np.hstack( (self.matrix[i:, 1:], zero_part[:self.matrix[i:].shape[0]] ) )

                    # print(x_padded.shape)

                    if method == 'mean':
                        r = x_padded.mean(axis=0).reshape(-1, level).mean(axis=1)
                    elif method == 'max':
                        r = x_padded.max(axis=0).reshape(-1, level).max(axis=1)
                    else:
                        r = x_padded.sum(axis=0).reshape(-1, level).sum(axis=1)

                    #rint(r.shape)

                else:

                    # Here handles outer
                    if i+level < self.shape[0]:
                        if method == 'mean':
                            r = self.matrix[i:i+level, 1:].mean(axis=0).reshape(-1, level).mean(axis=1)
                        elif method == 'max':
                            r = self.matrix[i:i+level, 1:].max(axis=0).reshape(-1, level).max(axis=1)
                        else:
                            r = self.matrix[i:i+level, 1:].sum(axis=0).reshape(-1, level).sum(axis=1)
                    else:
                        remain = self.shape[0]-i
                        if method == 'mean':
                            r = self.matrix[i:, 1:].mean(axis=0).reshape(-1, remain).mean(axis=1)
                        elif method == 'max':
                            r = self.matrix[i:, 1:].max(axis=0).reshape(-1, remain).max(axis=1)
                        else:
                            r = self.matrix[i:, 1:].sum(axis=0).reshape(-1, remain).sum(axis=1)

                i = i + level

                outCmap[count, 1:] = r
                count = count + 1


            # Get minimum value othar than zero
            ma = np.ma.masked_equal(outCmap, 0.0, copy=False)
            minvalue = ma.min()
            del ma

            # Save all other attributes
            if self.bNoData is not None:
                bNoData = np.zeros(outputShape[0], dtype=np.bool)
                if pad_size_inner != 0:
                    x_padded = np.hstack( (self.bNoData[1:], np.zeros(pad_size_inner)) )
                else:
                    x_padded = self.bNoData[1:]

                bNoData[1:] = x_padded.reshape(-1, level).sum(axis=1)

                if  self.hdf5[self.groupName].attrs['compression'] == 'lzf':
                    self.hdf5[self.groupName].create_dataset(resolution+'-bNoData', bNoData.shape, dtype=bNoData.dtype, data=bNoData, chunks=True, compression="lzf", shuffle=True)
                else:
                    self.hdf5[self.groupName].create_dataset(resolution+'-bNoData', bNoData.shape, dtype=bNoData.dtype, data=bNoData, chunks=True, compression="gzip", shuffle=True, compression_opts=4)

            outCmap.attrs['minvalue'] = minvalue
            outCmap.attrs['maxvalue'] = np.amax(outCmap)
            outCmap.attrs['binsize'] = newBinsize
            outCmap.attrs['xshape'] = outputShape[0]
            outCmap.attrs['yshape'] = outputShape[1]

        except:
            # map might be incomplete, remove it
            if resolution in self.hdf5[self.groupName]:
                self.hdf5[self.groupName].pop(resolution)
            if resolution+'-bNoData' in self.hdf5[self.groupName]:
                self.hdf5[self.groupName].pop(resolution+'-bNoData')
            raise

        return True

    def performDownSampling(self, method='sum'):
        """Downsample recursively and store the maps

        It Downsample the maps and automatically add it to same input ``gcmap`` file.
        Downsampling works recursively, and downsampled maps are generated untill map has a size of less than 500.

        Parameters
        ----------
        method : str
            Method of downsampling. Three accepted methods are ``sum``: sum all values, ``mean``: Average of all values
            and ``max``: Maximum of all values.

        """

        allowed_methods= ['sum', 'mean', 'max']
        if method not in allowed_methods:
            raise ValueError(' "{0}" is not a valid keyword to downsample. Use: "sum", "mean" or "max". '.format(method))

        while self.shape[0] > 500 or self.shape[1] > 500:
            if not self._performDownSampling(method=method):
                break
            self.binsizes.append(self.binsize*2)
            self.toCoarserResolution()


def loadGCMapAsCCMap(filename, mapName=None, chromAtX=None, chromAtY=None, resolution=None, workDir=None):
    """ Load a map from gcmap file as a :class:`ccmap.CCMAP`.

    Parameters
    ----------
    filename : str
        A gcmap file to which map will be added
    mapName : str
        Name of contact map. e.g.: ``chr1`` or ``chr2``.
    chromAtX : str
        Name of chromosome at X-axis
    chromAtY : str
        Name of chromosome at Y-axis. If ``chromAtY = None``, both x-axis and y-axis contains same chromosome and map is of 'intra' of 'cis' type.
    resolution : str
        Resolution of required map. If contact map of input resolution is not found, ``None`` will be returned.
    workDir : str
        Name of directory where temporary files will be kept. These files will be automatically deleted.

    Returns
    -------
    ``None`` or :class:`gcMapExplorer.lib.ccmap.CCMAP`

    """

    hdf5 = h5py.File(filename)

    # Working and output directory
    if workDir is None:
        workDir = config['Dirs']['WorkingDirectory']

    groupName = None
    xlabel = None
    ylabel = None

    if mapName is not None:
        if mapName not in hdf5:
            hdf5.close()
            return None
        groupName = mapName
        xlabel = hdf5[mapName].attrs['xlabel']
        ylabel = hdf5[mapName].attrs['ylabel']
    else:
        if chromAtX is not None:
            xlabel = chromAtX
            if chromAtY is not None:
                ylabel = chromAtY
            else:
                ylabel = xlabel
        elif chromAtY is not None:
            ylabel = chromAtY
            if chromAtX is not None:
                xlabel = chromAtX
            else:
                xlabel = ylabel
        else:
            raise AssertionError('Either mapName or chromAtX or chromAtY should be provided for further processing.')

        groupName = None
        if xlabel == ylabel:
            groupName = xlabel
        else:
            groupName = xlabel + '-' + ylabel

        if groupName not in hdf5:
            hdf5.close()
            return None

    mapType = None
    if xlabel == ylabel:
        mapType = 'intra'
    else:
        mapType = 'inter'

    if resolution is not None:
        if resolution not in hdf5[groupName].keys():
            hdf5.close()
            return None
    else:
        binsizes = []
        for key in hdf5[groupName].keys():
            if 'bNoData' not in key:
                binsizes.append( cmp.resolutionToBinsize(key) )
        binsizes = sorted(binsizes)
        resolution = cmp.binsizeToResolution(binsizes[0])
        del binsizes

    cmap = cmp.CCMAP(dtype=hdf5[groupName][resolution].dtype)

    for key in ['xlabel', 'ylabel']:
        cmap.__dict__[key] = hdf5[groupName].attrs[key]
    for key in ['minvalue', 'maxvalue', 'binsize']:
        cmap.__dict__[key] = hdf5[groupName][resolution].attrs[key]
    cmap.shape = (hdf5[groupName][resolution].attrs['xshape'], hdf5[groupName][resolution].attrs['yshape'])
    cmap.xticks = [0, cmap.shape[0]*cmap.binsize]
    cmap.yticks = [0, cmap.shape[1]*cmap.binsize]

    cmap.title = xlabel+'_vs_'+ylabel

    if resolution+'-bNoData' in hdf5[groupName].keys():
        cmap.bNoData = np.asarray( hdf5[groupName][resolution+'-bNoData'][:], dtype=np.bool )

    cmap.gen_matrix_file(workDir)
    cmap.make_writable()
    cmap.matrix[:] = hdf5[groupName][resolution][:]

    cmap.make_unreadable()

    hdf5.close()

    return cmap


def addCCMap2GCMap(cmap, filename, compression='lzf', generateCoarse=True, coarsingMethod='sum', logHandler=None):
    """ Add :class:`ccmap.CCMAP` to a gcmap file

    Parameters
    ----------
    cmap : :class:`ccmap.CCMAP`
        An instance of :class:`ccmap.CCMAP`, which will be added to gcmap file
    filename : str
        Name of ``gcmap`` file
    compression : str
        Compression method. Presently allowed : ``lzf`` for LZF compression and ``gzip`` for GZIP compression.
    generateCoarse : bool
        Also generates all coarser maps where resolutions will be coarsed by a factor of two, consequetively.
        e.g.: In case of 10 kb input resolution, downsampled maps of ``20kb``, ``40kb``, ``80kb``, ``160kb``, ``320kb`` etc.
        will be generated untill, map size is less than 500.
    coarsingMethod : str
        Method of downsampling. Three accepted methods are ``sum``: sum all values, ``mean``: Average of all values
        and ``max``: Maximum of all values.


    Returns
    -------
    success : bool
        If addition was successful ``True`` otherwise ``False``.

    """
    # logger
    logger = logging.getLogger('addCCMap2GCMap')
    if logHandler is not None:
        logger.propagate = False
        logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)


    # Check compression method
    allowed_compressions = ['gzip', 'lzf']
    if compression not in allowed_compressions:
        raise KeyError('Compression method: "{0}" is not a valid keyword. Use "lzf" or "gzip".'.format(compression))

    hdf5 = h5py.File(filename)
    logger.info(' Opened file [{0}] for reading writing..'.format(filename))

    cmap.make_readable()

    # Get x-label and y-label
    xlabel = cmap.xlabel
    ylabel = cmap.ylabel

    # Determine name of dataset/map on the basis of xlabel and ylabel
    groupName = None
    if xlabel == ylabel:
        groupName = xlabel
    else:
        groupName = xlabel+'-'+ylabel

    try:
        # If map is already present in file, remove it
        logger.info(' Adding data to [{0}] for [{1}] ...'.format(filename, groupName))
        if groupName in hdf5:
            logger.info(' Data for {0} is already present in [{1}], replacing it... '.format(groupName, filename))
            hdf5.pop(groupName)

        # Create group
        group = hdf5.create_group(groupName)
        group.attrs['xlabel'] = xlabel
        group.attrs['ylabel'] = ylabel
        group.attrs['compression'] = compression

        # Create and add map
        resolution = cmp.binsizeToResolution(cmap.binsize)
        if compression == 'lzf':
            newCmap = group.create_dataset(resolution, cmap.shape, dtype=cmap.dtype, data=cmap.matrix, chunks=True, compression="lzf", shuffle=True)
        else:
            newCmap = group.create_dataset(resolution, cmap.shape, dtype=cmap.dtype, data=cmap.matrix, chunks=True, compression="gzip", shuffle=True, compression_opts=4)

        # Save all other attributes
        if cmap.bNoData is not None:
            if compression == 'lzf':
                group.create_dataset(resolution+'-bNoData', cmap.bNoData.shape, dtype=cmap.bNoData.dtype, data=cmap.bNoData, chunks=True, compression="lzf", shuffle=True)
            else:
                group.create_dataset(resolution+'-bNoData', cmap.bNoData.shape, dtype=cmap.bNoData.dtype, data=cmap.bNoData, chunks=True, compression="gzip", shuffle=True, compression_opts=4)

        # Get minimum value othar than zero
        if cmap.minvalue == 0:
            ma = np.ma.masked_equal(cmap.matrix, 0.0, copy=False)
            cmap.minvalue = ma.min()
            del ma

        newCmap.attrs['minvalue'] = cmap.minvalue
        newCmap.attrs['maxvalue'] = cmap.maxvalue
        newCmap.attrs['binsize'] = cmap.binsize
        newCmap.attrs['xshape'] = cmap.shape[0]
        newCmap.attrs['yshape'] = cmap.shape[1]

        logger.info('     ...Finished adding data for [{0}] ...'.format(groupName))
        cmap.make_unreadable()

        if generateCoarse:
            logger.info(' Generating downsampled maps for [{0}] ...'.format(groupName))
            gcmap = GCMAP(hdf5, mapName=groupName)
            gcmap.performDownSampling(method=coarsingMethod)
            del gcmap
            logger.info('     ... Finished downsampling for [{0}] ...'.format(groupName))

        hdf5.close()
        logger.info(' Closed file [{0}]...'.format(filename))

        if logHandler is not None:
            logger.removeHandler( logHandler )

        return True

    except (KeyboardInterrupt, SystemExit) as e:
        # map might be incomplete, remove it
        if groupName in hdf5:
            hdf5.pop(groupName)

        hdf5.close()
        logger.info(' Closed file [{0}]...'.format(filename))

        cmap.make_unreadable()
        if logHandler is not None:
            logger.removeHandler( logHandler )

        raise e

    except:
        # Added map might be incomplete, remove it
        if groupName in hdf5:
            hdf5.pop(groupName)
        raise

        hdf5.close()
        logger.info(' Closed file [{0}]...'.format(filename))

        cmap.make_unreadable()
        if logHandler is not None:
            logger.removeHandler( logHandler )

        return False

def changeGCMapCompression(infile, outfile, compression, logHandler=None):
    """Change compression method in GCMAP file

    Change compression method in GCMAP file. Currently LZF and GZIP  compression is allowed. LZF is fast and moderately compressing algorithm.
    However, GZIP is slower with large compressing ratio.

    .. warning:: GCMAP with ``gzip`` compression can be universally read from any programming language using HDF5 library, however ``LZF`` compression can be only decompressed using Python h5py package.


    Parameters
    ----------
    infile : str
        Input GCMAP file
    outfile : str
        Output GCMAP file
    compression : str
        Method of compression: `lzf`` or ``gzip``


    """

    # logger
    logger = logging.getLogger('changeGCMapCompression')
    if logHandler is not None:
        logger.propagate = False
        logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

    # Check compression method
    allowed_compressions = ['gzip', 'lzf']
    if compression not in allowed_compressions:
        raise KeyError('Compression method: "{0}" is not a valid keyword. Use "lzf" or "gzip".'.format(compression))

    inHdf5 = h5py.File(infile, 'r')
    logger.info(' Opened file [{0}] for reading ..'.format(infile))

    outHdf5 = h5py.File(outfile)
    logger.info(' Opened file [{0}] for reading writing ..'.format(outfile))


    for mapName in inHdf5:
        try:
            if mapName in outHdf5:
                logger.info('Data for {0} is already present in [{1}], replacing it... '.format(mapName, outfile))
                outHdf5.pop(mapName)

            if inHdf5[mapName].attrs['compression'] == compression:
                logger.info('Group [{0}] is already compressed by requested {1} method. Skipping!!!' .format(mapName))
                continue

            outHdf5.create_group(mapName)
            for attr in inHdf5[mapName].attrs:
                outHdf5[mapName].attrs[attr] = inHdf5[mapName].attrs[attr]

            outHdf5[mapName].attrs['compression'] = compression

            for data in inHdf5[mapName].keys():
                group = outHdf5[mapName]
                dset = inHdf5[mapName][data]
                if compression == 'lzf':
                    newDset = group.create_dataset(data, dset.shape, dtype=dset.dtype, data=dset[:], chunks=True, compression="lzf", shuffle=True)
                else:
                    newDset = group.create_dataset(data, dset.shape, dtype=dset.dtype, data=dset[:], chunks=True, compression="gzip", shuffle=True, compression_opts=4)

                for attr in dset.attrs:
                    newDset.attrs[attr] = dset.attrs[attr]

            logger.info('     ...Finished compressing data for [{0}] ...'.format(mapName))

        except:
            # map might be incomplete, remove it
            if mapName in outHdf5:
                outHdf5.pop(mapName)

            outHdf5.close()
            inHdf5.close()
            logger.info(' Closed files [{0}] and [{1}]...'.format(infile, outfile))

            if logHandler is not None:
                logger.removeHandler( logHandler )

            raise


    inHdf5.close()
    outHdf5.close()
    logger.info(' Closed files [{0}] and [{1}]...'.format(infile, outfile))
    if logHandler is not None:
        logger.removeHandler( logHandler )

    return True
