import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import subprocess
from typing import Literal
from datetime import timedelta
from freyja.sample_deconv import buildLineageMap #, map_to_constellation

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

lineage_parents_default = {'A': None, 'B': 'A', 'B.1': 'B', 'B.1.1': 'B.1', 'C.37': 'B.1.1.1', 'B.1.1.7': 'B.1.1', 'B.1.1.28': 'B.1.1', 'P.1': 'B.1.1.28', 'N.10': 'B.1.1.33', 'B.1.1.161': 'B.1.1', 'B.1.1.529': 'B.1.1', 'BA.1': 'B.1.1.529', 'BA.1.1': 'BA.1', 'BA.1.1.1': 'BA.1.1', 'BA.1.1.2': 'BA.1.1', 'BA.1.1.15': 'BA.1.1', 'BA.1.1.16': 'BA.1.1', 'BA.1.1.18': 'BA.1.1', 'BA.1.13.1': 'BA.1.13', 'BA.1.14': 'BA.1', 'BA.1.15': 'BA.1', 'BA.1.17': 'BA.1', 'BA.1.17.2': 'BA.1.17', 'BA.1.18': 'BA.1', 'BA.1.20': 'BA.1', 'BA.1.21': 'BA.1', 'BA.2': 'B.1.1.529', 'BA.2.1': 'BA.2', 'BA.2.3': 'BA.2', 'BA.2.3.2': 'BA.2.3', 'BS.1': None, 'BS.1.1': 'BS.1', 'BA.2.3.7': 'BA.2.3', 'BA.2.3.9': 'BA.2.3', 'BA.2.3.10': 'BA.2.3', 'BA.2.3.15': 'BA.2.3', 'BA.2.3.20': 'BA.2.3', 'CM.1': None, 'CM.2': None, 'CM.2.1': 'CM.2', 'CM.3': None, 'CM.4': None, 'CM.4.1': 'CM.4', 'CM.5': None, 'CM.5.1': 'CM.5', 'CM.5.2': 'CM.5', 'CM.6': None, 'CM.6.1': 'CM.6', 'CM.7': None, 'CM.8': None, 'CM.8.1': 'CM.8', 'CM.8.1.1': 'CM.8.1', 'CM.8.1.2': 'CM.8.1', 'CM.8.1.3': 'CM.8.1', 'CM.8.1.4': 'CM.8.1', 'CM.9': None, 'CM.10': None, 'CM.11': None, 'CM.12': None, 'BA.2.3.21': 'BA.2.3', 'BA.2.3.22': 'BA.2.3', 'BA.2.9': 'BA.2', 'BA.2.9.5': 'BA.2.9', 'BA.2.10': 'BA.2', 'BA.2.10.1': 'BA.2.10', 'BA.2.12': 'BA.2', 'BA.2.12.1': 'BA.2.12', 'BG.2': None, 'BG.4': None, 'BA.2.13': 'BA.2', 'BA.2.14': 'BA.2', 'BA.2.21': 'BA.2', 'BA.2.23': 'BA.2', 'BA.2.24': 'BA.2', 'BA.2.27': 'BA.2', 'BA.2.30': 'BA.2', 'BA.2.31.1': 'BA.2.31', 'BA.2.33': 'BA.2', 'BA.2.36': 'BA.2', 'BA.2.40.1': 'BA.2.40', 'BA.2.56': 'BA.2', 'BA.2.61': 'BA.2', 'BA.2.64': 'BA.2', 'BA.2.65': 'BA.2', 'BA.2.67': 'BA.2', 'BA.2.68': 'BA.2', 'BA.2.74': 'BA.2', 'BA.2.75': 'BA.2', 'BA.2.75.1': 'BA.2.75', 'BL.1': None, 'BL.1.1': 'BL.1', 'BL.1.3': 'BL.1', 'BL.1.4': 'BL.1', 'BL.1.5': 'BL.1', 'BL.2': None, 'BL.3': None, 'BL.4': None, 'BL.5': None, 'BL.6': None, 'BA.2.75.2': 'BA.2.75', 'CA.1': None, 'CA.2': None, 'CA.3': None, 'CA.3.1': 'CA.3', 'CA.4': None, 'CA.5': None, 'CA.6': None, 'CA.7': None, 'BA.2.75.3': 'BA.2.75', 'BM.1': None, 'BM.1.1': 'BM.1', 'BM.1.1.1': 'BM.1.1', 'CJ.1': None, 'CJ.1.1': 'CJ.1', 'BM.1.1.3': 'BM.1.1', 'CV.1': None, 'CV.2': None, 'BM.1.1.4': 'BM.1.1', 'EP.1': None, 'EP.2': None, 'BM.1.1.5': 'BM.1.1', 'BM.2': None, 'BM.2.1': 'BM.2', 'BM.2.2': 'BM.2', 'BM.2.3': 'BM.2', 'BM.4': None, 'BM.4.1': 'BM.4', 'BM.4.1.1': 'BM.4.1', 'CH.1': None, 'CH.1.1': 'CH.1', 'CH.1.1.1': 'CH.1.1', 'DV.1': None, 'DV.1.1': 'DV.1', 'DV.2': None, 'DV.3': None, 'DV.3.1': 'DV.3', 'DV.4': None, 'DV.5': None, 'CH.1.1.2': 'CH.1.1', 'CH.1.1.3': 'CH.1.1', 'CH.1.1.4': 'CH.1.1', 'CH.1.1.5': 'CH.1.1', 'CH.1.1.6': 'CH.1.1', 'CH.1.1.7': 'CH.1.1', 'CH.1.1.8': 'CH.1.1', 'CH.1.1.9': 'CH.1.1', 'CH.1.1.10': 'CH.1.1', 'CH.1.1.11': 'CH.1.1', 'CH.1.1.12': 'CH.1.1', 'CH.1.1.13': 'CH.1.1', 'CH.1.1.14': 'CH.1.1', 'CH.1.1.15': 'CH.1.1', 'CH.1.1.16': 'CH.1.1', 'CH.1.1.17': 'CH.1.1', 'CH.1.1.18': 'CH.1.1', 'CH.1.1.19': 'CH.1.1', 'FJ.1': None, 'CH.1.1.20': 'CH.1.1', 'CH.1.1.21': 'CH.1.1', 'CH.1.1.22': 'CH.1.1', 'CH.2': None, 'CH.3': None, 'CH.3.1': 'CH.3', 'BM.5': None, 'BA.2.75.4': 'BA.2.75', 'BR.1': None, 'BR.1.2': 'BR.1', 'BR.2': None, 'BR.2.1': 'BR.2', 'BR.3': None, 'BR.4': None, 'BR.5': None, 'BA.2.75.5': 'BA.2.75', 'BN.1': None, 'BN.1.1': 'BN.1', 'BN.1.1.1': 'BN.1.1', 'BN.1.2': 'BN.1', 'BN.1.2.1': 'BN.1.2', 'BN.1.2.2': 'BN.1.2', 'BN.1.2.3': 'BN.1.2', 'BN.1.2.4': 'BN.1.2', 'BN.1.3': 'BN.1', 'BN.1.3.1': 'BN.1.3', 'DS.1': None, 'DS.2': None, 'DS.3': None, 'BN.1.3.2': 'BN.1.3', 'BN.1.3.3': 'BN.1.3', 'BN.1.3.4': 'BN.1.3', 'BN.1.3.5': 'BN.1.3', 'BN.1.3.6': 'BN.1.3', 'BN.1.3.7': 'BN.1.3', 'BN.1.3.8': 'BN.1.3', 'EJ.1': None, 'EJ.2': None, 'BN.1.3.9': 'BN.1.3', 'BN.1.4': 'BN.1', 'BN.1.4.1': 'BN.1.4', 'BN.1.4.2': 'BN.1.4', 'BN.1.4.3': 'BN.1.4', 'BN.1.4.4': 'BN.1.4', 'BN.1.4.5': 'BN.1.4', 'BN.1.5': 'BN.1', 'BN.1.5.1': 'BN.1.5', 'BN.1.5.2': 'BN.1.5', 'BN.1.6': 'BN.1', 'BN.1.7': 'BN.1', 'BN.1.8': 'BN.1', 'BN.1.9': 'BN.1', 'BN.1.10': 'BN.1', 'BN.1.11': 'BN.1', 'BN.2': None, 'BN.2.1': 'BN.2', 'BN.3': None, 'BN.3.1': 'BN.3', 'BN.4': None, 'BN.5': None, 'BN.6': None, 'BA.2.75.6': 'BA.2.75', 'BY.1': None, 'BY.1.1': 'BY.1', 'BY.1.1.1': 'BY.1.1', 'BY.1.2': 'BY.1', 'BA.2.75.7': 'BA.2.75', 'BA.2.75.8': 'BA.2.75', 'BA.2.75.9': 'BA.2.75', 'CB.1': None, 'BA.2.75.10': 'BA.2.75', 'BA.2.76': 'BA.2', 'BA.2.78': 'BA.2', 'BA.2.79': 'BA.2', 'BA.2.82': 'BA.2', 'BA.3.1': 'BA.3', 'BA.4': 'B.1.1.529', 'BA.4.1': 'BA.4', 'BA.4.1.1': 'BA.4.1', 'BA.4.1.6': 'BA.4.1', 'BA.4.1.8': 'BA.4.1', 'BA.4.1.9': 'BA.4.1', 'BA.4.1.10': 'BA.4.1', 'BA.4.1.11': 'BA.4.1', 'BA.4.2': 'BA.4', 'BA.4.4': 'BA.4', 'BA.4.5': 'BA.4', 'BA.4.6': 'BA.4', 'BA.4.6.1': 'BA.4.6', 'BA.4.6.2': 'BA.4.6', 'BA.4.6.3': 'BA.4.6', 'BA.4.6.4': 'BA.4.6', 'BA.4.6.5': 'BA.4.6', 'DC.1': None, 'BA.4.7': 'BA.4', 'BA.5': 'B.1.1.529', 'BA.5.1': 'BA.5', 'BA.5.1.1': 'BA.5.1', 'BA.5.1.2': 'BA.5.1', 'BA.5.1.3': 'BA.5.1', 'BA.5.1.4': 'BA.5.1', 'BA.5.1.5': 'BA.5.1', 'BA.5.1.6': 'BA.5.1', 'BA.5.1.7': 'BA.5.1', 'BA.5.1.8': 'BA.5.1', 'BA.5.1.9': 'BA.5.1', 'BA.5.1.10': 'BA.5.1', 'BK.1': None, 'BA.5.1.12': 'BA.5.1', 'BA.5.1.15': 'BA.5.1', 'DL.1': None, 'BA.5.1.16': 'BA.5.1', 'BA.5.1.17': 'BA.5.1', 'BA.5.1.18': 'BA.5.1', 'BA.5.1.19': 'BA.5.1', 'BA.5.1.20': 'BA.5.1', 'BA.5.1.21': 'BA.5.1', 'BT.1': None, 'BT.2': None, 'BA.5.1.22': 'BA.5.1', 'BA.5.1.23': 'BA.5.1', 'DE.1': None, 'DE.2': None, 'BA.5.1.24': 'BA.5.1', 'BA.5.1.25': 'BA.5.1', 'DJ.1': None, 'DJ.1.1': 'DJ.1', 'DJ.1.1.1': 'DJ.1.1', 'DJ.1.2': 'DJ.1', 'DJ.1.3': 'DJ.1', 'BA.5.1.26': 'BA.5.1', 'CU.1': None, 'BA.5.1.27': 'BA.5.1', 'BA.5.1.28': 'BA.5.1', 'BA.5.1.29': 'BA.5.1', 'CL.1': None, 'CL.1.1': 'CL.1', 'CL.1.2': 'CL.1', 'CL.1.3': 'CL.1', 'BA.5.1.30': 'BA.5.1', 'BA.5.1.31': 'BA.5.1', 'BA.5.1.32': 'BA.5.1', 'BA.5.1.33': 'BA.5.1', 'EQ.1': None, 'BA.5.1.34': 'BA.5.1', 'BA.5.1.35': 'BA.5.1', 'EB.1': None, 'BA.5.1.36': 'BA.5.1', 'BA.5.1.37': 'BA.5.1', 'BA.5.1.38': 'BA.5.1', 'BA.5.2': 'BA.5', 'BA.5.2.1': 'BA.5.2', 'BF.1': None, 'BF.2': None, 'BF.3': None, 'BF.4': None, 'BF.5': None, 'BF.5.1': 'BF.5', 'BF.5.2': 'BF.5', 'BF.5.3': 'BF.5', 'BF.5.4': 'BF.5', 'BF.5.5': 'BF.5', 'BF.6': None, 'BF.7': None, 'BF.7.1': 'BF.7', 'BF.7.2': 'BF.7', 'BF.7.3': 'BF.7', 'BF.7.4': 'BF.7', 'BF.7.4.1': 'BF.7.4', 'BF.7.4.2': 'BF.7.4', 'BF.7.4.3': 'BF.7.4', 'BF.7.5': 'BF.7', 'BF.7.5.1': 'BF.7.5', 'BF.7.6': 'BF.7', 'BF.7.7': 'BF.7', 'BF.7.8': 'BF.7', 'BF.7.9': 'BF.7', 'BF.7.10': 'BF.7', 'BF.7.11': 'BF.7', 'BF.7.12': 'BF.7', 'BF.7.13': 'BF.7', 'BF.7.13.1': 'BF.7.13', 'BF.7.13.2': 'BF.7.13', 'BF.7.14': 'BF.7', 'BF.7.14.1': 'BF.7.14', 'BF.7.14.2': 'BF.7.14', 'BF.7.14.3': 'BF.7.14', 'BF.7.14.4': 'BF.7.14', 'BF.7.14.5': 'BF.7.14', 'BF.7.14.6': 'BF.7.14', 'BF.7.14.7': 'BF.7.14', 'BF.7.15': 'BF.7', 'BF.7.16': 'BF.7', 'BF.7.16.1': 'BF.7.16', 'BF.7.17': 'BF.7', 'BF.7.18': 'BF.7', 'BF.7.19': 'BF.7', 'BF.7.19.1': 'BF.7.19', 'BF.7.20': 'BF.7', 'BF.7.21': 'BF.7', 'BF.7.22': 'BF.7', 'BF.7.23': 'BF.7', 'BF.7.24': 'BF.7', 'BF.7.26': 'BF.7', 'BF.7.27': 'BF.7', 'BF.8': None, 'BF.9': None, 'BF.10': None, 'BF.10.1': 'BF.10', 'BF.11': None, 'BF.11.1': 'BF.11', 'BF.11.2': 'BF.11', 'BF.11.3': 'BF.11', 'BF.11.4': 'BF.11', 'BF.11.5': 'BF.11', 'BF.12': None, 'BF.13': None, 'BF.14': None, 'BF.15': None, 'BF.16': None, 'BF.17': None, 'BF.18': None, 'BF.19': None, 'BF.20': None, 'BF.21': None, 'BF.22': None, 'BF.23': None, 'BF.24': None, 'BF.25': None, 'BF.26': None, 'BF.27': None, 'BF.28': None, 'BF.29': None, 'BF.30': None, 'BF.31': None, 'BF.31.1': 'BF.31', 'BF.32': None, 'BF.33': None, 'BF.34': None, 'BF.35': None, 'BF.36': None, 'BF.37': None, 'BF.38': None, 'BF.38.1': 'BF.38', 'BF.38.2': 'BF.38', 'BF.38.3': 'BF.38', 'BF.39': None, 'BF.39.1': 'BF.39', 'BF.40': None, 'BF.41': None, 'BF.41.1': 'BF.41', 'BA.5.2.2': 'BA.5.2', 'BA.5.2.3': 'BA.5.2', 'BZ.2': None, 'BA.5.2.4': 'BA.5.2', 'BA.5.2.6': 'BA.5.2', 'CP.1': None, 'CP.1.1': 'CP.1', 'CP.1.2': 'CP.1', 'CP.1.3': 'CP.1', 'CP.2': None, 'CP.3': None, 'CP.4': None, 'CP.5': None, 'CP.6': None, 'CP.7': None, 'CP.8': None, 'CP.8.1': 'CP.8', 'BA.5.2.7': 'BA.5.2', 'CY.1': None, 'CY.2': None, 'BA.5.2.8': 'BA.5.2', 'BA.5.2.9': 'BA.5.2', 'BA.5.2.10': 'BA.5.2', 'BA.5.2.11': 'BA.5.2', 'BA.5.2.12': 'BA.5.2', 'BA.5.2.13': 'BA.5.2', 'BA.5.2.14': 'BA.5.2', 'BA.5.2.16': 'BA.5.2', 'BU.1': None, 'BU.2': None, 'BU.3': None, 'BA.5.2.18': 'BA.5.2', 'CR.1': None, 'CR.1.1': 'CR.1', 'CR.1.2': 'CR.1', 'CR.1.3': 'CR.1', 'CR.2': None, 'BA.5.2.19': 'BA.5.2', 'BA.5.2.20': 'BA.5.2', 'BV.1': None, 'BV.2': None, 'BA.5.2.21': 'BA.5.2', 'CN.1': None, 'CN.2': None, 'BA.5.2.22': 'BA.5.2', 'BA.5.2.23': 'BA.5.2', 'BA.5.2.24': 'BA.5.2', 'CK.1': None, 'CK.1.1': 'CK.1', 'CK.1.2': 'CK.1', 'CK.2': None, 'CK.2.1': 'CK.2', 'CK.2.1.1': 'CK.2.1', 'CK.3': None, 'DG.1': None, 'BA.5.2.25': 'BA.5.2', 'DB.1': None, 'DB.2': None, 'DB.3': None, 'BA.5.2.26': 'BA.5.2', 'BA.5.2.27': 'BA.5.2', 'CF.1': None, 'CG.1': None, 'BA.5.2.28': 'BA.5.2', 'BA.5.2.29': 'BA.5.2', 'BA.5.2.30': 'BA.5.2', 'BA.5.2.31': 'BA.5.2', 'CD.1': None, 'CD.2': None, 'BA.5.2.32': 'BA.5.2', 'BA.5.2.33': 'BA.5.2', 'CE.1': None, 'BA.5.2.34': 'BA.5.2', 'BA.5.2.35': 'BA.5.2', 'BA.5.2.36': 'BA.5.2', 'CT.1': None, 'BA.5.2.37': 'BA.5.2', 'BA.5.2.38': 'BA.5.2', 'DA.1': None, 'BA.5.2.39': 'BA.5.2', 'BA.5.2.40': 'BA.5.2', 'BA.5.2.41': 'BA.5.2', 'BA.5.2.42': 'BA.5.2', 'BA.5.2.43': 'BA.5.2', 'BA.5.2.44': 'BA.5.2', 'BA.5.2.45': 'BA.5.2', 'BA.5.2.46': 'BA.5.2', 'BA.5.2.47': 'BA.5.2', 'DQ.1': None, 'BA.5.2.48': 'BA.5.2', 'DY.1': None, 'DY.1.1': 'DY.1', 'DY.2': None, 'DY.3': None, 'DY.4': None, 'BA.5.2.49': 'BA.5.2', 'DZ.1': None, 'DZ.2': None, 'BA.5.2.50': 'BA.5.2', 'BA.5.2.51': 'BA.5.2', 'BA.5.2.52': 'BA.5.2', 'BA.5.2.53': 'BA.5.2', 'BA.5.2.54': 'BA.5.2', 'BA.5.2.55': 'BA.5.2', 'BA.5.2.56': 'BA.5.2', 'BA.5.2.57': 'BA.5.2', 'BA.5.2.58': 'BA.5.2', 'BA.5.2.59': 'BA.5.2', 'BA.5.2.60': 'BA.5.2', 'BA.5.2.61': 'BA.5.2', 'BA.5.2.62': 'BA.5.2', 'BA.5.2.63': 'BA.5.2', 'BA.5.3': 'BA.5', 'BA.5.3.1': 'BA.5.3', 'BE.1': None, 'BE.1.1': 'BE.1', 'BE.1.1.1': 'BE.1.1', 'BQ.1': None, 'BQ.1.1': 'BQ.1', 'BQ.1.1.1': 'BQ.1.1', 'CZ.1': None, 'CZ.2': None, 'BQ.1.1.2': 'BQ.1.1', 'DU.1': None, 'BQ.1.1.3': 'BQ.1.1', 'DR.1': None, 'DR.2': None, 'BQ.1.1.4': 'BQ.1.1', 'EE.1': None, 'EE.2': None, 'EE.3': None, 'EE.4': None, 'EE.5': None, 'BQ.1.1.5': 'BQ.1.1', 'DN.1': None, 'DN.1.1': 'DN.1', 'DN.1.1.1': 'DN.1.1', 'DN.1.1.2': 'DN.1.1', 'DN.1.1.3': 'DN.1.1', 'DN.1.1.4': 'DN.1.1', 'BQ.1.1.6': 'BQ.1.1', 'BQ.1.1.7': 'BQ.1.1', 'DK.1': None, 'BQ.1.1.8': 'BQ.1.1', 'DP.1': None, 'BQ.1.1.9': 'BQ.1.1', 'BQ.1.1.10': 'BQ.1.1', 'FA.1': None, 'FA.2': None, 'BQ.1.1.11': 'BQ.1.1', 'BQ.1.1.12': 'BQ.1.1', 'BQ.1.1.13': 'BQ.1.1', 'EF.1': None, 'EF.1.1': 'EF.1', 'EF.1.1.1': 'EF.1.1', 'EY.1': None, 'EF.1.2': 'EF.1', 'EF.1.3': 'EF.1', 'EF.2': None, 'BQ.1.1.14': 'BQ.1.1', 'BQ.1.1.15': 'BQ.1.1', 'DM.1': None, 'BQ.1.1.16': 'BQ.1.1', 'BQ.1.1.17': 'BQ.1.1', 'BQ.1.1.18': 'BQ.1.1', 'ED.1': None, 'ED.2': None, 'ED.3': None, 'BQ.1.1.19': 'BQ.1.1', 'BQ.1.1.20': 'BQ.1.1', 'BQ.1.1.21': 'BQ.1.1', 'BQ.1.1.22': 'BQ.1.1', 'ER.1': None, 'ER.1.1': 'ER.1', 'BQ.1.1.23': 'BQ.1.1', 'BQ.1.1.24': 'BQ.1.1', 'BQ.1.1.25': 'BQ.1.1', 'BQ.1.1.26': 'BQ.1.1', 'BQ.1.1.27': 'BQ.1.1', 'BQ.1.1.28': 'BQ.1.1', 'EH.1': None, 'BQ.1.1.29': 'BQ.1.1', 'BQ.1.1.30': 'BQ.1.1', 'BQ.1.1.31': 'BQ.1.1', 'BQ.1.1.32': 'BQ.1.1', 'DT.1': None, 'DT.2': None, 'DT.3': None, 'BQ.1.1.34': 'BQ.1.1', 'BQ.1.1.35': 'BQ.1.1', 'ET.1': None, 'BQ.1.1.36': 'BQ.1.1', 'BQ.1.1.37': 'BQ.1.1', 'BQ.1.1.38': 'BQ.1.1', 'EW.1': None, 'EW.2': None, 'EW.3': None, 'BQ.1.1.39': 'BQ.1.1', 'BQ.1.1.40': 'BQ.1.1', 'BQ.1.1.41': 'BQ.1.1', 'BQ.1.1.42': 'BQ.1.1', 'BQ.1.1.43': 'BQ.1.1', 'EZ.1': None, 'BQ.1.1.44': 'BQ.1.1', 'BQ.1.1.45': 'BQ.1.1', 'BQ.1.1.46': 'BQ.1.1', 'EN.1': None, 'BQ.1.1.47': 'BQ.1.1', 'BQ.1.1.48': 'BQ.1.1', 'BQ.1.1.49': 'BQ.1.1', 'BQ.1.1.50': 'BQ.1.1', 'BQ.1.1.51': 'BQ.1.1', 'BQ.1.1.52': 'BQ.1.1', 'EA.1': None, 'EA.2': None, 'BQ.1.1.53': 'BQ.1.1', 'BQ.1.1.54': 'BQ.1.1', 'BQ.1.1.55': 'BQ.1.1', 'BQ.1.1.56': 'BQ.1.1', 'BQ.1.1.57': 'BQ.1.1', 'BQ.1.1.58': 'BQ.1.1', 'BQ.1.1.59': 'BQ.1.1', 'BQ.1.1.60': 'BQ.1.1', 'BQ.1.1.61': 'BQ.1.1', 'BQ.1.1.62': 'BQ.1.1', 'BQ.1.1.63': 'BQ.1.1', 'BQ.1.1.64': 'BQ.1.1', 'BQ.1.1.65': 'BQ.1.1', 'ES.1': None, 'BQ.1.1.66': 'BQ.1.1', 'BQ.1.1.67': 'BQ.1.1', 'BQ.1.1.68': 'BQ.1.1', 'BQ.1.1.69': 'BQ.1.1', 'BQ.1.1.70': 'BQ.1.1', 'BQ.1.1.71': 'BQ.1.1', 'EV.1': None, 'BQ.1.1.72': 'BQ.1.1', 'FC.1': None, 'BQ.1.2': 'BQ.1', 'BQ.1.2.1': 'BQ.1.2', 'FB.1': None, 'FB.2': None, 'BQ.1.3': 'BQ.1', 'BQ.1.4': 'BQ.1', 'BQ.1.5': 'BQ.1', 'BQ.1.6': 'BQ.1', 'BQ.1.7': 'BQ.1', 'BQ.1.8': 'BQ.1', 'BQ.1.8.1': 'BQ.1.8', 'BQ.1.8.2': 'BQ.1.8', 'FF.1': None, 'BQ.1.9': 'BQ.1', 'BQ.1.10': 'BQ.1', 'BQ.1.10.1': 'BQ.1.10', 'EC.1': None, 'EC.1.1': 'EC.1', 'BQ.1.10.2': 'BQ.1.10', 'BQ.1.10.3': 'BQ.1.10', 'BQ.1.11': 'BQ.1', 'BQ.1.11.1': 'BQ.1.11', 'BQ.1.12': 'BQ.1', 'BQ.1.13': 'BQ.1', 'BQ.1.13.1': 'BQ.1.13', 'BQ.1.14': 'BQ.1', 'BQ.1.15': 'BQ.1', 'BQ.1.15.1': 'BQ.1.15', 'BQ.1.15.2': 'BQ.1.15', 'BQ.1.16': 'BQ.1', 'BQ.1.17': 'BQ.1', 'BQ.1.18': 'BQ.1', 'BQ.1.19': 'BQ.1', 'BQ.1.20': 'BQ.1', 'BQ.1.21': 'BQ.1', 'BQ.1.22': 'BQ.1', 'BQ.1.23': 'BQ.1', 'BQ.1.24': 'BQ.1', 'BQ.1.25': 'BQ.1', 'BQ.1.25.1': 'BQ.1.25', 'BQ.1.26': 'BQ.1', 'BQ.1.26.1': 'BQ.1.26', 'BQ.1.26.2': 'BQ.1.26', 'BQ.1.27': 'BQ.1', 'BQ.1.28': 'BQ.1', 'BQ.1.29': 'BQ.1', 'BQ.1.30': 'BQ.1', 'BQ.1.31': 'BQ.1', 'BQ.1.32': 'BQ.1', 'BQ.2': None, 'BE.1.2': 'BE.1', 'BE.1.1.2': 'BE.1.1', 'CC.1': None, 'BE.1.2.1': 'BE.1.2', 'DW.1': None, 'BE.1.3': 'BE.1', 'BE.1.4': 'BE.1', 'BE.1.4.1': 'BE.1.4', 'BE.1.4.2': 'BE.1.4', 'BE.1.4.4': 'BE.1.4', 'BE.2': None, 'BE.3': None, 'BE.4': None, 'BE.4.1': 'BE.4', 'BE.4.1.1': 'BE.4.1', 'CQ.1': None, 'CQ.1.1': 'CQ.1', 'CQ.2': None, 'BE.4.2': 'BE.4', 'BE.5': None, 'BE.6': None, 'BE.7': None, 'BE.8': None, 'BE.9': None, 'BE.10': None, 'BE.11': None, 'BE.12': None, 'BE.13': None, 'BA.5.3.3': 'BA.5.3', 'BA.5.3.4': 'BA.5.3', 'BA.5.3.5': 'BA.5.3', 'BA.5.5': 'BA.5', 'BA.5.5.1': 'BA.5.5', 'BA.5.5.2': 'BA.5.5', 'BA.5.5.3': 'BA.5.5', 'BA.5.6': 'BA.5', 'BA.5.6.1': 'BA.5.6', 'BA.5.6.2': 'BA.5.6', 'BW.1': None, 'BW.1.1': 'BW.1', 'BW.1.1.1': 'BW.1.1', 'BW.1.1.2': 'BW.1.1', 'BW.1.2': 'BW.1', 'BA.5.6.3': 'BA.5.6', 'BA.5.6.4': 'BA.5.6', 'BA.5.7': 'BA.5', 'BA.5.8': 'BA.5', 'BA.5.9': 'BA.5', 'BA.5.10': 'BA.5', 'BA.5.10.1': 'BA.5.10', 'DF.1': None, 'DF.1.1': 'DF.1', 'BA.5.11': 'BA.5', 'BA.5.12': 'BA.5', 'B.1.351': 'B.1', 'B.1.503': 'B.1', 'B.1.595': 'B.1', 'B.1.617': 'B.1', 'B.1.617.2': 'B.1.617', 'AY.4': 'B.1.617.2', 'AY.9.2.2': 'AY.9.2', 'AY.14': 'B.1.617.2', 'AY.25': 'B.1.617.2', 'AY.26': 'B.1.617.2', 'AY.33.2': 'AY.33', 'AY.43': 'B.1.617.2', 'AY.44': 'B.1.617.2', 'AY.46.1': 'AY.46', 'AY.46.6': 'AY.46', 'AY.103': 'B.1.617.2', 'AY.112': 'B.1.617.2', 'AY.113': 'B.1.617.2', 'AY.127': 'B.1.617.2', 'B.6': 'B', 'XAC': None, 'XAE': None, 'XAH': None, 'XAS': None, 'XAV': None, 'XAY': None, 'XAY.1': 'XAY', 'XAY.1.1': 'XAY.1', 'XAY.1.1.1': 'XAY.1.1', 'XAY.1.2': 'XAY.1', 'XAY.2': 'XAY', 'XAY.2.1': 'XAY.2', 'XAY.2.2': 'XAY.2', 'XAY.3': 'XAY', 'XAZ': None, 'XBB': None, 'XBB.1': 'XBB', 'XBB.1.1': 'XBB.1', 'XBB.1.3': 'XBB.1', 'XBB.1.4': 'XBB.1', 'XBB.1.4.1': 'XBB.1.4', 'XBB.1.5': 'XBB.1', 'XBB.1.5.1': 'XBB.1.5', 'XBB.1.5.2': 'XBB.1.5', 'XBB.1.5.3': 'XBB.1.5', 'XBB.1.5.4': 'XBB.1.5', 'XBB.1.5.5': 'XBB.1.5', 'XBB.1.5.6': 'XBB.1.5', 'XBB.1.5.7': 'XBB.1.5', 'XBB.1.5.8': 'XBB.1.5', 'XBB.1.5.9': 'XBB.1.5', 'XBB.1.5.10': 'XBB.1.5', 'XBB.1.5.11': 'XBB.1.5', 'XBB.1.5.12': 'XBB.1.5', 'XBB.1.5.13': 'XBB.1.5', 'XBB.1.5.14': 'XBB.1.5', 'XBB.1.5.15': 'XBB.1.5', 'XBB.1.5.16': 'XBB.1.5', 'XBB.1.5.17': 'XBB.1.5', 'XBB.1.5.18': 'XBB.1.5', 'XBB.1.5.19': 'XBB.1.5', 'XBB.1.5.20': 'XBB.1.5', 'XBB.1.5.21': 'XBB.1.5', 'XBB.1.5.22': 'XBB.1.5', 'XBB.1.5.23': 'XBB.1.5', 'XBB.1.5.24': 'XBB.1.5', 'XBB.1.5.25': 'XBB.1.5', 'XBB.1.5.26': 'XBB.1.5', 'XBB.1.5.27': 'XBB.1.5', 'XBB.1.5.28': 'XBB.1.5', 'XBB.1.5.29': 'XBB.1.5', 'XBB.1.5.30': 'XBB.1.5', 'XBB.1.5.31': 'XBB.1.5', 'XBB.1.5.32': 'XBB.1.5', 'XBB.1.5.33': 'XBB.1.5', 'XBB.1.5.34': 'XBB.1.5', 'XBB.1.5.35': 'XBB.1.5', 'XBB.1.5.36': 'XBB.1.5', 'XBB.1.5.37': 'XBB.1.5', 'XBB.1.5.38': 'XBB.1.5', 'XBB.1.5.39': 'XBB.1.5', 'XBB.1.6': 'XBB.1', 'XBB.1.7': 'XBB.1', 'XBB.1.8': 'XBB.1', 'XBB.1.9': 'XBB.1', 'XBB.1.9.1': 'XBB.1.9', 'XBB.1.9.2': 'XBB.1.9', 'XBB.1.9.3': 'XBB.1.9', 'XBB.1.9.4': 'XBB.1.9', 'XBB.1.9.5': 'XBB.1.9', 'XBB.1.10': 'XBB.1', 'XBB.1.11': 'XBB.1', 'XBB.1.11.1': 'XBB.1.11', 'XBB.1.12': 'XBB.1', 'XBB.1.13': 'XBB.1', 'XBB.1.14': 'XBB.1', 'XBB.1.15': 'XBB.1', 'XBB.1.16': 'XBB.1', 'XBB.1.16.1': 'XBB.1.16', 'XBB.1.17': 'XBB.1', 'XBB.1.17.1': 'XBB.1.17', 'XBB.1.17.2': 'XBB.1.17', 'XBB.1.18': 'XBB.1', 'XBB.1.18.1': 'XBB.1.18', 'XBB.1.19': 'XBB.1', 'XBB.1.19.1': 'XBB.1.19', 'XBB.1.20': 'XBB.1', 'XBB.1.21': 'XBB.1', 'XBB.1.22': 'XBB.1', 'XBB.1.22.1': 'XBB.1.22', 'XBB.1.22.2': 'XBB.1.22', 'XBB.1.23': 'XBB.1', 'XBB.1.24': 'XBB.1', 'XBB.1.25': 'XBB.1', 'XBB.1.26': 'XBB.1', 'XBB.1.27': 'XBB.1', 'XBB.1.28': 'XBB.1', 'XBB.1.29': 'XBB.1', 'XBB.1.30': 'XBB.1', 'XBB.2': 'XBB', 'XBB.2.1': 'XBB.2', 'XBB.2.2': 'XBB.2', 'XBB.2.3': 'XBB.2', 'XBB.2.3.1': 'XBB.2.3', 'XBB.2.3.2': 'XBB.2.3', 'XBB.2.4': 'XBB.2', 'XBB.2.5': 'XBB.2', 'XBB.2.6': 'XBB.2', 'XBB.2.7': 'XBB.2', 'XBB.2.7.1': 'XBB.2.7', 'XBB.2.8': 'XBB.2', 'XBB.3': 'XBB', 'XBB.3.1': 'XBB.3', 'XBB.3.2': 'XBB.3', 'XBB.3.3': 'XBB.3', 'XBB.4': 'XBB', 'XBB.4.1': 'XBB.4', 'XBB.5': 'XBB', 'XBB.6': 'XBB', 'XBB.6.1': 'XBB.6', 'XBB.7': 'XBB', 'XBB.8': 'XBB', 'XBC': None, 'XBC.1': 'XBC', 'XBC.1.1': 'XBC.1', 'XBC.1.1.1': 'XBC.1.1', 'XBC.1.2': 'XBC.1', 'XBC.1.2.1': 'XBC.1.2', 'XBC.1.3': 'XBC.1', 'XBC.1.4': 'XBC.1', 'XBC.1.5': 'XBC.1', 'XBC.1.6': 'XBC.1', 'XBC.2': 'XBC', 'XBC.2.1': 'XBC.2', 'XBD': None, 'XBE': None, 'XBF': None, 'XBF.1': 'XBF', 'XBF.2': 'XBF', 'XBF.3': 'XBF', 'XBF.4': 'XBF', 'XBF.5': 'XBF', 'XBF.6': 'XBF', 'XBF.7': 'XBF', 'XBF.7.1': 'XBF.7', 'XBF.8': 'XBF', 'XBF.8.1': 'XBF.8', 'XBF.9': 'XBF', 'XBG': None, 'XBH': None, 'XBJ': None, 'XBJ.1': 'XBJ', 'XBJ.1.1': 'XBJ.1', 'XBJ.2': 'XBJ', 'XBJ.3': 'XBJ', 'XBJ.4': 'XBJ', 'XBK': None, 'XBK.1': 'XBK', 'XBL': None, 'XBM': None, 'XBN': None, 'XBP': None, 'XBQ': None, 'XBR': None, 'XBS': None, 'XBT': None, 'XBU': None, 'XBV': None, 'XBW': None, 'XBY': None, 'XBZ': None}

