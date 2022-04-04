Some tools that I wrote for my use in Minecraft server administration.

- [Deluser.py](#deluserpy) - delete player data from usercache.json, world/playerdata/, Plan/database.db and Essentials/userdata/
- [Backup](#backup) - backup semi-incrementally (always hardlinking to the previous backup) the whole spigot server folder with rsync, but copy only those parts of the world, that were inhabited for some minimum time. It's done using [mca-selector](https://github.com/Querz/mcaselector).
- [PlanSqlTools](#plansqltools) - SQL tools for moving user's data to different username/UUID and cleaning the database

# Deluser.py

Deletes user data from:

- usercache.json
- world/playerdata/
- Plan/database.db ([**Player Analytics** plugin](https://www.spigotmc.org/resources/plan-player-analytics.32536/))
- Essentials/userdata/ ([**EssentialsX** plugin](https://essentialsx.net))

### Usage

Change these linen in the code:
```
spigdir = '/home/mc/spigot'
datadir = spigdir + '/worlds/world/playerdata/'
```
The first should point to the root dir of your minecraft server, where your .jar lies. The second to the playerdata dir in your overworld folder, usually `/world/playerdata` if you haven't changed that in your `spigot.yml` or somewhere.

Then you can use something like:
```
python -m deluser.py Playername1 Playername2 Player3 playerrrrr4 playerrr5
```
or:
```
python -m deluser.py `cat PlainListOfUsersToDelete.txt`
```
Don't use UUIDs. But the code can be easily edited to accept UUIDs too.

# PlanSqlTools

Small tools written in **bash** for making useful changes in the database of the **Player Analytics** (**Plan**) spigot plugin ([resource page](https://www.spigotmc.org/resources/plan-player-analytics.32536/), [github repo](https://github.com/plan-player-analytics/Plan)). They were tested in Plan-**5.2**-build-1124 and earlier 5.2 build, but they are very simple so you can easily adapt the scripts to the future changes in the database schema.

### merge.sh 

"Merges" two users. The script takes two arguments - usernames of two players. It's changing the UUIDs of the first user's data to the UUIDs of the second, so that in the database it appears as if they were the same users from the start. Useful when the user's got a new account or when the server is in the offline mode and user has changed his username (in the offline mode the UUIDs are generated from the username).

Specifically, the script:

* finds the UUIDs of both users and prints them to the stdout
* replaces the first UUID with the second in tables with sessions, nicknames, time spent in specific worlds etc.
* checks if the first user joined the server before the second, if yes, it changes the join date of the second user to the join date of the first
* DELETES every data of the first user which can't be changed to the second user (data that describes the "present", like user's balance, current username, groups etc.) and additionally ping and geolocation data, much like `/plan db remove`. If you don't want to delete this, you can remove or modify the last line in the script:

`delete plan_extension_groups plan_extension_user_values plan_geolocations plan_ping plan_user_info plan_users`

... which specifies the tables from which the data will be removed.

Of course, you should do a backup and verify the effects manually in the database, or by checking the web interface of Plan.

### clean-sessions.sh

Second, tiny script takes one argument - time in seconds. It removes every session which was shorter than the specified time from tables: plan_world_times, plan_kills and plan_sessions. Useful when you have users with connection problems (I had people who logged in like 50 times a day), random users who just log in once and never come back, and maybe when dealing with some DoS attacks? Could be improved to remove every user without sessions, so that it would be a much more convenient alternative to `/plan db remove`.

### Usage

Turn off the server (but I'm not sure if this is necessary). Put the scripts in the `<yourserver>/plugins/Plan/` directory.

`./merge.sh <old-username> <new-username>`

`./clean-sessions.sh <seconds>`

For example:

`./merge.sh Notch Dinnerbone` - after this, Notch would disappear from Plan, but each of his sessions, kills, deaths, seen usernames etc. would be assigned to Dinnerbone.

`./clean-sessions.sh 120` - every session shorter than two minutes disappears from Plan.

### Dependencies

* **sqlite3**, of course


# Backup

If you want to know how to use that, ask me.
