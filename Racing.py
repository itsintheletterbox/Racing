#Imports

import time
import datetime
import urllib2
from lxml import etree
from multiprocessing import Pool

## Parameters
valid_meets = {"AR"} #, "BR", "MR", "SR", "PR", "NR", "QR", "VR"}

## Date
curDate = datetime.datetime.today()
year = curDate.year
month = curDate.month
day = curDate.day

## Daylight savings time adjustment
dstAdj = time.localtime().tm_isdst

# Collection times (minutes before/after the race)
collectTimes = [-30,-25,-20,-15,-10,-5,-4,-3,-2,-1,1,3,5,10]
collectTimes = [-5,-4,-3,-2,-1,1,3,5]


#Function to load xml feed into etree object
def load_tree(url):
    
    #Open url
    xml_data = urllib2.urlopen(url)

    #Parse xml
    tree = etree.parse(xml_data)

    #Close url
    xml_data.close()
    
    del xml_data
    
    return tree
    
### Function to check a field exists, then assign the value
def get_val(var, attr):
    if attr in var.keys():
        return var[attr]
    else:
        return None


### Function to get race data
def get_race_data(race_tree):
    #Track details
    meetingInfo = race_tree.findall("//Meeting")[0].attrib
    venueName = meetingInfo["VenueName"]
    trackDesc = get_val(meetingInfo,"TrackDesc")
    trackCond = get_val(meetingInfo,"TrackCond")
    trackRating = get_val(meetingInfo,"TrackRating")
    
    ## Race details
    raceInfo = race_tree.findall("//Race")[0].attrib
    raceDate = raceInfo["RaceTime"].split("T")[0]
    raceTime = raceInfo["RaceTime"].split("T")[1]
    raceName = raceInfo["RaceName"]
    raceDist = raceInfo["Distance"]
    raceFav = get_val(raceInfo,"SubFav")
    
    ## Tipsters
    tipsterList = race_tree.findall("//Tipster")
    tipsterTipList = race_tree.findall("//TipsterTip")
    tipsters = [tipster.attrib["TipsterName"] for tipster in tipsterList]
    tips = ["x-"+tip.attrib["Tips"].replace("*","") for tip in tipsterTipList]
    
    ## Results
    resultList = race_tree.findall("//Result")
    poolList = race_tree.findall("//PoolResult")
    winPlace = [get_val(result.attrib,"RunnerNo") for result in resultList]
    poolDivCode  = [get_val(pool.attrib,"PoolType") for pool in poolList]
    poolDividend = [get_val(pool.attrib,"Dividend") for pool in poolList]
    
    ## Exotics
    exoticsList = race_tree.findall("//Pool")
    dividendList = race_tree.findall("//Dividend")
    exoticType = [get_val(exotic.attrib, "PoolType") for exotic in exoticsList]
    exoticPool = [get_val(exotic.attrib, "PoolTotal") for exotic in exoticsList]
    divAmt  = [get_val(div.attrib, "DivAmount") for div in dividendList]
    divID   = [get_val(div.attrib, "DivId") for div in dividendList]
    
    return {"Date":raceDate, "Meet":meet, "VenueName":venueName, "TrackDesc":trackDesc, \
            "TrackCond":trackCond, "TraclRating": trackRating, "RaceNo":raceNo,\
            "Time":raceTime, "RaceName":raceName, "RaceDist":raceDist, \
            "RaceFav":raceFav, "Tipsters":tipsters, "Tips":tips, \
            "WinPlace":winPlace, "PoolDivCode":poolDivCode, "PoolDividend":poolDividend, \
            "ExoticType":exoticType, "ExoticPool":exoticPool, "DivAmt":divAmt, "DivID":divID}


        
### Function to get field data
def get_field_data(race_tree):
    #Get data
    runnerList = race_tree.findall("//Runner")
    winOddsList = race_tree.findall("//WinOdds")
    placeOddsList = race_tree.findall("//PlaceOdds")
    fixedOddsList = race_tree.findall("//FixedOdds")
    
    #Get details for each runner for each race 
    fieldDict = {}
    for i in range(0,len(runnerList)):
        #Grab details for the race
        runnerInfo = runnerList[i].attrib
        winOddsInfo = winOddsList[i].attrib
        placeOddsInfo = placeOddsList[i].attrib
        fixedOddsInfo = fixedOddsList[i].attrib
        
        #Get horse details
        runnerNo = get_val(runnerInfo,"RunnerNo")
        runnerName = get_val(runnerInfo,"RunnerName")
        runnerWeight = get_val(runnerInfo,"Weight")
        runnerJockey = get_val(runnerInfo,"Rider")
        runnerForm = get_val(runnerInfo, "LastResult")
        runnerChanged = get_val(runnerInfo,"RiderChanged")
        runnerBarrier = get_val(runnerInfo,"Barrier")
        runnerScratched = get_val(runnerInfo,"Scratched")
        runnerRtng = get_val(runnerInfo,"Rtng")
        runnerHandicap = get_val(runnerInfo,"Handicap")
        
        #Odds
        oddsWin = get_val(winOddsInfo,"Odds")
        oddsWinLost = get_val(winOddsInfo,"Lastodds")
        
        oddsPlace = get_val(placeOddsInfo,"Odds")
        oddsPlaceLast = get_val(placeOddsInfo,"Lastodds")
        
        fixWin = get_val(fixedOddsInfo, "Odds")
        retailWin = get_val(fixedOddsInfo,"RetailWinOdds")
        fixPlace = get_val(fixedOddsInfo,"PlaceOdds")
        retailPlace = get_val(fixedOddsInfo,"RetailPlaceOdds")
        
        #Timestamp
        calcTime = get_val(winOddsInfo,"CalcTime")
        lastCalcTime = get_val(winOddsInfo,"LastCalcTime")
        
        if calcTime is not None:
            calcTime =  calcTime.split("T")[1]
        
        if lastCalcTime is not None:
           lastCalcTime = lastCalcTime.split("T")[1]
        
        #Compile all details into dict    
        fieldDict[runnerNo] =  {"Name":runnerName, "Weight":runnerWeight, "Jockey":runnerJockey,\
                                "Form":runnerForm, "Changed":runnerChanged, "Barrier":runnerBarrier, \
                                "Scratched":runnerScratched, "Rating":runnerRtng, "Handicap":runnerHandicap, \
                                "OddsWin":oddsWin, "OddsWinLost":oddsWinLost, "OddsPlace":oddsPlace,\
                                "OddsPlaceLast":oddsPlaceLast, "FixWin":fixWin, "RetailWin":retailWin, \
                                "FixPlace":fixPlace, "RetailPlace":retailPlace, \
                                "CalcTime":calcTime, "LastCalcTime":lastCalcTime}
        
    #Return dict holding details for all runners in the race                         
    return fieldDict



