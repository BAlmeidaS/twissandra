from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from cassandra.cluster import Cluster
from django.core.management.base import NoArgsCommand
from  HTMLParser import HTMLParser
import urllib
import urllib2
import json
import ast
import re

def show_statements(request):
    #get_statements

    while True:
        f = urllib2.urlopen('http://ec2-54-213-235-203.us-west-2.compute.amazonaws.com/getstat/8/')
        stat = f.read()
        a = ast.literal_eval(stat)

        stat_json = json.dumps(a)

        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect()
        session.set_keyspace("twissandra")

        prepared = session.prepare('INSERT INTO statements JSON ?')
        test = {'id':8, 'json':stat_json}
        session.execute(prepared, [json.dumps(test)])
    


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