# -*- coding: UTF-8 -*-
# Create your views here.
from synpix.form import *
from synpix.models import *
from synpix.globalFunctions import *
from synpix.eventFunctions import *
from synpix.photoSetFunctions import *

#import time
import json
from pytz import timezone
from datetime import datetime
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse
from django.utils.timezone import utc
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

'''
APIs of Synpix.
Created By Matrix in 2013.	(matrix0415@gmail.com)
'''

'''
Notes Section

Change All DateField into DateTimeField

'''

'''
Function:::::
	Global Functions:::
		def getPostData(catagory, req)
		def sessionFunction(userID, token, session)
		def errMsg(funcName, action, errMsg)
	Event Functions:::	
		def eventCreateFunction(ptda)
	PhotoSet Functions:::
		def photoSetCreateFunction(ptda)
		def photoSetAttribuetFoundFunction(ptda)
		def	photoSetCreateMainFunction(ptda)
	Session Functions::
		def sessionIdentifyFunction(req)
		def sessionRegisterFunction(req)
			
API:::::
	Event:::
		def eventCreate(request)
		def eventGet(request)
		def eventUpdate(request)
		def eventInvite(request)
		def eventAccept(request)
		def eventUserStatus(request)
	PhotoSet:::	
		def photoSetCreate(request)
		def photoSetUpdate(request)
		def photoSetGet(request)
		def photoSetInit(request)
	Photo:::
		def photoCreate(request)
		def photoStatus(request)
	User:::
		def userGetID(request)
		def userUpdate(request)
	Overall:::
		def init(request)
		def versionGet(request)
		def sessionRegister(request)
'''


