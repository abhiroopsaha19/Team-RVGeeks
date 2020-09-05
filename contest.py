import traceback
import bs4 as bs
import requests
import datetime 
import pytz
from pytz import timezone
from dateutil import tz
import json
import logging
import json
logger=logging.getLogger() 

logger.setLevel(logging.DEBUG) 

def make_request(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"
    }
    return requests.get(url,headers=headers)

def codeforces_contest():
    url = 'https://codeforces.com/api/contest.list'
    r = make_request(url)
    contest_list = []
    # print(r)
    if r.status_code != 200:
        return []

    data = json.loads(r.text)
    contests =  data['result']
    live_contests = [n for n in contests if n["phase"]=="BEFORE" or n["phase"]=="CODING"]
    # print(live_contests)

    # to_zone = tz.gettz('Asia/Kolkata')
    tz = pytz.timezone('Asia/Kolkata')

    for contest in live_contests:
        ct = {}
        
        dt= datetime.datetime.utcfromtimestamp(contest['startTimeSeconds'])
        
        dt = pytz.UTC.localize(dt)
        ist = pytz.timezone('Asia/Kolkata')
        dt = dt.astimezone(ist)
        enddt= dt + datetime.timedelta(seconds=contest['durationSeconds'])
        
        date = dt.strftime('%d-%m-%y')
        time = dt.strftime('%H:%M')

        ct['date'] = str(date)
        ct['time'] = str(time)

        ct['enddate'] = enddt.strftime('%d-%m-%y')
        ct['endtime'] = enddt.strftime('%H:%M')


        ct['name'] = contest['name']
        ct['id'] = contest['id']
        ct['url'] = 'https://codeforces.com/contests'
        ct['platform'] = "CODEFORCES"
        ct['timestamp'] = dt.timestamp()
        ct['endtimestamp'] = enddt.timestamp()

        logger.info("{} @ {} {}".format(ct['name'], ct['date'], ct['time']  ))

        contest_list.append(ct)
    print(len(contest_list) , "data collected")
    return contest_list
  
def atcoder_contest():
    
    url = 'https://atcoder.jp/'
    r = make_request(url)

    source2 = r.text
    soup = bs.BeautifulSoup(source2,'lxml')

    table = soup.table
    table = soup.findAll('tbody')
    table = table[1]
    table_rows = table.findAll('tr')

    contest_list = []
    for tr in table_rows:
        ct = {}
        td = tr.findAll('td')
        
        row = [i.text for i in td]
        # print(  td[1].find('a').get('href'))
        
        link = tr.findAll('a')[0]['href']
        a =link.split("iso=")[1]
        a = a.split("&")[0] + '+0900'
        tm = datetime.datetime.strptime(a,'%Y%m%dT%H%M%z')
        
        ist = pytz.timezone('Asia/Kolkata')
        tm =tm.astimezone(ist)

        
        date = tm.strftime('%d-%m-%y')
        time = tm.strftime('%H:%M')

        ct['date'] = str(date)
        ct['time'] = str(time)

        td[1].find('a').get('href')
        ct['url'] = 'https://www.atcoder.jp' +  td[1].find('a').get('href')

        # print(ct['url'])

        ct['name'] = row[1]
        ct['platform'] = "ATCODER"
        ct['timestamp'] = tm.timestamp()

        logger.info("{} @ {} {}".format(ct['name'], ct['date'], ct['time']  ))

        
        contest_list.append(ct)
    print(len(contest_list) , "data collected")
    return contest_list

