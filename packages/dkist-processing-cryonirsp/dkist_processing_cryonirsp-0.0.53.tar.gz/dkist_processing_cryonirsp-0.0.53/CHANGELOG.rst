v0.0.53 (2024-04-04)
====================

Features
--------

- The ability to rollback tasks in a workflow for possible retry has been added via dkist-processing-common 6.1.0. (`#112 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/112>`__)


v0.0.52 (2024-04-02)
====================

Misc
----

- Update bad pixel correction method such that if more than a given fraction of the frame is impacted, a faster and more general algorithm is used. This reduces processing time in cases where the data has readout problems or other large scale issues. (`#109 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/109>`__)


v0.0.51 (2024-03-27)
====================

Features
--------

- Wavelength range of CI data is now determined using header keys containing the filter central wavelength and full width half maximum. (`#111 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/111>`__)


v0.0.50 (2024-03-26)
====================

Misc
----

- Update `dkist-processing-common` to v6.0.4 to fix bug affecting NAXISn keys in `FitsAccessBase` subclasses.

v0.0.49 (2024-03-15)
====================

Bugfixes
--------

- Correctly identify *partially* incomplete scan steps. Previously any scan step that had at least a single file was
  considered to exist in its entirety, even if some of its files were missing. (`#108 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/108>`__)


v0.0.48 (2024-03-15)
====================

Bugfixes
--------

- Fixes a bug in `ParseL0CryonirspLinearizedData` which conflated dark frames with the same exposure time but different OD filters. We need to be able to identify dark frame based on their exposure conditions (exposure time, Optical Density Filter) and use the exposure conditions to correlate the sets of dark frames with the frames sets they will be used to correct (lamp gain, solar gain, observe). (`#106 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/106>`__)


v0.0.47 (2024-03-15)
====================

Bugfixes
--------

- Fixed a bug in `LinearityCorrection` that allowed an incomplete ramp to be linearized and passed onto the next processing stage. Incomplete ramps are now skipped and the parsing task will detect any incompleteness in the map and respond appropriately. (`#105 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/105>`__)


v0.0.46 (2024-03-13)
====================

Features
--------

- Normalize Q, U, and V polarimetric beams by their respective Stokes-I prior to beam combination, then multiply the combination
  by the average Stokes-I data. (`#104 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/104>`__)


Bugfixes
--------

- L1 CI Science frames now have array values that are given relative to value at disk center. Previously they had been raw counts per second.
  With this change the L1 CI frames have the same units as the L1 SP frames (i.e., counts/sec relative to disk center). (`#103 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/103>`__)


v0.0.45 (2024-03-06)
====================

Features
--------

- Save spectral corrected solar arrays as an intermediate file for inclusion in trial data products. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/101>`__)


Misc
----

- Add option to `l0_to_l1` local trial workflow to mimic running the `TransferCryoTrialData`. The command line option is `-X` and an optional argument can point
  to a specific place (anywhere in the filesystem) to save the trial outputs. If no argument to `-X` is specified then trial data will be saved in a directory called
  "trial_output" under the recipe run directory. (`#102 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/102>`__)


v0.0.44 (2024-03-05)
====================

Misc
----

- Update dkist-processing-common to v6.0.3 (adding the SOLARRAD keyword to L1 headers)


v0.0.43 (2024-03-04)
====================

Misc
----

- Bump common to v6.0.2 (`#100 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/100>`__)


v0.0.42 (2024-02-29)
====================

Bugfixes
--------

- Update dkist-processing-common to v6.0.1 (all movies are now forced to have an even number of pixels in each dimension)


v0.0.41 (2024-02-27)
====================

Misc
----

- Update the versions of the dkist-data-simulator and dkist-inventory packages. (`#99 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/99>`__)


v0.0.40 (2024-02-26)
====================

Misc
----

- Update dkist-fist-specifications to 4.1.1 (allow DEAXES = 0)


v0.0.39 (2024-02-23)
====================

Features
--------

- Added time-based computation of flux-scaled, fringe-removed, lamp gain to correct for spectral lines leaking into the average solar gain images. This problem will be resolved by the installation of a new optical filter. (`#98 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/98>`__)


v0.0.38 (2024-02-22)
====================

Bugfixes
--------

- Fixed bugs in `SPGeometricCalibration` task to use basic-corrected or gain-corrected arrays where needed. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/97>`__)
- Fixed errors in `CorrectionsMixin` that caused problems in rotation, shift and spectral curvature computations. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/97>`__)


v0.0.37 (2024-02-21)
====================

Bugfixes
--------

