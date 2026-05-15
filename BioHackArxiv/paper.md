---
title: "2nd SpatialData Hackathon: Frameworks, Formats and Interoperability
title_short: "2nd SpatialData Hackathon"
tags:
  - spatial omics
  - Bioconductor
  - scverse
  - OME-NGFF
authors:
  - name: Luca Marconato
    orcid: 0000-0003-3198-1326
    affiliation: 1
  - name: Kevin A. Yamauchi
    orcid: 0000-0002-7818-1388
    affiliation: 2, 3
  - name: Mark S. Keller
    orcid: 0000-0003-3003-874X
    affiliation: 4
  - name: Grzegorz Bokota
    orcid: 0000-0002-5470-1676
    affiliation: 5
  - name: Tong Li
    orcid: 0000-0002-8240-4476
    affiliation: 6
  - name: Sonja Stockhaus
    orcid: 0009-0005-7712-8154
    affiliation: 7
  - name: Benjamin Rombaut
    orcid: 0000-0002-4022-715X
    affiliation: 8, 9, 10
  - name: Louise Deconinck
    orcid: 0000-0001-8100-6823
    affiliation: 8, 9, 10
  - name: Chiara Schiller
    orcid: 0009-0000-3771-2202
    affiliation: 11
  - name: Yixing E. Dong
    orcid: 0009-0003-5115-5686
    affiliation: 12
  - name: Vincent J. Carey
    orcid: 0000-0003-4046-0063
    affiliation: 13, 4
  - name: Helena L. Crowell
    orcid: 0000-0002-4801-1767
    affiliation: 14
  - name: Dario Righelli
    orcid: 0000-0003-1504-3583
    affiliation: 15
  - name: Artür Manukyan
    orcid: 0000-0002-0441-9517
    affiliation: 21
  - name: Wouter-Michiel Vierdag
    orcid: 0000-0003-1666-5421
    affiliation: 1, 16
  - name: Miguel A. Ibarra-Arellano
    orcid: 0000-0001-8411-4854
    affiliation: 11
  - name: Lotte Pollaris
    orcid: 0000-0002-9509-9386
    affiliation: 8, 9, 10
  - name: Quentin Blampey
    orcid: 0000-0002-3836-2889
    affiliation: 17, 18
  - name: Clarence Mah
    orcid: 0000-0001-9926-5209
    affiliation: 19, 20
  - name: Laurens Lehner
    orcid: 0000-0001-7690-7168
    affiliation: 7

affiliations:
  - name: Max Delbrück Center for Molecular Medicine, Berlin Institute for Molecular Systems Biology (MDC-BIMSB)
    index: 1
  - name: Computational Genomics and System Genetics, German Cancer Research Center (DKFZ), Heidelberg, Germany
    index: 2
  - name: Genome Biology Unit, European Molecular Biology Laboratory, Heidelberg, Germany
    index: 3
  - name: D-BSSE, ETH Zurich, Basel, Switzerland
    index: 4
  - name: German BioImaging - Gesellschaft für Mikroskopie und Bildanalyse e.V., Germany
    index: 5
  - name: BioVisionCenter, University of Zurich, Zurich, Switzerland
    index: 6
  - name: Centro Nacional de Análisis Genómico (CNAG), Barcelona, Spain
    index: 7
  - name: Institute of Computational Biology, Helmholtz Center Munich, Germany
    index: 8
  - name: Friedrich Miescher Institute for Biomedical Research, Basel, Switzerland
    index: 9
  - name: Science for Life Laboratory, Department of Biochemistry and Biophysics, Stockholm University, Stockholm, Sweden
    index: 10
  - name: Pittsburgh Supercomputing Center
    index: 11
  - name: Carnegie Mellon University
    index: 12
  - name: Italian Institute of Technology
    index: 13
  - name: University of Bologna
    index: 14
  - name: HIDIVE Lab, Department of Biomedical Informatics, Harvard Medical School (HMS)
    index: 15
  - name: CeMM Research Center for Molecular Medicine of the Austrian Academy of Sciences
    index: 16
  - name: Faculty of Computer Science, University of Vienna
    index: 17
  - name: Centre for Human Genetics, University of Oxford
    index: 18
  - name: Computational Mass Spectrometry, TUM School of Life Sciences, Technical University of Munich
    index: 19
  - name: Department of Computational Biology, University of Lausanne, Lausanne, Switzerland
    index: 20
  - name: Data Intuitive BV, Korte Breestraat 4a, 9280 Lebbeke, Belgium, BE 0833.160.219
    index: 21

