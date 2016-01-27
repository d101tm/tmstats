# Drop all the tmstats tables
drop table if exists clubs;
drop table if exists clubperf;
drop table if exists clubchanges;
drop table if exists distperf;
drop table if exists areaperf;
drop table if exists loaded;
#drop table if exists geo;
source tmstats.sql;
