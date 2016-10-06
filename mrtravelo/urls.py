from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mrtravelo.views.home', name='home'),
    # url(r'^mrtravelo/', include('mrtravelo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	url(r'^api/',include('synpix.urls')),
    #url(r'^api/(?P<catagory>\w+)/(?P<method>\w+)/$', 'synpix.views.api'),
)
