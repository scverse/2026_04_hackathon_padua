## R Interoperability track

This track introduced numerous utilities and R packages to the existing collection of Bioconductor packages to interface with SpatialData objects.

Key achievements are: 
* Complete Zarr v2/v3 (read) support in `SpatialData`, including table based queries. 
* A novel Python package `dummy-spatialdata` to be used in collaboration with `SpatialData.data` to generate test spatialdata objects.
  - GH: https://github.com/BIMSBbioinfo/dummy-spatialdata
  - PyPI: https://pypi.org/project/dummy-spatialdata/0.1.9/
* Write Support for the `SpatialData` package 
  - PR: https://github.com/HelenaLC/SpatialData/pull/163
* XYCZT coordinate system and OME-ZARR support for `ImageArray` package
  - PR: https://github.com/BIMSBbioinfo/ImageArray/pull/43 
  - PR: https://github.com/BIMSBbioinfo/ImageArray/pull/41
* Complete Zarr v2/v3 and (write v2) support in `anndataR` package 
  - PR: https://github.com/scverse/anndataR/pull/190
* A minimal R wrapper for reading and writing OME-ZARR images, `rome` package. 
  - GH: https://github.com/Huber-group-EMBL/rome
