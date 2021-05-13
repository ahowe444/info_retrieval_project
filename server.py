from flask import Flask, render_template, request
from wtforms import Form, TextField 


import json
import requests
clientID = '0asbh4mg6ocktnlrvkjts9l29g9h8n'
secret = 'rifuh05a1wpxcwhrx75fqb8ga3aez3'
r = requests.post('https://id.twitch.tv/oauth2/token?client_id='
        +clientID+'&client_secret='+secret+'&grant_type=client_credentials')
token = json.loads(r.content)['access_token']


def get_id(user):
    headers = {'Client-ID': clientID, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get('https://api.twitch.tv/kraken/users?login='+user, headers =headers)
    try:
        return json.loads(r.content)['users'][0]['_id']
    except:
        return None

def get_user(id):
    headers = {'Client-ID': clientID, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get('https://api.twitch.tv/kraken/users/'+id, headers =headers)
    return json.loads(r.content)['display_name']

def follows_who(id):
    headers = {'Authorization': 'Bearer '+token,
              'Client-ID': clientID, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get('https://api.twitch.tv/helix/users/follows?from_id='
            +id+'&first=100', headers =headers)
    res = json.loads(r.content)
    users = [name['to_name'] for name in res['data']]
    page = res['pagination'].get('cursor', None)
    while page:
        headers = {'Authorization': 'Bearer '+token,
                'Client-ID': clientID, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get('https://api.twitch.tv/helix/users/follows?from_id='
                +id+'&first=100&after='+page, headers =headers)
        res = json.loads(r.content)
        new_users = [name['to_name'] for name in res['data']]
        users= users + new_users
        page = res['pagination'].get('cursor', None)
    return users

def compare(streamer1, streamer2):
    follow1 = follows_who(get_id(streamer1))
    follow2 = follows_who(get_id(streamer2))
    sim = [x for x in follow1 if x in follow2]
    return (sim, len(sim))


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def load_home():
    return render_template("home.html")

@app.route('/result', methods=['GET', 'POST'])
def load_result():
    s1 = request.form['streamer1']
    s2 = request.form['streamer2']
    intersect, length = compare(s1, s2)
    return render_template("home.html", intersect=intersect, length=length)


if __name__ == "__main__":
    app.run()
