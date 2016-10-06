from synpix.globalFunctions import errMsg
from synpix.models import eventUser, event
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

'''
Functions of Event.
Created By Matrix in 2013.	(matrix0415@gmail.com)
'''

@transaction.commit_manually()		# manually commit the transaction
def eventCreateFunction(ptda):
	rsdata ={}
	try:	
		eventID =event.objects.values('eventID').filter(createDate =ptda['createDate'])
		eu =eventUser.objects.values('eventID').get(userID =ptda['userID'], eventID__in =eventID)
		transaction.commit()
		rsdata['rs'] =2
		rsdata['msg'] =eu['eventID']
		
	except ObjectDoesNotExist:
		# save event
		saveEvent =event(createDate =ptda['createDate'], startDate =ptda['startDate'], endDate =ptda['endDate'], title =ptda['title'], rev =ptda['rev'], eventType_id =int(ptda['eventType']))
		saveEvent.save()			
		# save event user
		saveUser =eventUser(eventID =saveEvent, userID_id =ptda['userID'], userPermissionID_id =ptda['userPermissionID'], userAcceptOrNot =True, userReadedOrNot =True)
		saveUser.save()
		transaction.commit()
		
		rsdata['rs'] =1
		rsdata['msg'] =saveEvent.pk
	except Exception, e:
		transaction.rollback()
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('eventCreateFunction', 'save event', e)
	return rsdata

