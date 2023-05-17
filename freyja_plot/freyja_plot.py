import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

def save(fig,fn):
    """Saves `fig` to filename `fn`, if possible"""
    suffix = Path(fn).suffix
    if suffix == ".html":
        fig.write_html(fn)
    elif suffix == ".png":
        fig.write_image(fn,engine="kaleido")
    else:
        raise Exception(f"The requested image type ({suffix}) is not currently supported. Try a different filename rather than `fn='{fn}'`.")

color2hex = {"blue": ["#003f5c","#034f6f","#065f83","#0a7097","#0c82ac","#0d94c0","#0da7d5","#0bbaea","#07cdff","#29585c","#2b696e","#2d7a81","#2d8c95","#2c9ea9","#29b0be","#24c3d3","#19d6e9","#00eaff","#3d5eb3","#3c69be","#3c74c8","#3c7fd2","#3d8bdb","#3f96e5","#42a1ee","#46adf7","#4bb8ff","#349ad9","#43ade2","#59bfe9","#72d2f0","#8de3f7","#a9f5ff"],
            "green": ["#0e750f","#1f851b","#2d9626","#256b3c","#247c42","#238e48","#3aa631","#47b83b","#54c946","#60db51","#6ded5d","#7aff68","#21a04e","#1db253","#18c558","#12d85d","#0aeb61","#00ff65","#3b6619","#467720","#528828","#5e9a2f","#6aac36","#76bf3e","#83d246"],
            "red": ["#b50000","#bf260e","#c93b1c","#d24c2a","#dc5d37","#e56c45","#ee7b53","#f68a62","#ff9971","#a3001e","#af202a","#bb3436","#c74543","#d25450","#de635e","#e9726c","#f4817a","#ff9088","#a72f35","#bc353d","#d23b46","#e8414f","#ff4758","#a62e2e","#ae3836","#b7423e","#bf4c46","#c8554f"],
            "purple": ["#34106d","#49217e","#2f2a8d","#44389b","#58508d","#655c9b","#5e3290","#7344a1","#5847a8","#6b56b6","#7268a8","#7f74b6","#8856b4","#9e68c6","#b37ad9","#c98dec","#dfa1ff","#7d66c5","#8f76d3","#a187e2","#b398f0","#c5a9ff","#8d81c5","#9a8dd3","#a89ae1","#b6a8f0","#c4b5ff"],
            "orange": ["#e05131","#e5603c","#e96e48","#ed7b54","#f18860","#f5956d","#f8a17b","#fcad89","#ffb997","#bf711d","#c77a2d","#ce843b","#d68d49","#dd9756","#e4a064","#ebaa72","#f1b47f","#f8be8d","#e09100","#e4991c","#e8a22d","#ecaa3c","#efb24a","#f3bb57","#f7c364","#fbcb71","#ffd37e"],
            "yellow": ["#695a26","#7d6c27","#907e27","#a39226","#b6a624","#c9ba21","#dbd01b","#ede612","#fffc00","#96863c","#a3923a","#b09e38","#beab34","#cbb830","#d8c52b","#e5d223","#f2df18","#ffed00"],
            "pink": ["#a60f67","#b12674","#bd3781","#c8468f","#d3549d","#de62ab","#e970b9","#f47dc7","#ff8bd5","#bc5090","#c4599a","#cd62a5","#d56bb0","#de74bb","#e67dc5","#ee86d1","#f78fdc","#ff98e7"],
            "brown": ["#b48b71","#b1876b","#af8266","#ac7e60","#a97a5b","#a67556","#a07154","#9b6e51","#956a4e","#90664b","#8b6248","#855e46","#805b43","#7b5740","#75533d","#704f3a","#6b4b38","#654835","#604432","#5b402f","#553c2c","#50382a","#4a3527","#453124","#402d21","#3a291e"]}

def colors2list(d:dict):
    colorlist = []
    count = 0
    while 1:
        endoflists = True
        for lst in d.values():
            if len(lst) > count:
                colorlist.append(lst[count])
                endoflists = False
        if endoflists:
            return colorlist
        count += 1

def getAggDF(file,name):
    """Returns freyja aggregated DataFrame
    
    Args:
    * `file` (str|Path): file to read in as DataFrame
    * `name` (str): label for this dataset
    """
    df = pd.read_csv(file,sep="\t")
    df = df.rename(columns={"Unnamed: 0":"Sample name"})
    df["scheme"] = name
    return df

