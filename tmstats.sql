# Create tables for TMSTATS (Toastmasters Stats)

# Club table

drop table clubs;
drop table loaded;
drop table clubchanges;
drop table distperf;
drop table clubperf;

CREATE TABLE IF NOT EXISTS clubs (
    # This table is derived from the Toastmasters clublist and has mostly static data about clubs.
    district INT,
    division CHAR(2),
    area CHAR(2),
    clubnumber INT,
    clubname VARCHAR(100) ,
    charterdate date,
    suspenddate date,
    address VARCHAR(200) ,
    city VARCHAR(100) ,
    state VARCHAR(100) ,
    zip VARCHAR(20) ,
    country VARCHAR(100) ,
    phone VARCHAR(40) ,
    meetingtime VARCHAR(100) ,
    meetingday VARCHAR(100) ,
    clubstatus VARCHAR(100) ,
    clubwebsite VARCHAR(100) ,
    clubemail VARCHAR(100) ,
    facebook VARCHAR(100) ,
    advanced BOOL,
    firstdate date, 
    lastdate date,
    primary key(clubnumber, firstdate)
) CHARACTER SET utf8;
        
# Data currency table

CREATE TABLE IF NOT EXISTS loaded (
    tablename VARCHAR(8),
    loadedfor date,
    primary key(tablename, loadedfor)
);
        
# Club changes table

CREATE TABLE IF NOT EXISTS clubchanges (
    item VARCHAR(100),
    old VARCHAR(200),
    new VARCHAR(200),
    clubnumber INT,
    changedate date,
    primary key(item, clubnumber, changedate)
);

CREATE TABLE IF NOT EXISTS distperf (
    # This table is derived from the daily "District Performance" report. 
    district INT,
    division CHAR(2),
    area CHAR(2),
    clubnumber INT,
    clubname VARCHAR(100),
    newmembers INT,
    laterenewals INT,
    octrenewals INT,
    aprrenewals INT,
    totalrenewals INT,
    totalcharter INT,
    totaltodate INT,
    dist CHAR(1),
    month VARCHAR(12),
    asof date,
    action VARCHAR(40),
    primary key(clubnumber, asof)
) CHARACTER SET utf8;
        
CREATE TABLE IF NOT EXISTS clubperf (
    # This table is derived from the daily "Club Performance" report.
    district INT,
    division CHAR(2),
    area CHAR(2),
    clubnumber INT,
    clubname VARCHAR(100),
    clubstatus VARCHAR(20),
    membase INT,
    activemembers INT,
    goalsmet INT,
    ccs INT,
    addccs INT,
    acs INT,
    addacs INT,
    claldtms INT,
    addclaldtms INT,
    newmembers INT,
    addnewmembers INT,
    offtrainedround1 INT,
    offtrainedround2 INT,
    memduesontimeoct INT,
    memduesontimeapr INT,
    offlistontime INT,
    clubdistinguishedstatus CHAR(1),
    color CHAR(1),
    goal9 INT,
    goal10 INT,
    asof date,
    primary key(clubnumber, asof)
) CHARACTER SET utf8;