def getCovLineages():
    """Returns dict of lineages mapped to their immediate parents based on data from 'cov-lineages', downloading new data, if possible"""

    try:
        info = subprocess.check_output("curl -fsL https://raw.githubusercontent.com/cov-lineages/lineages-website/master/data/lineages.yml", shell=True).decode()
    except:
        print("Could not download data from https://raw.githubusercontent.com/cov-lineages/lineages-website/master/data/lineages.yml. Using defaults instead.")
        return lineage_parents_default
    import yaml
    lineages_data = yaml.safe_load(info)
    lineage_parents = {d["name"]:d.get("parent") for d in lineages_data}
    return lineage_parents

def listParents(lineage,parents_dict):
    """Returns list of parents for `lineage` ascending from immediate parent to root/None
    
    Args:
    * `lineage` (str): the lineage
    * `parents_dict` (dict): dict mapping lineages to their immediate parents
    """

    parents = []
    parent = ""
    while parent is not None:
        parent = parents_dict.get(lineage)
        if parent:
            parents.append(parent)
        lineage = parent
    return parents

def getAggDF(file,name):
    """Returns freyja aggregated DataFrame
    
    Args:
    * `file` (str|Path): file to read in as DataFrame
    * `name` (str): label for this dataset
    """

    df = pd.read_csv(file,sep="\t")
    df = df[df["Unnamed: 0"].notna()]
    df = df.rename(columns={"Unnamed: 0":"Sample name"})
    df["scheme"] = name
    return df