def getLineageAbundanceDfs(agg_df,summarized=False,date_col=None):
    """Yields lineage abundance df for each freyja sample
    
    Args:
    * `agg_df` (DataFrame): output from freyja aggregate
    * `summarized` (bool): whether to use summarized lineages rather than all lineages lineages
    """
    for i,r in agg_df.iterrows():
        # these are always a single row turning into a single-rowed dataframe
        if r.lineages in ("Undetermined","Error"):
            sn_col = [r["Sample name"]]
            lineages = [r["lineages"]]
            abundances = [r["abundances"]]
            scheme = [r["scheme"]]
        # each lineage gets its own row in the new dataframe
        else:
            # get lists of lineages and their associated abundances
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
        # create and yield dataframe
        data = {"Sample name":sn_col,"lineages":lineages,"abundances":abundances,"scheme":scheme}
        # include date info, if requested
        if date_col: data[date_col] = r[date_col]
        yield pd.DataFrame(data)
    
def getSuperLineage(lineage,level=0):
    """Returns superlineage of `lineage` at given `level`
    
    Args:
    * `lineage` (str): the lineage.
    * `level` (int): maximum number of sublineages of the superlineage to return (0 gives the base superlineage).
    """
    if lineage in ["Undetermined","Error","Other"]: return lineage
    return ".".join(lineage.split(".")[:level+1])+".*"

def getLineageCol(summarized=False,superlineage=None):
    """Returns consistent name for different lineage columns, depending on specifications

    Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False.
        * `superlineage` (bool)int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None.
    """
    if superlineage == None:
        return "lineages"
    else: # if superlineage requested:
        if summarized:
            raise AttributeError("`superlineage` details cannot be provided if `summarized` is True")
        return f"superlineage-{superlineage}"

def _parse_file_map(file_map,compare:bool):
    """Converts `file_map` argument from multiple input datatypes to dictionary"""
    if type(file_map) == dict:
        file_dict = file_map
    elif isinstance(file_map,(str,Path)):
        file_dict = {file_map:Path(file_map).stem }
    elif isinstance(file_map,(list,set,tuple)):
        file_dict = {file:Path(file).stem for file in file_map}
    else:
        raise AttributeError("`filemap` must be a string, Path, iterable, or dict")
    # determine whether this dataset is a comparison or not
    num_schemes_found = len(set(file_dict.values()))
    comparison = False if num_schemes_found==1 else compare
    # reset num_schemes and file_dict if multiple files but not a batch comparison
    if num_schemes_found > 1 and comparison == False:
        num_schemes_found = 1
        for key in file_dict.keys(): file_dict[key] = "Freyja Data"
    num_schemes = num_schemes_found
    return file_dict,comparison,num_schemes

def _parse_agg_df(agg_df:pd.DataFrame,compare:bool):
    """Determines whether this dataset is for comparison or not"""
    file_dict = "Files unknown"
    num_schemes = len(agg_df["scheme"].unique())
    comparison = num_schemes>1 if compare==True else compare
    return file_dict,comparison,num_schemes