# ===============================================================================================		
# API Region.
# ===============================================================================================

	
# Event Region.	-------------------------------------------------------------------
@csrf_exempt
@transaction.commit_manually()		# manually commit the transaction
def eventCreate(request):
	rsdata ={}
	ptda =getPostData('event', request)
	try:
		rsdata =eventCreateFunction(ptda)
		if rsdata['rs'] ==1:
			transaction.commit()
		else:
			transaction.rollback()
	except Exception, e:
		transaction.rollback()
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('eventCreate' ,'all', e)
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")

	
@csrf_exempt
def eventGet(request):	
	rsdata ={}
	
	ptda =getPostData('event', request)
	
	try:
		e =event.objects.get(eventID =ptda['id'])
		if e.compareRev(ptda['rev']) !=1:
			rsdata['rs'] =e.compareRev(ptda['rev'])		# rsdata contain 2,3
		else:
			try:
				psid =photoSet.objects.values().filter(eventID =ptda['id'])
				rsdata['rs'] =1
				rsdata['msg'] =list(psid)
				rsdata['rev'] =e.rev
			except ObjectDoesNotExist:
				rsdata['rs'] =4
				rsdata['rev'] =str(e.rev)
	except ObjectDoesNotExist:
		rsdata['rs'] =5	
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
	
	
@csrf_exempt
def eventUpdate(request):
	ptda =getPostData('event', request)
	try:
		data =event.objects.get(eventID =request.POST['eventID'])
		try:
			data.startDate =ptda['startDate']
			data.endDate =ptda['endDate']
			data.title =ptda['title']
			data.rev =ptda['rev']
			data.save()
			rsdata['rs'] =1
		except Exception, e:
			rsdata['rs'] =0
			rsdata['msg'] =errMsg('eventUpdate', 'Update Event', e)			
	
	except ObjectDoesNotExist:
		rsdata['rs'] =2		
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")

	
@csrf_exempt
#@transaction.commit_manually()		# manually commit the transaction
def eventInvite(request):			# ##############################################
	rsdata ={}
	
	ptda =getPostData('eventInvite', request)
	if len(ptda) !=0:
		try:
			eUser =eventUser.objects.values('userPermissionID').get(userID =ptda['userID'], eventID =ptda['eventID'])
			if eUser['userPermissionID'] ==1:		# user is the event owner.
				for i in ptda['friend']:
					try:  
						if i.has_key('userID'):
						# take the one who have synpix user id
							form =eventUserForm(i)
							if form.is_valid():
								try:
									form.save()
									rsdata['rs'] =1
								except Exception, e:
									rsdata['rs'] =0
									rsdata['msg'] =errMsg('eventInvite', 'save eventUser Form', e)
							else:
								rsdata['rs'] =0
								rsdata['msg'] =errMsg('eventInvite', 'create evenUser Form', form.errors)
						elif i.has_key('fbID'):
							rsdata['rs'] =1
						elif i.has_key('phone'):
							rsdata['rs'] =1
						#transaction.commit()
					except Exception, e:
						rsdata['rs'] =0
						rsdata['msg'] =errMsg('eventInvite', 'Invite user in loop', e)
						#transaction.rollback()
				#rsdata['rs'] =1
			elif eUser ==2:
				rsdata['rs'] =2
				#transaction.commit()
		except ObjectDoesNotExist:		# Event User not found.
			rsdata['rs'] =2
			#transaction.commit()
		except Exception, e:
			rsdata['rs'] =0
			rsdata['msg'] =errMsg('eventInvite', 'all', e)
			#transaction.rollback()
	else:
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('eventInvite', 'all', 'Attribute Friend cannot be null.')
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")

	
@csrf_exempt
def eventAccept(request):
	rsdata ={}
	try:
		eu =eventUser.objects.get(eventID =request.POST['eventID'], userID =request.POST['userID'])
		rs =eu.make_accept(request.POST['acceptOrNot'])
		if rs[0]:
			rsdata['rs'] =1
		else:
			rsdata['rs'] =0
			rsdata['msg'] =errMsg('eventAccept', 'save accept', rs[1])		
	except ObjectDoesNotExist:
		rsdata['rs'] =2
	except Exception, e:	
		rsdata['rs'] =1
		rsdata['msg'] =errMsg('eventAccept', 'all', e)
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
		
		
@csrf_exempt
@transaction.commit_manually()		# manually commit the transaction
def eventUserStatus(request):
	try:
		eU =eventUser.objects.get(userID =request.POST['userID'], eventID =request.POST['eventID'])
		rs =eU.make_status(request.POST['enable'])
		if rs[0]:
			rsdata['rs'] =1
			transaction.commit()
		else:
			rsdata['rs'] =0
			rsdata['msg'] =errMsg('eventUserStatus', 'save disable', rs[1])
			transaction.rollback()
	except ObjectDoesNotExist:
		rsdata['rs'] =2
		transaction.commit()
	except Exception, e:
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('eventUserStatus', 'all', e)
		transaction.rollback()
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
		
		
# PhotoSet Region.	-------------------------------------------------------------------
@csrf_exempt
def photoSetCreate(request):
	rsdata ={}
	ptda =getPostData('photoset', request)	
	try:
		rsdata =photoSetCreateMainFunction(ptda)
	except ObjectDoesNotExist:	
		# Event user not found.
		rsdata['rs'] =2
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
	

@csrf_exempt		
def photoSetUpdate(request):
	try:
		getps =photoSet.objects.get(photoSetID =ptda['id'])
		getps.location =ptda['location']
		getps.lon =ptda['lon']
		getps.lat =ptda['lat']
		getps.title =ptda['title']
		getps.save()
		
		rsdata['rs'] =1
	except ObjectDoesNotExist:
		rsdata['rs'] =2		
	except Exception, e:
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('photoSetUpdate', 'all', e)
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")

	
@csrf_exempt		
def photoSetGet(request):
	rsdata ={}
	ptda =getPostData('photoset', request)	
	# print ptda
	try:
		psObj =photoSet.objects.get(photoSetID =ptda['id'])
		rsdata =psObj.compareRev(ptda['rev'])
	except ObjectDoesNotExist:
		rsdata['rs'] =5
	except Exception, e:
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('photoSetGet', 'all', e)
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")

