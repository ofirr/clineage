
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
import clineage.settings as settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^CLineage/', include('LinApp.urls')),

    #Homepage
    (r'^$', 'LinApp.views.homepage'),
    (r'^tab:(?P<tab>\w+)$', 'LinApp.views.homepage'),

    # Login/Logout/Register Account
    (r'^accounts/', include('accounts.urls')),

    # Dojango path
    (r'^dojango/', include('dojango.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    #Tree test
    ('^treetest/$', TemplateView.as_view(template_name='treetest.html')),

    #TriStateCheckbox tests
    ('^tristatecheckboxtest/$', TemplateView.as_view(template_name='tristatecheckboxtest.html')),
    ('^externaltristatecheckboxtest/$', TemplateView.as_view(template_name='external_tristatecheckboxtest.html')),
    #TriStateCheckbox tests
    ('^success_page_background/$', TemplateView.as_view(template_name='success_page_background.html')),

    #soap test
    (r'^soap/', include('soap.urls')),
    ### Media
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),
    ### Media
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
)
