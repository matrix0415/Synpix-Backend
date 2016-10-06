from django.conf.urls import *

urlpatterns =patterns('',
	# Event 
	(r'^event/create/$', 'synpix.views.eventCreate'),
	(r'^event/update/$', 'synpix.views.eventUpdate'),
	(r'^event/get/$', 'synpix.views.eventGet'), 
	(r'^event/accept/$', 'synpix.views.eventAccept'),
	(r'^event/invite/$', 'synpix.views.eventInvite'),
	(r'^event/userStatus/$', 'synpix.views.eventUserStatus'),
	
	# PhotoSet
	(r'^photoset/create/$', 'synpix.views.photoSetCreate'),
	(r'^photoset/update/$', 'synpix.views.photoSetUpdate'),
	(r'^photoset/get/$', 'synpix.views.photoSetGet'), 
	(r'^photoset/init/$', 'synpix.views.photoSetInit'),
	
	# Photo
	(r'^photo/create/$', 'synpix.views.photoCreate'),
	(r'^photo/status/$', 'synpix.views.photoStatus'),
	
	# User
	(r'^user/getID/$', 'synpix.views.userGetID'),
	(r'^user/update/$', 'synpix.views.userUpdate'),
	
	# Overall
	(r'^init/$', 'synpix.views.init'),
	(r'^version/get/$', 'synpix.views.versionGet'),
	(r'^session/register/$', 'synpix.views.sessionRegister'),
)