# !/usr/bin/env python3

__version__="0.7.26"

def __init__():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    subparsers.add_parser('cpp', help='[cpp] connector cpp')
    subparsers.add_parser('gpp', help='[gpp] connector gpp')
    subparsers.add_parser('g', help='[g] cli connector g')
    subparsers.add_parser('c', help='[c] gui connector c')
    subparsers.add_parser('m', help='[m] menu')
    subparsers.add_parser('w', help='[w] page/container')
    subparsers.add_parser('r', help='[r] metadata reader')
    subparsers.add_parser('pp', help='[pp] pdf analyzor pp')
    subparsers.add_parser('cp', help='[cp] pdf analyzor cp')
    args = parser.parse_args()

    if args.subcommand == 'm':
        from gguf_connector import m
    elif args.subcommand=="r":
        from gguf_connector import r
    elif args.subcommand=="w":
        from gguf_connector import w
    elif args.subcommand=="cp":
        from gguf_connector import cp
    elif args.subcommand=="pp":
        from gguf_connector import pp
    elif args.subcommand=="c":
        from gguf_connector import c
    elif args.subcommand=="cpp":
        from gguf_connector import cpp
    elif args.subcommand=="g":
        from gguf_connector import g
    elif args.subcommand=="gpp":
        from gguf_connector import gpp