def _updateSummaryDict(main_dict:dict,adjustments:dict):
    """Updates `main_dict` using `adjustments`.

    If a lineage <key> ends with '.*', it and its sublineages will all recieve the <value>
    """

    if not adjustments:
        return main_dict

    main_dict.update({k:v for k,v in adjustments.items() if not k.endswith(".*")})
    main_dict.update({k.rstrip('.*'):v for k,v in adjustments.items() if k.endswith(".*")})
    # # old, simple way
    # return main_dict
    for k in main_dict.keys():
        for update_key, update_value in adjustments.items():
            if update_key.endswith(".*"):
                base = update_key.replace(".*","")
                if k == base or k.startswith(f"{base}."):
                    main_dict[k] = update_value
            else:
                if k == update_key:
                    main_dict[k] = update_value
    # temp check:

    return main_dict

def summarizeLineages(lineage_list:list, abundance_list:list, summary_dict:dict):
    """Converts unsummarized `lineage_dict` to summarized lineage and abundance lists
    
    Args:
    * `lineage_list` (list): lineages to summarize
    * `abundance_list` (list): abundances associated with each lineage in `lineage_list`
    * `summary_dict` (dict): overrides for default summary dict used by Freyja
    """

    # for lineage, abundance in lineage_dict.items():
    #     for summary_lineage,s_abundance in 
    summarized_lineages = map_to_constellation(lineage_list, abundance_list, summary_dict)
    if len(summarized_lineages) == 1:
        if summarized_lineages[0][1] > .9999:
            summarized_lineages = [(summarized_lineages[0][0], 1.0)]
    # print("summarized_lineages:",summarized_lineages)
    # with open("/projects/enviro_lab/decon_compare/freyja/MixedControl-plots/lineages.tsv", "w") as out:
    #     for l, a in summary_dict.items():
    #         out.write(f"{l}\t{a}\n")
    found_lineages = set()
    lineages, abundances = [], []
    for lineage, abundance in summarized_lineages:
        lineages.append(lineage)
        abundances.append(abundance)
        if lineage in found_lineages:
            print("already exists: l")
            exit(1)
    return lineages, abundances

