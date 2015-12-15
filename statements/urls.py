from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('statements.views',
	url(r'^$', 'report', name='report'),
    url(r'^loginsbyuser/$', 'logins_by_user', name='logins_by_user'),
    url(r'^verbsbyuser/$', 'verbs_by_user', name='verbs_by_user'),
    url(r'^usercourserelation/$', 'user_course_relation_with_view', name='user_course_relation'),
    url(r'^verbtypes/$', 'verb_types', name='verb_types'),
    url(r'^usertypes/$', 'user_types', name='user_types'),
    url(r'^loginlogouts/$', 'login_logouts', name='login_logouts'),
    url(r'^basica/$', 'show_statements', name='show_statements'),
    url(r'^avancada/$', 'show_statements2', name='show_statements2'),
)