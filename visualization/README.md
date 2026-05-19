## Accessibility, maintainability and performance of visualization tools track

This track extended visualization capabilities across multiple tools, introduced a multiscale chunked point format, and improved documentation and annotation workflows.

Key achievements are:
* Notebook-based annotation workflow using `anybioimage` (anywidget).
  - Issue: https://github.com/scverse/2026_04_hackathon_padua/issues/22
* 3D/2.5D rendering in `napari-spatialdata`, and exploration of large 3D volumes via Neuroglancer embedded in Vitessce.
  - Issue (2.5D): https://github.com/scverse/napari-spatialdata/issues/330
  - PR: https://github.com/scverse/napari-spatialdata/pull/393
* Improved `spatialdata-plot` documentation and identification of caching issues at the Vitessce transition.
  - Issue: https://github.com/scverse/2026_04_hackathon_padua/issues/23
* Matplotlib-style plot gallery with CI-tested, copy-pastable code for `spatialdata-plot`.
  - Issue: https://github.com/scverse/2026_04_hackathon_padua/issues/20
  - PR: https://github.com/scverse/spatialdata-plot/pull/590
* Multiscale, chunked point representation (spatial-first and gene-first layouts) benchmarked against an unindexed baseline. Local code in this folder.
  - Issue: https://github.com/scverse/2026_04_hackathon_padua/issues/24
* Initial labels layer support in `SpatialData.js` with interactive element picking.
  - PR: https://github.com/Taylor-CCB-Group/SpatialData.js/pull/22