def raceLoop(meet, collectTimes):
    nraces = int(race_meets[meet])
    
    for race in range(1,nraces):
    
        raceKey = meet+str(race)

        raceTimeStr = raceDict[raceKey]['Time'].split(":")
        raceTime = datetime.datetime(year,month,day,int(raceTimeStr[0]),int(raceTimeStr[1]), int(raceTimeStr[2]))

        if (raceTime + datetime.timedelta(hours = dstAdj, minutes = min(collectTimes))) < datetime.datetime.now():
            None ## If missed the first collection time skip the race
        else:
            for wait in collectTimes:
                
                curTime = datetime.datetime.now()
                colTime = raceTime + datetime.timedelta(hours = dstAdj, minutes = wait)
                waitTime = (colTime-curTime).total_seconds()
                
                print "Waiting for %s%s at %s in %i minutes" %(meet,race,raceTime,waitTime/60)
                time.sleep(waitTime)
                fieldDict[raceKey,wait] = get_field_data(race_tree)
    
    return fieldDict        


def main():
    
    for k in range(nMeets):
        meet = race_meets.keys()[k]
        print "*** Meet = " + meet + " ***" 
        raceLoop(meet, collectTimes)
    
    
    #Create multiprocessing pool - one stream for each race meet
    pool = Pool(processes = nMeets)
    
    for k in range(nMeets):
        meet = race_meets.keys()[k]
        print "*** Meet = " + meet + " ***" 
        try:
            pools[meet] = pool.apply_async(raceLoop, [meet, collectTimes])
        except:
            pool.close()
            
    pool.close()
    pool.join()
    
    for k in range(nMeets):
        meet = race_meets.keys()[k]
        results[meet] = pools[meet].get()




########################################
## First get the race meets for the day
########################################

url = "https://tatts.com/pagedata/racing/%s/%s/%s/RaceDay.xml" %(year,month,day)

tree = load_tree(url)

## Build dict mapping race meets to number of races in each
race_meets = {}
for meet in tree.iterfind("Meeting"):
    code = meet.attrib["MeetingCode"]
    if code in valid_meets and meet.attrib["Abandoned"] == "N":
        race_meets[code] = meet.attrib["HiRaceNo"]

nMeets = len(race_meets.keys())


######################################
## Next loop through each of the races
######################################

# Column lookup key for raceDict and fieldDict

# raceCols: "Date", "Code", "Venue", "TrackDescription", "TrackCondition", \
#              "TrackRating", "RaceNo", "Time", "RaceName", "Distance",       \
#              "Favourite", "Tipster", "Tip", "WinPlace", "DivCode",          \
#              "Dividend", "Exotic", "Pool", "ExoticDividend", "DividendId"
#

# fieldCols: "Number", "Name", "Weight", "Jockey", "Form", "RiderChange",    \
#             "Barrier", "Scratched", "Rating", "Handicap", "WinLast", "Win", \
#             "PlaceLast", "Place", "FixWin", "RetailWin", "FixPlace",        \
#             "RetailPlace", "LastTime", "Time"

'''

raceDict = {}
for meet in race_meets.keys():
    last_race = int(race_meets[meet])
    for raceNo in range(1,last_race+1):
        race_url = "http://tatts.com/pagedata/racing/%s/%s/%s/%s%s.xml" %(year, month, day, meet, raceNo)
        print race_url
        race_xml = urllib2.urlopen(race_url)
        race_tree = etree.parse(race_xml)
        race_xml.close()
        
        # Race data
        raceDict[meet+str(raceNo)] = get_race_data(race_tree)


print "Races:"
print sorted(raceDict.keys())

'''


## Loop over race meets
fieldDict = {}
pools = {}   
results = {}

#raceLoop('AR',[-60]) 
 

if __name__ == '__main__':
        main()
        #sys.exit()



