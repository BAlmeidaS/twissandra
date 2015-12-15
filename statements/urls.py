from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('statements.views',
    url(r'^report/', 'report_statements', name='report_statements'),
    url('^basica/', 'show_statements', name='show_statements'),
    url('^avancada/', 'show_statements2', name='show_statements2'),
)