- Added ObsIpStartTimeBud to ramp parser to support parameter access outside of parse tasks (`#95 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/95>`__)
- Fix local workflow code to use the correct polyfit coefficients for local data processing. (`#96 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/96>`__)


v0.0.36 (2024-02-20)
====================

Features
--------

- Browse movies for polarimetric data now only show Stokes-I (with a label indicating this). (`#92 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/92>`__)


v0.0.35 (2024-02-16)
====================

Misc
----

- Transform the `cryonirsp_linearization_polyfit_coeffs_ci` and `cryonirsp_linearization_polyfit_coeffs_sp` parameters storage from being a file to json. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/94>`__)


v0.0.34 (2024-02-15)
====================

Misc
----

- Bump common to 6.0.0 (total removal of `FitsData` mixin). (`#93 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/93>`__)


v0.0.33 (2024-02-14)
====================

Features
--------

- SP movie frames now show the 2D spectra for each L1 frame instead of stacked slit positions integrated over a wavelength range.
  This means that each spatial step now gets its own movie frame. It is expected that this is a temporary change. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/91>`__)


Bugfixes
--------

- Movies now have the same aspect ratio as the L1 output frames. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/91>`__)


Misc
----

- Update local trial workflow scripts to improve functionality. (`#90 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/90>`__)
- Replace overly chatty APM spans in MakeMovieFrames task with `logger` statements. These spans recorded map scan and step numbers, which
  are both unbounded. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/91>`__)


v0.0.32 (2024-02-08)
====================

Bugfixes
--------

- Improved accuracy of beam identification algorithm in `BeamBoundariesCalibration` by using a different algorithm to align the images. This also results in less data being discarded. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Improved accuracy of beam angle and offset calcuations in `SPGeometricCalibration` by using a different algorithm to align the images. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Update algorithm used to compute translations between two arrays (which is used for alignment in both translation and rotation). The new method is based on T. Schad's gradient approach. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Fixed missing flip on spectral axis in linearized_frame mixin. (`#89 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/89>`__)


Misc
----

- Created the `ShiftMeasurementsMixin` class to share shift measurement calculation methods with both the `BeamBoundariesCalibration` and `SPGeometricCalibration` classes. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Renamed 3 `geo_strip` parameters in the `CryonirspParameters` class, as they are now used on both spectral and spatial axes. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Added the `AxisParams` dataclass to the `ShiftMeasurementsMixin` class to support axis information required when computing shifts along an axis. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Added the `BeamBoundaries` dataclass to the `BeamBoundariesCalibrationBase` class to support aggregation of beam boundary information into a single data structure. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)


v0.0.31 (2024-02-06)
====================

Bugfixes
--------

- Flipping value of CDELT1 to account for the dispersion axis flip. (`#80 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/80>`__)
- Flipping dispersion axis in the final reduced data. (`#80 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/80>`__)


v0.0.30 (2024-02-02)
====================

Features
--------

- Enable intensity mode observations to be calibrated with polarized calibration data. (`#83 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/83>`__)


v0.0.29 (2024-02-01)
====================

Misc
----

- Add tasks to trial workflows enabling ASDF, dataset inventory, and movie generation. (`#88 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/88>`__)


v0.0.28 (2024-01-31)
====================

Misc
----

- Bump versions of `dkist-fits-specifications`, `dkist-data-simulator`, and `dkist-header-validator` for fits spec version 4.1.0 (`#85 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/85>`__)


v0.0.27 (2024-01-29)
====================

Features
--------

- Modify parsing to correctly detect the use of dual nested internal scanning loops, with the outer loop step size set to zero to emulate a DSP map scan. (`#79 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/79>`__)


Bugfixes
--------

- Fixed errors in the ordering of the Helioprojective Latitude and Longitude axes in the L1 headers. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/71>`__)


v0.0.26 (2024-01-25)
====================

Misc
----

- Update version of dkist-processing-common to 5.1.0 which includes common tasks for cataloging in trial workflows. (`#87 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/87>`__)


v0.0.25 (2024-01-12)
====================

Bugfixes
--------

- Compute polarimetric noise and sensitivity values and add to L1 headers (POL_NOIS, and POL_SENS, respectively). These
  keywords are now required by the fits-spec. (`#84 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/84>`__)


Misc
----

- Update `dkist-fits-specifications` and associated (validator, simulator) to use new conditional requiredness framework. (`#84 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/84>`__)


v0.0.24 (2024-01-03)
====================

Misc
----

- Bump version of `dkist-processing-pac` to v3.0.1. No change to pipeline behavior at all. (`#82 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/82>`__)


v0.0.23 (2023-12-20)
====================

Misc
----

