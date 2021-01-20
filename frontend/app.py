from flask import Flask
import datetime
import json
from hashlib import sha256
import requests
from flask import render_template, redirect, request
import plotly.express as px
import pandas as pd

from db import verify_exists

app = Flask(__name__)

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

votes = []


def fetch_votes():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    global CONNECTED_NODE_ADDRESS
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global votes
        votes = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)

@app.route('/', methods=['GET'])
def lander():
    return render_template('landing.html')

@app.route('/land', methods=['GET'])
def land():
    return render_template('landing.html')

@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')

@app.route('/mine', methods=['GET'])
def mine():
    global CONNECTED_NODE_ADDRESS
    requests.get(f"{CONNECTED_NODE_ADDRESS}/mine")
    return redirect('/')

@app.route('/vote', methods=['GET'])
def voting():
    global CONNECTED_NODE_ADDRESS
    return render_template('voting.html', node_address=CONNECTED_NODE_ADDRESS)


@app.route('/error', methods=['GET'])
def index3():
    return render_template('error.html',
                           title='Voter Dashboard',
                           votes=[],
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/votes', methods=['GET'])
def adminweb():
    global votes
    print(votes)
    fetch_votes()
    return render_template('adminweb.html',
                           title='Blockchain Votes',
                           votes=votes,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/changeNode', methods=['GET'])
def changeNode():
    global CONNECTED_NODE_ADDRESS
    CONNECTED_NODE_ADDRESS = "http://127.0.0.1:9000"
    return f'changed node to pper node {CONNECTED_NODE_ADDRESS}'


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    global CONNECTED_NODE_ADDRESS
    ### need to send this data off to a validator, then check it out later
    print(request.form)
    bools = verify_exists(request.form['first_name'], request.form['last_name'], request.form['password'], request.form['voterid'])

    ## we only want to store the candidate data, we assume that the verification is done
    ## truly anonymous 
    if bools:
        ## preparing the identitiy hash first
        hashstr = request.form['first_name'] + request.form['last_name'] + request.form['password'] + request.form['voterid']
        hashed = sha256(hashstr.encode()).hexdigest()
        post_object = {
            'candidate': request.form['candidate'],
            'voterhash': hashed
        }

        new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address, json=post_object, headers={'Content-type': 'application/json'})

        return redirect('/success')

    else:
        return render_template('error.html', message="MYSQL ERROR")


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')



@app.route('/count', methods=['GET'])
def count_votes():
    global CONNECTED_NODE_ADDRESS
    candids = {}
    data = requests.get(f'{CONNECTED_NODE_ADDRESS}/chain')
    dat = data.json()['chain']
    
    for i in dat:
        for j in i['transactions']:
            ## now we have to verify this voterhash. hmm
            
            ### ver = j['voterhash']
            ver = True
            if ver:
                # means that the voterhash was verified and crosschecked with the database
                if j['candidate'] in candids:
                    candids[j['candidate']] += 1
                else:
                    candids[j['candidate']] = 1
    df = pd.DataFrame.from_dict(candids, orient='index')
    df.columns = ['votes']
    df.index
    print(df.head())
    fig = px.pie(df, names=df.index, values='votes', title='Voting Distribution for Candidates')
    fig.write_html('./templates/count.html')
    return render_template('count.html')