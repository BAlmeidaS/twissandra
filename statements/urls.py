from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('statements.views',
	url(r'^$', 'report', name='report'),
    url(r'^loginsbyuser/$', 'logins_by_user', name='logins_by_user'),
    url(r'^basica/$', 'show_statements', name='show_statements'),
    url(r'^avancada/$', 'show_statements2', name='show_statements2'),
)