@csrf_exempt		
def photoSetInit(request):
	rsdata ={'photoSetNeedToCreate':{}, 'photoSetNeedToSync':{}}
	try:
		if len(request.POST) ==0:
			ptda =json.loads(request.body)
		else:
			ptda =request.POST
		rsrow =[]
		if len(ptda['photoSetNeedToCreate']) !=0:
			for row in ptda['photoSetNeedToCreate']:
				row['userID'] =ptda['userID']
				row['date'] =datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
				row['lat'] =row['latitude']
				row['lon'] =row['longitude']
				row['loc'] =row['location']
				rsrow.append(photoSetCreateMainFunction(row))
				
			rsdata['photoSetNeedToCreate'] =rsrow
				#rsdata['photoSetNeedToCreate'] =row['localID']
		
		rsrow =[]	
		if len(ptda['photoSetNeedToSync']) !=0:
			for row in ptda['photoSetNeedToSync']:
				row['rev'] =datetime.strptime(row['rev'], '%Y-%m-%d %H:%M:%S')
				psobj =photoSet.objects.get(photoSetID =row['photoSetID'])
				rsrow.append(psobj.compareRev(row['rev']))
			rsdata['photoSetNeedToSync'] =rsrow
			
	except Exception, e:	
		rsdata ={}
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('photoSetInit', 'all', e)
	
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")	
		
		
		
# Photo Region.		-------------------------------------------------------------------
@csrf_exempt
@transaction.commit_manually()		# manually commit the transaction
def photoCreate(request):
	rsdata ={}
	ptda =getPostData('photo', request)	
	try:
		photoSetObj =photoSet.objects.get(photoSetID =ptda['photoSetID'])
		userobj =eventUser.objects.get(userID =ptda['userID'], eventID =ptda['eventID'])
		eobj =event.objects.get(eventID =ptda['eventID'])
		
		if userobj.userAcceptOrNot:
			# preparing to save photo.
			sphoto =photo(photoID =ptda['photoID'], createDate =ptda['createDate'], lon =ptda['lon'], lat =ptda['lat'], location =ptda['location'], title =ptda['title'], thumb =ptda['thumb'])
			# save photo.
			sphoto.save()
			# preparing to save photo in photoset.
			sphotoinset =photoInPhotoSet(photoSetID_id =ptda['photoSetID'], photoID_id =ptda['photoID'], eventUserID_id =userobj.id)
			# save photo in photoset.
			sphotoinset.save()
			# update event and photoset rev.
			psRev =photoSetObj.updateRev()			
			eRev =eobj.updateRev()
			if psRev[0] and eRev[0]:
				rsdata['rs'] =1
				transaction.commit()
			else:
				rsdata['rs'] =0
				rsdata['msg'] =errMsg('photoCreate', 'Update Rev', psRev[1]+eRev[1])
				transaction.rollback()
		else:
			rsdata['rs'] =2
			transaction.commit()
	except ObjectDoesNotExist:
		rsdata['rs'] =3
		transaction.commit()
	except Exception, e:
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('photoCreate', 'all', e)
		transaction.rollback()
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
	
