#!/usr/bin/python3

import sys
from glob import glob
from nbt import nbt
from datetime import date

datafile = sys.argv[1]


def do_thing():

    world = nbt.NBTFile(datafile, 'rb')
    try:
        time = world['Data']['LastPlayed'].value
    except KeyError:
        print('ups')

    print('last played:', date.fromtimestamp(time // 1000))


if __name__ == '__main__':
    do_thing()