date: 14 April 2026
cito-bibliography: paper.bib
event: SpatialDataHackathonApril2026
biohackathon_name: "2nd SpatialData Hackathon"
biohackathon_url: "https://docs.google.com/document/d/1GC3GlajLtQsn1GJULbabflwolI1U3Lb9zNWZ47FXcwE/edit?tab=t.0"
biohackathon_location: "Padua, Italy, 2026"
group: Code repository
# URL to project git repo --- should contain the actual paper.md:
git_url: https://github.com/scverse/2026_04_hackathon_padua
# This is the short authors description that is used at the
# bottom of the generated paper (typically the first two authors):
authors_short: 2nd SpatialData Hackathon participants
---

<!-- Note that you can use https://sparontologies.github.io/cito/current/cito.html#objectproperties
for more detailed citations for text mining e.g. [@uses_method_in:marconato_spatialdata_2024] -->

<!-- # Abstract
This pre-print outlines the results of the "1st SpatialData workshop," organized by the SpatialData team and funded by the Chan Zuckerberg Initiative (CZI). The event gathered experts to advance spatial omics through four hackathon tracks: R interoperability, visualization interoperability, scalability and benchmarking, and ergonomics.
Key achievements include integrating R with the SpatialData Python framework, developing a tool-agnostic configuration for visualization, addressing computational bottlenecks, and enhancing usability through improved documentation and interfaces. The workshop fostered collaboration, creating infrastructure prototypes and identifying interoperability challenges. Documented on GitHub, these efforts involved 20 participants from the US and Europe, promoting a FAIR ecosystem of spatial omics tools. -->

# Introduction

This work outlines the results of the "2nd SpatialData workshop", an in-person event organized by the SpatialData team (scverse) and Bioconductor team, and funded by the Helmholtz Association (ScienceServe project call) that brought together expertise from different fields, including methods developers of a variety of tools for bioimaging, single-cell and spatial omics1. The purpose is to explore new directions to advance the field of spatial omics1. By leveraging multiple programming languages, including Python, R, and JavaScript, the event focuses on four central hackathon tracks:

1. R interoperability 
2. Accessibility, maintainability and performance of visualization tools 
3. Design modernization for the SpatialData framework
4. File formats and transformations (NGFF)

Key achievements include 

1. **R interoperability**: The R SpatialData package gained support for Zarr v2/v3 read/write, spatial, table-based queries and coordinate transformations. Several new and extended R packages improve OME-Zarr handling (ImageArray package), cross-language AnnData compatibility (Zarr support for anndataR package), and conformance with OME-NGFF specifications (rome package).
2. **Accessibility, maintainability and performance of visualization tools**: Visualization capabilities were extended across napari, Vitessce, Neuroglancer, and SpatialData.js, with new support for 2.5D/3D rendering and interactive annotation. A chunked, multiscale point representation was designed and benchmarked, substantially reducing data read for large-scale viewport queries. A new notebook-based interactive annotation workflow is presented.
3. **Design modernization for the SpatialData framework**: Cloud-based I/O was introduced, enabling direct read/write against remote object stores via fsspec. Prototypes were developed for lazy external file linking, bidirectional element-table relationships, and contour-aware spatial density profiling.
4. **File formats and transformations (NGFF)**: A language-agnostic conformance test suite for OME-NGFF RFC-5 coordinate transformations was developed, alongside extensions to the transformnd library covering most RFC-5 transformations across multiple array backends. A prototype integration with multiview-stitcher enables tile stitching and fusion directly within SpatialData workflows.

The workshop fostered collaboration, creating infrastructure prototypes and identifying interoperability challenges. Documented on GitHub, these efforts involved 24 participants from the US and Europe, promoting a FAIR ecosystem of spatial omics and imaging tools.

# Results

All the issues were tracked in a public project board accessible here: [https://github.com/orgs/scverse/projects/70/views/1](https://github.com/orgs/scverse/projects/70/views/1.

## R interoperability track

## Accessibility, maintainability and performance of visualization tools track

## Design modernization for the SpatialData framework track

## File formats and transformations (NGFF) track

# Conclusions

The hackathon brought together 24 participants from institutions across the US and Europe, who collaboratively enhanced the usability and interoperability of the SpatialData format and framework.

# Acknowledgements

The event was made possible thanks to the support of the Helmholtz Association via the Helmholtz ScienceServe project call.

# References

