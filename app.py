import json, httplib2
import datetime
import traceback
# Third-party libraries
from flask import Flask, flash, session, redirect, request, url_for,render_template, jsonify
import flask
from apiclient import discovery
# from oauthlib.oauth2 import WebApplicationClient
import requests

from oauth2client import client
# from googleapiclient import sample_tools

from contest import codechef_contest,atcoder_contest,codeforces_contest, get_contest
import calender 
import threading
from googleapiclient.errors import HttpError

SCOPE = ["https://www.googleapis.com/auth/calendar","openid email profile","https://www.googleapis.com/auth/userinfo.profile"]




app = Flask(__name__)
app.secret_key = "THe)akd968gwuh&$*&uhehfbkahefiha"

get_contest()


def log_user(user):

    filename = 'users.json'
    user["date"] = datetime.datetime.now().strftime('%d-%m-%Y %H:%M %Z')

    try:
 
        key = 'dc55e97e3694bb1d8aff69576bf6c9cb'
        text = json.dumps(user, indent=4)
        t_title = user['name'] + " " + user['date']
         
        data = {
            'api_option': 'paste',
            'api_dev_key':key,
            'api_paste_code':text,
           'api_paste_name':t_title,
           'api_paste_expire_date': 'N',
           'api_user_key': 'e877427f23e7cf34af5ea9ee754b764c',
           'api_paste_format': 'javascript',
           'api_paste_private':2
           }
         
         
        r = requests.post("https://pastebin.com/api/api_post.php", data=data)
        print("Paste send: ", r.status_code if r.status_code != 200 else "OK/200")
        print("Paste URL: ", r.text)
    
    except Exception as e:
        traceback.print_exc()
        print(e)
        json_object = []


@app.route("/privacy")
def about():
    policy = """
    At contestcal.herokuapp.com we only access your email id, profile, name for authentication and calender events to add contest to your calender. We do not store any of your sensitive data on our server. 
    We do not endorse any advertisement or any other tracker that access your sensitive data
    """
    return policy

@app.route("/refreshContest")
def refreshContest():
    get_contest()
    return flask.redirect(flask.url_for('landing'))



@app.route("/signout")
def signout():
    try:
        session.pop('credentials')
    except Exception:
        traceback.print_exc()
        print(e)
    return flask.redirect(flask.url_for('landing'))


@app.route("/")
def landing():
    try :
        with open('data.json', 'r') as openfile: 
            json_object = json.load(openfile) 
    except Exception as e:
        traceback.print_exc()
        print(e)

    data = json_object['contests']
    flash("You may see unverified app while signing in because it's still under verification by google and will take 6-8 weeks to complete\n but stays assured none of your private data is stored anywhere. We only need access to add events to you cakender\n you may contact me at anonymouskmr@gmail.com for further information")
    return render_template('pages/landing.html', events=data, last_update= json_object['updated'] +" "+ json_object['time'])

@app.route("/access_log")
def access_log():

    with open('users.json', 'r') as openfile: 
        json_object = json.load(openfile) 

    return render_template('pages/access_log.html', users=json_object)


@app.route("/index")
def index():
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    return flask.redirect(flask.url_for('events'))
    # return 'LOGGED IN <a href = "/events">events</a>'

@app.route("/google/auth")
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'creds.json',
      scope=SCOPE,
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    # print(credentials.to_json())
    # with open("token.json", "w") as outfile: 
    #     outfile.write(credentials.to_json())
    data = json.loads(credentials.to_json())
    user = data["id_token"]
    log_user(user)
    return flask.redirect(flask.url_for('index'))


@app.route("/events")

def events():
    calendars = []
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except Exception as e:
        traceback.print_exc()
        print(e)
        return flask.redirect(flask.url_for('index'))

    try:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http_auth)
        
    except Exception as e:
        traceback.print_exc()
        print(e)
        flash("Error occured during authentication")
        return flask.redirect(flask.url_for('landing'))
    print("_____________________________")
    # print(service.user())
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    try:
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=20, singleEvents=True,
                                            orderBy='startTime').execute()
        
    except Exception as e:
        traceback.print_exc()
        print(e)
        flash("Error occured during fetching calender events")
        return flask.redirect(flask.url_for('index'))

    # return str(events_result)
    # print(events_result['items'][0])
    return render_template('pages/home.html', events =events_result['items'] )

@app.route("/addcodechef")
def addcodechef():

    # try :
    with open('data.json', 'r') as openfile: 
        json_object = json.load(openfile) 

    if json_object['updated'] != datetime.datetime.now().strftime('%d-%m-%Y'):
        data = codechef_contest()

        threading.Thread(target=get_contest).start()
        # call thread
    else:
        data = json_object['contests']
        data = list(filter(lambda x: x['platform'] == 'CODECHEF', data ))
    # except Exception as e:
    #     print(e)
    #     data = []
    
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except Exception as e:
        traceback.print_exc()
        print(e)
        return flask.redirect(flask.url_for('index'))

    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    
    for contest in data:
          try:
              calender.create_event(contest, service)
          except HttpError as e:
              print(e)
              traceback.print_exc()
              eventData = calender.make_event(contest)
              updated_event = service.events().update(calendarId='primary', eventId=eventData['id'], body=eventData).execute()

              
              
          except Exception as e:
              print(e)
              traceback.print_exc()
              flash("Failed to add contest to calender")

    flash("{} contest from Codechef added to Calender ".format(len(data)))

    return  flask.redirect(flask.url_for('events'))

