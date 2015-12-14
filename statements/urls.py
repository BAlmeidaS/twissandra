from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('statements.views',
    url('', 'show_statements', name='show_statements'),
)