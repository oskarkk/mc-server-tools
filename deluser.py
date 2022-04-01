#!/usr/bin/python3 -i

import json, os, sys
from glob import glob
from nbt import nbt
from datetime import date
import sqlite3


spigdir = '/home/mc/spigot'
datadir = spigdir + '/worlds/world/playerdata/'
essdir = spigdir + '/plugins/Essentials/userdata/'
cachefile = spigdir + '/usercache.json'
plandb = spigdir + '/plugins/Plan/database.db'


with open(cachefile, 'r') as f:
    cached_users = json.loads(f.read())


### loading data
def users_from_usercache():
    users = {}
    for user in cached_users:
        uuid = user['uuid']
        users[uuid] = {'name': user['name']}
    return users


def users_from_playerdata():
    users = {}
    for player in glob(datadir + '*.dat'):
        uuid = player.replace(datadir, '').replace('.dat', '')
        users[uuid] = {}

        playernbt = nbt.NBTFile(player, 'rb')

        try:
            users[uuid]['name'] = playernbt['bukkit']['lastKnownName'].value
        except KeyError:
            pass

        try:
            first_date = date.fromtimestamp(
                playernbt['bukkit']['firstPlayed'].value // 1000
            )
            last_date = date.fromtimestamp(
                playernbt['bukkit']['lastPlayed'].value // 1000
            )
            users[uuid]['first_seen'] = first_date
            users[uuid]['last_seen'] = last_date
            users[uuid]['days'] = (last_date - first_date).days
        except KeyError:
            pass

    return users


def delta(data, days):
    if 'days' in data:
        return data['days'] <= days
    else:
        return True


def find_users(days=None):
    users = users_from_playerdata()
    for uuid, data in users_from_usercache().items():
        user = users.setdefault(uuid, {})
        user.update(data)

    if days:
        users = {k: v for k, v in users.items() if delta(v, days)}

    return users


def print_users(days=None):
    users = find_users(days=days)
    for uuid, data in users.items():
        print(
            uuid,
            data.get('name').ljust(20),
            data.get('first_seen'),
            data.get('last_seen'),
            '   ',
            data.get('days'),
        )


### removing


def remove_usercache(uuids):
    with open(spigdir + '/usercache-backup.json', 'w') as f:
        f.write(json.dumps(cached_users))

    cached_users[:] = [x for x in cached_users if not x['uuid'] in uuids]

    with open(spigdir + '/usercache.json', 'w') as f:
        f.write(json.dumps(cached_users))

    print('removed users from usercache')


def remove_playerdata_essentials(uuids):
    for uuid in uuids:
        remove_file(uuid + '.dat', datadir)
        remove_file(uuid + '.yml', essdir)


def remove_file(filename, dir):
    if not os.path.exists(dir + 'removed'):
        os.mkdir(dir + 'removed')
    if os.path.exists(dir + filename):
        os.rename(dir + filename, dir + '/removed/' + filename)
        print('removed ' + filename + ' from ' + dir)


# https://github.com/plan-player-analytics/Plan/blob/master/Plan/common/src/main/java/com/djrapitops/plan/storage/database/transactions/commands/RemovePlayerTransaction.java
def remove_plan(uuids):
    con = sqlite3.connect(plandb)

    tables = [
        'plan_geolocations',
        'plan_nicknames',
        'plan_world_times',
        'plan_sessions',
        'plan_ping',
        'plan_user_info',
        'plan_users',
        'plan_extension_user_table_values',
        'plan_extension_user_values',
        'plan_extension_groups',
    ]

    rows = [f''{uuid}'' for uuid in uuids]

    for table in tables:
        cur = con.execute(f'DELETE FROM {table} WHERE uuid IN ({", ".join(rows)})')
        print(f'rows deleted from {table}: {cur.rowcount}')

    count = 0
    cur = con.execute(
        f'DELETE FROM plan_kills WHERE killer_uuid IN ({", ".join(rows)})'
    )
    count += cur.rowcount
    cur = con.execute(
        f'DELETE FROM plan_kills WHERE victim_uuid IN ({", ".join(rows)})'
    )
    count += cur.rowcount

    print(f'rows deleted from plan_kills: {count}')

    con.commit()
    con.close()


users = find_users()


def remove_users(names=[], uuids=[]):
    print('\nto remove:')

    for uuid in users:
        name = users[uuid]['name']
        if name in names:
            uuids.append(uuid)
            print(uuid, name)

    print()
    remove_plan(uuids)
    print()
    remove_playerdata_essentials(uuids)
    print()
    remove_usercache(uuids)


if __name__ == '__main__':
    remove_users(names=sys.argv[1:])