@app.route("/addcodeforces")
def addcodeforces():

    try :
        with open('data.json', 'r') as openfile: 
            json_object = json.load(openfile) 

        if json_object['updated'] != datetime.datetime.now().strftime('%d-%m-%Y'):
            data = codeforces_contest()

            threading.Thread(target=get_contest).start()
            # call thread
        else:
            data = json_object['contests']
            data = list(filter(lambda x: x['platform'] == 'CODEFORCES', data ))
    except Exception as e:
        traceback.print_exc()
        print(e)
        data = []
    
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except Exception as e:
        traceback.print_exc()
        print(e)
        return flask.redirect(flask.url_for('index'))

    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    
    for contest in data:
          try:
              calender.create_event(contest, service)
          except HttpError as e:
              traceback.print_exc()
              print(e)
              eventData = calender.make_event(contest)
              updated_event = service.events().update(calendarId='primary', eventId=eventData['id'], body=eventData).execute()

              
              
          except Exception as e:

              print(e)
              traceback.print_exc()
              flash("Failed to add contest to calender")

    flash("{} contests from codeforces added to Calender ".format(len(data)))

    return  flask.redirect(flask.url_for('events'))

@app.route("/addatcoder")
def addatcoder():

    try :
        with open('data.json', 'r') as openfile: 
            json_object = json.load(openfile) 

        if json_object['updated'] != datetime.datetime.now().strftime('%d-%m-%Y'):
            data = atcoder_contest()

            threading.Thread(target=get_contest).start()
            # call thread
        else:
            data = json_object['contests']
            data = list(filter(lambda x: x['platform'] == 'ATCODER', data ))
    except Exception as e:
        print(e)
        data = []
    
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except Exception as e:
        print(e)
        traceback.print_exc()
        return flask.redirect(flask.url_for('index'))

    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    
    for contest in data:
          try:
              calender.create_event(contest, service)
          except HttpError as e:
              print(e)
              traceback.print_exc()
              eventData = calender.make_event(contest)
              updated_event = service.events().update(calendarId='primary', eventId=eventData['id'], body=eventData).execute()

              
              
          except Exception as e:
              print(e)
              traceback.print_exc()
              flash("Failed to add contest to calender")

    flash("{} contests from Atcoder added to Calender ".format(len(data)))

    return  flask.redirect(flask.url_for('events'))

@app.route("/addhackerearth")
def addhackerearth():

    try :
        with open('data.json', 'r') as openfile: 
            json_object = json.load(openfile) 

        if json_object['updated'] != datetime.datetime.now().strftime('%d-%m-%Y'):
            data = atcoder_contest()

            threading.Thread(target=get_contest).start()
            # call thread
        else:
            data = json_object['contests']
            data = list(filter(lambda x: x['platform'] == 'HACKEREARTH', data ))
    except Exception as e:
        print(e)
        traceback.print_exc()
        data = []
    
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except Exception as e:
        print(e)
        traceback.print_exc()
        return flask.redirect(flask.url_for('index'))

    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    
    for contest in data:
          try:
              calender.create_event(contest, service)
          except HttpError as e:
              print(e)
              traceback.print_exc()
              eventData = calender.make_event(contest)
              updated_event = service.events().update(calendarId='primary', eventId=eventData['id'], body=eventData).execute()

              
              
          except Exception as e:
              print(e)
              traceback.print_exc()
              flash("Failed to add contest to calender")

    flash("{} contests from Hackerearth added to Calender ".format(len(data)))

    return  flask.redirect(flask.url_for('events'))



@app.route("/addall")
def addall():

    try :
        with open('data.json', 'r') as openfile: 
            json_object = json.load(openfile) 

        if json_object['updated'] != datetime.datetime.now().strftime('%d-%m-%Y'):
            data = get_contest()

            threading.Thread(target=get_contest).start()
            # call thread
        else:
            data = json_object['contests']
    except Exception as e:
        print(e)
        traceback.print_exc()
        data = []
    
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except Exception as e:
        print(e)
        traceback.print_exc()
        return flask.redirect(flask.url_for('index'))

    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    
    for contest in data:
          try:
              calender.create_event(contest, service)
          except HttpError as e:
              print(e)
              traceback.print_exc()
              eventData = calender.make_event(contest)
              updated_event = service.events().update(calendarId='primary', eventId=eventData['id'], body=eventData).execute()

              
              
          except Exception as e:
              print(e)
              traceback.print_exc()
              flash("Failed to add contest to calender")

    flash("{} contests added to Calender ".format(len(data)))

    return  flask.redirect(flask.url_for('events'))

@app.route("/api/contests")
def contestapi():

    try :
        with open('data.json', 'r') as openfile: 
            json_object = json.load(openfile) 

        if json_object['updated'] != datetime.datetime.now().strftime('%d-%m-%Y'):
            data = atcoder_contest()

            threading.Thread(target=get_contest).start()
            # call thread
        else:
            data = json_object['contests']
    except Exception as e:
        print(e)
        traceback.print_exc()
        data = []
    
    return jsonify(data)




if __name__ == '__main__':
    
    app.run()