class FreyjaPlotter:
    """A FreyjaPlotter object
    
    Args:
    * `file_map` (dict|str|iterable): stores filename(s) and optionally maps those to labels for use in plots
    * `colormap` (dict): maps `lineage` -> `color`

    Derived attributes:
    * `file_dict` (dict): `aggregated_filename` -> `label`
    * `num_schemes` (int): number of batches being compared
    * `compare` (bool): True if batches are being compared #TODO: remove?
    * `freyja_df` (DataFrame): lineage/abundance df
    * `summarized_freyja_df` (DataFrame): summarized lineage/abundance df
    """

    def __init__(self,file_map=None,colormap={},compare=True,date_col=None,agg_df=None) -> None:
        """Instantiates a FreyjaPlotter object
        
        Args:
        * `file_map` (dict|list|str|None):
            As a str: `aggregated_filename`.
            As a dict: `aggregated_filename` -> `label`.
            As a list: [file1,file2] - file stem will be used as label.
        * `colormap` (dict): `lineage` -> `color`.
        * `compare` (bool): whether to compare samples from multiple files, defaults to True.
            If `True`, the same samples will be sought from each file and labeled in plots accordingly.
            If `False`, samples from multiple files will simply be aggregated.
        * `agg_df` (DataFrame|None): Dataset to use instead of files from file_map, defaults to None.
            Must have typical fields from `freyja aggregate` output.
        """
        self.colorlist = colors2list(color2hex)
        self.color_index = 0
        self.date_col = date_col

        if not "Other" in colormap.keys(): colormap["Other"] = "grey"
        self.colormap = colormap
        if isinstance(agg_df,pd.DataFrame):
            self.file_dict,self.compare,self.num_schemes = _parse_agg_df(agg_df=agg_df,compare=compare)

        # read in files as DataFrames for further analysis
        else:
            self.file_dict,self.compare,self.num_schemes = _parse_file_map(file_map=file_map,compare=compare)
            agg_df = self._getCombinedAggDf()
        self.freyja_df = self._getFreyjaDf(agg_df)
        self.summarized_freyja_df = self._getFreyjaDf(agg_df,summarized=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(compare: {self.compare}, data: {list(self.file_dict.values()) if type(self.file_dict)==dict else self.file_dict})"

    # reading in freyja demix output
    def _getCombinedAggDf(self):
        """Returns freyja aggregated df combining dfs for each file,name pair in `rename_scheme`
        
        Adds an extra column "scheme" which holds the `name` details for each file
        
        Args:
        * `rename_scheme` (dict): key:`file`,value:`name`
        """
        return pd.concat((getAggDF(file,name) for file,name in self.file_dict.items()))

    # convert agggregated data to lineage/abundance df (summarized or all)
    def _getFreyjaDf(self,agg_df,summarized=False):
        """Returns DataFrame of all lineages, their abundances, and the related sample/scheme
        
        Args:
        * `agg_df` (DataFrame): freyja aggreagated outfile(s) as df
        * `summarized` (bool): whether to use summarized lineages rather than all lineages lineages
        """
        # create and concat dfs for each row
        df = pd.concat((
            df for df in getLineageAbundanceDfs(agg_df,summarized=summarized,date_col=self.date_col)
        )).drop_duplicates()
        # finalize data type
        df["abundances"] = df["abundances"].astype(float)
        if self.date_col:
            df[self.date_col] = pd.to_datetime(df[self.date_col])
        return df

    # Plotting
    def getPlottingDf(self,summarized=False,superlineage=False,samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,minimum=0.05,df=None,filter=True):
        """Returns DataFrame of desired data/samples for plotting
        
        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool)int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `samples` (list|"all"): only the listed samples will be plotted
        * `include_pattern` (str): samples to include like "sample1|sample2" used by pandas.Series.str.contains()
        * `exclude_pattern` (str): samples to exclude like "sample1|sample2" used by pandas.Series.str.contains()
        * `start_date` (str): First date of samples to include. Defaults to None.
        * `end_date` (str): First date of samples to include. Defaults to None.
        * `minimum` (float): minimum abundance value to include in dataset - anything less is categorized in "Other", defualts to 0.05
        * `df` (DataFrame): dataframe to use and filter rather than internal freyja_df, defaults to None
        * `filter` (bool): if False, returns df with any superlineage col added but no filtration steps, defaults to True
        """
        if isinstance(df,pd.DataFrame):
            freyja_df = self.addSuperLineageCol(superlineage=superlineage,summarized=summarized,df=df)
        else:
            self.addSuperLineageCol(superlineage=superlineage,summarized=summarized)
            freyja_df:pd.DataFrame = self.summarized_freyja_df.copy() if summarized else self.freyja_df.copy()
        if filter == False:
            return freyja_df
        if type(samples) != str:
            freyja_df = freyja_df[freyja_df["Sample name"].isin(samples)]
        if include_pattern != None:
            freyja_df = freyja_df[freyja_df["Sample name"].str.contains(include_pattern)]
        if exclude_pattern != None:
            freyja_df = freyja_df[freyja_df["Sample name"].str.contains(exclude_pattern)]
        if (start_date or end_date) and not self.date_col:
            raise AttributeError("Can't use `start_date` or `end_date` if no `date_col` attribute provided")
        if start_date:
            freyja_df = freyja_df[freyja_df[self.date_col]>=start_date]
        if end_date:
            freyja_df = freyja_df[freyja_df[self.date_col]<=end_date]
        if minimum > 0:
            freyja_df = freyja_df[freyja_df["abundances"]>=minimum]
        return freyja_df
    
    def update_colormap(self,fig):
        """Uses each Bar in `fig` to update the colormap"""
        for bar in fig.data:
            # print(bar.name)
            # print(bar.marker["color"])
            if bar.marker.color == None:
                bar.marker.color = self.colormap[bar.name] = self.colorlist[self.color_index % len(self.colorlist)]
                self.color_index += 1

    def orderLineages(self,summarized=False,superlineage=None,samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,minimum=0.05,ascending=False,df=None,filter=True):
        """Returns a df of desired lineages and abundances roughly organized from most to least common in the filtered dataset

        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool)int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `samples` (list|"all"): only the listed samples will be plotted
        * `include_pattern` (str): samples to include like "sample1|sample2" used by pandas.Series.str.contains()
        * `exclude_pattern` (str): samples to exclude like "sample1|sample2" used by pandas.Series.str.contains()
        * `start_date` (str): First date of samples to include. Defaults to None.
        * `end_date` (str): First date of samples to include. Defaults to None.
        * `minimum` (float): minimum abundance value to include in dataset - anything less is categorized in "Other", defualts to 0.05
        * `ascending` (bool): whether results should be ordered from low to high abundance values, defaults to False
        * `df` (DataFrame): dataframe to use and filter rather than internal freyja_df, defaults to None
        * `filter` (bool): if False, returns df with any superlineage col added but no filtration steps, defaults to True
        """
        if isinstance(df,pd.DataFrame):
            freyja_df = df
        else:
            freyja_df = self.getPlottingDf(summarized=summarized,superlineage=superlineage,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=minimum,filter=filter)
        lineage_col = getLineageCol(summarized=summarized,superlineage=superlineage)
        # from this, get the lineages column
        return (freyja_df[[lineage_col,"abundances"]].groupby(lineage_col).sum()/len(freyja_df["Sample name"].unique())).sort_values(by=["abundances"],ascending=ascending).reset_index()

    def listLineages(self,summarized=False,superlineage=None,samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,minimum=0.05,ascending=False,num_lineages=-1,df=None,filter=True):
        """Returns a list of desired lineages roughly organized from most to least common in the filtered dataset

        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool)int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `samples` (list|"all"): only the listed samples will be plotted
        * `include_pattern` (str): samples to include like "sample1|sample2" used by pandas.Series.str.contains()
        * `exclude_pattern` (str): samples to exclude like "sample1|sample2" used by pandas.Series.str.contains()
        * `start_date` (str): First date of samples to include. Defaults to None.
        * `end_date` (str): First date of samples to include. Defaults to None.
        * `minimum` (float): minimum abundance value to include in dataset - anything less is categorized in "Other", defualts to 0.05
        * `ascending` (bool): whether results should be ordered from low to high abundance values, defaults to False
        * `num_lineages` (int): maximum number of lineages to return starting from beginning of list, defaults to -1 which returns all 
        * `df` (DataFrame): dataframe to use and filter rather than internal freyja_df, defaults to None
        """
        lineage_col = getLineageCol(summarized=summarized,superlineage=superlineage)
        # from this, get the lineages column
        ordered_lineages_df = self.orderLineages(summarized=summarized,superlineage=superlineage,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=minimum,ascending=ascending,df=df,filter=filter)
        return ordered_lineages_df[lineage_col].to_list()[:num_lineages]

    def addSuperLineageCol(self,summarized=False,superlineage=None,df=None):
        """Adds superlineage column to freyja df if not yet there

        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool)int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `df` (DataFrame): dataframe to use and filter rather than internal freyja_df, defaults to None
        """
        lineage_col = getLineageCol(superlineage=superlineage,summarized=summarized)
        if isinstance(df,pd.DataFrame):
            if not lineage_col in df.columns:
                df[lineage_col] = df["lineages"].apply(getSuperLineage,level=superlineage)
            return df
        else:
            if not lineage_col in self.freyja_df.columns:
                self.freyja_df[lineage_col] = self.freyja_df["lineages"].apply(getSuperLineage,level=superlineage)
            return self.freyja_df

    def plotAppearance(self,summarized=False,superlineage=None,minimum=0.05,fn=None,title="Freyja lineage appearance over time",samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,num_lineages=20):
        """Returns plot showing appearance of each lineage over time
        
        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `minimum` (float): minimum abundance value to include in plot - anything less is categorized in "Other", defualts to 0.05
        * `fn` (str|Path): where to write fig, if provided, defaults to None
        * `title` (str): plot title, defualts to "Freyja lineage abundance"
        * `samples` (list|"all"): only the listed samples will be plotted
        * `include_pattern` (str): samples to include like "sample1|sample2"
        * `exclude_pattern` (str): samples to exclude like "sample1|sample2"
        * `num_lineages` (int): maximum number of most common lineages to show (where -1 which returns all), defaults to 20
        """
        if not self.date_col: raise AttributeError("`date_col` required to plot time series data")
        freyja_df = self.getPlottingDf(summarized=summarized,superlineage=superlineage,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=minimum)
        lineage_col = getLineageCol(superlineage=superlineage,summarized=summarized)
        lineage_list = self.listLineages(superlineage=superlineage,summarized=summarized,df=freyja_df,num_lineages=num_lineages,filter=False)
        freyja_df = freyja_df[freyja_df[lineage_col].isin(lineage_list)]
        freyja_df = freyja_df.sort_values(by="abundances")
        fig = px.scatter(
            freyja_df,
            x=self.date_col,
            y=lineage_col,
            # colormap=self.colormap,
            color=lineage_col,
            title=title,
            facet_col="scheme" if self.compare else None,
        )
        if fn: save(fig,fn)
        return fig

    def plotLineages(self,summarized=False,superlineage=None,minimum=0.05,fn=None,title="Freyja lineage abundance",samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None):
        """Returns stacked bar chart showing lineage abundances for each sample
        
        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool)int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `minimum` (float): minimum abundance value to include in plot - anything less is categorized in "Other", defualts to 0.05
        * `fn` (str|Path): where to write fig, if provided, defaults to None
        * `title` (str): plot title, defualts to "Freyja lineage abundance"
        * `samples` (list|"all"): only the listed samples will be plotted
        * `include_pattern` (str): samples to include like "sample1|sample2"
        * `exclude_pattern` (str): samples to exclude like "sample1|sample2"
        """
        # filter  data and decide what to loop through
        freyja_df = self.getPlottingDf(summarized=summarized,superlineage=superlineage,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=0.0)
        lineage_col = getLineageCol(superlineage=superlineage,summarized=summarized)
        names = freyja_df["Sample name"].unique().tolist()
        schemes = freyja_df["scheme"].unique().tolist()
        lineages = freyja_df.sort_values(by="abundances")[lineage_col].unique().tolist()[::-1]
        name_scheme_array = [
            [name for name in names for _ in range(self.num_schemes)],
            [scheme for name in names for scheme in schemes]]
        if self.num_schemes > 1:
            x = [f"{name_scheme_array[0][i]}-{name_scheme_array[1][i]}" for i in range(len(name_scheme_array[0]))]
        else: x = names
        # add count each lineage abundance and add this as bars for each sample
        other_counts = [0] * len(names) * len(schemes)
        fig = go.Figure()
        for lineage in lineages:
            y = []
            for i,name in enumerate(name_scheme_array[0]):
                scheme = name_scheme_array[1][i]
                abundance = freyja_df.loc[(freyja_df["Sample name"]==name) & (freyja_df[lineage_col]==lineage) & (freyja_df["scheme"]==scheme), "abundances"].sum()
                if not isinstance(abundance, (np.floating, float)):
                    # print("setting zero",abundance)
                    abundance = 0
                # only add lineages above minimum to plot, save others for later
                if lineage.lower() == "other" or abundance < minimum:
                    y.append(0)
                    other_counts[i] += abundance
                else:
                    y.append(abundance)
            if not set(y) == {0}:
                fig.add_bar(x=x,y=y,name=lineage,
                            text=lineage,textposition="inside",
                            marker_color=self.colormap.get(lineage),
                            )
        # finalize figure
        fig.add_bar(
            x=x,y=other_counts,name="Other",
            text="Other",textposition="inside",
            marker_color=self.colormap["Other"],
            )
        fig.update_layout(
                        barmode="stack",
                        title=title,
                        # uniformtext=dict(mode="hide", minsize=10),
                        #   xaxis_tickangle=-45,
                        )
        self.update_colormap(fig)
        if fn: save(fig,fn)
        return fig
    
    def combineLineagePlots(self,figs,subplot_titles=None,title="Freyja Lineage Abundance",height=900,shared_xaxes=True,fn=None):
        """Returns plot with `figs` combined as subplots

        Args:
        * `figs` (list): lineage abundance plots to combine as suplots
        * `subplot_titles` (list): titles to use for subplots, if desired. Must have 1 title per fig in `figs`, if used
        * `title` (str): plot title
        * `height` (int): plot height
        * `shared_xaxes` (bool): whether x axis labels are needed for each subplot
        * `fn` (str|Path): where to write fig, if provided, defaults to None
        """
        from plotly.subplots import make_subplots
        if subplot_titles and len(subplot_titles)!=len(figs):
            raise AttributeError("If providing `subplot_titles`, you must have the same number of titles as number of `figs`.")
        fig = make_subplots(len(figs),shared_xaxes=shared_xaxes,subplot_titles=subplot_titles)
        for i,bar_fig in enumerate(figs):
            for bar in bar_fig.data:
                fig.add_trace(bar,row=i+1,col=1)
        legend_set = set()
        fig.for_each_trace(
            lambda trace:
                trace.update(showlegend=False)
                if (trace.name in legend_set) else legend_set.add(trace.name))
        fig.update_layout(
                barmode='stack',height=height,
                title=title
            )
        if fn: save(fig,fn)
        return fig