import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

class FreyjaPlotter:
    """A FreyjaPlotter object
    
    Args:
        file_dict (dict): `aggregated_filename` -> `label`
        colormap (dict): `lineage` -> `color`

    Derived attributes:
        num_schemes (int): number of batches being compared
        compare (bool): True if batches are being compared #TODO: remove?
        freyja_df (DataFrame): lineage/abundance df
        summarized_freyja_df (DataFrame): summarized lineage/abundance df
    """

    def __init__(self,file_map,colormap={},compare=True) -> None:
        """Instantiates a FreyjaPlotter object
        
        Args:
            file_map (dict|list):
                as dict: `aggregated_filename` -> `label`
                as list: [file1,file2] - file stem will be used as label
            colormap (dict): `lineage` -> `color`
            compare (bool): whether to compare samples from multiple files, defaults to True
                if `True`: the same samples will be sought from each file and labeled in plots accordingly
                if `False`: samples from multiple files will simply be aggregated
        """
        if not "Other" in colormap.keys(): colormap["Other"] = "grey"
        self.colormap = colormap
        if type(file_map) == dict:
            self.file_dict = file_map
        elif isinstance(file_map,(str,Path)):
            self.file_dict = {file_map:Path(file_map).stem }
        elif type(file_map) == list:
            self.file_dict = {file:Path(file).stem for file in file_map}
        self.compare = compare
        num_schemes_found = len(set(self.file_dict.values()))

        # reset num_schemes and file_dict if multiple files but not a batch comparison
        if num_schemes_found > 1 and self.compare == False:
            num_schemes_found = 1
            for key in self.file_dict.keys(): self.file_dict[key] = 1
        self.num_schemes = num_schemes_found

        # read in files as DataFrames for further analysis
        agg_df = self._getCombinedAggDf()
        self.freyja_df = self._getFreyjaDf(agg_df)
        self.summarized_freyja_df = self._getFreyjaDf(agg_df,summarized=True)

    def __repr__(self) -> str:
        return f"{__name__}(compare: {self.compare}, batch{'es' if self.num_schemes>1 else ''}: {list(self.file_dict.values())})"

    # reading in freyja demix output
    def _getAggDF(self,file,name):
        """Returns freyja aggregated DataFrame
        
        Args:
            file (str|Path): file to read in as DataFrame
            name (str): label for this dataset
        """
        df = pd.read_csv(file,sep="\t")
        df = df.rename(columns={"Unnamed: 0":"Sample name"})
        df["scheme"] = name
        return df

    def _getCombinedAggDf(self):
        """Returns freyja aggregated df combining dfs for each file,name pair in `rename_scheme`
        
        Adds an extra column "scheme" which holds the `name` details for each file
        
        Args:
            rename_scheme (dict): key:`file`,value:`name`
        """
        return pd.concat((self._getAggDF(file,name) for file,name in self.file_dict.items()))

    # convert agggregated data to lineage/abundance df (summarized or all)
    def getSuperLineage(self,lineage,level=0):
        """Returns superlineage of lineage at given level
        
        Args:
            lineage (str): the lineage
            level (int): maximum number of sublineages of the superlineage to return (0 gives the superlineage)
        """
        if lineage in ["Undetermined","Error","Other"]: return lineage
        return ".".join(lineage.split(".")[:level+1])+".*"

    def _getLineageAbundanceDfs(self,agg_df,summarized=False):
        """Yields lineage abundance df for each freyja sample
        
        Args:
            agg_df (DataFrame): output from freyja aggregate
            summarized (bool): whether to use summarized lineages or all lineages
        """
        for i,r in agg_df.iterrows():
            if r.lineages in ("Undetermined","Error"):
                yield pd.DataFrame({"Sample name":[r["Sample name"]],"lineages":[r["lineages"]],"abundances":[r["abundances"]],"scheme":[r["scheme"]]})
                continue
            # get list of lineages and associated abundances
            if summarized == False:
                lineages = r["lineages"].split(" ")
                abundances = r["abundances"].split(" ")
            else:
                summarized = r["summarized"].lstrip("[(").rstrip("])").split("), (")
                lineages,abundances = [],[]
                # print(summarized)
                for grp in summarized:
                    lin,ab = grp.split(", ")
                    lin = lin.strip("'")
                    # print(lin,ab)
                    lineages.append(lin)
                    abundances.append(ab)
            # prepare/yield lineage/abundance df
            scheme = r["scheme"]
            sn_col = [r["Sample name"]]*len(lineages)
            df = pd.DataFrame({"Sample name":sn_col,"lineages":lineages,"abundances":abundances,"scheme":scheme})
            yield df
        
    def _getFreyjaDf(self,agg_df,summarized=False):
        """Returns DataFrame of all lineages, their abundances, and the related sample/scheme
        
        Args:
            agg_df (DataFrame): freyja aggreagated outfile(s) as df
            summarized (bool): whether to use summarized lineages or all lineages
        """
        # create and concat dfs for each row
        df = pd.concat((
            df for df in self._getLineageAbundanceDfs(agg_df,summarized=summarized)
        )).drop_duplicates()
        # finalize data type
        df["abundances"] = df["abundances"].astype(float)
        return df

    # Plotting
    def _getPlottingDf(self,summarized,samples="all",include_pattern=None,exclude_pattern=None):
        """Returns DataFrame of desired data/samples for plotting
        
        Args:
            summarized (bool): whether to use summarized lineages or all, defaults to False
            samples (list|"all"): only the listed samples will be plotted
            include_pattern (str): samples to include like "sample1|sample2" used by pandas.Series.str.contains()
            exclude_pattern (str): samples to exclude like "sample1|sample2" used by pandas.Series.str.contains()
        """
        freyja_df = self.summarized_freyja_df.copy() if summarized else self.freyja_df.copy()
        if type(samples) != str:
            freyja_df = freyja_df[freyja_df["Sample name"].isin(samples)]
        if include_pattern != None:
            freyja_df = freyja_df[freyja_df["Sample name"].str.contains(include_pattern)]
        if exclude_pattern != None:
            freyja_df = freyja_df[freyja_df["Sample name"].str.contains(exclude_pattern)]
        return freyja_df
    
    def save(self,fig,fn):
        """Saves fig to filename, if possible"""
        suffix = Path(fn).suffix
        if suffix == ".html":
            fig.write_html(fn)
        elif suffix == ".png":
            fig.write_image(fn,engine="kaleido")
        else:
            raise Exception(f"The requested image type ({suffix}) is not currently supported. Try a different filename rather than `fn='{fn}'`.")

    def plotLineages(self,summarized=False,superlineage=None,minimum=0.05,fn=None,title="Freyja lineage prevalence",samples="all",include_pattern=None,exclude_pattern=None):
        """Returns plot of stacked bars showing lineage abundances for each sample
        
        Args:
            summarized (bool): whether to use summarized lineages or all, defaults to False
            superlineage (int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
            minimum (float): minimum abundance value to include in plot - anything less is categorized in "Other", defualts to 0.05
            fn (str|Path): where to write fig, if provided, defaults to None
            title (str): plot title, defualts to "Freyja lineage prevalence"
            samples (list|"all"): only the listed samples will be plotted
            include_pattern (str): samples to include like "sample1|sample2"
            exclude_pattern (str): samples to exclude like "sample1|sample2"
        """
        freyja_df = self._getPlottingDf(summarized,samples)
        if superlineage == None:
            lineage_col="lineages"
        else:
            if summarized:
                raise AttributeError("`sublineage` details cannot be ascertained if `summarized` is True")
            lineage_col = f"superlineage-{superlineage}"
            freyja_df[lineage_col] = freyja_df["lineages"].apply(self.getSuperLineage,level=superlineage)
        names = freyja_df["Sample name"].unique().tolist()
        schemes = freyja_df["scheme"].unique().tolist()
        lineages = freyja_df.sort_values(by="abundances")[lineage_col].unique().tolist()[::-1]
        name_scheme_array = [
            [name for name in names for _ in range(self.num_schemes)],
            [scheme for name in names for scheme in schemes]]
        if self.num_schemes > 1:
            x = [f"{name_scheme_array[0][i]}-{name_scheme_array[1][i]}" for i in range(len(name_scheme_array[0]))]
        else: x = names
        # otherx
        other_counts = [0] * len(names) * 2
        fig = go.Figure()
        for lineage in lineages:
            y = []
            for i,name in enumerate(name_scheme_array[0]):
                scheme = name_scheme_array[1][i]
                # print(name,lineage,scheme)
                # df = freyja_df.loc[(freyja_df["Sample name"]==name) & (freyja_df[lineage_col]==lineage) & (freyja_df["scheme"]==scheme)]
                # if not df.empty:
                #     print(df)
                abundance = freyja_df.loc[(freyja_df["Sample name"]==name) & (freyja_df[lineage_col]==lineage) & (freyja_df["scheme"]==scheme), "abundances"].sum()
                if not isinstance(abundance, (np.floating, float)):
                    # print("setting zero",abundance)
                    print(abundance)
                    abundance = 0
                # only add lineages above minimum to plot, save others for later
                if lineage.lower() == "other" or abundance < minimum:
                    y.append(0)
                    other_counts[i] += abundance
                else:
                    y.append(abundance)
            # print(y)
            # fig.add_bar(x=x,y=y,name=lineage) # with barmode: relative
            if not set(y) == {0}:
                fig.add_bar(x=x,y=y,name=lineage,marker_color=self.colormap.get(lineage))
        fig.add_bar(x=x,y=other_counts,name="Other",marker_color=self.colormap["Other"])
        fig.update_layout(
                        #   barmode="relative",
                        barmode="stack",
                        title=title,
                        #   xaxis_tickangle=-45,
                        )
        if fn: self.save(fig,fn)
        return fig