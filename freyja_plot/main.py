from freyja_plot import __version__
from argparse import ArgumentParser

def main():
    parser = ArgumentParser(description="A python module for plotting aggregated `freyja demix` lineage abundances.")
    parser.add_argument('-V', '--version', action='version', version="%(prog)s ("+__version__+")")
    parser.parse_args()
