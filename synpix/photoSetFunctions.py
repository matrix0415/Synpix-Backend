from synpix.models import photoSet, eventUser, event
from synpix.globalFunctions import errMsg

from datetime import datetime
from datetime import timedelta 
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

'''
Functions of PhotoSet.
Created By Matrix in 2013.	(matrix0415@gmail.com)
'''

@transaction.commit_manually()		# manually commit the transaction
def photoSetCreateFunction(ptda):
	rsdata ={}
	try:
		# change event rev.
		eobj =event.objects.get(eventID =ptda['eventID'])
		changeRev =eobj.updateRev()
		# change event rev success.
		if changeRev[0]:
			savePhotoSet =photoSet(eventID_id =ptda['eventID'], title =ptda['title'], createDate =ptda['date'], location =ptda['loc'], lat =ptda['lat'], lon =ptda['lon'], rev =ptda['rev'])
			savePhotoSet.save()
			transaction.commit()
			rsdata['rs'] =1
			rsdata['msg'] =savePhotoSet.pk
			if ptda.has_key('localID'):
				rsdata['localID'] =ptda['localID']
		# change event rev failed.
		else:
			transaction.rollback()
			rsdata['rs'] =0
			rsdata['msg'] =errMsg('photoSetCreateFunction', 'Change event rev', changeRev[1])
	except Exception, e:
		transaction.rollback()
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('photoSetCreateFunction', 'all', e)
	return rsdata

def photoSetAttribuetFoundFunction(ptda):
	rs ={}
	try:
		# found the photoset.
		smlTimeRange =ptda['date']-timedelta(minutes =15)
		lrgTimeRange =ptda['date']+timedelta(minutes =15)
		smlLat =float(ptda['lat'])-0.0005
		lrgLat =float(ptda['lat'])+0.0005
		smlLon =float(ptda['lon'])-0.0005
		lrgLon =float(ptda['lon'])+0.0005
			
		psID =photoSet.objects.values('photoSetID', 'rev').get(eventID =ptda['eventID'], createDate__range =[smlTimeRange, lrgTimeRange], lat__range =[smlLat, lrgLat], lon__range =[smlLon, lrgLon])
			
		rs['rs'] =1
		rs['msg'] =psID['photoSetID']
	except ObjectDoesNotExist:
		# Create a new photoset.
		rs =photoSetCreateFunction(ptda)
	except Exception, e:
		rs['rs'] =0
		rs['msg'] =errMsg('photoSetAttribuetFoundFunction', 'all', e)	
	return rs

def photoSetCreateMainFunction(ptda):
	rsdata ={}
	#print ptda
	userobj =eventUser.objects.values('userAcceptOrNot').get(userID =ptda['userID'], eventID =ptda['eventID'])
	if userobj['userAcceptOrNot']:
		# found the photoset.
		rsdata =photoSetAttribuetFoundFunction(ptda)
	else:
		# Event user not accept the event.
		rsdata['rs'] =3
	return rsdata
	
	