def codechef_contest():
    url = 'https://www.codechef.com/contests'
    r = make_request(url)

    source2 = r.text
    soup = bs.BeautifulSoup(source2,'lxml')

    table = soup.table
    table = soup.findAll('tbody')
    table = table[1]
    table_rows = table.findAll('tr')

    contest_list = []
    for tr in table_rows:
        ct = {}
        td = tr.findAll('td')

        row = [i.text for i in td]
        # print("++++++++++++++++++")
        # print('https://www.codechef.com' + td[1].find('a').get('href').split('?')[0])
        # print("++++++++++++++++++")

        # print(row[2]) 27 Jun 2020  19:30:00
        tm = datetime.datetime.strptime(row[2],'%d %b %Y  %H:%M:%S')
        date = tm.strftime('%d-%m-%y')
        time = tm.strftime('%H:%M')

        endtm = datetime.datetime.strptime(row[3],'%d %b %Y  %H:%M:%S')
        enddate = endtm.strftime('%d-%m-%y')
        endtime = endtm.strftime('%H:%M')

        ct['date'] = str(date)
        ct['time'] = str(time)

        ct['enddate'] = str(enddate)
        ct['endtime'] = str(endtime)

        
        ct['url'] = 'https://www.codechef.com' + td[1].find('a').get('href').split('?')[0] 

        ct['name'] = row[1].strip()
        ct['platform'] = "CODECHEF"
        ct['timestamp'] = tm.timestamp()
        ct['endtimestamp'] = endtm.timestamp()

        logger.info("{} @ {} {}".format(ct['name'], ct['date'], ct['time']  ))
        
        
        contest_list.append(ct)
    print(len(contest_list) , "data collected")
    return contest_list

def hackerearth():

    url = 'https://www.hackerearth.com/challenges'
    r = make_request(url)
    source = r.text
    soup = bs.BeautifulSoup(source,'html.parser')
    upcoming = soup.find('div',{'class':'upcoming challenge-list'})
    events = upcoming.findAll('div',{'class':'challenge-card-modern'})

    contest_list = []
    for event in events:
        raw_date = event.find('div',{'class':'date'}).text.strip()
        name = event.find('span',{'class':'challenge-list-title'}).text.strip()
        types = event.find('div',{'class':'challenge-type'}).text.strip()
         
        print(raw_date)
        tm = datetime.datetime.strptime(raw_date,'%b %d, %I:%M %p %Z')
        tm = tm.replace(year = datetime.datetime.now().year)
        ist = pytz.timezone('Asia/Kolkata')
        tm = tm.astimezone(ist)
        
        date = tm.strftime('%d-%m-%y')
        time = tm.strftime('%H:%M')
        ct = {}
        ct['date'] = str(date)
        ct['time'] = str(time)

        ct['name'] = name
        ct['platform'] = "HACKEREARTH"
        ct['type'] = types
        ct['timestamp'] = tm.timestamp()
        
        contest_list.append(ct)

    return contest_list



def get_contest():
    contests = []
    try:

        # print("codechef")
        logger.info("fetching codechef contest ")
        contests +=  codechef_contest()
    except Exception as e:
        # contests['codechef'] += []
        print(e)
        logger.error(e, exc_info=True)

    try:
        logger.info("fetching codeforces contest ")
        

        contests +=  codeforces_contest()
    except Exception as e:
        print(e)
        logger.error(e, exc_info=True)
        

    try:
        
        logger.info("fetching atcoder contest ")
        
        contests +=  atcoder_contest()
    except Exception as e:
        print(e)
        logger.error(e, exc_info=True)

    try:
        
        logger.info("fetching hackerearth contest ")
        
        contests +=  hackerearth()
    except Exception as e:
        print(e)
        logger.error(e, exc_info=True)



    def sort_param(x):    
        return x['timestamp']
    contests.sort(key=sort_param )

    logger.info("{} contest details found".format(len(contests)))

    data = {}
    data['updated'] = datetime.datetime.now().strftime('%d-%m-%Y')
    data['time'] = datetime.datetime.now().strftime('%H:%M %Z')
    data['contests'] = contests

    with open("data.json", "w") as outfile: 
        json_object = json.dumps(data, indent=4)
        outfile.write(json_object) 

    return contests

# print(json.dumps(get_contest(), indent=4))