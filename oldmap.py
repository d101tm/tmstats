#*********** Start copy to Phone file here ****************************************** 

#*********** Info window tabs-content and marker creation: **************************

 #**** multiple club marker  - first club number used for mpoint and marki ***
 
import re
import tmparms, dbconn
import os, sys


# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
reload(sys).setdefaultencoding('utf8')

parms = tmparms.tmparms()
parms.parse()
conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
curs = conn.cursor()

pat = r'.*Meets.*?<br>(.*)<a.*Find-a-Club/([0-9]*).*$'
locpat = r'.*'

def makeTab(club, str):
    m = re.match(pat, str)
    if m:
        clubnumber = int(m.group(2))
        address = m.group(1)
    else:
        print "no match for", club
    curs.execute("INSERT INTO map  (clubnumber, areaicon, lat, lng, address) VALUES (%s, %s, %s, %s, %s)", (clubnumber, areaIcon, latlong[0], latlong[1], address))
 
 
latlong = (36.986890,-122.034685)     
areaIcon = "AM";

makeTab("<b>Santa Cruz Orators</b>","<font face=verdana size=2px>(Area A3)</b>&nbsp;&nbsp;&nbsp;<br>Open to all interested parties<br>Meets 12:10 PM - 1:00 PM, Monday<br>Goodwill Industries Conference Rm<br>(closed federal holidays)<br>350 Encinal Street<br>Santa Cruz 95060<br><a href=http:#www.toastmasters.org/Find-a-Club/00007481-Santa-Cruz-Orators-SCO-Club target=new>club contact information</a>")     
makeTab("<b>Surf City Advanced Club</b>","<font face=verdana size=2px>(Area A3)<br>Membership prerequisite,<br>Contact for Requirements<br>Meets 9:00 AM, 4th Saturday<br>Goodwill Industries<br>350 Encinal St<br>Santa Cruz 95060<br><a href=http:#www.toastmasters.org/Find-a-Club/00005127-Surf-City-Advanced-Toastmasters target=new>club contact information</a>")     



 #**** multiple club marker  - first club number used for mpoint and marki ***
latlong = (37.329034,-121.894264)     
areaIcon = "BM";

makeTab("<b>Adobe Fontificators Club</b>","<font face=verdana size=2px> (Area B5)<br>Open to all interested parties<br>Meets 12:05 PM, Wednesday<br>Adobe Systems, Inc.<br>345 Park Avenue<br>San Jose 95110<br><a href=http:#www.toastmasters.org/Find-a-Club/00006274-Adobe-Fontificators-Club target=new>club contact information</a><br>&nbsp;")     
makeTab("<b>Silicon Valley JETS</b>","<font face=verdana size=2px>Japanese-English (Area B5)<br>Open to all interested parties<br>Meets 7:00 PM, 1st and 3rd Thursday<br>Adobe Systems, Inc.<br>345 Park Ave<br>West Tower 2F Alexa Conference Rm<br>San Jose 95110<br><a href=http:#www.toastmasters.org/Find-a-Club/00007998-Silicon-Valley-JETS-Japanese-English-Toastmasters target=new>club contact information</a>")     



 #**** multiple club marker  ***
latlong = (37.25285,-121.96191)     
areaIcon = "AB";

makeTab("<b>Silver Tongued Cats Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:45 AM, Thursday<br>Addison-Penzak JCC of Silicon Valley<br>14855 Oka Rd<br>Los Gatos 95032<br><a href=http:#www.toastmasters.org/Find-a-Club/00006654-Silver-Tongued-Cats-Club target=new>club contact information</a><br>&nbsp;")     
makeTab("<b>West Valley Communicators</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 pm, 1st & 3rd Tuesdays <br>Addison Penzak Jewish Community Center<br>14855 Oka Rd<br>Los Gatos 95032<br><a href=http:#www.toastmasters.org/Find-a-Club/2997821-West-Valley-Communicators target=new>club contact information</a>")     



 #**** multiple club marker  ***
latlong = (37.38445,-121.90078)     
areaIcon = "BM";

