# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- ( new features )

### Changed

- ( changes in existing functionality )

### Deprecated

- ( soon-to-be removed features )

### Removed

- ( now removed features )

### Fixed

- ( any bug fixes )

### Security

- ( in case of vulnerabilities )

## [0.0.5] - 2024-04-08

### Added

- Support for Reading/Writing MultiStepIDs other than 1.
- Support for Reading MultiStep with unsorted StepValues (requires sort before writing)

### Changed

- CFSResultData to contain data of a single MultiStep only.
- Improved testing using numpy.testing
- Improved import for better usability of data submodule
- Renamed nearest neighbor interpolator based on search direction

## [0.0.4] - 2024-03-25

### Added

- Possibility to read Meshes with groups/regions that have only Nodes defined. (As occuring when defining a nodeList)
  in an openCFS simulation.
- Method to find closest node/element for CFSMeshData objects
- Warning when element quality and centroids are not computed automatically due to size.

### Changed

- Website URL to openCFS Homepage.
- Testing of CFSReader to check read mesh and data values

### Fixed

- Critical bug when reading MultiStepData

## [0.0.3] - 2024-03-20

### Added

- Possibility to just run the meshing for the given parameters.
- Additional meshing setup control with `remeshing_on` and `mesh_present`
- `track_results` property to choose which results from the hdf file to track.
- Getter functions for hdf and sensor array results.

### Changed

- Running simulations in parallel does not do an initial mesh generation if `remeshing_on = False`.

### Removed

- `init_params` that needed to be passed to the `pyCFS` constructor, it is no longer used.

### Fixed

- Data module import.

## [0.0.2] - 2024-03-18

### Added

- `pyCFS.data` package
    - code, tests and doc
- Sensor array result support
    - Because CFS currently does not write SA results into the `hdf` file

### Changed

- Extended dependencies to accommodate `pyCFS.data` package

## [0.0.1] - 2024-03-12

### Added

- Old `pycfs` package code (refactored)
- CI pipeline for automated testing
- GitLab pages for documentation

### Fixed

- Parallelization when meshing
- Type hints

### Removed

- History results are no longer supported
    - These are now to be written into the `hdf` file
- Sensor array results are the only exception
    - When CFS can directly write these to the `hdf` file this package will change accordingly
    - Users should not see much difference in behavior