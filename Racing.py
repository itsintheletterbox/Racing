#Imports

import urllib2
from lxml import etree

## Parameters
valid_meets = {"AR", "BR", "MR", "SR", "PR", "NR", "QR", "VR"}
year = 2014
month = 9
day = 21

url = "https://tatts.com/pagedata/racing/%s/%s/%s/RaceDay.xml" %(year,month,day)

#Open url
xml_data = urllib2.urlopen(url)

#Parse xml
tree = etree.parse(xml_data)

#Close url
xml_data.close()


########################################
## First get the race meets for the day
########################################

## Build dict mapping race meets to number of races in each
race_meets = {}
for meet in tree.iterfind("Meeting"):
    code = meet.attrib["MeetingCode"]
    if code in valid_meets:
        race_meets[code] = [meet.attrib["Abandoned"], meet.attrib["HiRaceNo"]]


###############################
## Next the times for each race
###############################

race_times = {}
for meet in race_meets.keys():
    last_race = int(race_meets[meet][1])
    for raceNo in range(1,last_race+1):
        race_url = "http://tatts.com/pagedata/racing/%s/%s/%s/%s%s.xml" %(year, month, day, meet, raceNo)
        print race_url
        race_xml = urllib2.urlopen(race_url)
        race_tree = etree.parse(race_xml)
        race_xml.close()
        time = race_tree.xpath("//Race")[0].attrib["RaceTime"].split("T")[1]
        race_times[meet+str(raceNo)] = time

print "Race times:" 
print race_times


###############################
## Next get field data
###############################







