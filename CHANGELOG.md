# Change Log

## TODO
Maybe incorporate aliases into superlineage/sublineage detection. See https://github.com/cov-lineages/pango-designation/blob/master/pango_designation/alias_key.json for more.

## unversioned updates

## v0.8.2
### Fixed
* previous fix actually added to commit this time

## v0.8.1
### Fixed
* `mapDict` works with all freyja versions

## v0.8.0
### Added
* Can now adjust order of lineage appearance in legend/bar stacks in plotLineages with `ordered_lineages`
* Can now select which `schemes` to use in plotLineages
### Fixed
* `sort_by` is now more clear and more consistent in its defaults
* various clarifications/typo corrections

## v0.7.0
### Added
* `return_df` functionality for plotLineageDetections
* can now choose which column to sort by for plots (x-axis) (partially implemented)
### Fixed
* missing bars in lineage plots are back for samples that should have them
* updated docstrings
* neater formatting

## v0.6.2
### Fixed
* cleanup from previous update

## v0.6.1
### Fixed
* freyjaPlotter methods now correctly compare samples for which one group is missing samples of the same grouping (name/date)

## v0.6.0
### Added
* can now bin low-abundance lineage into their superlineages in `FreyjaPlotter.plotLineages`

## v0.5.0
### Added
* plots to summarize lineage detection when abundance values aren't relevent
* boxplot capability
* can now return the data behind some figures using `return_df`

## v0.4.0
### Added
* can now plot lineage proportions over vs time
* can now stack subplots, one for each scheme (with shared x-axis)

## v0.3.0
### Added
* superlineages can optionally be based on data from cov-lineages
* date info can be added in for plotting lineage appearance

## v0.2.0
### Changed
* lineage plot now has lineages labeled
* general reorgaizing
### Added
* Can now combine multiple lineage plots as subplots via FreyjaPlotter.combineLineagePlots()
* Can now view lineage appearance over time via FreyjaPlotter.plotAppearance()
* FreyjaPlotter.colorMap updates each time new lineages are plotted and keeps colors the same across plots

## v0.1.0
### Changed
* initial release