def getLineagesAndAbundances(r):
    if isinstance(r["lineages"],  float) and np.isnan(r["lineages"]):
        lineages = []
        abundances = []
    else:
        lineages = r["lineages"].split(" ") if r["lineages"] else []
        abundances = [float(x) for x in r["abundances"].split(" ")] if r["abundances"] else []
    return lineages, abundances

def getLineageAbundanceDfs(agg_df,summarized=False,date_col=None,summary_dict:dict={}):
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
            if not summarized:
                lineages, abundances = getLineagesAndAbundances(r)
            else:
                if summary_dict:
                    # lineages = r["lineages"].split(" ")
                    # abundances = [float(x) for x in r["abundances"].split(" ")]
                    lineages, abundances = getLineagesAndAbundances(r)
                    # print()
                    # print(f"sample = {r['Sample name']}")
                    # print("lineages:",lineages)
                    # print("abundances:",abundances)
                    lineages, abundances = summarizeLineages(lineages, abundances, summary_dict)
                else:
                    summarized_results = r["summarized"].lstrip("[(").rstrip("])").split("), (")
                    lineages,abundances = [],[]
                    # print(summarized_results)
                    for grp in summarized_results:
                        lin,ab = grp.split(", ")
                        lin = lin.strip("'")
                        # print(lin,ab)
                        lineages.append(lin)
                        abundances.append(float(ab))
            # prepare/yield lineage/abundance df
            scheme = r["scheme"]
            sn_col = [r["Sample name"]]*len(lineages)
        # create and yield dataframe
        data = {"Sample name":sn_col,"lineages":lineages,"abundances":abundances,"scheme":scheme}
        # include date info, if requested
        if date_col:
            data[date_col] = r[date_col]
        yield pd.DataFrame(data)

def getLineageCol(summarized=False,superlineage=None,super_method="dot-split"):
    """Returns consistent name for different lineage columns, depending on specifications

    Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False.
        * `superlineage` (bool|int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None.
        * `super_method` (bool): indicates method used to find superlineages.
            "dot-split" (default): split `lineage` on ".". 
            "cov-lineages": use definitions from cov-lineage.
    """

    if superlineage is None:
        return "lineages"
    else: # if superlineage requested:
        if summarized:
            raise AttributeError("`superlineage` details cannot be provided if `summarized` is True")
        return f"superlineage-{superlineage}-{super_method}"

def _parse_file_map(file_map,compare:bool):
    """Converts `file_map` argument from multiple input datatypes to dictionary"""

    if isinstance(file_map, dict):
        file_dict = {Path(f):n for f,n in file_map.items()}
    elif isinstance(file_map,(str,Path)):
        file_dict = {Path(file_map):Path(file_map).stem }
    elif isinstance(file_map,(list,set,tuple)):
        file_dict = {Path(file):Path(file).stem for file in file_map}
    else:
        raise AttributeError("`filemap` must be a string, Path, iterable, or dict")
    for f in file_dict.keys():
        if not f.exists():
            raise FileNotFoundError(f)
    # determine whether this dataset is a comparison or not
    num_schemes_found = len(set(file_dict.values()))
    comparison = False if num_schemes_found==1 else compare
    # reset num_schemes and file_dict if multiple files but not a batch comparison
    if num_schemes_found > 1 and not comparison:
        num_schemes_found = 1
        for key in file_dict.keys():
            file_dict[key] = "Freyja Data"
    num_schemes = num_schemes_found
    return file_dict,comparison,num_schemes

def _parse_agg_df(agg_df:pd.DataFrame,compare:bool):
    """Determines whether this dataset is for comparison or not"""

    file_dict = "Files unknown"
    if "scheme" in  agg_df.columns:
        num_schemes = len(agg_df["scheme"].unique())
    else:
        agg_df["scheme"] = "all"
        num_schemes = 1
    comparison = num_schemes>1 if compare else False
    return file_dict,comparison,num_schemes,agg_df

