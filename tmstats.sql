# Create tables for TMSTATS (Toastmasters Stats)

# Club table


CREATE TABLE IF NOT EXISTS clubs (
    # This table is derived from the Toastmasters clublist and has mostly static data about clubs.
    district INT,
    division CHAR(2),
    area CHAR(2),
    clubnumber INT,
    clubname VARCHAR(100) ,
    charterdate date,
    suspenddate date,
    place VARCHAR(200),
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
    loadedfor DATE,
    monthstart DATE,
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
    monthstart DATE,
    asof date,
    charterdate VARCHAR(10),
    suspenddate VARCHAR(10),
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
    color CHAR(6),
    goal9 INT,
    goal10 INT,
    asof date,
    monthstart DATE,
    primary key(clubnumber, asof)
) CHARACTER SET utf8;

CREATE TABLE IF NOT EXISTS areaperf (
    # This table is derived from the daily "Area/Division Performance" report.
    district INT,
    division CHAR(2),
    area CHAR(2),
    clubnumber INT,
    clubname VARCHAR(100),
    octoberrenewals INT,
    aprilrenewals INT,
    novvisitaward INT,
    mayvisitaward INT,
    membershiptodate INT,
    clubgoalsmet INT,
    distinguishedclub VARCHAR(20),
    areaclubbase INT,
    areapaidclubgoalfordist INT,
    areapaidclubgoalforselectdist INT,
    areapaidclubgoalforpresdist INT,
    totalpaidareaclubs INT,
    areadistclubgoalfordist INT,
    areadistclubgoalforselectdist INT,
    areadistclubgoalforpresdist INT,
    totaldistareaclubs INT,
    distinguishedarea VARCHAR(30),
    divisionclubbase INT,
    divisionpaidclubgoalfordist INT,
    divisionpaidclubgoalforselectdist INT,
    divisionpaidclubgoalforpresdist INT,
    totalpaiddivisionclubs INT,
    divisiondistclubgoalfordist INT,
    divisiondistclubgoalforselectdist INT,
    divisiondistclubgoalforpresdist INT,
    totaldistdivisionclubs INT,
    distinguisheddivision VARCHAR(30),
    charterdate VARCHAR(10),
    suspenddate VARCHAR(10),
    asof date,
    monthstart DATE,
    primary key(clubnumber, asof)
) CHARACTER SET utf8;

CREATE TABLE IF NOT EXISTS geo (
    id INT UNSIGNED AUTO_INCREMENT,
    clubnumber INT,
    clubname VARCHAR(100),
    place VARCHAR(200),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(10),
    zip VARCHAR(10),
    latitude REAL,
    longitude REAL,
    locationtype VARCHAR(30),
    partialmatch BOOL,
    nelat REAL,
    nelong REAL,
    swlat REAL,
    swlong REAL,
    area REAL,
    formatted VARCHAR(200),
    types VARCHAR(100),
    INDEX(id)
);
