#!/usr/bin/python3 -i

from glob import glob
from nbt import nbt
import struct

spigdir = 'spigot'
datadir = spigdir + '/worlds/world/playerdata/'
skriptdir = spigdir + '/plugins/Skript/scripts/'


def get_nbt():
    players = {}
    for player in glob(datadir + '*.dat'):
        p = nbt.NBTFile(player, 'rb')
        try:
            name = p['bukkit']['lastKnownName'].value
        except KeyError:
            continue
        uuid = player.replace(datadir, '').replace('.dat', '')
        players[name] = uuid
    return players


def four_ints(players):
    f = ''
    for player in players:
        # if player != 'okarkalic': continue
        uuid = players[player].replace('-', '')
        ints = [uuid[i * 8 : (i + 1) * 8] for i in range(4)]
        ints = [struct.unpack('>i', bytes.fromhex(i))[0] for i in ints]
        array = (
            '[I;'
            + str(ints[0])
            + ','
            + str(ints[1])
            + ','
            + str(ints[2])
            + ','
            + str(ints[3])
            + ']'
        )
        yaml = player + ': "' + array + '"'
        f += yaml + '\n'
    return f


if __name__ == '__main__':
    with open(skriptdir + 'fourints.yml', 'w') as f:
        f.write(four_ints(get_nbt()))
