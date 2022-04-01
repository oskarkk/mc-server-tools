#!/usr/bin/python3 -i

import requests, json, base64


def getUUID(username):
    r = requests.get('https://api.mojang.com/users/profiles/minecraft/' + username)
    return r.json()['id']


def getskinjson(uuid):
    r = requests.get(
        'https://sessionserver.mojang.com/session/minecraft/profile/'
        + uuid
        + '?unsigned=false'
    )
    encoded = r.json()['properties'][0]['value']
    return base64.b64decode(encoded).decode()


def getskinurl(s):
    o = json.loads(s)
    return o['textures']['SKIN']['url']


def getskin(username):
    return getskinurl(getskinjson(getUUID(username)))


def skintype(uuid):
    lsb = [int(x, 16) & 1 for x in uuid[7::8]]
    print(lsb)
    # 1 is alex
    return (lsb[0] + lsb[1] + lsb[2] + lsb[3]) & 1


# like in: https://github.com/crafatar/crafatar/blob/master/lib/skins.js
# probably wrong
def skintype2(uuid):
    lsb = [int(x, 16) for x in uuid[7::8]]
    print(lsb)
    return lsb[0] ^ lsb[1] ^ lsb[2] ^ lsb[3]