@csrf_exempt	
def photoStatus(request):
	rsdata ={}
	try:
		phoID =photoInPhotoSet.objects.select_related().get(photoID =request.POST['photoID'])
		if phoID.eventUserID.userID ==request.POST['userID']:
			try:
				phoID.enable =request.POST['enable']
				phoID.save()
				rsdata['rs'] =1
			except Exception, e:
				rsdata['rs'] =0
				rsdata['msg'] =errMsg('photoStatus', 'save photo', e)
		else:
			rsdata['rs'] =2
	except ObjectDoesNotExist:
		rsdata['rs'] =3
	except Exception, e:
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('photoStatus', 'all', e)
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
	
	
# User Region.	-------------------------------------------------------------------
@csrf_exempt			
def userGetID(request):
	rsdata ={}

	pNum =request.POST.get('phoneNumber', 'x')
	fbid =request.POST.get('fbID', 'x')
	
	if pNum !='' and fbid !='':
	# check whether the values are blank or not.
		try:
			user =synpixUser.objects.get(Q(fbID=fbid) | Q(phoneNumber=pNum))
			form =synpixUserForm(request.POST, instance =user)
			# find the user obj, and ready to update.
			if form.is_valid():		
				# update user obj success.
				form.save()
				rsdata['rs'] =2
				rsdata['msg'] =user.userID		
			else:
				rsdata['rs'] =0
				rsdata['msg'] =errMsg("userGetID", "update User", form.errors)
				# find the user obj, but didn't ready to update.
		except ObjectDoesNotExist:	
			# didn't find the user obj.
			form =synpixUserForm(request.POST)
			
			if form.is_valid():
			# ready to create a new one.
				try:
					form.save()
					# create.
					rsdata['rs'] =1
					rsdata['msg'] =synpixUser.objects.values('userID').latest('userID')['userID']
				except Exception, e:
					rsdata['rs'] =0
					rsdata['msg'] =errMsg('getUserID', 'save Form',e)
					# create failed.
			else:
				rsdata['rs'] =0
				rsdata['msg'] =errMsg('getUserID','create Form', form.errors)
				# didn't ready the object form to create a new one.
		except Exception, e:
			rsdata['rs'] =0
			rsdata['msg'] =errMsg('getUserID', 'all', e)
	else:
		rsdata['rs'] =3
		rsdata['msg'] =errMsg('getUserID', 'Init', 'Do Not Give Me Any Blank Value.')
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
	
	
@csrf_exempt	
def userUpdate(request):
	rsdata ={}
	try:
		try:
			uObj =synpixUser.objects.get(userID =request.POST['userID'])
		except ObjectDoesNotExist:
			rsdata['rs'] =2
		form =synpixUserForm(request.POST, instance =uObj)
		if form.is_valid:
			try:
				form.save()
				rsdata['rs'] =1
				
			except Exception, e:
				rsdata['rs'] =0
				rsdata['msg'] =errMsg('userUpdate', 'save form', e)
		else:
			rsdata['rs'] =0
			rsdata['msg'] =errMsg('userUpdate', 'create form', form.errors)
	
	except Exception, e:
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('userUpdate', 'all', e)
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
	
	
# Overall Region.	-------------------------------------

