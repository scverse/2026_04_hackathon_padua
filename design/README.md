## Design modernization for the SpatialData framework track

This track introduced cloud-based I/O and prototyped several extensions to the SpatialData data model, covering versioned storage, bidirectional element-table linking, hierarchical objects, lazy file references, and contour-aware density profiling.

Key achievements are:
* Cloud-based read/write via UPath and fsspec.
  - PR: https://github.com/scverse/spatialdata/pull/1087
* Prototype integration of Icechunk for transactional, versioned Zarr storage.
* Prototypes for bidirectional element-table linking; DuckDB explored for cross-element SQL queries. Local code in this folder (`hackathon_duckdb.py`).
  - Discussion in the issue: https://github.com/scverse/2026_04_hackathon_padua/issues/6
* Prototype for soft-linking external files (CSV, OME-TIFF, proprietary) as lazy representations within SpatialData.
  - Code in the issue: https://github.com/scverse/2026_04_hackathon_padua/issues/12
* Design discussion for "simple" SpatialData and HierarchicalSpatialData object abstractions.
* Contour-aware density profiling (`ring_density`, `smooth_density_by_distance`) prototyped in a Squidpy fork, formalized as upstream issue and draft PR.
  - Squidpy issue: https://github.com/scverse/squidpy/issues/1160
  - Squidpy PR: https://github.com/scverse/squidpy/pull/1163
  - SpatialData issue: https://github.com/scverse/spatialdata/issues/975