makeTab("<b>LSI Speaks Club</b>","<font face=verdana size=2px> (Area B4)<br>Open to all interested parties<br>Meets 6:00 PM, Tuesdays<br>LSI Corp. - Corp. Conference Center<br>1320 Ridder Park Drive<br>San Jose 95131<br><a href=http:#www.toastmasters.org/Find-a-Club/00007596-LSI-Speaks-Club target=new>club contact information</a><br>&nbsp;")     
makeTab("<b>Classy Toasters</b>","<font face=verdana size=2px>(Area B4)<br>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Santa Clara County Office of Education<br>1290 Ridder Park Drive<br>San Jose 95131<br><a href=http:#www.toastmasters.org/Find-a-Club/1027656-Classy-Toasters target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.324516,-122.030647)     
areaIcon = "BG";

makeTab("<b>Cupertino Toastmasters</b>","<font face=verdana size=2px>(Area B1)<br>Open to all interested parties<br>Meets 6:00 PM, Monday<br>St. Joseph of Cupertino<br>10110 N. DeAnza Blvd<br>Cupertino 95014<br><a href='http://www.toastmasters.org/Find-a-Club/00004608-Cupertino-Toastmasters' target='new''</a>")     
makeTab("<b>Excalibur Toastmasters</b>","<font face=verdana size=2px> (Area G2)<br>Open to all interested parties<br>Meets 6:45 PM, Wednesday<br>St. Joseph of Cupertino Church<br>10110 North De Anza Boulevard<br>Cupertino 95014<br><a href=http:#www.toastmasters.org/Find-a-Club/00002914-Excalibur-Toastmasters-Club target=new>club contact information</a>")     



 #**** multiple club marker  ***
latlong = (37.400889,-122.144984)     
areaIcon = "CM";

makeTab("<b>Electric</b>","<font face=verdana size=2px><b>Electric Toasters</b> (Area C1)<br>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>EPRI, Inc.<br>3420 Hillview Avenue, Rm C1021<br>Palo Alto 94304<br><a href=http:#www.toastmasters.org/Find-a-Club/00009913-Electric-Toasters-Club target=new>club contact information</a><br>&nbsp;")     
makeTab("<b>SAP</b>","<font face=verdana size=2px><b>SAP Toastmasters</b> (Area C2)<br>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Building A in A2.20 Sycamore<br>(see club website for details)<br>3475 Deer Creek Road<br>Palo Alto 94304<br><a href=http:#www.toastmasters.org/Find-a-Club/00596069-SAP-Toastmasters target=new>club contact information</a>")     
makeTab("<b>Virtual</b>","<font face=verdana size=2px><b>Virtual Speak</b> (Area C2)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>VMWare<br>3495 Deer Creek Rd<br>Palo Alto 94304<br><a href=http:#www.toastmasters.org/Find-a-Club/00937505-Virtual-Speak-Toastmasters-Club target=new>club contact information</a>")     



 #**** multiple club marker  ***
latlong = (37.772097,-122.419172)     
areaIcon = "DM";

makeTab("<b>Twenty-Five Alive Club</b>","<font face=verdana size=2px>(Area D6)<br>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Department of Aging & Adult Services<br>1650 Mission St.<br>5th  Floor Rm 542<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/00007201-Twenty-Five-Alive-Club target=new>club contact information</a>")     
makeTab("<b>IMPACT Toastmasters</b>","<font face=verdana size=2px>(Area D3)<br>Open to all interested parties<br>Meets 12:00 PM, Monday<br>1650 Mission St.<br>4th or 5th Flr. Conf. Rm. (sign at front desk)<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/01378531-IMPACT-Toastmasters target=new>club contact information</a>")     




	 #**** multiple club marker  ***
latlong = (37.76296,-122.45911)     
areaIcon = "EM";

makeTab("<b>Downtown 65 Club</b>","<font face=verdana size=2px>(Area E3)<br>Open to all interested parties<br>Meets 7:00 PM, Monday<br>UCSF Chancellors Conference Room S118<br>513 Parnassus Avenue<br>San Francisco 94143<br><a href=http:#www.toastmasters.org/Find-a-Club/00000065-Downtown-65 target=new>club contact information</a><br>&nbsp;<br>&nbsp;")     
makeTab("<b>UC Oracles Toastmasters</b>","<font face=verdana size=2px> (Area E3)<br>Closed Other/Specialized Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday (except 1st Thu)<br>Nursing Building Room N417<br>521 Parnassus Ave<br>San Francisco 94143<br><a href=http:#www.toastmasters.org/Find-a-Club/00004292-UC-Oracles-Toastmasters-Club target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.791821,-122.396773)     
areaIcon = "IM";

makeTab("<b>Shield Speaks</b>","<font face=verdana size=2px> (Area I3)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>Blue Shield of California<br>50 Beale St<br>San Francisco 95105<br><a href=http:#www.toastmasters.org/Find-a-Club/1073164-Shield-Speaks-Toastmasters-Club target=new>club contact information</a>")     
makeTab("<b>Toastmasters For Health</b>","<font face=verdana size=2px> (Area D2)<br>Closed Other/Specialized Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>50 Beale St<br>Library (12th Fl) or Fishbowl (13th Fl)<br>San Francisco 95105<br><a href=http:#www.toastmasters.org/Find-a-Club/3030595-Toastmasters-For-Health target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.788780,-122.403840)     
areaIcon = "DM";

makeTab("<b>2nd Street Masters</b>","<font face=verdana size=2px>(Area D5)<br>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Capital Cafe<br>101 Post Street<br>San Francisco 94108<br><a href=http:#www.toastmasters.org/Find-a-Club/714439-2nd-Street-Masters target=new>club contact information</a><br>&nbsp;")     
makeTab("<b>Crownmasters</b>","<font face=verdana size=2px>(Area D5)<br>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Capital One Cafe<br>101 Post Street<br>San Francisco 94108<br>(Please confirm location; changes occasionally)<br><a href=http:#www.toastmasters.org/Find-a-Club/00001133-Crownmasters-Club target=new>club contact information</a>")     
makeTab("<b>Fightin' 49ers</b>","<font face=verdana size=2px>(Area D5)<br>Open to all interested parties<br>Meets 12:05 PM, Fridays<br>Capital One Cafe<br>101 Post Street<br>San Francisco 94108<br><a href=http:#www.toastmasters.org/Find-a-Club/00001244-fightin-49ers-club target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.790488,-122.393014)     
areaIcon = "IM";

makeTab("<b>Evening Stars</b>","<font face=verdana size=2px>(Area I5)<br> Membership eligibility criteria,<br>Contact for Requirements<br>Meets 6:00 PM, 1st Friday<br>Schwab Bldg<br>211 Main St<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/1424967-Evening-Stars target=new>club contact information</a>")     
makeTab("<b>Main Street Maniacs</b>","<font face=verdana size=2px> (Area I5)<br>Open to all interested parties<br>Meets 4:00 PM, 2nd and 4th Wed<br>Schwab Bldg / Diamond Conf Rm<br>7th Flr / Rm 493<br>211 Main St<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/00008557-Main-Street-Maniacs-Toastmasters-Club target=new>club contact information</a>")     




	 #**** multiple club marker  ***
latlong = (37.792179,-122.397478)     
areaIcon = "IM";

makeTab("<b>Stagecoach Speakers Frontier</b>","<font face=verdana size=2px>(Area I3)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>333 Market St.<br>Sequoia Conference Rm., 3rd Fl.<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/1214446-Stagecoach-Speakers-Frontier target=new>club contact information</a>")     
makeTab("<b>Upwardly Global </b>","<font face=verdana size=2px>(Area I1)<br>Open to all interested parties<br>Meets 6:30 pm, Tuesdays<br>333 Market St.<br>28th Floor<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/1567667-Upwardly-Global-Toastmasters-Club target=new>club contact information</a>")     
makeTab("<b>SF Bilingual Cantonese-English</b>","<font face=verdana size=2px>(Area I2)<br>Open to all interested parties<br>Meets 6:30 PM, 1st & 3rd Wednesday<br>Wells Fargo, 2nd Fl Break Room<br>333 Market St<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/04409370-san-francisco-bilingual-cantonese-english-toastmasters target=new>club contact information</a>")     




	 #**** multiple club marker  ***
latlong = (37.789519,-122.389035)     
areaIcon = "IM";

makeTab("<b>San Francisco Mandarin English </b>","<font face=verdana size=2px>(Area I5)<br>Open to all interested parties<br>Meets  6:30 PM, Wednesday<br>Gensler Architecture (3rd Floor)<br>2 Harrison Street<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/2258108-San-Francisco-Mandarin-English target=new>club contact information</a>")     
makeTab("<b>Toastmasters of Wharton West </b>","<font face=verdana size=2px>(Area I4)<br>Closed Club,<br>Contact for Requirements<br>Meets 6:45 PM , Fridays<br>Wharton School of Business<br>2 Harrison St Fl 6<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/03223203-toastmasters-of-wharton-west target=new>club contact information</a>")     
makeTab("<b>Gensler Toastmasters</b>","<font face=verdana size=2px>(Area I5)<br>Closed Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>2 Harrison St, Suite 400<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/4060756-Gensler-Toastmasters target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.416153,-121.919193)     
areaIcon = "FM";

makeTab("<b>Mandarin English</b>","<font face=verdana size=2px><b>Mandarin English Toastmasters<br>San Jose</b>&nbsp; (Area F4)<br>Open to all interested parties<br>Meets 7:00 PM, Wednesday<br>Cisco Building 22<br>Willow Conference Room<br>821 Alder Drive<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/2410520-Mandarin-English-Toastmasters-San-Jose target=new>club contact information</a>")     
makeTab("<b>Mandarin English Silicon Valley</b>","<font face=verdana size=2px><b>Mandarin English Toastmasters Silicon Valley</b>&nbsp; (Area F3)<br>Open to all interested parties<br>Meets 7:00 PM, Thursdays<br>Cisco Building 22<br>Willow Conference Room<br>821 Alder Drive<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/2072562-Mandarin-English-Toastmasters-Silicon-Valley target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.396721,-121.919106)     
areaIcon = "FM";

makeTab("<b>Cadence AHgorithms</b>","<font face=verdana size=2px><b>Cadence AHgorithms Club</b>&nbsp; (Area F2)<br>Open to all interested parties<br>Meets 12:00 PM, Tuesday<br>Cadence Design Systems, Inc.<br>Building 3 Duluth Conference Room<br>2655 Seely Ave<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/00007922-Cadence-AHgorithms-Club target=new>club contact information</a>")     
makeTab("<b>SV English Vietnamese</b>","<font face=verdana size=2px><b>Silicon Valley English Vietnamese<BR>Toastmasters</b>&nbsp; (Area F4)<br>Open to all interested parties<br>Meets 7:00 PM - 8:30 PM, Tuesday<br>Cadence Design Systems, Inc. Building 5<br>2655 Seely Ave<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/2663147-Silicon-Valley-English-Vietnamese-Toastmasters target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.41850, -121.95004)     
areaIcon = "FM";

makeTab("<b>Brocade Communicators</b>","<font face=verdana size=2px> (Area F2)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 - 1:00 pm, Tuesday<br>IMC Theater 1 or 2 Building 2<br>130 Holger Way<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/2492534-Brocade-Communicators target=new>club contact information</a>")     
makeTab("<b>ESV Toastmaster</b>","<font face=verdana size=2px>(Area F4)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 11:30 AM, Tuesday<br>300 Holger Way<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/2433002-ESV-Toastmaster target=new>club contact information</a>")     




	 #**** multiple club marker  ***
latlong = (37.41455,-122.02635)     
areaIcon = "GM";

makeTab("<b>G-E-M Club &nbsp;</b>","<font face=verdana size=2px>(Area G4)<br>Open to all interested parties<br>Meets 11:55 AM, Tuesday<br>Lockheed Martin B/166<br>1111 Lockheed Way<br>(corner of G St & 8th Ave)<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/00004124-g-e-m-club target=new>club contact information</a><br>&nbsp;")     
makeTab("<b>Toast Launchers Club &nbsp;</b>","<font face=verdana size=2px>(Area G1)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 5:00 PM, Thursday<br>Lockheed Martin Sunnyvale Campus B/157 Conference Rm 5A<br>1111 Lockheed Martin Way<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/733423-Toast-Launchers-Club target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.416384,-122.024853)     
areaIcon = "GM";

makeTab("<b>Agile Articulators</b>","<font face=verdana size=2px><b>Agile Articulators -<br>Speech and Debate</b>&nbsp; (Area G4)<br>Open to all interested parties<br>Meets 6:00 PM, 1st and 3rd Monday<br>Yahoo! Building D Yahoo!poly<br>701 First Avenue<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/3104-Agile-Articulators---Speech-and-Debate target=new>club contact information</a><br>&nbsp;")     
makeTab("<b>Sierra 49ers</b>","<font face=verdana size=2px><b>Sierra 49ers</b>&nbsp; (Area G1)<br>Open to all interested parties<br>Meets 6:00 PM, Friday<br>PMC Sierra Cafeteria<br>1380 Bordeaux Drive<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/00000049-Sierra-49ers target=new>club contact information</a>")     
makeTab("<b>Yahoo! Yapsters</b>","<font face=verdana size=2px><b>Yahoo! Yapsters Club</b>&nbsp; (Area G1)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>Yahoo! Building D Yahoo!poly<br>701 First Avenue<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/00605653-yahoo-yapsters-club target=new>club contact information</a>")     



	 #**** multiple club marker  ***
latlong = (37.506253,-122.261813)     
areaIcon = "CM";

makeTab("<b>Point Of Order Club</b>","<font face=verdana size=2px>(Area C5)<br>Membership prerequisite,<br>contact for information<br>Meets 6:00 PM, 3rd Tuesday<br>SamTrans, 3rd floor<br>1250 San Carlos Avenue<br>San Carlos 94070<br><a href=http:#www.toastmasters.org/Find-a-Club/00006028-Point-Of-Order-Club target=new>club contact information</a>")     
makeTab("<b>San Carlos Toastmasters &nbsp;</b>","<font face=verdana size=2px>(Area C5)<br>Open to all interested parties<br>Meets 7:30 PM, 3rd Thursday<br>SamTrans, 3rd floor<br>1250 San Carlos Avenue<br>San Carlos 94070<br><a href=http:#www.toastmasters.org/Find-a-Club/00000318-san-carlos-toastmasters-formerly-speak4yourself target=new>club contact information</a>")     




	 #**** multiple club marker  ***
latlong = (37.655069,-122.382138)     
areaIcon = "HM";

makeTab("<b>Genentech Toastmasters</b>","<font face=verdana size=2px>(Area H6)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Friday<br>Genentech Inc.<br>1 DNA Way<br>South San Francisco 94080<br><a href=http:#www.toastmasters.org/Find-a-Club/859889-Genentech-Toastmasters-Club target=new>club contact information</a>")     
makeTab("<b>MA&S Toastmasters	</b>","<font face=verdana size=2px>(Area H5)<br>Open to all interested parties<br>Meets 12:00 PM Tuesday<br>GNE Upper Campus<br>Genentech Building 26<br>1 DNA Way<br>South San Francisco 94080<br><a href=http:#www.toastmasters.org/Find-a-Club/03835218-mas-toastmasters target=new>club contact information</a>")     




	 #**** multiple club marker  ***
latlong = (37.789900, -122.3948)     
areaIcon = "IM";

makeTab("<b>100 California Toastbusters</b>","<font face=verdana size=2px>(Area I5)<br>Open to all interested parties<br>Meets 6:00 PM, Tuesday<br>Apollo Group<br>199 Fremont St<br>Suite 1400<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/1267190-100-California-Toastbusters target=new>club contact information</a>")     
makeTab("<b>StubHub Toastmasters </b>","<font face=verdana size=2px>(Area I4)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Monday<br>StubHub<br>199 Fremont St<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/2778439-StubHub-Toastmasters target=new>club contact information</a>")     




	 #**** multiple club marker  ***
latlong = (37.389319,-121.979076)     
areaIcon = "JM";

makeTab("<b>Inteligent Speakers Club</b>","<font face=verdana size=2px>(Area J2)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Wednesday<br>Intel Security office building<br>2821 Mission College Blvd<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/3972673-Inteligent-Speakers-Club target=new>club contact information</a>")     
makeTab("<b>McAfee Thursday Toastmasters</b>","<font face=verdana size=2px>(Area J4)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Thursday<br>McAfee<br>2821 Mission College Blvd<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/4023252-McAfee-Thursday-Toastmasters-Club target=new>club contact information</a>")     
makeTab("<b>McAfee Tuesday Toastmasters</b>","<font face=verdana size=2px>(Area J5)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Tuesday<br>McAfee<br>2821 Mission College Blvd<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/4023267-McAfee-Rise-and-Shine-Toastmasters-Club target=new>club contact information</a>")     






 #**** single club marker  ***
latlong = (37.060131,-122.008633)     
areaIcon = "A3";
makeTab("<b>831 Storytellers</b>","<font face=verdana size=2px>Closed Club, Contact for Requirements<br>Meets 7:00 PM 1st and 3rd Wednesday<br>American Dream Realty<br>5522 Scotts Valley Dr<br>Scotts Valley 95066<br><a href=http:#www.toastmasters.org/Find-a-Club/04670726-831-storytellers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.444349,-122.164774)     
areaIcon = "C4";
makeTab("<b>A9 Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Thursday<br>130 Lytton Ave<br>Palo Alto 94301<br><a href=http:#www.toastmasters.org/Find-a-Club/03989851-A9-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.781114,-122.418062)     
areaIcon = "D4";
makeTab("<b>AAC-Seiu1000</b>","<font face=verdana size=2px>Closed Company Club, Contact for Requirements<br>Meets 12:15 PM Tuesdays<br>State of California Building<br>Santa Barbara Room<br>455 Golden Gate Ave<br>San Francisco 94102<br><a href=http:#www.toastmasters.org/Find-a-Club/04413845-aacseiu1000 target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.44239, -121.921401)     
areaIcon = "F1";
makeTab("<b>ABBYY Talk</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00pm, 2nd Wednesday<br>880 N McCarthy Blvd<br>Ste 220<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/1862699-ABBYY-Talk target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.550500,-122.291959)     
areaIcon = "H5";
makeTab("<b>ABD Toastmasters</b>","<font face=verdana size=2px>Closed Company Club, Contact for Requirements<br>Meets 10:30 AM, 2nd and 4th Friday<br>ABD Main Conference Room<br>3 Waters Park Dr Ste 100<br>San Mateo 94403<br><a href=http:#www.toastmasters.org/Find-a-Club/04147122-abd-toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.770151,-122.466706)     
areaIcon = "E3";
makeTab("<b>Academy Toastmasters</b>","<font face=verdana size=2px>Closed Other/Specialized Club,<br>Contact for Requirements<br>Meets 12:00 PM, 2nd 3rd and 4th Thursday<br>California Academy of Sciences<br>55 Music Concourse Drive<br>San Francisco 94118<br><a href=http:#www.toastmasters.org/Find-a-Club/00769523-Academy-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.287029,-121.948335)     
areaIcon = "B2";
makeTab("<b>Adelante Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:15 AM, Tuesday<br>Hick'ry Pit Restaurant<br>980 East Campbell Avenue<br>Campbell 95008<br><a href=http:#www.toastmasters.org/Find-a-Club/00005232-Adelante-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.2441,-121.8287)     
areaIcon = "A6";
makeTab("<b>Adlibmasters Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 1st and 3rd Tuesday 5:00 PM, 4th Tuesday 12:00 PM<br>Hitachi Global Storage Technologies / IBM<br>5600 Cottle Road Bd. 50 - B1<br>San Jose 95193<br><a href=http:#www.toastmasters.org/Find-a-Club/00001898-Adlibmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.77173,-122.402019)     
areaIcon = "D1";
makeTab("<b>Townsend Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Monday<br>600 Townsend Street<br>San Francisco 94107<br><a href=http:#www.toastmasters.org/Find-a-Club/1280840-Townsend-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.523495,-122.258799)     
areaIcon = "C5";
makeTab("<b>All EArs Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Every other Wednesday<br>Provident Credit Union<br>Filene Meeting Room<br>303 Twin Dolphin Drive<br>Redwood City 94065<br><a href=http:#www.toastmasters.org/Find-a-Club/590123-All-EArs-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.246873,-121.874615)     
areaIcon = "A6";
makeTab("<b>Almaden Valley Orators Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, 1st and 3rd Thursday<br>Santa Clara Valley Water District (Adminstration Building Room B108)<br>5750 Almaden Expressway<br>San Jose 95118<br><a href=http:#www.toastmasters.org/Find-a-Club/00004148-Almaden-Valley-Orators-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.400355,-121.935355)     
areaIcon = "F2";
makeTab("<b>Altera Innovators Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>Altera Corporation<br>101 Innovation Drive, Bldg 1<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/00586504-Altera-Innovators-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.409374,-122.036496)     
areaIcon = "G4";
makeTab("<b>Amazon Lab126 Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12 PM, 2nd & 4th Thursday<br>Amazon Lab 126<br>Hangar Conference Room<br>1120 Enterprise Way<br>Sunnyvale, California, 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/4340878-Amazon-Lab126-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.386764,-121.998567)     
areaIcon = "J1";
makeTab("<b>AMD Speak</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>Commons Building, Rooms 5, 6, and 7<br>1 AMD Place<br>Sunnyvale, CA 94088<br><a href=http:#www.toastmasters.org/Find-a-Club/1424963-AMD-Speak target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.339816,-122.041400)     
areaIcon = "B1";
makeTab("<b>APPADAA Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 10:00 AM, 2nd & 4th Sunday<br>Madura Restaurant<br>1635 Hollenbeck Ave<br>Sunnyvale, CA 940884<br><a href=http:#www.toastmasters.org/Find-a-Club/2929202-APPADAA-TamilEnglish-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.372654,-121.959326)     
areaIcon = "J4";
makeTab("<b>Applied Materials Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Applied Materials Central Campus<br>2861 Scott Boulevard / Building 19 (Call to confirm)<br>Santa Clara 95050<br><a href=http:#www.toastmasters.org/Find-a-Club/00005015-Applied-Materials-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.969832, -121.90448)     
areaIcon = "A4";
makeTab("<b>Aptos Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Rio Sands Hotel<br>116 Aptos Beach Drive<br>Aptos 95003<br><a href=http:#www.toastmasters.org/Find-a-Club/00000595-Aptos-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.431771,-121.8942)     
areaIcon = "F1";
makeTab("<b>ArtICCulators Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Wednesday<br>ICC Milpitas<br>525 Los Coches Street<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/00584244-ArtICCulators-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.796555,-122.411566)     
areaIcon = "E5";
makeTab("<b>Asian Express Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM, 2nd and 4th Wed<br>True Sunshine Church<br>1430 Mason St<br>San Francisco 94133<br><a href=http:#www.toastmasters.org/Find-a-Club/00002203-Asian-Express-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.334392,-121.891396)     
areaIcon = "B5";
makeTab("<b>ASPIRE Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 11:30 AM, 2nd & 4th Thursday<br>55 S Market St<br>San Jose 95113<br><a href=http:#www.toastmasters.org/Find-a-Club/1977581-ASPIRE-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.657302,-121.658806)     
areaIcon = "A2";
makeTab("<b>B.L.T. Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Monday<br>TAMC Office<br>155 Plaza Circle<br>Salinas 93901<br><a href=http:#www.toastmasters.org/Find-a-Club/638813-BLT-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.793066,-122.399051)     
areaIcon = "E2";
makeTab("<b>Bay Masters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:10 PM, Thursday<br>201 California Street<br>(between Front and Davis Streets)<br>2nd floor conference room<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/00007806-Bay-Masters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.421541,-121.954772)     
areaIcon = "F2";
makeTab("<b>Baytech Speak Easy</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>Boston Scientific<br>150 Baytech Dr<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/1286356-Baytech-Speak-Easy target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (36.619342, -121.843189)     
areaIcon = "A1";
makeTab("<b>Bayview Club</b>","<font face=verdana size=2px> (Area A1)<br>Open to all interested parties<br>Meets 6:00 PM, 1st and 3rd Wednesday<br>Panera Bread<br>2080 California Ave.<br>Suite C,<br>Sand City 93955<br><a href=http:#www.toastmasters.org/Find-a-Club/00008221-Bayview-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.789191,-122.395210)     
areaIcon = "I4";
makeTab("<b>BlackRock Speaks San Francisco</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 2:00 - 4:30 PM, 1st & 3rd Thursday<br>400 Howard St<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/2694124-BlackRock-Speaks-San-Francisco target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.397463,-121.886837)     
areaIcon = "B4";
makeTab("<b>BD Biosciences</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>BD Biosciences<br>2350 Qume Dr<br>San Jose 95131<br><a href=http:#www.toastmasters.org/Find-a-Club/04727466-bd-biosciences target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.793676,-122.401746)     
areaIcon = "E4";
makeTab("<b>BrightRoll</b>","<font face=verdana size=2px>Contact for Requirements<br>Meets 5:00 PM Tuesday<br>BrightRoll Headquarters<br>343 Sansome St Ste 600<br>San Francisco 94104<br><a href=http:#www.toastmasters.org/Find-a-Club/4191015-BrightRoll target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.67278,-122.38800)     
areaIcon = "H5";
makeTab("<b>Brisbane Club: Speaking Under the Stars</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM Monday<br>Radisson Hotel SFO Bayfront <br>5000 Sierra Point Pkwy<br>Brisbane 94005<br><a href=http:#www.toastmasters.org/Find-a-Club/00001818-Brisbane-Club-Speaking-Under-the-Stars target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.760869,-122.412252)     
areaIcon = "D3";
makeTab("<b>Burning Man Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 6:00 PM, 1st & 3rd Wednesdays<br>Burning Man HQ<br>660 Alabama St Fl 4<br>San Francisco 94110<br><a href=http:#www.toastmasters.org/Find-a-Club/3890460-Burning-Man-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.791406,-122.39844)     
areaIcon = "I2";
makeTab("<b>Cable Car Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 AM, Tuesday<br>United Health Care - 12th Floor<br>425 Market Street<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/00001243-Cable-Car-Toastmasters-Club target=new>club contact information</a><br>&nbsp;")     


 #**** single club marker  ***
latlong = (37.38579,-121.97313)     
areaIcon = "J5";
makeTab("<b>CA Toasties</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, 2nd and 4th Thursday<br>CA Technologies Office	<br>3965 Freedom Circle<br>Santa Clara, CA, 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/2394422-CA-Toasties target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.5372,-122.297540)     
areaIcon = "H4";
makeTab("<b>Chamber Speakers Circle Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:00 PM, Monday<br>Hillsdale Shopping Center<br>Basement Conference Room<br>San Mateo 94403<br><a href=http:#www.toastmasters.org/Find-a-Club/00600591-Chamber-Speakers-Circle-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.410613,-121.951783)     
areaIcon = "F5";
makeTab("<b>Champion Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Friday<br>Cypress Semiconductor Corporation<br>198 Champion Court, Bldg 6<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/00662205-Champion-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.4273,-122.071)     
areaIcon = "G5";
makeTab("<b>Google Quad Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Google<br>399 N. Whisman Road<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/1565818-Chatterbox target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.408291,-121.950216)     
areaIcon = "F5";
makeTab("<b>Cisco Speaks Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:15 PM, Tues<br>Cisco Systems, Inc / Bldg P<br>125 W Tasman Dr<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/00008124-Cisco-Speaks-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.795936,-122.400003)     
areaIcon = "E4";
makeTab("<b>CityMasters North</b>","<font face=verdana size=2px>(Area E4)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, 2nd & 4th Friday<br>San Francisco Regional Center<br>CA Room,Walnut Creek Conf Room<br>150 California St Fl 12<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/3349324-CityMasters-North target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.90874,-121.754895)     
areaIcon = "A4";
makeTab("<b>City Shakers Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Monday<br>City Council Chambers<br>250 Main Street<br>Watsonville 95077<br><a href=http:#www.toastmasters.org/Find-a-Club/00000301-City-Shakers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.77928,-122.411256)     
areaIcon = "D6";
makeTab("<b>Civic Center Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 11:30 AM, 1st and 3rd Wednesday<br>USan Francisco Federal Building<br>90 7th Street, B-110<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/00600229-Civic-Center-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.403837,-121.984464)     
areaIcon = "J2";
makeTab("<b>Coherent Communicators Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:05 PM, Thursday<br>Coherent Inc<br>5100 Patrick Henry Drive<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/00005098-Coherent-Communicators-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.770374,-122.387269)     
areaIcon = "D1";
makeTab("<b>Cloudmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Cisco Meraki<br>500 Terry Francois St<br>San Francisco 94158<br><a href=http:#www.toastmasters.org/Find-a-Club/04640219-cisco-meraki-toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.404648,-122.036321)     
areaIcon = "G4";
makeTab("<b>Comcast Silicon Valley Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:15PM, Thursday<br>Comcast Silicon Valley Innovation Center<br>1050 Enterprise Way<br>Sunnyvale, California, 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/4100886-Comcast-Silicon-Valley-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.557708,-122.300993)     
areaIcon = "Unassigned";
makeTab("<b>CSG Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, 2nd & 4th Thursdays<br>1700 S Amphlett Blvd<br>Floor 3<br>San Mateo 94402<br><a href=http:#www.toastmasters.org/Find-a-Club/04840673-csg-toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.654434,-121.808091)     
areaIcon = "A2";
makeTab("<b>CSUMB Oratory Otters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:00 PM, Thursday<br>Cal State Monterey Bay<br>100 Campus Ctr<br>Seaside 93955<br><a href=http:#www.toastmasters.org/Find-a-Club/2571179-CSUMB-Oratory-Otters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.32089,-122.01052)     
areaIcon = "B6";
makeTab("<b>Cupertino Morningmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 AM, Thursday<br>Bethel Lutheran Church<br>10181 Finch Avenue<br>Cupertino 95014<br><a href=http:#www.toastmasters.org/Find-a-Club/00004606-Cupertino-Morningmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.662895,-122.470421)     
areaIcon = "H6";
makeTab("<b>Daly City Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:10 PM, Fridays<br>Daly City Public Library<br>Serramonte Branch<br>40 Wembley Dr.<br>Daly City 94015<br><a href=http:#www.toastmasters.org/Find-a-Club/00001881-Daly-City-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.389285,-121.97018)     
areaIcon = "J2";
makeTab("<b>Dedupe This</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Data Domain<br>2421 MIssion College Blvd<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/1280493-Dedupe-This target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.412301, -121.977725)     
areaIcon = "J2";
makeTab("<b>Dell Silicon Valley Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:30 PM, Thursday<br>Dell Inc.<br>5480 Great America Pkwy<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/2811817-Dell-Silicon-Valley-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.788472, -122.39871)     
areaIcon = "I2";
makeTab("<b>Deloitte Toastmasters San Francisco</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 2:00 PM, 1st & 3rd Friday<br>Deloitte<br>555 Mission St<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/3972735-Deloitte-Toastmasters-San-Francisco target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.388075,-122.003906)     
areaIcon = "J1";
makeTab("<b>Destination Articulation</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:45 PM Tuesday<br>950 De Guigne Dr<br>Conference/Training Room A216<br>Sunnyvale 94085<br><a href=http:#www.toastmasters.org/Find-a-Club/2960268-Destination-Articulation target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.770127,-122.406883)     
areaIcon = "D3";
makeTab("<b>Dolby Speakers</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:05 PM, Wednesday<br>Dolby Laboratories<br>2999 Brannan St<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/2616974-Dolby-Speakers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.426515,-122.118028)     
areaIcon = "C1";
makeTab("<b>Early Risers Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 AM, Tuesday<br>Unity Church<br>3391 Middlefield Road<br>Palo Alto 94304<br><a href=http:#www.toastmasters.org/Find-a-Club/00002117-Early-Risers-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.793058,-122.403177)     
areaIcon = "E4";
makeTab("<b>Earthjustice</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 121:30 PM, 1st & 3rd Thursday<br>Earthjustice - Bay Conference Room<br>500 California St # 500 San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/04720111-earthjustice target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.792895,-122.396644)     
areaIcon = "I1";
makeTab("<b>Electric Toasters Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>PG&E Corporation General Office<br>245 Market Street<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/999399-Electric-Toasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.762123,-122.425212)     
areaIcon = "E5";
makeTab("<b>Eloquent Elocutionists</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 7:00 PM, Monday<br>65 Dorland Street<br>San Francisco 94110<br><a href=http:#www.toastmasters.org/Find-a-Club/1279215-Eloquent-Elocutionists target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.388179,-121.978004)     
areaIcon = "J4";
makeTab("<b>EMC Masters Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>EMC Corporation<br>2831 Mission College Blvd<br>Pinot Noir Conference Room<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/1514703-EMC-Masters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.785188,-122.398239)     
areaIcon = "D2";
makeTab("<b>EPA Speak Easy</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 pm, 2nd & 4th Wednesday<br>US EPA Region 9<br>75 Hawthorne St<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/1440375-EPA-Speak-Easy target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.784677,-122.404508)     
areaIcon = "D2";
makeTab("<b>Epicurean SF</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 3:30 PM, Tuesday<br>SF City College, Culinary Dept.<br>88 4th St<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/3960208-Epicurean-SF target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.414367,-122.017175)     
areaIcon = "G1";
makeTab("<b>EPL Toasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 pm, 2nd & 4th Thursday<br>1325 Borregas Ave<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/2853873-EPL-Toasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.975898,-121.982276)     
areaIcon = "A4";
makeTab("<b>Evening Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM, Monday<br>Elena Baskin Live Oak Senior Ctr<br>1777 Capitola Rd<br>Santa Cruz 95062<br><a href=http:#www.toastmasters.org/Find-a-Club/00003802-Evening-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.775914,-122.418027)     
areaIcon = "D4";
makeTab("<b>Everybody Speaks Club</b>","<font face=verdana size=2px><br>Open to all interested parties<br>Meets 6:45 PM, 2nd & last Tuesday<br>Bank of America<br>1455 Market Street<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/00009408-Everybody-Speaks-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.366627,-122.023602)     
areaIcon = "G3";
makeTab("<b>Fair Oaks Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 11:30 AM, Sunday<br>Fair Oaks West Club House (Movie Room)<br>655 S Fairoaks Avenue<br>Sunnyvale 94086<br><a href=http:#www.toastmasters.org/Find-a-Club/00007528-Fair-Oaks-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.79232,-122.39820)     
areaIcon = "E4";
makeTab("<b>First Republic Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 5:30 PM, Wednesday<br>First Republic Bank<br>15th Floor-Conf Rm 15G<br>388 Market St<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/3154261-First-Republic-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.38610,-122.08407)     
areaIcon = "G6";
makeTab("<b>Flying Toasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM - 7:30 PM, Tuesday<br>Ooyala Inc.<br>Zamba Conference Room<br>800 W El Camino Real Ste 350<br>Mountain View 94040<br><a href=http:#www.toastmasters.org/Find-a-Club/3179320-Flying-Toasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.558642,-122.27106)     
areaIcon = "H2";
makeTab("<b>Foster City Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 PM, 1st and 3rd Wednesday<br>Foster City Community Center<br>1000 East Hillsdale Boulevard<br>Foster City 94404<br><a href=http:#www.toastmasters.org/Find-a-Club/00004014-Foster-City-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.789252,-122.398553)     
areaIcon = "I2";
makeTab("<b>GGU Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM, Monday<br>Golden Gate University<br>536 Mission St<br>(between 1st and 2nd)<br>3rd Floor, Room 3323<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/00006094-GGU-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.790388,-122.400631)     
areaIcon = "E2";
makeTab("<b>Golden Gate Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:00 PM, Wed<br>American Arbitration Assoc<br>Citigroup Ctr<br>1 Sansome St; 16th Flr<br>San Francisco 94104<br><a href=http:#www.toastmasters.org/Find-a-Club/00000056-Golden-Gate-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.78075,-122.42346)     
areaIcon = "E5";
makeTab("<b>Golden Poppy Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 5:30 PM, Tuesdays<br>San Francisco Federal Credit Union<br>Golden Gate Meeting Room 2nd Floor<br>770 Golden Gate Ave<br>San Francisco 94102<br><a href=http:#www.toastmasters.org/Find-a-Club/3084032-Golden-Poppy-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.411344, -121.977097)     
areaIcon = "J5";
makeTab("<b>Great America Speakers</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:30 pm, Thursdays<br>Conference Center<br>5451 Great America Pkwy<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/04486360-great-america-speakers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.237041, -121.78521)     
areaIcon = "A6";
makeTab("<b>The Grummarians</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 pm, Thursdays<br>Northrup Grumman<br>6377 San Ignacio Avet<br>San Jose 95119<br><a href=http:#www.toastmasters.org/Find-a-Club/01842218-the-grummarians target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.566229,-122.282778)     
areaIcon = "H2";
makeTab("<b>GToast</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 pm, Alt Wednesday & Tuesday<br>Gilead Sciences Inc<br>333 Lakeside Dr<br>Foster City 94404<br><a href=http:#www.toastmasters.org/Find-a-Club/1488183-GToast target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.560019,-122.270341)     
areaIcon = "H1";
makeTab("<b>Guidewire Premium Presenters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:05 pm, Monday<br>Ocean Conference Room, E3<br>1051 E Hillsdale Blvd Ste 800<br>Foster City 94404<br><a href=http:#www.toastmasters.org/Find-a-Club/2626176-Guidewire-Premium-Presenters target=new>club contact information</a>")     


  #**** single club marker  ***
latlong = (37.373568,-121.949744)     
areaIcon = "B3";
makeTab("<b>Hi Definition Speakers</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 pm, Wednesday<br>Hitachi<br>750 Central Expy<br>Santa Clara 95050 94404<br><a href=http:#www.toastmasters.org/Find-a-Club/2294225-Hi-Definition-Speakers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.515318,-122.283742)     
areaIcon = "H1";
makeTab("<b>High Spirits of Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 PM, 2nd and 4th Friday<br>Norte Dame de Namur University - Cuvilly Hall<br>1500 Ralston Avenue<br>Belmont 94002<br><a href=http:#www.toastmasters.org/Find-a-Club/00004368-high-spirits-of-toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.377426,-121.921474)     
areaIcon = "B4";
makeTab("<b>Hot Buttered Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>2211 North First St<br>San Jose 95131<br><a href=http:#www.toastmasters.org/Find-a-Club/827125-Hot-Buttered-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.415998,-122.144914)     
areaIcon = "C2";
makeTab("<b>HP Hilltop Speakers Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Thursday<br>Hewlett Packard<br>3000 Hanover Street<br>Palo Alto 94304<br><a href=http:#www.toastmasters.org/Find-a-Club/00004515-HP-Hilltop-Speakers-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.782259, -122.406417)     
areaIcon = "D2";
makeTab("<bHubmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM, Tuesday<br>The Hub, South of Market (SOMA)<br>901 Mission St<br>(Second Floor at 5th Street)<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/2020878-Hubmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.423021,-122.083739)     
areaIcon = "G5";
makeTab("<b>I'm Feeling Chatty Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Google - Bldg 43<br>1600 Amphitheatre Pkwy<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/607909-Im-Feeling-Chatty-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.430808,-122.097888)     
areaIcon = "G5";
makeTab("<b>Intuitively Speaking Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Thursday<br>Intuit<br>2700 Coast Ave<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/00007871-Intuitively-Speaking-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.433907,-121.921433)     
areaIcon = "F1";
makeTab("<b>JDSU Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Thursday<br>JDSU Office<br>400 N McCarthy Blvd<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/2814312-JDSU-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.41001,-122.051944)     
areaIcon = "G5";
makeTab("<b>Jetstream Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Monday<br>Ames Research Center<br>Building N-269 Room 179<br>Moffett Field 94035<br><a href=http:#www.toastmasters.org/Find-a-Club/00002624-Jetstream-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.409813,-122.026549)     
areaIcon = "G4";
makeTab("<b>Juniper Jabbers Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Juniper Networks<br>1194 Mathilda Ave<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/853108-Juniper-Jabbers-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.419084,-121.927309)     
areaIcon = "F3";
makeTab("<b>KT Talkers Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 11:40 AM Tuesday<br>KLA-Tencor, Building 7, Waikiki Beach Conf Room<br>One Technology Drive<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/00007168-KT-Talkers-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.781285,-122.503672)     
areaIcon = "E5";
makeTab("<b>Land's End Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 5:00 PM, 2nd and 4th Wednesday<br>Veterans Affairs Medical Ctr / 1A-122 / Teall Rm<br>4150 Clement Street<br>San Francisco 94121<br><a href=http:#www.toastmasters.org/Find-a-Club/00003976-Lands-End-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.386183,-121.984333)     
areaIcon = "J1";
makeTab("<b>Laser Sharp Speakers Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Thursday<br>Spectra-Physics<br>3635 Peterson Way<br>Santa Clara CA, 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/00009946-Laser-Sharp-Speakers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.428083,-122.161502)     
areaIcon = "C3";
makeTab("<b>Lee Emerson Bassett Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:15 PM, Wednesday<br>McClelland Bldg, RM M109<br>Knight Management Center<br>655 Knight Way<br>Palo Alto 94305<br><a href=http:#www.toastmasters.org/Find-a-Club/00000033-Lee-Emerson-Bassett-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.789306,-122.403564)     
areaIcon = "E1";
makeTab("<b>Linkedin San Francisco</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 2:00 PM, Wednesday<br>Linkedin SF Office<br>120 Kearny St Fl 15<br>San Francisco 94108<br><a href=http:#www.toastmasters.org/Find-a-Club/3789758-Linkedin-San-Francisco target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.331741, -122.030333)     
areaIcon = "B1";
makeTab("<b>MacinTalkers Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 5:30 PM, Wednesday<br>Apple Computer<br>1 Infinite Loop, Singapore Conference Room<br>Cupertino 95014<br><a href=http:#www.toastmasters.org/Find-a-Club/00007430-MacinTalkers-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.743101,-122.478204)     
areaIcon = "E3";
makeTab("<b>Magic Sunrisers</b>","<font face=verdana size=2px><br>Open to all interested parties<br>Meets 7:00 AM, Wednesday<br>Tennessee Grill<br>1128 Taraval Avenue<br>San Francisco 94116<br><a href=http:#www.toastmasters.org/Find-a-Club/00002407-Magic-Sunrisers-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.793642,-122.396399)     
areaIcon = "E2";
makeTab("<b>Marsh Mellow Toasters </b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 8:30 AM, 1st and 3rd Wednesdays<br>Marsh Risk & Insurance Services<br>One California Street, 7th Floor<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/00000779-Marsh-Mellow-Toasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.405652,-121.950263)     
areaIcon = "F5";
makeTab("<b>Maxim Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>Maxim<br>160 Rio Robles<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/2419756-Maxim-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.376224,-121.959751)     
areaIcon = "J4";
makeTab("<b>MCA Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Thursday<br>Maryam Banquet Hall<br>3003 Scott Blvd<br>Santa Clara 95054<br><br><a href=http:#www.toastmasters.org/Find-a-Club/685103-MCA-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.789026,-122.402249)     
areaIcon = "D5";
makeTab("<b>McKesson Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>McKesson Corporation - 30 Floor<br>One Post Street<br>San Francisco 94104<br><a href=http:#www.toastmasters.org/Find-a-Club/00003275-McKesson-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.788047,-122.402945)     
areaIcon = "E2";
makeTab("<b>MCOM</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets Friday<br>Macys.com<br>685 Market St. Ste 800<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/2409787-MCOM target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.396348,-121.935245)     
areaIcon = "F4";
makeTab("<b>Memory Masters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM Friday<br>Micron Technology Inc.<br>3060 N 1st St<br>Conference Room #148<br>San Jose, California, 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/2432521-Memory-Masters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.432869,-122.199976)     
areaIcon = "C4";
makeTab("<b>Menlo Park Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Tuesday<br>Bethany Lutheran Church<br>1095 Cloud Ave<br>Menlo Park 94025<br><a href=http:#www.toastmasters.org/Find-a-Club/00001372-Menlo-Park-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.411718,-121.947807)     
areaIcon = "F2";
makeTab("<b>Microsemi Masters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:35 PM, Thursday<br>Microsemi Corporation<br>3850 N 1st Street<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/854912-Microsemi-Masters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.599942,-122.401129)     
areaIcon = "H3";
makeTab("<b>Millbrae'ers Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 PM, 1st and 3rd Tuesday<br>Millbrae Community Center<br>477 Lincoln Circle<br>Millbrae 94030<br><a href=http:#www.toastmasters.org/Find-a-Club/00002168-Millbraeers-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.445866,-121.908963)     
areaIcon = "F1";
makeTab("<b>Milpitas Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Mondays<br>919 Hanson Court<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/00007242-Milpitas-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.403461, -122.036060)     
areaIcon = "G2";
makeTab("<b>MoToast</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesdays <br>Motorola, Floor 1<br>1000 Enterprise Way Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/04712057-motoast target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.396100, -122.056143)     
areaIcon = "G5";
makeTab("<b>MobileIron Speakers Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, 1st & 3rd Wednesdays <br>MobileIron Headquarters<br>1415 E Middlefield Rd<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/04361768-mobileiron-speakers-club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.793606,-122.39571)     
areaIcon = "I1";
makeTab("<b>Money Talks Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 11:45 AM, Wednesday<br>Federal Reserve Bank<br>101 Market Street<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/00003295-Money-Talks-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.600034,-121.897804)     
areaIcon = "A1";
makeTab("<b>Monterey Institute Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:10 PM, Tuesday<br>Morse Bldg / Rm A101<br>426 Van Buren St<br>Monterey 93940<br><a href=http:#www.toastmasters.org/Find-a-Club/00007120-Monterey-Institute-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.582645, -121.901556)     
areaIcon = "A1";
makeTab("<b>Monterey Peninsula Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:45 AM, Thursday<br>Crazy Horse Restaurant, Bay Park Hotel<br>1425 Munras Ave<br>Monterey 93940<br><a href=http:#www.toastmasters.org/Find-a-Club/00000934-Monterey-Peninsula-Toastmasters-Club-934 target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.788530,-122.395144)     
areaIcon = "I3";
makeTab("<b>Moody's SF Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM , 1st & 3rd Wednesday<br>Moody's Analytics<br>405 Howard St Ste 300<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/3790836-Moodys-SF-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.129395,-121.651681)     
areaIcon = "A6";
makeTab("<b>Morgan Hill</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 AM, Thursday<br>BookSmart <br>80 East 2nd Street <br>Morgan Hill 95037<br><a href=http:#www.toastmasters.org/Find-a-Club/00008337-Morgan-Hill-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.401026,-122.097745)     
areaIcon = "G6";
makeTab("<b>Mountain View Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Wednesday<br>Mountain View Community Center<br>201 S Rengstorff Ave<br>Mountain View 94040<br><a href=http:#www.toastmasters.org/Find-a-Club/04528013-mountain-view-toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.416957,-122.152517)     
areaIcon = "C1";
makeTab("<b>Move Fast and Say Things</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00, Wednesday<br>BookSmart <br>1601 S. California Avenue<br>Palo Alto 94304<br><a href=http:#www.toastmasters.org/Find-a-Club/1573264-Move-Fast-and-Say-Things target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.598237,-121.877225)     
areaIcon = "A1";
makeTab("<b>Naval Postgraduate School Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:10 PM, Friday<b>Naval Postgraduate School<br>Glasgow Hall, Building 302, Room 303<br>Monterey 93943<br><a href=http:#www.toastmasters.org/Find-a-Club/00002032-Naval-Postgraduate-School-Club target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.38724,-121.96697)     
areaIcon = "J5";
makeTab("<b>NCVI Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Friday<br>Main Conference Room - 14th Floor<br>2350 Mission College Blvd<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/3143455-NCVI-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.382771,-121.962213)     
areaIcon = "J3";
makeTab("<b>Next Step Toastmasters</b>","<font face=verdana size=2px>Closed Community Club,<br>Contact for Requirements<br>Meets 1:30 PM, 2nd Sun<br>Biltmore Hotel (Montague Cafe)<br>2151 Laurelwood Drive<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/770392-Next-Step-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.40153, -121.911161)     
areaIcon = "F2";
makeTab("<b>North Valley Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 AM, Friday<br>Brandon's Restuarant at Beverly Heritage Hotel <br>1820 Barber Ln<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/00002038-North-Valley-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.423654,-122.071128)     
areaIcon = "G5";
makeTab("<b>Now You're Talk[In]</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Friday<br>Culture Club, Linkedin HQ<br>2051 Stierlin Ct<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/1852523-Now-Youre-TalkIn target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.371091,-121.966500)     
areaIcon = "J4";
makeTab("<b>nSpeak</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Nvidia Corp<br>2700 San Tomas Expressway<br>Santa Clara 95050<br><a href=http:#www.toastmasters.org/Find-a-Club/1490234-nSpeak target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.654344,-122.395637)     
areaIcon = "H4";
makeTab("<b>Onyx Orators</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, 1st & 3rd Wednesday<br>Onyx Pharmaceuticals<br>249 E Grand Ave<br>outh San Francisco 94080<br><a href=http:#www.toastmasters.org/Find-a-Club/2908804-Onyx-Orators target=new>club contact information</a>")     


#**** single club marker  ***
latlong = (37.775120,-122.398874)     
areaIcon = "D1";
makeTab("<b>OpenDNS</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 5:00 PM Tuesdays <br>OpenDNS Headquarters<br>145 Bluxome St<br>San Francisco 94107<br><a href=http:#www.toastmasters.org/Find-a-Club/3710811-OpenDNS target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.741543,-122.504297)     
areaIcon = "E3";
makeTab("<b>Opportunity Speakers</b>","<font face=verdana size=2px><br>Closed Community Club,<br>Contact for Requirements<br>Meets 6:45 PM, 2nd Tuesday<br>Congregation B'nai Emunah<br>3595 Taraval at 46th<br>San Francisco 94116<br><a href=http:#www.toastmasters.org/Find-a-Club/00004282-Opportunity-Speakers-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.412146,-122.019148)     
areaIcon = "G1";
makeTab("<b>Optical Orators</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Infinera<br>169 W Java Dr<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/1571496-Optical-Orators target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.526775,-122.26387)     
areaIcon = "H2";
makeTab("<b>OracleDirect Toastmasters - RWS</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, 1st & 3rd Thurs<br>Oracle Plaza / B4022<br>10 Twin Dolphin Dr<br>Redwood Shores 94065<br><a href=http:#www.toastmasters.org/Find-a-Club/00005022-OracleDirect-Toastmasters-RWS target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.529537,-122.267126)     
areaIcon = "H1";
makeTab("<b>Oracle Speakers</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Oracle Corporation<br>Room 3OP-588<br>Redwood Shores 94065<br><a href=http:#www.toastmasters.org/Find-a-Club/00002544-Oracle-Speakers-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.401355,-122.098551)     
areaIcon = "G6";
makeTab("<b>Orbiters Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM, 1st & 3rd Thursdays<br>Mountain View Community Center<br>210 S Rengstorff Ave<br>Mountain View 94040<br><a href=http:#www.toastmasters.org/Find-a-Club/00002943-Orbiters-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.384028, -121.926119)     
areaIcon = "B4";
makeTab("<b>Orchard  Orators</b>","<font face=verdana size=2px>(Area B4)<br>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Room: L1 Travel/L 1.2.001 First Class (16)<br>2525 N 1st St<br>San Jose 95131<br><a href=http:#www.toastmasters.org/Find-a-Club/2669924-Orchard-Orators target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.598881,-122.499333)     
areaIcon = "H4";
makeTab("<b>Pacifica PM Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 pm to 8:30pm, Thursday<br>Pacifica Community Center<br>540 Crespi Drive<br>Pacifica 94044<br><a href=http:#www.toastmasters.org/Find-a-Club/00001618-Pacifica-PM-Club target=new>club contact information</a>")     

 
 #**** single club marker  ***
latlong = (37.60044,-122.37552)     
areaIcon = "H4";
makeTab("<b>Pacific Rim Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 pm to 8:00pm, Wednesday<br>Global Vision's Meeting Room<br>1818 Gilbreth Rd Ste 145<br>Burlingame 94010<br><a href=http:#www.toastmasters.org/Find-a-Club/3572098-Pacific-Rim-Toastmasters target=new>club contact information</a>")     


#**** single club marker  ***
latlong = (36.9226,-121.74682)     
areaIcon = "A4";
makeTab("<b>Pajaro Valley Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 AM, Tuesday<br>Santa Cruz Fair Grounds/ Board Room<br>East Lake Ave<br>Watsonville 95076<br><a href=http:#www.toastmasters.org/Find-a-Club/00002373-Pajaro-Valley-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.444494,-122.160755)     
areaIcon = "C3";
makeTab("<b>Palo Alto Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 11:00 AM, Tuesday<br>City Hall Of Palo Alto<br>250 Hamilton Avenue<br>Palo Alto 94301<br><a href=http:#www.toastmasters.org/Find-a-Club/00008218-Palo-Alto-Toastmsters target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (36.609165,-121.861361)     
areaIcon = "A1";
makeTab("<b>Peninsula Pros Club</b>","<font face=verdana size=2px> (Area A1)<br>Membership prerequisite,<br>Contact for Requirements<br>Meets 6:00 PM, 2nd Wednesday of Month<br>Monterey Beach Hotel<br>2600 Sand Dunes Drive<br>Monterey 93940<br><a href=http:#www.toastmasters.org/Find-a-Club/00008275-Peninsula-Pros-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.666722,-122.466829)     
areaIcon = "H6";
makeTab("<b>Peninsula Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 PM, 2nd & 4th Wednesday<br>333 Gellert Blvd<br>Second Floor, Suite 204<br>Daly City 94-15<br><a href=http:#www.toastmasters.org/Find-a-Club/00002697-Peninsula-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.775951,-122.393118)     
areaIcon = "D1";
makeTab("<b>Perkins+Will</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Friday<br>Titanium Conference Room<br>185 Berry St Ste 5100<br>San Francisco 94107<br><a href=http:#www.toastmasters.org/Find-a-Club/2525149-PerkinsWill target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.6168297,-122.3976183)     
areaIcon = "H5";
makeTab("<b>Plane Talk</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 11:45 AM, Tuesday<br>575 N. McDonnell Road 2nd Floor<br>San Francisco 94128<br><a href=http:#www.toastmasters.org/Find-a-Club/1863501-Plane-Talk target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.643761, -121.79785)     
areaIcon = "A2";
makeTab("<b>Planet Ord Toastmasters</b>","<font face=verdana size=2px>Closed Govt Agency Club,<br>Contact for Requirements<br>Meets 4:00 PM, Tuesday<br>Defense Manpower Data Center<br>400 Gigling Road<br>Seaside 93955<br><a href=http:#www.toastmasters.org/Find-a-Club/00004094-Planet-Ord-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.783052, -122.391071)     
areaIcon = "D1";
makeTab("<b>Ponytalk Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Splunk SF Headquarters<br>250 Brannan St<br>San Francisco 94107<br><a href=http:#www.toastmasters.org/Find-a-Club/4049645-Ponytalk-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.559957,-122.284161)     
areaIcon = "H3";
makeTab("<b>Pro Masters Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 AM, Thurs<br>Mimi's Cafe<br>2208 Bridgepoint Pkwy<br>San Mateo 94402<br><a href=http:#www.toastmasters.org/Find-a-Club/00004512-Promasters-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.336007,-121.901310)     
areaIcon = "B3";
makeTab("<b>Public Speak Easy's Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:05 PM, Wednesday<br>Social Services Agency<br>373 West Julian Street, Santa Clara Room<br>San Jose 95110<br><a href=http:#www.toastmasters.org/Find-a-Club/00008266-Public-Speak-Easys-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.780247,-122.420403)     
areaIcon = "D4";
makeTab("<b>Puc(k)sters Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:05 PM, Thursday<br>CA Public Utilities Commission<br>505 Van Ness Avenue<br>San Francisco 94102<br><a href=http:#www.toastmasters.org/Find-a-Club/00003873-Pucksters-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.785002, -122.400197)     
areaIcon = "D5";
makeTab("<b>Quantcast Toastmasters Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 5:15 PM, 2nd & 4th Wednesday<br>Quantcast Corporation<br>201 3rd Street (Fl 8)<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/04408242-quantcast-toastmasters-club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.771704,-122.423845)     
areaIcon = "E5";
makeTab("<b>Rainbow Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:00 PM, Thursday<br>SF LGBT Community<br>1800 Market St<br>San Francisco 94117<br><a href=http:#www.toastmasters.org/Find-a-Club/822664-Rainbow-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.485528,-122.238892)     
areaIcon = "C5";
makeTab("<b>Redwood City Orators Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 AM, Friday<br>Saint Peters Church<br>178 Clinton Street<br>Redwood City 94062<br><a href=http:#www.toastmasters.org/Find-a-Club/00005707-Redwood-City-Orators-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.056422,-122.011724)     
areaIcon = "A3";
makeTab("<b>Redwood Ramblers Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>St. Philip Episcopal Church<br>5271 Scotts Valley Drive<br>Scotts Valley 95066<br><a href=http:#www.toastmasters.org/Find-a-Club/00008203-Redwood-Ramblers-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.784137,-122.408646)     
areaIcon = "D4";
makeTab("<b>Renaissance Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM, Wednesday<br>Please arrive in lobby 6:20<br><b>NextSpace</b><font face=verdana size=2px>1 Hallidie Plaza, 2th Floor<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/00009825-San-Francisco-Renaissance-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.788865,-122.399359)     
areaIcon = "I3";
makeTab("<b>Rhino Business Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM, Tues<br>Arup Bldg 7th Fl Conf Room<br>560 Mission Street, Suite 700<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/00009109-Rhino-Business-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.784380, -122.398549)     
areaIcon = "D2";
makeTab("<b>Riverbed Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Silverdome Conference Rm, 6th Fl<br>680 Folsom Street, 6th Floor San Francisco 94107<br><a href=http:#www.toastmasters.org/Find-a-Club/1576533-Riverbed-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.338241,-121.886182)     
areaIcon = "B5";
makeTab("<b>Rollertoasters Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, 1st and 3rd Wednesday<br>City of San Jose City Hall<br>200 E. Santa Clara St 11th Floor<br>San Jose 95113<br><a href=http:#www.toastmasters.org/Find-a-Club/00008499-Rollertoasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.64815,-122.41813)     
areaIcon = "H6";
makeTab("<b>Royalty Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30-9:00 pm, 2nd & 4th Tuesday<br>Royalty Auto Collision Center <br>476 Victory Avenu<br>South San Francisco 94080<br><a href=http:#www.toastmasters.org/Find-a-Club/1049172-Royalty-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.794473,-122.394864)     
areaIcon = "I3";
makeTab("<b>Salesforce Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>One Market Street Suite 300<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/1488281-Salesforce-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.65828,-121.657046)     
areaIcon = "A2";
makeTab("<b>Salinas Sunrisers Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:45 AM, Tues<br>St Ansgars / Meeting Rm<br>72 East San Joaquin St<br>Salinas 93901<br><a href=http:#www.toastmasters.org/Find-a-Club/00001829-Salinas-Sunrise-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.578380,-122.336441)     
areaIcon = "H3";
makeTab("<b>SAMCAR Speakers</b>","<font face=verdana size=2px>Closed Club,<br>Contact for Requirements<br>Meets 2:00 PM, 1st & 3rd Thursday<br>San Mateo County Association of Realtors<br>850 Woodside Way<br>San Mateo 94401<br><a href=http:#www.toastmasters.org/Find-a-Club/3524803-SAMCAR-Speakers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.516758,-122.279435)     
areaIcon = "H1";
makeTab("<b>San Carlos-Belmont Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 PM, 2nd & 4th Thursday<br>Twin Pines Senior & Community Center<br>1223 Ralston Ave<br>Belmont 94002<br><a href=http:#www.toastmasters.org/Find-a-Club/00000530-San-Carlos-Belmont-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.793192, -122.400164)     
areaIcon = "E2";
makeTab("<b>San Francisco Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:15 PM, Wednesday<br>315 California Street San Francisco 94104<br><a href=http:#www.toastmasters.org/Find-a-Club/00001771-San-Francisco-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.352234,-121.984363)     
areaIcon = "B6";
makeTab("<b>San Jose Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 AM, Tuesday<br>Carrows Restaurant<br>3180 El Camino Real<br>Santa Clara 95051<br><a href=http:#www.toastmasters.org/Find-a-Club/00001577-San-Jose-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.530186,-122.338608)     
areaIcon = "H3";
makeTab("<b>San Mateo Storytellers</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 - 9:00 pm, Tuesday<br>San Mateo Community College District Office<br>3401 CSM Drive, 2nd Floor<BR>San Mateo 94402<br><a href=http:#www.toastmasters.org/Find-a-Club/3461760-San-Mateo-Storytellers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.576064,-122.346544)     
areaIcon = "H4";
makeTab("<b>San Mateo Toastmasters 191</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 - 9:00 pm, Tuesday<br>Burlingame United Methodist Church<br>1443 Howard Ave<br>Burlingame 94010<br><a href=http:#www.toastmasters.org/Find-a-Club/00000191-San-Mateo-Toastmasters-Club-191 target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.243997,-121.889198)     
areaIcon = "A5";
makeTab("<b>San Pedro Squares Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 8:15 AM, Tues<br>Cup and Saucer Restaurant<br>1375 Blossom Hill Rd<br>San Jose 95118<br><a href=http:#www.toastmasters.org/Find-a-Club/00004860-San-Pedro-Squares-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.393388,-121.950395)     
areaIcon = "J3";
makeTab("<b>Santa Clara SweetTalkers Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Tuesday<br>Sun Microsystems<br>4170 Network Circle, Building 17<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/00004099-Santa-Clara-SweetTalkers-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.976196,-121.982026)     
areaIcon = "A4";
makeTab("<b>Santa Cruz Downtown Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:15 AM, Friday<br>Live Oak Senior Center <br>1777 Capitola Rd<br>Santa Cruz 95062<br><a href=http:#www.toastmasters.org/Find-a-Club/00001803-Santa-Cruz-Downtown-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.989600,-122.003386)     
areaIcon = "A3";
makeTab("<b>Santa Cruz Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Thursday<br>Quaker House<br>225 Rooney Street<br>Santa Cruz 95065<br><a href=http:#www.toastmasters.org/Find-a-Club/2498932-Santa-Cruz-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.281989,-122.001789)     
areaIcon = "B6";
makeTab("<b>Saratoga Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 8:00-10:00 am, Saturday<br>Prince of Peace Church, Rooms 5 & 6<br>12770 Saratoga Avenue (Corner of Cox Avenue)<br>Saratoga 95070<br><a href=http:#www.toastmasters.org/Find-a-Club/00003572-Saratoga-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.351844,-121.937238)     
areaIcon = "B3";
makeTab("<b>SCUMBAT Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:00 PM, Friday<br>Leavey School of Business Santa Clara University<br>500 El Camino Real, Kenna Hall Rm 216<br>Santa Clara 95053<br><a href=http:#www.toastmasters.org/Find-a-Club/00005474-SCUMBAT-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.320313,-122.032188)     
areaIcon = "B1";
makeTab("<b>Seagate Cupertino Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, 1st and 3rd Thursday<br>Seagate Technology<br>10200 S De Anza Blvd<br>Cupertino 95014<br><a href=http:#www.toastmasters.org/Find-a-Club/2672033-Seagate-Cupertino-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.395318,-122.053852)     
areaIcon = "G3";
makeTab("<b>Securely Speaking</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:05 PM, Tuesday<br>VeriSign<br>501 E. Middlefield Rd<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/1029428-Securely-Speaking target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.777843,-122.421657)     
areaIcon = "D4";
makeTab("<b>SFAR Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Mon<br>SF Association of Realtors<br>301 Grove St<br>San Francisco 94102<br><a href=http:#www.toastmasters.org/Find-a-Club/00006521-SFAR-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.795818,-122.401892)     
areaIcon = "E2";
makeTab("<b>San Francisco JETS (Japanese-English)</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM, 1st,2nd & 3rd Friday<br>Japan Society<br>500 Washington Street<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/00007025-sf-japaneseenglish-toastmasters-jets target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.797573, -122.400651)     
areaIcon = "E4";
makeTab("<b>Sierra Speakers Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:03 PM, Thursdays<br>McCann Erickson ~ Jack Morton Worldwide<br>600 Battery Street<br>3rd Floor Conference Room<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/00005610-Sierra-Speakers-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.405833, -121.980413)     
areaIcon = "J2";
makeTab("<b>Silicon Valley Entrepreneurs Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:15 PM, Thursday<br>2953 Bunker Hill Ln<br>Ste 400<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/1828921-Silicon-Valley-Entrepreneurs-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.274578,-121.879486)     
areaIcon = "A5";
makeTab("<b>Silicon Valley Storytellers</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 - 8:30 PM, 2nd & 4th Mondays<br>Denny's Diner<b>1140 Hillsdale Ave<br>Ste 400<br>San Jose 95118<br><a href=http:#www.toastmasters.org/Find-a-Club/3308016-Silicon-Valley-Storytellers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.374724,-122.029518)     
areaIcon = "G3";
makeTab("<b>Silicon Valley Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 5:00 PM, Wednesday<br>Sunnyvale Chamber of Commerce<br>260 South Sunnyvale Ave, Suite 4<br>Sunnyvale 94086<br><a href=http:#www.toastmasters.org/Find-a-Club/00004802-Silicon-Valley-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.791230,-122.392423)     
areaIcon = "I4";
makeTab("<b>Slalom Consulting</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 11:30 AM-12:30 PM,<br>1st & 3rd Wednesday<br>201 Spear St, 15th Floor<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/2738479-Slalom-Consulting target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.794107,-122.403846)     
areaIcon = "E4";
makeTab("<b>Soapmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 3:00 PM, 2nd & 4th Thursday<br>Method Office<br>637 Commercial St Ste 300<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/2210753-Soapmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.784063,-122.395764)     
areaIcon = "D6";
makeTab("<b>SoMa Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, 2nd & 4th Wednesday<br>600 Harrison St, 3rd Floor<br>Hawaii Room (alt Contra Costa Room)<br>San Francisco 94107<br><a href=http:#www.toastmasters.org/Find-a-Club/2512526-SoMa-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.794997, -122.399435)     
areaIcon = "E1";
makeTab("<b>Spanish Bilingual SF</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 PM 2nd and 4th Wednesday<br>Latino Community Foundation<br>1 Embarcadero Ctr Ste 1400<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/04634690-spanish-bilingual-sf target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.381435, -122.036909)     
areaIcon = "G4";
makeTab("<b>Sparksense@Sunnyvale Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Monday<br>Walmartlabs<br>860 W California Ave<br>Sunnyvale 94086<br><a href=http:#www.toastmasters.org/Find-a-Club/03970418-sparksensesunnyvale-toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.334841, -121.884920)     
areaIcon = "B5";
makeTab("<b>Spartans Toastmasters - SJSU</b>","<font face=verdana size=2px>Closed Club,<br>Contact for Requirements<br>Meets 6:00 PM, Alternate Friday<br>San Jose State University<br>One Washington Square<br>San Jose 95112<br><a href=http:#www.toastmasters.org/Find-a-Club/02113833-spartans-toastmasters-sjsu target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.048231, -122.018203)     
areaIcon = "A3";
makeTab("<b>Speeches With Friends</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Thursday<br>Seagate Technology<br>Hawaii Conference Room<br>4575 Scotts Valley Dr<br>Scotts Valley 95066<br><a href=http:#www.toastmasters.org/Find-a-Club/00002425-Speeches-With-Friends target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.28463, -121.93091)     
areaIcon = "B2";
makeTab("<b>Speak 4 Success</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 8:00 AM, Thursday<br>Keller Williams Realty<br>2110 S. Bascom Ave. Ste 101, <br>Campbell 95008<br><a href=http:#www.toastmasters.org/Find-a-Club/02430190-speak-4-success target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.583962,-121.827594)     
areaIcon = "A1";
makeTab("<b>Speakeasy Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>CTB/McGraw-Hill<br>20 Ryan Ranch Road<br>Monterey 93940<br>info@speakeasytm.org<br><a href=http:#www.toastmasters.org/Find-a-Club/00004547-Speakeasy-Club target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.790922,-122.400100)     
areaIcon = "I1";
makeTab("<b>Speakeasy</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Friday<br>Basement Conference Room<br>1 Bush St<br>San Francisco 94104<br><a href=http:#www.toastmasters.org/Find-a-Club/3373015-Speakeasy target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.392853, -121.950022)     
areaIcon = "J3";
makeTab("<b>SpeakEasy@Sun Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Friday<br>Oracle America Inc.<br>4200 Network Circle<br>Building SCA-20 / Louis Armstrong CR<br>Santa Clara 95054<br> <a href=http:#www.toastmasters.org/Find-a-Club/00002736-speakeasysun-club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.454,-122.1765)     
areaIcon = "C4";
makeTab("<b>SRI Organon Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 11:45 AM, Tuesday<br>SRI International, Building G<br>Laurel St. at Mielke Dr.<br>Menlo Park 94025<br><a href=http:#www.toastmasters.org/Find-a-Club/00001435-SRI-Organon-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.792942,-122.403483)     
areaIcon = "E1";
makeTab("<b>Stagecoach Speakers-SF Financial District</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:05 PM, Thursday<br>Odd months: 455 Market, 3rd Fl Barrel Conf Rm<br>Even months: 550 California, 2nd Fl Merengue Conf Rm<br><a href=http:#www.toastmasters.org/Find-a-Club/1095735-Stagecoach-Speakers-SF-Financial-District target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.790775,-122.399199)     
areaIcon = "I2";
makeTab("<b>Stagecoach Speakers - 525 Market</b></b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>525 Market Street<br>12th Floor<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/01070395-stagecoach-speakers-525-market target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.501504,-122.217613)     
areaIcon = "C4";
makeTab("<b>Stand & Deliver</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 7:00 AM, Wednesday<br>Abbott Vascular<br>400 Saginaw Drive<br>Redwood City 94063<br><a href=http:#www.toastmasters.org/Find-a-Club/01409881-stand-deliver target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.429223,-122.177340)     
areaIcon = "C1";
makeTab("<b>Stanford Toastmasters</b>","<font face=verdana size=2px>Closed Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>Redwood Hall G19<br>243 Panama St<br>Stanford 94305<br><a href=http:#www.toastmasters.org/Find-a-Club/3528251-Stanford-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.383538,-122.013305)     
areaIcon = "G3";
makeTab("<b>Startup Speakers</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 7:00 AM, Wednesday<br>Plug and Play Tech Center<br>440 North Wolfe Road<br>Sunnyvale 94085<br><a href=http:#www.toastmasters.org/Find-a-Club/1510119-Startup-Speakers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.655499,-121.662868)     
areaIcon = "A2";
makeTab("<b>Steinbeck Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:00 PM, Thursday<br>Villa Serra<br>1320 Padre Dr<br>Salinas 93906<br><a href=http:#www.toastmasters.org/Find-a-Club/00001939-Steinbeck-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.255047,-121.783522)     
areaIcon = "A6";
makeTab("<b>Stryker Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM 2nd & 4th Wednesday<br>Stryker Endoscopy<br>5900 Optical Ct<br>San Jose 95138<br><a href=http:#www.toastmasters.org/Find-a-Club/3890474-Stryker-Toastmasters target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.40296,-122.049849)     
areaIcon = "G6";
makeTab("<b>Study Group Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 3:30 PM 1st & 3rd Sunday<br>Hacker Dojo<br>599 Fairchild Dr<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/3559296-Study-Group-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.666292,-122.397541)     
areaIcon = "H6";
makeTab("<b>SuccessFactors</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Wednesday<br>SuccessFactors<br>1 Tower Pl Ste 1100<br>South San Francisco 94080<br><a href=http:#www.toastmasters.org/Find-a-Club/3428872-SuccessFactors target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.492674,-122.227793)     
areaIcon = "C5";
makeTab("<b>Sumo Logic Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Friday<br>Sumo Logic Boardroom<br>305 Main St<br>Redwood City 94063<br><a href=http:#www.toastmasters.org/Find-a-Club/04718669-sumo-logic-toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.533285,-122.271569)     
areaIcon = "H2";
makeTab("<b>SunEdison Belmont Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>SunEdison<br>Belmont Large Conf Rm<br>600 Clipper Dr<br>Belmont 94002<br><a href=http:#www.toastmasters.org/Find-a-Club/3968079-SunEdison-Belmont-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.37281,-122.03545)     
areaIcon = "G3";
makeTab("<b>Sunnyvale Speakeasies Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 11:45 AM, 2nd & 4th Friday<br>Bank Of America - Open to the General Public<br>440 S Mathilda Ave<br>Sunnyvale 94086<br><a href=http:#www.toastmasters.org/Find-a-Club/00007975-Sunnyvale-Speakeasies-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.405022,-121.946594)     
areaIcon = "F3";
makeTab("<b>Sunpower Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Sunpower Corporation<br>145 Rio Robles<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/1776130-Sunpower-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.478553,-122.17949)     
areaIcon = "C3";
makeTab("<b>Sunset Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 11:45 am<br>1st, 3rd & 5th Thursday<br>Allstate Research and Planning Center<br>4200 Bohannon Drive, Suite 200<br>Menlo Park 94025<br><a href=http:#www.toastmasters.org/Find-a-Club/00004304-Sunset-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.427765,-122.104186)     
areaIcon = "C1";
makeTab("<b>Superspace Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 11:30 AM, 1st & 3rd Wednesday<br>Space Systems Loral<br>3825 Fabian Way (Garden Room)<br>Palo Alto 94303<br><a href=http:#www.toastmasters.org/Find-a-Club/2784455-Superspace-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.397462,-122.053318)     
areaIcon = "G6";
makeTab("<b>SWAN Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Symantec Mountainview Campus<br>350 Ellis St<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/1152428-SWAN-Toastmasters-Club target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.323828,-122.013702)     
areaIcon = "B1";
makeTab("<b>SweetTalk</b>","<font face=verdana size=2px>Closed Club,<br>Contact for Requirements<br>Meets 12:00 PM, 2nd and 4th Thursday<br>Kaiser Permanente<br>10050 N Wolfe Rd<br>Cupertino 95014<br><a href=http:#www.toastmasters.org/Find-a-Club/04400250-sweettalk target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.272410,-121.935837)     
areaIcon = "B2";
makeTab("<b>Switch-On Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Monday<br>Denny's <br>2060 S Bascom Ave<br>Campbell 95008<br><a href=http:#www.toastmasters.org/Find-a-Club/00004224-Switch-On-Toastmasters-Club target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.39169,-121.89076)     
areaIcon = "B4";
makeTab("<b>SynapTalks</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>1251 McKay Drive<br>San Jose, CA, 95131<br><a href=http:#www.toastmasters.org/Find-a-Club/1684769-SynapTalks target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.375721,-121.998395)     
areaIcon = "J1";
makeTab("<b>Talking Chips Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Tuesday<br>National Semiconductor Building 9 Room 5<br>3693 Tahoe Way<br>Santa Clara 95051<br><a href=http:#www.toastmasters.org/Find-a-Club/00003088-Talking-Chips-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.398915,-122.069845)     
areaIcon = "G6";
makeTab("<b>Talking Heads Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Thursday<br>Oakwood Corporate Apartments<br>555 Middlefield Road (Enter Parking lot at Cypress Point Dr)<br>Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/00004648-Talking-Heads-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (36.3637985,-121.239624)     
areaIcon = "A2";
makeTab("<b>Talk the Line</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 4:30 PM, Thursday<br>Soledad 93960<br><a href=http:#www.toastmasters.org/Find-a-Club/1083068-Talk-the-Line target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.32399,-122.03296)     
areaIcon = "B1";
makeTab("<b>Tandem Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Trend Micro<br>10101 N. De Anza Blvd<br>Cupertino 95014<br><a href=http:#www.toastmasters.org/Find-a-Club/00004658-Tandem-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.78914,-122.39430)     
areaIcon = "I4";
makeTab("<b>Techmasters Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:10 PM, Tuesday<br>Charles Schwab & Co. Inc.<br>First Floor, #123 and 125<br>215 Fremont Street<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/00004920-Techmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.386763,-121.995201)     
areaIcon = "J1";
makeTab("<b>TGIF Management Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:15 AM (7:00 AM open), Friday<br>Coco's Bakery Restaurant<br>1206 Oakmead Pkwy<br>Sunnyvale 94085<br><a href=http:#www.toastmasters.org/Find-a-Club/00003328-TGIF-Management-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.661892,-122.392512)     
areaIcon = "H5";
makeTab("<b>Thermo Fisher Toastmasters Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:05 pm, 1st & 3rd Tuesday<br>Thermo Fisher<br>200 Oyster Point Blvd.<br>South San Francisco 94080,<br><a href=http:#www.toastmasters.org/Find-a-Club/759427-Thermo-Fisher-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.773004,-122.410950)     
areaIcon = "D6";
makeTab("<b>Thumbtack</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 6:00 PM Tuesday<br>360 9th St<br>San Francisco, CA 94103,<br><a href=http:#www.toastmasters.org/Find-a-Club/04789581-thumbtack target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.407609,-122.145280)     
areaIcon = "C2";
makeTab("<b>TIB Toasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Fridays<br>Building 1.<br>3303 Hillview Ave<br>Palo Alto 94304<br><a href=http:#www.toastmasters.org/Find-a-Club/2823223-TIB-Toasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.391232,-122.039309)     
areaIcon = "G2";
makeTab("<b>Toasters R Us</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Tuesday<br>Synopsys Inc. <br>455 N Mary Ave<br>Sunnyvale 94048<br><a href=http:#www.toastmasters.org/Find-a-Club/587637-Toasters-R-Us-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.788531,-122.399308)     
areaIcon = "I1";
makeTab("<b>Toastitects</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>HDR Inc.<br>560 Mission St., Ste 900<br>San Francisco 94105<br><a href=http:#www.toastmasters.org/Find-a-Club/1285335-Toastitects target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.295757,-121.928084)     
areaIcon = "B2";
makeTab("<b>ToastItNow!</b>","<font face=verdana size=2px>Closed Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>2145 Hamilton Ave<br>San Jose 95125<br><a href=http:#www.toastmasters.org/Find-a-Club/03081591-toastitnow target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.49892,-122.213425)     
areaIcon = "C4";
makeTab("<b>Toastmasters DX</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Friday<br>Genomic Health Inc<br>101 Galveston Dr<br>Redwood City 94063<br><a href=http:#www.toastmasters.org/Find-a-Club/1600439-Toastmasters-DX target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.388364,-121.962459)     
areaIcon = "J5";
makeTab("<b>Toastmasters Insiders Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:05 PM, Wednesday<br>Intel Corporation<br>2200 Mission College Boulevard<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/00004306-Toastmasters-Insiders-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.392189, -122.031753)     
areaIcon = "G2";
makeTab("<b>Toastmasters Lead [In] SV</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>LinkedIn Building, 3rd Fl<br>599 N Mathilda Ave<br>Sunnyvale 94085<br><a href=http:#www.toastmasters.org/Find-a-Club/04302421-toastmasters-lead-in-sv target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.411929,-122.009870)     
areaIcon = "J2";
makeTab("<b>ToastMeisters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Thursday<br>NetApp<br>1345 Crossman Ave<br>Sunnyvale 94087<br><a href=http:#www.toastmasters.org/Find-a-Club/00002994-ToastMeisters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.794952,-122.397308)     
areaIcon = "E2";
makeTab("<b>Toast of the Bay</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 8:00 AM, Friday<br>PriceWaterHouse Coopers<br>3 Embarcadero Center<br>San Francisco 94111<br><a href=http:#www.toastmasters.org/Find-a-Club/1561024-Toast-of-the-Bay target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.776688,-122.417686)     
areaIcon = "D2";
makeTab("<b>Toast of the City</b>","<font face=verdana size=2px>Closed Club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesday<br>San Francisco City Hall Rm 305<br>1 Dr Carton B Goodlett Pl<br>San Francisco 94102<br><a href=http:#www.toastmasters.org/Find-a-Club/2527750-Toast-of-the-City target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.767672,-122.415354)     
areaIcon = "D3";
makeTab("<b>Toast of the Mission</b>","<font face=verdana size=2px>Membership eligibility criteria,<br>Contact club,<br>Contact for Requirements<br>Meets 12:00 PM, Tuesdays<br>Mission Center Building 126<br>1855 Folsom St Ste 126<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/1849809-Toast-of-the-Mission target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.417374,-121.947359)     
areaIcon = "F4";
makeTab("<b>Toast to ARM</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>ARM Inc.<br>150 Rose Orchard Way<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/3274069-Toast-to-ARM target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.413632,-121.933555)     
areaIcon = "F3";
makeTab("<b>Toast Twisters Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Wednesdays<br>Cisco Systems / Bldg 4<br>275 East Tasman Dr<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/00003598-Toast-Twisters-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.37728,-122.02600)     
areaIcon = "G3";
makeTab("<b>Top Gun Club</b>","<font face=verdana size=2px>Closed Company Club, Northrop Grumman Employees Only<br>Meets 11:45 AM, Thursday<br>Northrop Grumman Corp 21-4 Conference Room<br>401 East Hendy Avenue<br>Sunnyvale 94088<br><a href=http:#www.toastmasters.org/Find-a-Club/00004004-Top-Gun-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.381847, -121.959869)     
areaIcon = "J3";
makeTab("<b>Torchard Toastmasters Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>Teradata<br>2055 Laurelwood Rd<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/00004460-Torchard-Toastmasters target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.771658,-122.405036)     
areaIcon = "D1";
makeTab("<b>TravelMasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 5:00 pm, Tuesday<br>Concur + AIRBNB Office<br>880 Brannan St<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/3992915-TravelMasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.258933,-121.855066)     
areaIcon = "A5";
makeTab("<b>True Talking Toastmasters (TTT) Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:00 PM, Wednesday<br>Gunderson High School Room D1<br>622 Gaundabert Ln<br>San Jose 95136<br><a href=http:#www.toastmasters.org/Find-a-Club/00668615-true-talking-toastmasters-ttt target=new>club contact information</a>")     

 

 #**** single club marker  ***
latlong = (37.481725,-122.162832)     
areaIcon = "C3";
makeTab("<b>T*Toasters Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Thursday<br>TE Connectivity<br>306 Constitution Dr.<br>Room 2325<br>Menlo Park CA 94025<br><a href=http:#www.toastmasters.org/Find-a-Club/00004657-ttoasters-club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.793379,-122.400899)     
areaIcon = "E1";
makeTab("<b>UBSF Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Wednesday<br>350 California, 9th Floor<br>San Francisco 94104<br><a href=http:#www.toastmasters.org/Find-a-Club/3984272-UBSF-Toastmasters target=new>club contact information</a>")     


  #**** single club marker  ***
latlong = (37.792119,-122.402695)     
areaIcon = "E1";
makeTab("<b>United We Speak Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM Friday<br>315 Montgomery, 4th floor<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/00006535-United-We-Speak-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.420428,-121.921455)     
areaIcon = "F3";
makeTab("<b>Vakpatugalu</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 11:00 am, 1st & 3rd Sunday<br>Cisco Bldg #24<br>510 McCarthy Blvd<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/1259423-Vakpatugalu target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.294537,-121.917492)     
areaIcon = "B2";
makeTab("<b>Valley Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 AM, Thursday<br>Zell Associates, Inc.<br>1777 Hamilton Avenue, Suite 102A<br>San Jose 95125<br><a href=http:#www.toastmasters.org/Find-a-Club/00003626-Valley-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.417963,-121.920871)     
areaIcon = "F1";
makeTab("<b>Vanguard Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:10 pm arrive by noon, Thursday<br>Sandisk Corporation<br>601 McCarthy Blvd<br>Milpitas 95035<br><a href=http:#www.toastmasters.org/Find-a-Club/2693-Vanguard-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.40356,-122.14198)     
areaIcon = "C2";
makeTab("<b>VAPA Jabbers</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Monday<br>Palo Alto VA Hospital Bldg 4<br>2nd Flr, Room C-260<br>3801 Miranda Ave<br>Palo Alto 94304<br><a href=http:#www.toastmasters.org/Find-a-Club/1588569-VAPA-Jabbers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.398114,-122.031252)     
areaIcon = "G2";
makeTab("<b>Ventritalks</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 pm, Thursday<br>St. Jude Medical CRMD<br>645 Almanor Ave<br>Sunnyvale 94085<br><a href=http:#www.toastmasters.org/Find-a-Club/1114237-Ventritalks target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.346497,-121.868233)     
areaIcon = "B5";
makeTab("<b>Viet My</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 3:00pm Saturday<br>East San Jose Carnegie Library<br>1102 E Santa Clara St<br>San Jose 95116<br><a href=http:#www.toastmasters.org/Find-a-Club/3844625-Viet-My target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.558619,-122.277751)     
areaIcon = "H1";
makeTab("<b>Visa Speakers' Circle Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Visa Corporation<br>900 Metro Center Blvd<br>Foster City 94404<br><a href=http:#www.toastmasters.org/Find-a-Club/00007190-visa-speakers-circle-toastmasters-club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.421878,-121.961508)     
areaIcon = "F5";
makeTab("<b>Vox Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 12:00 PM, Wednesday<br>IBM North San Jose<br>4400 N. 1st Street (at Cursor Court)<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/00000225-Vox-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.627286,-122.424846)     
areaIcon = "H5";
makeTab("<b>Ecommunicators</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM Thursday<br>Walmart.com<br>850 Cherry Ave<br>San Bruno 94066<br><a href=http:#www.toastmasters.org/Find-a-Club/1198003-Ecommunicators target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.439682,-122.162649)     
areaIcon = "C4";
makeTab("<b>Wellness Toastmasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:30 pm, 1st & 3rd Monday<br>Palo Alto Medical Foundation<br>Room AF 3rd Fl Main Bldg<br>795 El Camino Real<br>Palo Alto 94301<br><a href=http:#www.toastmasters.org/Find-a-Club/2590625-Wellness-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.396093,-122.053157)     
areaIcon = "G6";
makeTab("<b>Wharton QuakeMasters</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 6:45 pm, Monday<br>Symantec<br>500 E. Middlefield Rd<br> Mountain View 94043<br><a href=http:#www.toastmasters.org/Find-a-Club/1463124-Wharton-QuakeMasters target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.293361,-121.965145)     
areaIcon = "B6";
makeTab("<b>Willow Glen Icebreaker Club</b>","<font face=verdana size=2px>Open to all interested parties<br>Meets 7:30 AM, Wednesdays<br>Sarahcare<br>450 Marathon Drive<br>Campbell 95008<br><a href=http:#www.toastmasters.org/Find-a-Club/00007281-Willow-Glen-Icebreaker-Club target=new>club contact information</a>")     



 #**** single club marker  ***
latlong = (37.4071,-121.927994)     
areaIcon = "F5";
makeTab("<b>Word Wizards Club</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Cisco Systems, Bldg 17, Galapagos Conference Room,<br>3650 Cisco Way<br>San Jose 95134<br><a href=http:#www.toastmasters.org/Find-a-Club/00001313-Word-Wizards-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.410430,-122.036504)     
areaIcon = "G4";
makeTab("<b>Wry Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Hewlett Packard  - Moffett Towers<br>Building F, 6th Fl, Fornax Meeting Rm<br>1140 Enterprise Way<br>Sunnyvale 94089<br><a href=http:#www.toastmasters.org/Find-a-Club/00004270-Wry-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.403017,-121.977972)     
areaIcon = "J3";
makeTab("<b>XenSpeakers</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Citrix Systems Santa Cruz Conference Room<br>4988 Great America Pkwy<br>Santa Clara 95054<br><a href=http:#www.toastmasters.org/Find-a-Club/1502076-XenSpeakers target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.253364,-121.933178)     
areaIcon = "A5";
makeTab("<b>Xilinx Xpressionists Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Xilinx Inc<br>2100 Logic Dr<br>San Jose 95124<br><a href=http:#www.toastmasters.org/Find-a-Club/00009473-Xilinx-Xpressionists-Toastmasters-Club target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.332741, -121.892001)     
areaIcon = "B3";
makeTab("<b>Year Up Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Wednesday<br>Year Up Bay Area - Silicon Valley <br>100 W San Fernando St<br>Ste 103<br>San Jose 95113<br><a href=http:#www.toastmasters.org/Find-a-Club/4048104-Year-Up-Toastmasters target=new>club contact information</a>")     


 #**** single club marker  ***
latlong = (37.781836,-122.410798)     
areaIcon = "D6";
makeTab("<b>Zendesk Toastmasters</b>","<font face=verdana size=2px>Closed Company Club,<br>Contact for Requirements<br>Meets 12:00 PM, Thursday<br>Zendesk <br>1019 Market St<br>San Francisco 94103<br><a href=http:#www.toastmasters.org/Find-a-Club/4096278-Zendesk-Toastmasters target=new>club contact information</a>")     

conn.commit()
curs.close()
conn.close()
