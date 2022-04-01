#!/usr/bin/python3

import sys
from glob import glob
from nbt import nbt
from datetime import date

datadir = '/home/mc/spigot/worlds/world/playerdata/'


def replace_date(old, new):

    oldfile = newfile = None

    for f in glob(datadir + '*.dat'):
        player = nbt.NBTFile(f, 'rb')

        try:
            name = player['bukkit']['lastKnownName'].value
            # print(name)
        except KeyError:
            continue

        if name == old:
            print("old: " + f)
            oldfile = player
            if newfile:
                break

        if name == new:
            print("new: " + f)
            newfile = player
            newfilename = f
            if oldfile:
                break

    else:
        print("error: player not found")
        return

    olddate = oldfile['bukkit']['firstPlayed']
    newdate = newfile['bukkit']['firstPlayed']

    print('olddate:', date.fromtimestamp(olddate.value // 1000))
    print('newdate:', date.fromtimestamp(newdate.value // 1000))

    if newdate.value > olddate.value:
        newdate.value = olddate.value
        newfile.write_file(newfilename)
        print("succesfully changed the date")
    else:
        print("error: first user joined later than second")


if __name__ == '__main__':
    replace_date(sys.argv[1], sys.argv[2])
