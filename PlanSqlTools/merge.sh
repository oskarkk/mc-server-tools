#!/bin/bash

sql() { sqlite3 database.db "$*"; }


# get UUIDs

from=`sql SELECT uuid FROM plan_users WHERE name = \'$1\'`
to=`sql SELECT uuid FROM plan_users WHERE name = \'$2\'`
echo $from $to

[[ -z "$from" || -z "$to" ]] && echo ERROR && exit 1

from=\'$from\'
to=\'$to\'


# change UUIDs to new

replace() {
  sql "
    UPDATE $1
    SET uuid = $to
    WHERE uuid = $from;
  "
}

replace plan_sessions
replace plan_world_times
replace plan_nicknames


# user's join date

fromdate=`sql SELECT registered FROM plan_users WHERE uuid = $from`
todate=`sql SELECT registered FROM plan_users WHERE uuid = $to`
echo $fromdate $todate

if [ "$fromdate" -lt "$todate" ]; then
  sql UPDATE plan_user_info SET registered = $fromdate WHERE uuid = $to
  sql UPDATE plan_users SET registered = $fromdate WHERE uuid = $to
fi


# kills

sql "
 UPDATE plan_kills
 SET killer_uuid = $to
 WHERE killer_uuid = $from;

 UPDATE plan_kills
 SET victim_uuid = $to
 WHERE victim_uuid = $from;
"


# same as "/plan db remove" I guess

delete() {
  for table in $*; do
    sql DELETE FROM $table WHERE uuid = $from
  done
}

delete plan_extension_groups plan_extension_user_values plan_geolocations plan_ping plan_user_info plan_users