@csrf_exempt	
#@transaction.commit_manually()		# manually commit the transaction
def init(request):
	i =0
	rsdata ={'EventNeedToSync':{'event':{}, 'users':{}}, 'EventNeedToCreate':{}, 'EventNeedToAccept':{}}
	ptda =json.loads(request.body)
	#ptda =getPostData(json)

	try:
		userID =ptda['userID']
		
		if len(ptda['EventNeedToCreate']) !=0:
			# declare multi ecreateDateta.
			multiEcreateDateta ={}
			
			# create event.
			try:
				for row in ptda['EventNeedToCreate']:
					# declare event create data.
					ecreateDateta ={}
					row['userID'] =userID
					ecreateDateta =eventCreateFunction(row)
					ecreateDateta['localID'] =row['localID']
					
					if ecreateDateta['rs'] ==1:
						#transaction.commit()
						pass
					else:
						#transaction.rollback()
						pass
					# put every ecreateDateta into multiEcreateDateta.
					multiEcreateDateta[i] =ecreateDateta
					i +=1
				rsdata['EventNeedToCreate'] =multiEcreateDateta
			except Exception, e:
				rsdata['EventNeedToCreate']['rs'] =0
				rsdata['EventNeedToCreate']['msg'] =errMsg('init', 'EventNeedToSync', e)
				
		i =0
		if len(ptda['EventNeedToSync']) !=0:	
			# event, compare client and server rev.
			multiData ={}	# multi eventData in this dictionary.
			try:
				for evn in ptda['EventNeedToSync']:
					# declare a new data dictionary.
					eventData ={}	
					
					eObj =event.objects.get(eventID =evn['eventID'])
					rs =eObj.compareRev(evn['rev'])
					if rs ==1:		# need sync
						eObj =event.objects.values().get(eventID =evn['eventID'])
						eventData['rs'] =rs
						eventData['msg'] =eObj
					elif rs ==3:	# new version, update the event attribute.
						eventData['eventID'] =evn['eventID']
						form =eventForm(evn, instance =eObj)
						if form.is_valid:
							try:
								form.save()
								eventData['rs'] =rs
							except Exception, e:
								eventData['rs'] =0
								eventData['msg'] =errMsg('init', 'EventNeedToSync: update event obj', e)
						else:
							eventData['rs'] =0
							eventData['msg'] =errMsg('init', 'EventNeedToSync: create update event form', e)
					elif rs ==2:	# synced
						eventData['rs'] =rs
					# put every execute result into multiData. 
					multiData[i] =eventData
					i +=1
				# put multiData into rsdata['event'].
				rsdata['EventNeedToSync'] =multiData
			except Exception, e:
				rsdata['EventNeedToSync']['rs'] =0
				rsdata['EventNeedToSync']['msg'] =errMsg('init', 'EventNeedToSync', e)
		else:
		# event, select all user event.
			try:
				eventID ={}
				
				euo =eventUser.objects.values('eventID', 'userPermissionID').filter(userID =ptda['userID'], userAcceptOrNot =True, enable =True)
				for tmp in euo:
					eventID[i] =tmp
					i +=1
				evnt =event.objects.values().filter(eventID__in =eventID)
				euo =eventUser.objects.values('userID', 'eventID', 'userPermissionID').select_related('synpixUser').filter(eventID__in =eventID)
				
				rsdata['EventNeedToSync']['event'] =list(evnt)
				rsdata['EventNeedToSync']['users'] =list(euo)
			except Exception, e:
				rsdata['EventNeedToSync']['rs'] =0
				rsdata['EventNeedToSync']['msg'] =errMsg('init', 'EventNeedToSync', e)
				
				
		# eventUser
		try:
			i =0
			eventID ={}
			rs ={'event' :{}, 'userInEvent' :{}, 'needToAccept' :{}}
			# filter the event need to accept.
			eu =eventUser.objects.values().filter(userID =userID, userAcceptOrNot =False, userReadedOrNot =False)
			# insert all the eventID into list, for later data filter.
			for eo in eu:
				eventID[i] =eo['eventID_id']
				i +=1
			# filter all the user where events of user.
			evnUser =eventUser.objects.values().select_related('synpixUser').filter(eventID__in =eventID)
			# filter all the event info which user need to accept.
			evnObj =event.objects.values().filter(eventID__in =eventID)
			
			# Give the execute result into rs['EventNeedToAccept'].
			rs['userInEvent'] =list(evnUser)
			rs['needToAccept'] =list(eu)
			
			rsdata['EventNeedToAccept'] =rs
		except Exception, e:
			rsdata['rs'] =0
			rsdata['msg'] =errMsg('init', 'EventNeedToAccept', e)
	except Exception, e:
		rsdata ={'rs' :0, 'msg' :errMsg('init', 'all', e)}
		
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
	
	
@csrf_exempt
def versionGet(request):
	rsdata ={}
	
	try:
		sessionRs =sessionRegisterFunction(request)
		version =content.objects.values('contentTitle', 'content').filter(contentType =4)[0:1]#.latest('contentCreate')
		rsdata['rs'] =1
		rsdata['ver'] =version[0]['contentTitle']
		rsdata['msg'] =version[0]['content']
		rsdata['session'] =sessionRs
	
	except Exception, e:
		rsdata['rs'] =0
		rsdata['msg'] =errMsg('versionGet', 'all', e)
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")


@csrf_exempt	
def sessionRegister(request):
	rsdata ={}
	sessRs =sessionRegisterFunction(request)
	rsdata['rs'] =sessRs
	return HttpResponse(json.dumps(rsdata, cls =DjangoJSONEncoder), content_type ="application/json")
	