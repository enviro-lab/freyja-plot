# Change Log

## TODO
Maybe incorporate aliases into superlineage/sublineage detection. See https://github.com/cov-lineages/pango-designation/blob/master/pango_designation/alias_key.json for more.

## v0.4.0
### Added
* can now plot lineages with date values on the x-axis

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
