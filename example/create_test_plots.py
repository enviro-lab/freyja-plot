from pathlib import Path

test_dir = Path(__file__).resolve().parent / "test_images"
test_dir.mkdir(exist_ok=True)

from freyja_plot import FreyjaPlotter

# simple plot of lineage abundances for all samples in file
plotter = FreyjaPlotter(test_dir/"wastewater-freyja-aggregated.tsv")
print("plotter details:\n",plotter)
plotter.plotLineages(superlineage=2,fn=test_dir/"superlineage_example.png")
plotter.plotLineages(summarized=True,fn=test_dir/"summarized_example.png")

# comparison plot two batches with shared samples
comp_plotter = FreyjaPlotter({
    test_dir/"wastewater-freyja-compare1.tsv":"plate1",
    test_dir/"wastewater-freyja-compare2.tsv":"plate2",
})
print("plotter details:\n",comp_plotter)
comp_plotter.plotLineages(summarized=True,fn=test_dir/"batch_comparison_example.png")
