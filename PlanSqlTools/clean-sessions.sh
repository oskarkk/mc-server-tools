# arg 1 is seconds

sql() { sqlite3 database.db "$*"; }

# delete this first because of foreign key constraints
sql "DELETE FROM plan_world_times WHERE session_id IN (SELECT id FROM plan_sessions WHERE session_end - session_start < $1 * 1000)"
sql "DELETE FROM plan_kills WHERE session_id IN (SELECT id FROM plan_sessions WHERE session_end - session_start < $1 * 1000)"

# delete sessions shorter than <arg 1> seconds
sql "DELETE FROM plan_sessions WHERE session_end - session_start < $1 * 1000;"
