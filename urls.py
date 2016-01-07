from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    url('^tweets/', include('controls.urls')),
    url('^statements/', include('statements.urls', namespace='statements')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^media/(?P<path>.*)$', 'serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
