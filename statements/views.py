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

    context = {
        'rows': rows,
        }

    return render_to_response(
        'statements/all_statements.html', context, context_instance=RequestContext(request))

def report(request):

    return render_to_response(
        'statements/reports.html', context_instance=RequestContext(request))

def logins_by_user(request):
         
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    statements = session.execute("""SELECT * FROM statements2""")

    logins_per_user = dict()

    for row in statements:
        if str(row.actor.name) in logins_per_user:
            logins_per_user[str(row.actor.name)] += 1

        else:
            logins_per_user[str(row.actor.name)] = 1
    df_actions = pd.DataFrame(logins_per_user.items())
    df2 = pd.DataFrame(logins_per_user.items())

    html_table_df2 = df2.to_html(index=False)
    
    df2.columns = ['user', 'logins']

    context = {
        'html_table_df2' : html_table_df2,
        'columns' : df2.columns,
        'lines' : df2.values,
        }


    return render_to_response(
        'statements/logins_by_user.html', context, context_instance=RequestContext(request))


def user_course_relation_with_view(request):
         
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    statements = session.execute("""SELECT * FROM statements2""")



    #ciews_user_course é um dicionario com as keys = usuarios e os values = dicts_course
    #dicts_course é um dicionario de key = curso e values = qtd que usuario viu o curso
    views_user_course = dict()
    for row in statements:
        if row.verb.display.get('en-US') == "viewed":
            try:
                curso = str(int(str(row.object.definition.description.get('en-US'))[-10:-1].split("'")[1]))
                if str(row.actor.name) not in views_user_course:                
                    views_user_course[row.actor.name] = dict()
                    views_user_course[row.actor.name][curso] = 1
                else:
                    if curso not in views_user_course[row.actor.name]:                
                        views_user_course[row.actor.name][curso] = 1
                    else:
                        views_user_course[row.actor.name][curso] += 1
            except:
                print "error in viewed"



    #df2.columns = ['user', 'logins']

    context = {
        'columns' : 'b',
        'lines' : 'a',
        }


    return render_to_response(
        'statements/user_course_relation_with_view.html', context, context_instance=RequestContext(request))

def verb_types(request):

    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    statements = session.execute("""SELECT * FROM statements2""")

    type_verbs = dict()

    for row in statements:
        if str(row.verb.display.get('en-US')) not in type_verbs:
            type_verbs[row.verb.display.get('en-US')] = row.verb.display.get('en-US')


    #print type_verbs

    #html_table_df2 = df2.to_html(index=False)

    
    #df2.columns = ['user', 'logins']


    context = {
        'html_table_df2' : 'html_table_df2',
        }


    return render_to_response(
        'statements/verb_types.html', context, context_instance=RequestContext(request))


def user_types(request):
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    statements = session.execute("""SELECT * FROM statements2""")

    # cria o vetor type_users, com todos os usuarios do sistema 
    type_users = dict()
    for row in statements:
        if str(row.actor.name) not in type_users:
            type_users[str(row.actor.name)] = str(row.actor.name)


    #df2.columns = ['user', 'logins']


    context = {
        'html_table_df2' : 'html_table_df2',
        }


    return render_to_response(
        'statements/user_types.html', context, context_instance=RequestContext(request))


def login_logouts(request):
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    statements = session.execute("""SELECT * FROM statements2""")
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


    #html_table_df2 = df2.to_html(index=False)


    #df2.columns = ['user', 'logins']


    context = {
        'html_table_df2' : 'html_table_df2',
        }


    return render_to_response(
        'statements/login_logout.html', context, context_instance=RequestContext(request))