- Adding manual processing worker capabilities via dkist-processing-common update. (`#81 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/81>`__)


v0.0.22 (2023-12-01)
====================

Misc
----

- Use `TaskName`, task-tags, and Task-parsing flowers from `dkist-processing-common`. These had all been defined in `dkist-processing-cryonirsp`, but
  were recetly moved up to `*-common`. (`#78 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/78>`__)


v0.0.21 (2023-11-24)
====================

Misc
----

- Updates to core and common to patch security vulnerabilities and deprecations. (`#77 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/77>`__)


v0.0.20 (2023-11-22)
====================

Misc
----

- Update the FITS header specification to remove some CRYO-NIRSP specific keywords from the L1 headers. (`#76 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/76>`__)


v0.0.19 (2023-11-15)
====================

Features
--------

- Define a public API for tasks such that they can be imported directly from dkist-processing-cryonirsp.tasks (`#75 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/75>`__)


v0.0.18 (2023-11-08)
====================

Bugfixes
--------

- Removes cross-talk correction from SP science task. (`#72 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/72>`__)
- Turn on bad-pixel correction of science observe frames for science team evaluation. (`#73 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/73>`__)
- Fix computation of characteristic spectrum by removing incorrect median normalization. (`#74 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/74>`__)


v0.0.17 (2023-11-06)
====================

Features
--------

- Implement relative photometric calibration. Linearized ramp sets are normalized to counts per second. Attenuation due to Optical Density filters is compensated. Solar gain image is no longer normalized to mean of 1. Observe images are now in units of flux relative to solar center. (`#70 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/70>`__)


v0.0.16 (2023-11-02)
====================

Features
--------

- Add check to ensure calibration frames with exposure times correlated with observe frames exist and fail fast if they do not. (`#51 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/51>`__)


v0.0.15 (2023-10-17)
====================

Bugfixes
--------

- Fixed bug in SP solar gain task where lamp gain was being applied to the average solar image,
  causing the spectral transmission profile to be removed from the resulting solar gain image.
  The lamp gain is no longer applied. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/67>`__)


Misc
----

- Complete refactorization of the SP solar gain task. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/67>`__)


v0.0.14 (2023-10-17)
====================

Features
--------

- Modifies the linearity correction to divide the process into smaller chunks using less memory. No longer requires that entire ramp set be stored in memory at once. (`#65 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/65>`__)


v0.0.13 (2023-10-11)
====================

Misc
----

- Use latest version of dkist-processing-common (4.1.4) which adapts to the new metadata-store-api. (`#68 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/68>`__)


v0.0.12 (2023-10-06)
====================

Misc
----

- Identify ramps with only one frame as invalid and do not linearize them. (`#62 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/62>`__)


v0.0.11 (2023-10-05)
====================

Features
--------

- Removes casts and flips used when loading parameter files. The files are now changed to be in the format we want. (`#68 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/68>`__)


v0.0.10 (2023-09-29)
====================

Misc
----

- Remove and edit selected APM spans to reduce load on aggregating span data. (`#64 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/64>`__)


v0.0.9 (2023-09-29)
===================

Features
--------

- Removes all references to the FitsDataMixin and its methods, which are deprecated. Uses the new self.read() and self.write() methods with encoder and decoder support. (`#63 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/63>`__)


Misc
----

- Update pillow to address security vulnerability. (`#66 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/66>`__)


v0.0.8 (2023-09-21)
===================

Misc
----

- Update dkist-fits-specifications to conform to Revision I of SPEC-0122.


v0.0.7 (2023-09-11)
===================

Bugfixes
--------

- Fixes error in intermediate file mixin log statement. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/57>`__)


Misc
----

- Refactor to reduce complexity and hidden mixin->mixin dependency. (`#55 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/55>`__)


v0.0.6 (2023-09-08)
===================

Misc
----

- Use the latest version of dkist-processing-common (4.1.2) to allow the Linearity Correction task to be run on a higher memory worker. (`#60 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/60>`__)


v0.0.5 (2023-09-06)
===================

Misc
----

- Refactor linearity correction to improve memory usage. (`#59 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/59>`__)


v0.0.4 (2023-09-06)
===================

Misc
----

- Update to version 4.1.1 of dkist-processing-common which primarily adds logging and scratch file name uniqueness. (`#58 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/58>`__)


v0.0.3 (2023-08-31)
===================

Misc
----

- Remove parallel computations from the linearity correction task. (`#56 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/56>`__)


v0.0.2 (2023-08-25)
===================

Misc
----

- Change workflow names in documentation builds.


v0.0.1 (2023-08-25)
===================

Misc
----

- Initial release of pipeline for science review
