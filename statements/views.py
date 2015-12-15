from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from cassandra.cluster import Cluster
from django.core.management.base import NoArgsCommand
from  HTMLParser import HTMLParser
import copy
import urllib
import urllib2
import json
import ast
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

def show_statements(request):
         
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")


    i = session.execute("""SELECT qtd FROM querries where type = 'states' """)
    if not i:
        i = 1
    else:
        i = i[0].qtd

    print i
    while True:
        f = urllib2.urlopen('http://ec2-54-213-235-203.us-west-2.compute.amazonaws.com/getstat/'+str(i))
        stat = f.read()

        if stat == "null":
            break
        a = ast.literal_eval(stat)
        stat_json = json.dumps(a)  
      

        prepared = session.prepare('INSERT INTO statements JSON ?')
        obj = {'id':i, 'json':stat_json}
        session.execute(prepared, [json.dumps(obj)])
        i = i + 1

    prepared = session.prepare('INSERT INTO querries JSON ?')
    obj = {'type':'states', 'qtd':i}
    session.execute(prepared, [json.dumps(obj)])


    #query = """INSERT INTO statements JSON {\"id\":1, \"json\":\"{\"a\":\"a\"}\"}""" #% re.escape(stat_json)
    #query = """INSERT INTO statements JSON '{"statement" : "teste", "json" : "%s"'""" % re.escape(stat_json)

    #session.execute(query)
    #session.execute("INSERT INTO statements (id, json) VALUES (%d, %s)", (1, "{'a':'a'}") )
    #session.execute("INSERT INTO statements (id, json) VALUES (%d, %s)", (1, "{'a':'a'}") )

    rows = session.execute("""SELECT * FROM statements""")

    context = {
        'rows': rows,
        }

    return render_to_response(
        'statements/all_statements.html', context, context_instance=RequestContext(request))


def show_statements2(request):
         
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    i=session.execute("""SELECT qtd FROM querries where type = 'states2' """)
    if not i:
        i=1
    else:
        i=i[0].qtd

    print i

    while True:
        f = urllib2.urlopen('http://ec2-54-213-235-203.us-west-2.compute.amazonaws.com/getstat/'+str(i))
        stat = f.read()

        if stat == "null":
            break
        obj = ast.literal_eval(stat)
        obj['idlrs'] = i 

        prepared = session.prepare('INSERT INTO statements2 JSON ?')
        session.execute(prepared, [json.dumps(obj)])
        i=i+1

    prepared = session.prepare('INSERT INTO querries JSON ?')
    obj = {'type':'states2', 'qtd':i}
    session.execute(prepared, [json.dumps(obj)])


    rows = session.execute("""SELECT * FROM statements2""")

    print "resultados do json"
    print rows[0].verb.id

    print rows[0].verb.display.get('en-US')

    print rows[0].version

    print rows[0].timestamp

    print rows[0].object.definition.name.get('en-US')
    print rows[0].object.definition.description.get('en-US')
    print rows[0].object.id
    print rows[0].object.objecttype


    print rows[0].actor.mbox
    print rows[0].actor.name
    print rows[0].actor.objecttype

    print rows[0].stored

    print rows[0].authority.mbox
    print rows[0].authority.name
    print rows[0].authority.objecttype

    print rows[0].id

    print rows[0].idlrs

    context = {
        'rows': rows,
        }

    return render_to_response(
        'statements/all_statements.html', context, context_instance=RequestContext(request))

def report_statements(request):
         
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")


    statements = session.execute("""SELECT * FROM statements2""")

    logins_per_user = dict()

    for row in statements:
        if str(row.actor.name) in logins_per_user:
            logins_per_user[str(row.actor.name)] += 1

        else:
            actions_per_user[str(row.actor.name)] = 1
    df_actions = pd.DataFrame(actions_per_user.items())


    statements_temp = statements
    for k in statements_temp:
        if k.verb.display.get('en-US') == "viewed":
            try:
                temp = str(k.object.definition.description.get('en-US'))[-10:-1]
                print k.actor.name + " " + k.verb.display.get('en-US') + " " + temp.split("'")[1]
            except:
                print "nao era view de curso"

    # cria o vetor type_verbs, com todos os verbos do sistema 
    statements_temp = copy.copy(statements)
    type_verbs = []
    for row in statements_temp:
        if str(row.verb.display.get('en-US')) not in type_verbs:
            type_verbs.append(str(row.verb.display.get('en-US')))
    #print type_verbs


    # cria o vetor type_users, com todos os usuarios do sistema 
    statements_temp = copy.copy(statements)
    type_users = []
    for row in statements_temp:
        if str(row.actor.name) not in type_users:
            type_users.append(str(row.actor.name))
    #print type_users


    #cria os dicts loogedin_users e loogedout_users
    #sao dicionarios que cada chave sao os usuarios e seus valores sao os vetores com todos as datas de login e logout (respectivamente)
    statements_temp = copy.copy(statements)
    loogedin_users = dict()
    loogedout_users = dict()
    for row in statements_temp:
        date = datetime.datetime.strptime(str(row.timestamp)[0:-13],"%Y-%m-%dT%H:%M:%S")
        if str(row.verb.display.get('en-US')) == "loggedin":
            if str(row.actor.name) in loogedin_users:
                #if datetetime.datetime(looged_users[str(row.actor.name)][-1][1][0:-13],"%Y-%m-%dT%H:%M:%S") > datetime.datetime(str(row.timestamp)[0:-13],"%Y-%m-%dT%H:%M:%S")
                loogedin_users[str(row.actor.name)].append(date)
            else:
                loogedin_users[str(row.actor.name)] = []
                loogedin_users[str(row.actor.name)].append(date)
        else:
            if str(row.verb.display.get('en-US')) == "loggedout":
                if str(row.actor.name) in loogedout_users:
                    loogedout_users[str(row.actor.name)].append(date)
                else:
                    loogedout_users[str(row.actor.name)] = []
                    loogedout_users[str(row.actor.name)].append(date)


     html_table_df2 = df2.to_html(index=False)

    #usuario por verbo mais uilizado

    df2.columns = ['user', 'logins']


    context = {
        'html_table_df2' : html_table_df2,
        'columns' : df2.columns,
        'lines' : df2.values,
        }


    return render_to_response(
        'statements/all_statements.html', context, context_instance=RequestContext(request))