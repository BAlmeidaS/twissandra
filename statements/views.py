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

    #views_user_course eh um dicionario com as keys = usuarios e os values = dicts_course
    #dicts_course eh um dicionario de key = curso e values = qtd que usuario viu o curso
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
                print "nao era view de curso"
   
    df2 = pd.DataFrame(views_user_course.items())
    
    df2.columns = ['user', 'course']

    context = {
        'columns' : df2.columns,
        'lines' : df2.values,
        }


    return render_to_response(
        'statements/user_course_relation_with_view.html', context, context_instance=RequestContext(request))



def verbs_by_user(request):

    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    statements = session.execute("""SELECT * FROM statements2""")

    verbs_per_user = dict()

    for row in statements:
        if str(row.actor.name) not in verbs_per_user:
            verbs_per_user[str(row.actor.name)] = dict()
            verbs_per_user[row.actor.name][row.verb.display.get('en-US')] = 1
        else:
            if row.verb.display.get('en-US') not in verbs_per_user[row.actor.name]:                
                verbs_per_user[row.actor.name][row.verb.display.get('en-US') ] = 1
            else:
                verbs_per_user[row.actor.name][row.verb.display.get('en-US') ] += 1


    df2 = pd.DataFrame(verbs_per_user.items())
    
    df2.columns = ['user', 'verb']

    context = {
        'columns' : df2.columns,
        'lines' : df2.values,
        }


    return render_to_response(
        'statements/verb_per_user.html', context, context_instance=RequestContext(request))   

def verb_types(request):

    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    statements = session.execute("""SELECT * FROM statements2""")

    type_verbs = dict()

    for row in statements:
        if str(row.verb.display.get('en-US')) not in type_verbs:
            type_verbs[row.verb.display.get('en-US')] = row.verb.display.get('en-US')


    column = 'verb'

    context = {
        'column' : column,
        'lines' : type_verbs.keys,
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


    column = 'user'

    context = {
        'column' : column,
        'lines' : type_users.keys,
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
        if str(row.verb.display.get('en-US')) == "loggedin":
            if str(row.actor.name) in loogedin_users:
                #if datetetime.datetime(looged_users[str(row.actor.name)][-1][1][0:-13],"%Y-%m-%dT%H:%M:%S") > datetime.datetime(str(row.timestamp)[0:-13],"%Y-%m-%dT%H:%M:%S")
                loogedin_users[str(row.actor.name)].append(str(row.timestamp)[0:-13])
            else:
                loogedin_users[str(row.actor.name)] = []
                loogedin_users[str(row.actor.name)].append(str(row.timestamp)[0:-13])
        else:
            if str(row.verb.display.get('en-US')) == "loggedout":
                if str(row.actor.name) in loogedout_users:
                    loogedout_users[str(row.actor.name)].append(str(row.timestamp)[0:-13])
                else:
                    loogedout_users[str(row.actor.name)] = []
                    loogedout_users[str(row.actor.name)].append(str(row.timestamp)[0:-13])


    #html_table_df2 = df2.to_html(index=False)

    df2 = pd.DataFrame(loogedin_users.items())
    df3 = pd.DataFrame(loogedout_users.items())

    columns_login = ['user', 'logins']
    columns_logout = ['user', 'logouts']


    context = {
        'columns_login' : columns_login,
        'lines_login' : df2.values,
        'columns_logout' : columns_logout,
        'lines_logout' : df3.values,
        }


    return render_to_response(
        'statements/login_logout.html', context, context_instance=RequestContext(request))

def last_ten_statements(request):
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace("twissandra")

    
    i = session.execute("""SELECT qtd FROM querries where type = 'states2' """)
    i = i[0].qtd
    temp = str(int(i-1))
    for k in range(9):
        temp = temp + ", " + str(i - (k+2))


    statements = session.execute("SELECT * FROM statements2 where idlrs in (" + temp + ")")

    # cria o vetor type_users, com todos os usuarios do sistema 

    last_ten_statements = dict()

    for row in statements:
        last_ten_statements[str(row.idlrs)] = str(row.object.definition.description.get('en-US'))


    df2 = pd.DataFrame(last_ten_statements.items())

    html_table_df2 = df2.to_html(index=False)
    
    df2.columns = ['id', 'statement']

    context = {
        'columns' : df2.columns,
        'lines' : df2.values,
        }


    return render_to_response(
        'statements/last_ten_statements.html', context, context_instance=RequestContext(request))