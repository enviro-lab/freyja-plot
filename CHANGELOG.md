# Change Log

## TODO
Maybe incorporate aliases into superlineage/sublineage detection. See https://github.com/cov-lineages/pango-designation/blob/master/pango_designation/alias_key.json for more.

## unversioned updates

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