def lowest_non_zero(abundance_map):
    """Returns value of lowest-abundance sample that is not in the other or below-threshold categories
    
    Args:
        * `abundance_map` (dict): key=lineage_name, value=abundance; if empty, returns 1
    """

    abundances = set()
    for k,v in abundance_map.items():
        if v == 0:
            continue
        elif k in  ("below-threshold","Other"):
            continue
        else:
            abundances.add(v)
    return min(abundances,default=1)

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

    def __init__(self,file_map=None,colormap={},compare=True,date_col=None,agg_df=None,summary_dict={}) -> None:
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
        * `summary_dict` (dict): overrides to use when summarizing lineages. If provided, summarized lineages from `agg_df` will not be considered.
        """

        self.colorlist = colors2list(color2hex)
        self.color_index = 0
        self.date_col = date_col
        self.summary_dict = summary_dict

        if "Other" not in colormap.keys():
            colormap["Other"] = "grey"
        if "below-threshold" not in colormap.keys():
            colormap["below-threshold"] = "black"
        self.colormap = colormap
        self.lineage_parent_list = {}
        # use input dataframe
        if isinstance(agg_df,pd.DataFrame):
            self.file_dict,self.compare,self.num_schemes,agg_df = _parse_agg_df(agg_df=agg_df,compare=compare)
        # read in files as DataFrames for further analysis
        else:
            self.file_dict,self.compare,self.num_schemes = _parse_file_map(file_map=file_map,compare=compare)
            agg_df = self._getCombinedAggDf()
        # convert to dict with minimum columns ("lineages","abundances")
        self.freyja_df = self._getFreyjaDf(agg_df)
        self.summarized_freyja_df = self._getFreyjaDf(agg_df,summarized=True)
        self.percent_expected_df = None
        self.summarized_percent_expected_df = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(compare: {self.compare}, data: {list(self.file_dict.values()) if isinstance(self.file_dict,dict) else self.file_dict})"

    def listSuperlineages(self):
        """Uses cov-lineages parents dict to list out parents in order for each lineage"""

        if not self.lineage_parent_list:
            parents_dict = getCovLineages()
            all_lineages = set(self.freyja_df["lineages"].unique())
            self.lineage_parent_list = {lineage:listParents(lineage,parents_dict) for lineage in parents_dict.keys() if lineage in all_lineages}
        return self.lineage_parent_list

    def getParents(self,lineage):
        """Returns list of all parents of `lineage` from most to least specific"""

        # if lineage not in cov-lineages list, return list from dict
        if lineage in self.lineage_parent_list.keys():
            return self.lineage_parent_list.get(lineage)
        # if lineage not in cov-lineages list, revert to getting immediate parent by dot-splitting then seeking the parent's parents
        if "." not in lineage:
            return []
        parent = ".".join(lineage.split(".")[:-1])
        return [parent] + self.getParents(parent)
        
    def getSuperLineage(self,lineage,level=0,super_method:Literal['dot-split','cov-lineages']='dot-split'):
        """Returns superlineage of `lineage` at given `level`
        
        Args:
        * `lineage` (str): the lineage.
        * `level` (int): maximum number of sublineages of the superlineage to return (0 gives the base superlineage, -1 give the immediate superlineage).
        * `super_method` (bool): indicates method used to find superlineages.
            "dot-split" (default): split `lineage` on ".". 
            "cov-lineages": use definitions from cov-lineage (downloading, if `curl` is available in the shell).
        """

        if lineage in ["Undetermined","Error","Other"]:
            return lineage
        if super_method=='dot-split':
            if level == -1:
                superlineage = ".".join(lineage.split(".")[:-1])
            else:
                superlineage = ".".join(lineage.split(".")[:level+1])
        elif super_method=='cov-lineages':
            self.listSuperlineages()
            # list parents from most general to most specific
            parents = self.getParents(lineage)[::-1]
            # print(lineage,parents)
            if level > len(parents)-1:
                superlineage = lineage if "." not in lineage else ".".join(lineage.split(".")[:level+1])
            elif len(parents) == 0:
                return lineage
            else:
                # print("level, parents:",level,parents[level])
                superlineage = parents[level]
        else:
            raise AttributeError("`super_method` must be one of 'dot-split' or 'cov-lineages'")
        return superlineage+".*"

    def _getCombinedAggDf(self):
        """Returns freyja aggregated df combining dfs for each file,name pair in `rename_scheme`
        
        Adds an extra column "scheme" which holds the `name` details for each file
        
        Args: (Not currently supported)
        * `rename_scheme` (dict): key:`file`,value:`name`
        """

        return pd.concat((getAggDF(file,name) for file,name in self.file_dict.items()))
    
    def updateSummaryDict(self):
        """Uses freyja summary dict as base and adds in user-supplied `summary_dict` entries"""

        mapDict = buildLineageMap("")
        if "Other" not in mapDict.keys():
            mapDict["Other"] = "Other"
        mapDict = _updateSummaryDict(main_dict=mapDict, adjustments=self.summary_dict)
        self.summary_dict = mapDict

    # convert agggregated data to lineage/abundance df (summarized or all)
    def _getFreyjaDf(self,agg_df,summarized=False):
        """Returns DataFrame of all lineages, their abundances, and the related sample/scheme
        
        Args:
        * `agg_df` (DataFrame): freyja aggreagated outfile(s) as df
        * `summarized` (bool): whether to use summarized lineages rather than all lineages lineages
        """

        if summarized:
            self.updateSummaryDict()

        # create and concat dfs for each row
        df = pd.concat((
            sample_abundance_df for sample_abundance_df in getLineageAbundanceDfs(agg_df,summarized=summarized,date_col=self.date_col,summary_dict=self.summary_dict)
        ))
        df = df.drop_duplicates()
        # finalize data type
        df["abundances"] = df["abundances"].astype(float)
        if self.date_col:
            df[self.date_col] = pd.to_datetime(df[self.date_col])
        df = df.reset_index().drop(columns=["index"])
        return df

    def getTaxonomyDf(self,summarized=False):
        """Returns DataFrame where columns are lineages, rows are samples"""

        df = self.summarized_freyja_df if summarized else self.freyja_df
        df = df.pivot(index="Sample name", columns="lineages", values="abundances").T
        return df

    # Plotting
    def getPlottingDf(self,summarized=False,superlineage=None,samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,minimum=0.05,df=None,filter=True,super_method='dot-split'):
        """Returns DataFrame of desired data/samples for plotting
        
        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool|int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
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
            abundance_df = self.addSuperLineageCol(superlineage=superlineage,summarized=summarized,df=df,super_method=super_method)
        else:
            if not summarized:
                self.addSuperLineageCol(superlineage=superlineage,summarized=summarized,super_method=super_method)
            abundance_df:pd.DataFrame = self.summarized_freyja_df.copy() if summarized else self.freyja_df.copy()
        if not filter:
            return abundance_df
        if not isinstance(samples,str):
            abundance_df = abundance_df[abundance_df["Sample name"].isin(samples)]
        if include_pattern is not None:
            abundance_df = abundance_df[abundance_df["Sample name"].str.contains(include_pattern)]
        if exclude_pattern is not None:
            abundance_df = abundance_df[abundance_df["Sample name"].str.contains(exclude_pattern)]
        if (start_date or end_date) and not self.date_col:
            raise AttributeError("Can't use `start_date` or `end_date` if no `date_col` attribute provided")
        if start_date:
            abundance_df = abundance_df[abundance_df[self.date_col]>=start_date]
        if end_date:
            abundance_df = abundance_df[abundance_df[self.date_col]<=end_date]
        if minimum > 0:
            abundance_df = abundance_df[abundance_df["abundances"]>=minimum]
        return abundance_df
    
    def update_colormap(self,fig):
        """Uses each Bar in `fig` to update the colormap"""

        for bar in fig.data:
            if bar.marker.color is None:
                bar.marker.color = self.colormap[bar.name] = self.colorlist[self.color_index % len(self.colorlist)]
                self.color_index += 1

    def orderLineages(self,summarized=False,superlineage=None,samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,minimum=0.05,ascending=False,df=None,filter=True,super_method='dot-split'):
        """Returns a df of desired lineages and abundances roughly organized from most to least common in the filtered dataset

        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool|int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
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
        lineage_col = getLineageCol(summarized=summarized,superlineage=superlineage,super_method=super_method)
        return (freyja_df[[lineage_col,"abundances"]].groupby(lineage_col).sum()/len(freyja_df["Sample name"].unique())).sort_values(by=["abundances"],ascending=ascending).reset_index()

    def listLineages(self,summarized=False,superlineage=None,samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,minimum=0.05,ascending=False,num_lineages=-1,df=None,filter=True,super_method='dot-split'):
        """Returns a list of desired lineages roughly organized from most to least common in the filtered dataset

        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool|int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
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

        lineage_col = getLineageCol(summarized=summarized,superlineage=superlineage,super_method=super_method)
        ordered_lineages_df = self.orderLineages(summarized=summarized,superlineage=superlineage,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=minimum,ascending=ascending,df=df,filter=filter,super_method=super_method)
        return ordered_lineages_df[lineage_col].to_list()[:num_lineages]

    def addSuperLineageCol(self,summarized=False,superlineage=None,df=None,super_method='dot-split'):
        """Adds superlineage column to freyja df if not yet there

        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool|int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `df` (DataFrame): dataframe to use and filter rather than internal freyja_df, defaults to None
        """

        lineage_col = getLineageCol(superlineage=superlineage,summarized=summarized,super_method=super_method)
        if isinstance(df,pd.DataFrame):
            if lineage_col not in df.columns:
                df[lineage_col] = df["lineages"].apply(self.getSuperLineage,level=superlineage,super_method=super_method)
            return df
        else:
            if lineage_col not in self.freyja_df.columns:
                self.freyja_df[lineage_col] = self.freyja_df["lineages"].apply(self.getSuperLineage,level=superlineage,super_method=super_method)
            return self.freyja_df

    def addDates(self,data,sample_col,date_col):
        """Adds date column to internal freyja_df
        
        Args:
        * `data` (str|Path|DataFrame|list): DataFrame(s) or file name(s) containing date data to add
        * `sample_col` (str): name of column containing sample names
        * `date_col` (str): name of column containing dates
        """

        if date_col in self.freyja_df.columns:
            raise Exception(f"'{__name__}' can only be used if `date_col` not already in dataset. To remove `date_col` ('{date_col}'), use method {self.__class__.__name__}.removeDateCol()")
        self.date_col = date_col
        if isinstance(data,(str,Path,pd.DataFrame)):
            data = [data]
        def getDateDF(item,sample_col,date_col):
            if isinstance(item,pd.DataFrame):
                return item[[sample_col,date_col]]
            if isinstance(item,(Path,str)):
                return pd.read_csv(Path(item))[[sample_col,date_col]]

        date_df = pd.concat((getDateDF(item,sample_col,date_col) for item in data))
        self.freyja_df = self.freyja_df.merge(date_df,left_on="Sample name",right_on=sample_col,how='left').drop(columns=sample_col)
        self.summarized_freyja_df = self.summarized_freyja_df.merge(date_df,left_on="Sample name",right_on=sample_col,how='left').drop(columns=sample_col)

    def removeDateCol(self):
        """Removes current date_col from freyja_df"""

        self.freyja_df = self.freyja_df.drop(columns=self.date_col)
        self.summarized_freyja_df = self.summarized_freyja_df.drop(columns=self.date_col)
        self.date_col = None

    def plotAppearance(self,summarized=False,superlineage=None,minimum=0.05,fn=None,title="Freyja lineage appearance over time",samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,num_lineages=20,super_method='dot-split',sort_by="abundances"):
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
        * `start_date` (str): First date of samples to include. Defaults to None.
        * `end_date` (str): First date of samples to include. Defaults to None.
        * `super_method` (str): method to use for determining superlineage. Defaults to 'dot-split'
        * `sort_by` (str): field used to sort bar placement. Defaults to 'abundances'. 
        """

        if not self.date_col:
            raise AttributeError(f"`date_col` required in {self.__class__.__name__}{".freyja_df" if not summarized else ".summarized_freyja_df"} to plot time series data. See {self.__class__.__name__}.addDates() to add that info.")
        freyja_df = self.getPlottingDf(summarized=summarized,superlineage=superlineage,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=minimum)
        lineage_col = getLineageCol(superlineage=superlineage,summarized=summarized,super_method=super_method)
        lineage_list = self.listLineages(superlineage=superlineage,summarized=summarized,df=freyja_df,num_lineages=num_lineages,filter=False,super_method=super_method)
        freyja_df = freyja_df[freyja_df[lineage_col].isin(lineage_list)]
        freyja_df = freyja_df.sort_values(by=sort_by)
        fig = px.scatter(
            freyja_df,
            x=self.date_col,
            y=lineage_col,
            # colormap=self.colormap,
            color=lineage_col,
            title=title,
            facet_col="scheme" if self.compare else None,
        )
        if fn:
            save(fig,fn)
        return fig
    
    def addDatePeriodCol(self,freyja_df,date_col,group_by_col,period):
        """Adds a column for the desired date period to freyja_df
        Args:
        * `group_by` (str): field by which to separate bars.
        * `freyja_df` (DataFrame): Long df with fields (Sample name, Lineages, Abundances, etc.) 
        * `date_col` (str): name of the date field in the metadata
        * `group_by_col` (str): column name to use when seeking each grouping
        * `period` (str): if `group_by=="date"`, the time period to use for each grouping.
        """

        period_strftime_map = dict(day="%Y-%m-%d",week="%Y-%m-%d",month="%Y-%m",year="%Y",)
        if period == "week":
            period_col = "Weeknum"
            if "Weeknum" not in freyja_df.columns:
                freyja_df["Weeknum"] = freyja_df[date_col].apply(lambda x: (x - timedelta(days=x.dayofweek) + timedelta(days=3)))
        else:
            period_col = date_col
        freyja_df[group_by_col] = [pandas_datetime.strftime(period_strftime_map[period]) for pandas_datetime in freyja_df[period_col]]
        return freyja_df

    def checkGroupByDetails(self,group_by,freyja_df,date_col,period='week',split_by_scheme=False):
        """Prepares to group by date, if needed

        Args:
        * `group_by` (str): field by which to separate bars.
        * `freyja_df` (DataFrame): Long df with fields (Sample name, Lineages, Abundances, etc.) 
        * `date_col` (str): name of the date field in the metadata
        * `period` (str): if `group_by=="date"`, the time period to use for each grouping. Defaults to 'week'
        * `split_by_scheme` (bool): if `True` and group_by=="date", abundance value will be relative to the number of samples within the same scheme rather than all samples in the same period. Defaults to False
        """

        if group_by=="sample":
            group_by_col:str="Sample name"
        else: # group_by=="date"
            if not date_col:
                date_col = self.date_col
                if not date_col:
                    raise AttributeError("Name of `date_col` must be provided if grouping by date")
            group_by_col = f"Time ({period}s)"
            if group_by_col not in freyja_df.columns:
                freyja_df = self.addDatePeriodCol(freyja_df=freyja_df,date_col=date_col,group_by_col=group_by_col,period=period)
            if not split_by_scheme:
                periods = {time_period:len(freyja_df.loc[(freyja_df[group_by_col]==time_period),"Sample name"].unique()) for time_period in freyja_df[group_by_col].unique()}
                freyja_df["abundances"] = freyja_df.apply(lambda x: x["abundances"]/periods[x[group_by_col]], axis=1)
            else:
                periods = {}
                for scheme in freyja_df["scheme"].unique():
                    scheme_df = freyja_df[freyja_df["scheme"]==scheme]
                    periods[scheme] = {time_period:len(scheme_df.loc[(scheme_df[group_by_col]==time_period),"Sample name"].unique()) for time_period in scheme_df[group_by_col].unique()}
                freyja_df["abundances"] = freyja_df.apply(lambda x: x["abundances"]/periods[x["scheme"]][x[group_by_col]], axis=1)
            # print("Periods: {}".format(periods))

        return group_by_col,date_col,freyja_df

        
    def getNearestSuperLineage(self,lineage,allowed_supers=None,original_lineage=None):
        """Returns the immediate parent superlineage of `lineage`
        
        Args:
            * `lineage` (str): the lineage to get parent of
            * `allowed_supers` (str): a collection of lineages allowed to be superlineages # not used?
            * `original_lineage` (str): used internally if looping through multiple iterations of this function 
        """

        if original_lineage is None:
            original_lineage = lineage
        superlineage = self.getSuperLineage(lineage,level=-1,super_method='dot-split').strip(".*")
        if not superlineage and "." not in lineage:
            superlineage = self.getSuperLineage(lineage,level=-1,super_method='cov-lineages').strip(".*")
            if not superlineage and "." not in lineage:
                return lineage
        # superlineage = self.getSuperLineage(lineage,level=-1,super_method='cov-lineages').strip(".*")
        # print("found:",superlineage)
        if not allowed_supers:
            return superlineage
        elif superlineage in allowed_supers:
            # print("good find")
            return superlineage
        elif "." not in superlineage:
            return superlineage
        elif superlineage == lineage:
            raise Exception()
        if not superlineage:
            # if "." not in lineage: return lineage
            print("no superlineage for",lineage)
            exit()
        if superlineage not in allowed_supers:
            # print(superlineage,"not allowed")
            return self.getNearestSuperLineage(superlineage,allowed_supers,original_lineage=original_lineage)
        # else:
        #     print(f"can't find superlineage {superlineage} for lineage {lineage}")

    def plotLineagesSinglePlot(self, lineages, schemes, freyja_df, group_by_col, lineage_col, minimum, return_df=False, threshold_strategy:Literal["other","superlineage"]="other", sort_by="lineages", y_title="Abundance", x_title="Samples", ordered_lineages=None):
        """Returns stacked bar chart showing lineage abundances for each sample
        
        Args:
        * `lineages` (list): lineages to include in output
        * `schemes` (list): the names of each scheme (used for naming each bar and setting how many are needed)
        * `freyja_df` (DataFrame): filtered dataframe to plot by
        * `group_by_col` (str): column name to use when seeking each grouping
        * `lineage_col` (str): column name to use when seeking each lineage
        * `minimum` (float): minimum abundance value to include in plot - anything less is categorized in "Other", defualts to 0.05
        * `return_df` (bool): a flag to return DataFrame insead of fig
        * `threshold_strategy` (str): where to place abundances for lineages below threshold. If "other" -> "Other" group; if "superlinege" -> added to abundance for superlineage.
        * `sort_by` (str): field used to sort dataframe and bars. Defaults to 'lineages' which attempts to order by lineage name. Use 'x' to sort by sample name. Use 'y' to sort by abundance.
        * `y_title` (str): title for y-axis
        * `x_title` (str): title for x-axis
        * `ordered_lineages` (list): list of lineages for ordering legend and bar stacks. Defaults to None which includes all lineages, unordered.
        """

        data = {
            "x":[],"y":[],"lineages":[],
            }
        if not return_df:
            fig = go.Figure()

        non_other_counts = {}
        other_counts = {}
        for lineage in lineages:
            lineage_df = freyja_df[freyja_df[lineage_col]==lineage]
            for scheme in schemes:
                scheme_df = lineage_df[lineage_df["scheme"]==scheme]
                for grouping in scheme_df[group_by_col].unique():
                    sample = f"{grouping}-{scheme}" if len(schemes) > 1 else grouping
                    abundance = scheme_df.loc[scheme_df[group_by_col]==grouping, "abundances"].sum()
                    if not isinstance(abundance, (np.floating, float)):
                        raise(f"weird abundance for {sample}: {abundance}")
                        # abundance = 0
                    # save "other"s to figure out later
                    if lineage.lower() == "other":
                        other_counts[sample] = other_counts.get(sample, 0) + abundance
                    elif threshold_strategy == "other" and abundance < minimum:
                        other_counts[sample] = other_counts.get(sample, 0) + abundance
                    else:
                        data["y"].append(abundance)
                        data["x"].append(sample)
                        data["lineages"].append(lineage)
                        non_other_counts[sample] = non_other_counts.get(sample, 0) + abundance

        for sample, count in non_other_counts.items():
            data["x"].append(sample)
            data["y"].append(1-count)
            data["lineages"].append("Other")

        df = pd.DataFrame(data)
        df = df.sort_values(sort_by)

        if threshold_strategy == "superlineage":
            grouping_dfs = []
            for grouping in df["x"].unique():
                gdf = df[df["x"]==grouping]
                abundance_map = dict(zip(gdf['lineages'],gdf["y"]))
                while lowest_non_zero(abundance_map) < minimum:
                    extra_abundance_map = {}
                    for lineage,abundance in abundance_map.items():
                        if lineage in  ("below-threshold","Other"):
                            continue
                        elif abundance == 0:
                            continue
                        elif abundance < minimum:
                            superlineage = self.getNearestSuperLineage(lineage)
                            if superlineage == lineage:
                                superlineage = "below-threshold"
                            if not abundance_map.get(superlineage):
                                extra_abundance_map[superlineage] = extra_abundance_map.get(superlineage, 0) + abundance
                            else:
                                abundance_map[superlineage] = abundance_map[superlineage] + abundance
                            abundance_map[lineage] = 0
                    abundance_map.update(extra_abundance_map)
                new_gdf = pd.DataFrame({"lineages":abundance_map.keys(),"y":abundance_map.values(),
                                        "x":[grouping]*len(abundance_map),
                                        })
                grouping_dfs.append(new_gdf)

            df = pd.concat(grouping_dfs)
            lineages2drop = [lin for lin in lineages if df.loc[df["lineages"]==lin, "y"].sum()==0]
            df = df[~df['lineages'].isin(lineages2drop)]

        if return_df:
            return df

        # create plot
        non_other_lineages = [lin for lin in df["lineages"].unique() if lin not in ('Other','below-threshold')]
        if ordered_lineages is not None:
            non_other_lineages = set(non_other_lineages)
            non_other_lineages = [l for l in ordered_lineages if l in non_other_lineages]
        lineage_list = non_other_lineages + ["Other"]
        if threshold_strategy == 'superlineage':
            lineage_list.append('below-threshold')

        for lineage in lineage_list:
            lindf = df[df["lineages"]==lineage]
            # skip lineages that are all 0 (or below minimum)
            if list(lindf["y"].unique()) == [0]:
                # print("Skipping because all 0s for",lineage)
                continue
            lindf = lindf.sort_values("x")
            fig.add_bar(
                x=lindf["x"],y=lindf["y"],name=lineage,
                text=lineage,textposition="inside",
                marker_color=self.colormap.get(lineage),
                )
        self.update_colormap(fig)
        if y_title:
            fig.update_layout(yaxis_title=y_title,xaxis_title=x_title)
        return fig

    def plotLineagesSubplots(self, lineages, schemes, freyja_df, group_by_col, lineage_col, minimum, subplot_order=None, return_df=False, threshold_strategy:Literal["other","superlineage"]="other", sort_by="lineages", y_title="Abundance",x_title="Samples", ordered_lineages=None):
        """Returns stacked bar charts showing lineage abundances for each grouping
        
        Args:
        * `lineages`: list of lineages to plot
        * `schemes`: list of schemes to plot (each in a separate subplot with shared x-axis)
        * `freyja_df` (DataFrame): df to plot from
        * `group_by_col` (str): field by which to separate bars.
        * `lineage_col` (str): field to use to gather lineage names.
        * `minimum` (float): minimum abundance value to include in plot - anything less is categorized in "Other", defualts to 0.05
        * `subplot_order` (str): list ordering each subplot, defaults to None"
        * `return_df` (bool): if True, returns dataframe used for plot instead of plot
        * `threshold_strategy` (str): where to place abundances for lineages below threshold. If "other" -> "Other" group; if "superlinege" -> added to abundance for superlineage.
        * `sort_by` (str): field used to sort dataframe and bars. Defaults to 'lineages' which attempts to order by lineage name. With subplots, this prioritizes the top subplot. Use 'x' to sort by sample name. Use 'y' to sort by abundance.
        * `y_title` (str): master y-axis title
        * `x_title` (str): master x-axis title
        * `ordered_lineages` (list): list of lineages for ordering legend and bar stacks. Defaults to None which includes all lineages, unordered.
        """

        if threshold_strategy=="superlineage":
            raise NotImplementedError("Not yet ready for threshold_strategy=='superlineage'")
        
        # subplot_order = [scheme.title() for scheme in schemes]
        if subplot_order is not None:
            subplot_order = subplot_order
        else:
            if "Expected" in schemes:
                subplot_order = ["Expected"] + sorted([s for s in schemes if s != "Expected"], key=str.casefold)
            else:
                subplot_order = sorted(schemes, key=str.casefold)

            # subplot_order = [scheme for scheme in subplot_order]
        if not return_df:
            fig = make_subplots(rows=len(schemes), cols=1, shared_xaxes=True ,subplot_titles=subplot_order, y_title=y_title, x_title=x_title)

        # loop through lineages/schemes/groupings to build abundance-based df
        data = {"x":[],"y":[],"lineages":[],"scheme":[],}
        for scheme in schemes:
            non_other_counts = {}
            other_counts = {}
            scheme_df = freyja_df[freyja_df["scheme"]==scheme]
            for lineage in lineages:
                lineage_df = scheme_df[scheme_df[lineage_col]==lineage]
                for grouping in lineage_df[group_by_col].unique():
                    abundance = lineage_df.loc[lineage_df[group_by_col]==grouping, "abundances"].sum()
                    if not isinstance(abundance, (np.floating, float)):
                        raise(f"weird abundance for {grouping}: {abundance}")
                        # abundance = 0
                    # save "other"s to figure out later
                    if lineage.lower() == "other":
                        other_counts[grouping] = other_counts.get(grouping, 0) + abundance
                    elif threshold_strategy == "other" and abundance < minimum:
                        other_counts[grouping] = other_counts.get(grouping, 0) + abundance
                    else:
                        data["x"].append(grouping)
                        data["scheme"].append(scheme)
                        data["y"].append(abundance)
                        data["lineages"].append(lineage)
                        non_other_counts[grouping] = non_other_counts.get(grouping, 0) + abundance
            for grouping, count in non_other_counts.items():
                data["x"].append(grouping)
                data["scheme"].append(scheme)
                data["y"].append(1-count)
                data["lineages"].append("Other")

        df = pd.DataFrame(data)
        if sort_by:
            df = df.sort_values(sort_by)
        if return_df:
            return df

        if ordered_lineages is not None:
            lineages = ordered_lineages
        else:
            lineages = [x for x in lineages if x!="Other"] + ["Other"]

        # loop through scheme/lineage details to create plots
        for i, scheme in enumerate(subplot_order):
            scheme_df = df[df["scheme"]==scheme]
            # print(scheme_df["x"])
            row = i+1
            # add bars to scheme-specific subplot
            for lineage in lineages:
                lin_df = scheme_df[scheme_df["lineages"]==lineage]
                if not lin_df.empty:
                    fig.add_bar(x=lin_df["x"],y=lin_df["y"],name=lineage,
                                text=lineage,textposition="inside",
                                marker_color=self.colormap.get(lineage),
                                row=row, col=1,
                                )
                else:
                    fig.add_bar(x=[],y=[],name=lineage,
                                text=lineage,textposition="inside",
                                marker_color=self.colormap.get(lineage),
                                row=row, col=1,
                                )
            self.update_colormap(fig)

        # update plot legend
        legend_set = set()
        fig.for_each_trace(
            lambda trace:
                trace.update(showlegend=False)
                if (trace.name in legend_set) else legend_set.add(trace.name))

        # update location of x-axis label
        if x_title:
            annot = list(fig.layout.annotations)
            for i, a in enumerate(annot):
                if a.text == x_title:
                    annot[i].y = -0.04
            fig.layout.annotations = annot

        return fig

    def plotLineages(self,summarized=False,superlineage=None,minimum=0.05,fn=None,title=None,samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,super_method='dot-split',group_by:Literal["sample","date"]="sample",group_by_col:str=None,date_col=None,period='week',subplots=False, height=None, subplot_order=None,return_df=False,threshold_strategy:Literal["other","superlineage"]="other",sort_by="lineages",y_title="Abundance",x_title="Samples",ordered_lineages=None,schemes=None):
        """Returns stacked bar chart showing lineage abundances for each sample
        
        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool|int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `minimum` (float): minimum abundance value to include in plot - anything less is categorized in "Other", defualts to 0.05
        * `fn` (str|Path): where to write fig, if provided, defaults to None
        * `title` (str): plot title, defualts to "Freyja lineage abundance"
        * `samples` (list|"all"): only the listed samples will be plotted
        * `include_pattern` (str): samples to include like "sample1|sample2"
        * `exclude_pattern` (str): samples to exclude like "sample1|sample2"
        * `group_by` (str): field by which to separate bars. Defaults to 'sample'.
           "sample" labels each bar by sample name. 'date', but it could be useful to use a date column (included in your agg_df) instead
        * `date_col` (str): name of the date field in the metadata
        * `period` (str): if `group_by=="date"`, the time period to use for each grouping. Defaults to 'week'
        * `subplots` (bool): if True, stacks each scheme on a different plot with a shared x axis. Defaults to False.
        * `return_df` (bool): if True, returns dataframe used for plot instead of plot
        * `threshold_strategy` (str): where to place abundances for lineages below threshold. If "other" -> "Other" group; if "superlinege" -> added to abundance for superlineage.
        * `sort_by` (str): field used to sort dataframe and bars. Defaults to 'lineages' which attempts to order by lineage name. With subplots, this prioritizes the top subplot. Use 'x' to sort by sample name. Use 'y' to sort by abundance.
        * `y_title` (str): master y axis title, defaults to "Abundance"
        * `ordered_lineages` (list): list of lineages for ordering legend and bar stacks. Defaults to None which includes all lineages, unordered.
        * `schemes` (list): list of schemes to include in plot. Used for naming/selected schemes and number of subplots if applicable. Defaults to all.

        Known issue:
        If a bar is 100% "Other", it may not appear in the plot. This is because we currently 
        assume samples with no abundance values assigned by freyja are not real when trying to 
        pair up corresponding samples.
        """

        # filter  data and decide what to loop through
        freyja_df = self.getPlottingDf(summarized=summarized,superlineage=superlineage,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=0.0,super_method=super_method)
        lineage_col = getLineageCol(superlineage=superlineage,summarized=summarized,super_method=super_method)
        group_by_col,date_col,freyja_df = self.checkGroupByDetails(group_by=group_by,date_col=date_col,period=period,freyja_df=freyja_df,split_by_scheme=subplots)
        schemes = freyja_df["scheme"].unique().tolist() if isinstance(schemes, type(None)) else schemes
        lineages = freyja_df.sort_values(by="abundances")[lineage_col].unique().tolist()[::-1]
        # print(freyja_df)
        # print(groupings,schemes,lineages)
        # exit(1)

        if subplots:
            fig = self.plotLineagesSubplots(lineages=lineages, schemes=schemes, freyja_df=freyja_df, group_by_col=group_by_col, lineage_col=lineage_col, minimum=minimum, subplot_order=subplot_order, return_df=return_df, threshold_strategy=threshold_strategy, sort_by=sort_by, y_title=y_title, x_title=x_title, ordered_lineages=ordered_lineages)
            if not height:
                height = len(schemes) * 250
        else:
            fig = self.plotLineagesSinglePlot(lineages=lineages, schemes=schemes, freyja_df=freyja_df, group_by_col=group_by_col, lineage_col=lineage_col, minimum=minimum, return_df=return_df, threshold_strategy=threshold_strategy, sort_by=sort_by, y_title=y_title, x_title=x_title, ordered_lineages=ordered_lineages)
        
        if return_df:
            return fig

        if not title:
            title = "Freyja lineage abundance" if not summarized else "Freyja lineage abundance - summary"

        fig.update_layout(
            barmode="stack",
            title=title,
            height=height,
            )

        if sort_by:
            pass
        else:
            print("sorting by category ascending")
            fig.update_layout(xaxis={'categoryorder':'category ascending'})

        if fn:
            save(fig,fn)

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
        if fn:
            save(fig,fn)
        return fig
    
    def plotPercentExpectedBox(self,summarized=False,superlineage=None,fn=None,color="scheme",x=None,title="Distribution of estimated abundance for each lineage as a percent of expected abundance",samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,super_method='dot-split',schemes=[],lineages=[],combine_lineages=False,return_df=False,sort_key=None):
        """Returns a box plot comparing each scheme vs the scheme containing expected abundance values

        Args:
        * `summarized` (bool): whether to use summarized lineages rather than all lineages, defaults to False
        * `superlineage` (bool|int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
        * `fn` (str|Path): where to write fig, if provided, defaults to None
        * `color` (str): color field to use for box plot. Defaults to 'scheme'.
        * `x` (str): x axis field to use for box plot. Defaults to 'scheme' if `combine_lineages` is True else 'lineages'.
        * `title` (str): plot title, defualts to "Distribution of estimated abundance for each lineage as a percent of expected abundance"
        * `samples` (list|"all"): only the listed samples will be plotted
        * `include_pattern` (str): samples to include like "sample1|sample2"
        * `exclude_pattern` (str): samples to exclude like "sample1|sample2"
        * `start_date` (str): exclude samples before this date
        * `end_date` (str): exclude samples after this date
        * `super_method` (str): method to use for determining superlineage. Defaults to 'dot-split'
        * `schemes` (list): list of schemes to include in plot,
        * `lineages` (list): (not implemented) list of lineages to include in plot,
        * `combine_lineages` (bool): if True, combines lineages and produces a box for each scheme by default. If False, produces a box for each lineage, defaults to False
        * `return_df` (bool): if True, retrurns the dataframe used to generate the plot rather than the plot, defaults to False
        * `sort_key` (function): function to use to sort the dataframe, defaults to None which sorts alphabetically (case insensitive)
        * `date_col` (str): name of the date field in the metadata
        * `period` (str): if `group_by=="date"`, the time period to use for each grouping. Defaults to 'week'
        * `subplots` (bool): if True, stacks each scheme on a different plot with a shared x axis. Defaults to False.
        """

        freyja_df = self.getPlottingDf(summarized=summarized,superlineage=superlineage,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=0.0,super_method=super_method)
        schemes = schemes if schemes else freyja_df["scheme"].unique().tolist()
        # lineage_col = getLineageCol(superlineage=superlineage,summarized=summarized,super_method=super_method)
        # lineages = lineages if lineages else freyja_df.sort_values(by="abundances")[lineage_col].unique().tolist()[::-1]

        expected_lineages = freyja_df.loc[freyja_df["scheme"]=="Expected", "lineages"].unique()
        freyja_df = pd.concat((dff for dff in add_missing_lineages(freyja_df,expected_lineages)))
        freyja_df["expected_abundance"] = freyja_df.apply(getExpectedAbundance,axis=1,df=freyja_df)
        freyja_df = freyja_df[freyja_df["scheme"]!="Expected"]
        freyja_df["percent_of_expected"] = freyja_df.apply(lambda row: row["abundances"] / row["expected_abundance"] * 100. if row["expected_abundance"] > 0.0 else pd.NA, axis=1)
        # print(freyja_df)
        # exit()

        if combine_lineages:
            x = x if x else "scheme"
            labels={'tool':'Tool', 'percent_of_expected':'Percent of expected abundance'}
        else:
            x = x if x else "lineages"
            labels={"percent_of_expected":"Percent of expected abundance","lineages":"Lineages","scheme":"Scheme"}

        key = sort_key if sort_key is not None else lambda col: col.str.lower()
        percent_df = freyja_df[freyja_df["percent_of_expected"].notna()].sort_values(["lineages","scheme"], key=key)
        # percent_df = freyja_df[freyja_df["percent_of_expected"].notna()].sort_values([x], key=key)
        
        if return_df:
            return percent_df

        fig = px.box(
            percent_df,x=x,y="percent_of_expected",
            color=color,
            points='all',
            hover_data=["scheme","lineages","percent_of_expected","Sample name"],
            title=title,
            # width=500,
            # height=550,
            labels=labels,
        )

        if fn:
            save(fig,fn)
        return fig
    
    def plotLineageDetections(self,show_counts=True,summarized=True,fn=None,color="scheme",title="Detection of expected lineages",include_unexpected_lineages=False,samples="all",include_pattern=None,exclude_pattern=None,start_date=None,end_date=None,minimum_abundance=0.0,height=None,return_df=False):
        """Creates a plot showing whether detected lineages are expected or false positives for each sample with subplots for each scheme.

        Args:
        * `show_counts` (bool): If True, show only the number of detected and failed-to-detect lineages. If False, plots each detected lineage in the positive y-axis of a stacked bar chart with a size of 1, each. Defaults to True.
        * `summarized` (bool): If True, uses summarized lineages (as opposed to pangolin lineages). Defaults to True.
        * `fn` (str|Path): where to write fig, if provided, defaults to None
        * `color` (str): The color variable to use for the plot. Defaults to "scheme".
        * `title` (str): The title of the plot. Defaults to "Detection of expected lineages".
        * `include_unexpected_lineages` (bool): Whether to include unexpectedly detected lineages (false positives) in the negative y-axis. Defaults to False.
        * `samples` (str): The samples to include in the plot. Defaults to "all".
        * `include_pattern` (str): A pattern of samples to include in the plot. Defaults to None.
        * `exclude_pattern` (str): A pattern of samples to exclude from the plot. Defaults to None.
        * `start_date` (str): Exclude data from before this date. Defaults to None.
        * `end_date` (str): Exclude data from after this date. Defaults to None.
        * `minimum_abundance` (float): The minimum abundance for a lineage to be included in the plot. Defaults to 0.0.
        * `height` (int): The height of the plot. Defaults to None.
        * `return_df` (bool): Whether to return the plotting dataframe. Defaults to False.

        Returns:
            DataFrame | Figure
        """

        # prep data
        freyja_df = self.getPlottingDf(summarized=summarized,samples=samples,include_pattern=include_pattern,exclude_pattern=exclude_pattern,start_date=start_date,end_date=end_date,minimum=0.0)
        lineage_col = getLineageCol(summarized=summarized)
        assert "Expected" in freyja_df["scheme"].unique()
        expected_df = freyja_df[freyja_df["scheme"]=="Expected"]
        freyja_df = freyja_df[freyja_df["scheme"]!="Expected"]
        sample_names = expected_df["Sample name"].unique()

        if show_counts:
            data = {"Sample name":[], "scheme":[], "Correctly detected": [], "Failed to detect": []}
            if include_unexpected_lineages:
                data["Unexpected but detected"] = []
        else:
            data = {"Sample name":[], "scheme":[], lineage_col:[], "abundances":[]}
        for scheme in sorted(freyja_df["scheme"].unique(),key=str.casefold):
            for sample in sample_names:
                sample_df = freyja_df.loc[(freyja_df["scheme"]==scheme) & (freyja_df["Sample name"]==sample)]
                expected_lineages = set(expected_df.loc[(expected_df["Sample name"]==sample), lineage_col].unique())
                lineages_to_include = expected_lineages if not include_unexpected_lineages else set(sample_df[lineage_col].unique()).union(expected_lineages)
                found_lineages = set(sample_df[lineage_col].unique())

                correctly_detected = expected_lineages.intersection(found_lineages)
                went_undetected = expected_lineages - found_lineages
                if show_counts:
                    data["Sample name"].append(sample)
                    data["scheme"].append(scheme)
                    data["Correctly detected"].append(len(correctly_detected))
                    data["Failed to detect"].append(len(went_undetected))
                    y_cols = ["Correctly detected","Failed to detect"]
                    if include_unexpected_lineages:
                        extras_detected = found_lineages - expected_lineages
                        data["Unexpected but detected"].append(len(extras_detected))
                        y_cols.append("Unexpected but detected")
                else:
                    for lineage in lineages_to_include:
                        if include_unexpected_lineages and lineage in went_undetected:
                            continue
                        if lineage == "Other":
                            continue
                        calculated_abundance = sample_df.loc[(sample_df["Sample name"]==sample) & (sample_df[lineage_col]==lineage), "abundances"].squeeze()
                        if isinstance(calculated_abundance,pd.Series) and calculated_abundance.empty:
                            calculated_abundance = 0
                            # print("calc_ab:",calculated_abundance,lineage)
                            # print(sample_df.loc[(sample_df["Sample name"]==sample) & (sample_df[lineage_col]==lineage), "abundances"])
                            # print(sample_df.loc[(sample_df["Sample name"]==sample) & (sample_df[lineage_col]==lineage)])
                            # print(sample_df.loc[(sample_df[lineage_col]==lineage)])
                            # print(sample_df.loc[(sample_df["Sample name"]==sample)])
                        if calculated_abundance < minimum_abundance:
                            continue
                        data["Sample name"].append(sample)
                        data["scheme"].append(scheme)
                        x = 1 if lineage in correctly_detected else -1
                        expected_abundance = expected_df.loc[(expected_df["Sample name"]==sample) & (expected_df[lineage_col]==lineage), "abundances"].squeeze()
                        # NOTE: to plot with even blocks for everything, replace expected_abundance with 1
                        data[lineage_col].append(lineage)
                        data["abundances"].append(x * (expected_abundance if not include_unexpected_lineages else 1))
                        # print(sample,scheme,x * expected_abundance)
        df = pd.DataFrame(data)
        # df = df.sort_values(by="Sample name")
        # print(df)
        if return_df:
            return df

        # plot
        if show_counts:
            fig = px.bar(
                df, 
                x="Sample name", 
                y=y_cols, 
                facet_row="scheme", 
                text_auto=True, 
                height=height, 
                labels={"variable":"Result", "value":"Count", "Sample name":"Sample","abundances":"Abundances","lineages":"Lineages"},
                title=title,
            )
        else:
            # # unsure why color was being edited here but not used anywhere
            # if include_unexpected_lineages:
            #     color = ""
            fig = px.bar(
                df, 
                x="Sample name", 
                y="abundances", 
                color=lineage_col, 
                facet_row="scheme", 
                text=lineage_col, 
                height=height,
                labels={"variable":"Result", "value":"Count", "Sample name":"Sample","abundances":"Abundances","lineages":"Lineages"},
                title=title,
            )
            fig.add_hline(y=0, line_dash="dot", row="all", col="all",
              annotation_text="", 
              annotation_position=None)
            fig.update_layout(
                # barmode='stack', 
                xaxis={'categoryorder':'category ascending'},
            )
            self.update_colormap(fig)
        fig.update_layout(
            font_family="Inconsolata",
            # font_family=["Inconsolata","Open Sans", "verdana", "arial", "sans-serif"],
        )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].replace(": ","<br>").replace(" (","<br>(")))
        if fn:
            save(fig,fn)
        return fig



### Additional helper functions

def add_missing_lineages(compare_df,expected_lineages):
    """For each sample name, add zero-abundance lineages for any that it lacks"""
    yield compare_df
    schemes = [s for s in compare_df["scheme"].unique() if s != "Expected"]
    for scheme in schemes:
        for sample in compare_df["Sample name"].unique():
            sample_df = compare_df[compare_df["Sample name"]==sample]
            for lineage in set(expected_lineages) - set(sample_df["lineages"].unique()) - set(["None"]):
                expected_abundance = compare_df.loc[(compare_df["scheme"]=="Expected") & (compare_df["scheme"]=="Expected") & (compare_df["lineages"]==lineage), "abundances"].sum()
                yield pd.DataFrame({"Sample name":[sample], "lineages":[lineage], "abundances":[0], "scheme":[scheme], "expected_abundance":[expected_abundance]})

# These are taken and adapted from Freyja so we can summarize lineages consistently
def getExpectedAbundance(s,df):
    if s["scheme"] == "Expected":
        return s["abundances"]
    else:
        x = df.loc[(df["Sample name"]==s["Sample name"]) & (df["lineages"]==s["lineages"]) & (df["scheme"]=="Expected"), "abundances"].squeeze()
        if type(x) == pd.Series and x.empty:
            return 0.0
        else:
            return x

def summarize_lineages(lineage_list, abundance_list):
    """Yields lineages and abundances summarized to WHO names and other larger grouplings"""

    mapDict = buildLineageMap("")
    if "Other" not in mapDict.keys():
        mapDict["Other"] = "Other"
    # for i,(k,v) in enumerate(mapDict.items()):
    #     print(k,v)
        # if i==5: exit()
    # TODO: add wt-wuhan and any other large groupings of interest to mapDict
    return (f"('{summary_lineage}', {s_abundance})" for summary_lineage,s_abundance in map_to_constellation(lineage_list, abundance_list, mapDict))

def get_lineage_summary(lineage_list, abundance_list):
    """Converts lineages and abundances to summary string like the one output by freyja"""

    return "[" + ", ".join(summarize_lineages(lineage_list, abundance_list)) + "]"

def map_to_constellation(sample_strains, vals, mapDict, prefix_groups=["NFW","Neg","Control"]):
    """Maps lineage names to constellations
    NOTE: edited from freyja.sample_deconvolv"""
    localDict = {}
    for jj, lin in enumerate(sample_strains):
        if lin in mapDict.keys():
            if mapDict[lin] not in localDict.keys():
                localDict[mapDict[lin]] = vals[jj]
                # # TODO: remove
                # if mapDict[lin] == "Omicron": print(lin,"-> omicron")
            else:
                localDict[mapDict[lin]] += vals[jj]
        elif lin.startswith('A.') or lin == 'A':
            if 'A' not in localDict.keys():
                localDict['A'] = vals[jj]
            else:
                localDict['A'] += vals[jj]
        else:
            # group together anything with specified prefixes. Good for grouping controls
            for prefix in prefix_groups:
                if lin.startswith(prefix):
                    if prefix not in localDict.keys():
                        localDict[prefix] = vals[jj]
                    else:
                        localDict[prefix] += vals[jj]
                    break
            else:
                # print("Other:", lin, vals[jj])
                if 'Other' not in localDict.keys():
                    localDict['Other'] = vals[jj]
                else:
                    localDict['Other'] += vals[jj]
    # convert to descending order
    localDict = sorted(localDict.items(), key=lambda x: x[1], reverse=True)
    return localDict
