import json
import hashlib
from pytz import timezone
from datetime import datetime
from datetime import timedelta 
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist



'''
Functions of Global.
Created By Matrix in 2013.	(matrix0415@gmail.com)
'''

	
def getPostData(catagory, req):
	rs ={}
	# Load HTML Form or JSON, Load JSON in json.loads
	if len(req.POST) ==0:
		data =json.loads(req.body)
	else:
		data =req.POST
	
	if catagory =='photo':
		rs['userID'] =data.get('userID', 0)
		rs['eventID'] =data.get('eventID', 0)
		rs['photoSetID'] =data.get('photoSetID', 0)
		rs['photoID'] =data.get('photoID', '')
		rs['createDate'] =datetime.strptime(data.get('createDate', '0001-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
		rs['location'] =data.get('location', '')
		rs['lon'] =data.get('longtitude', '')
		rs['lat'] =data.get('latitude', '')
		rs['title'] =data.get('title', '')
		rs['thumb'] =data.get('thumb', '')
	
	elif catagory =='photoset':	
		rs['id'] =data.get('photoSetID', 0)
		rs['id'] =data.get('id', 0)
		rs['eventID'] =data.get('eventID', 0)
		rs['userID'] =data.get('userID', 0)
		rs['date'] =datetime.strptime(data.get('date', '0001-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
		rs['loc'] =data.get('location', '')
		rs['lon'] =data.get('longtitude', '')
		rs['lat'] =data.get('latitude', '')
		rs['title'] =data.get('title', '')
		rs['rev'] =datetime.strptime(data.get('rev', '0001-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
	
	elif catagory =='eventInvite':
		i =0
		row =[]
		eventID =data.get('eventID',0)
		act =data.get('accessToken', '')
		fri =data.get('friend')
		userID =data.get('userID', 0)
		rs['userID'] =userID
		rs['eventID'] =eventID
		for friRow in fri:
			fdata ={}
			fdata['eventID'] =eventID								# eventID
			fdata['userPermissionID'] =data.get('userPermissionID', 0)		# userPermissionID
			fdata['accessToken'] =act
			if friRow.has_key('userID'):
				fdata['userID'] =data.get(fri[i]['userID'], 0)
			elif friRow.has_key('fbID'):
				fdata['fbID'] =data.get(fri[i]['fbID'], '')
			elif friRow.has_key('phone'):
				fdata['phone'] =data.get(fri[i]['phone'], '')
			row.append(fdata)
			i =i+1
		rs['friend'] =row 
		
		# rs ={[0, userID, eventID, userID, fbID, phone], [1, userID, eventID, userID, fbID, phone]}	
	elif catagory =='event':
		rs['id'] =data.get('eventID', 0)	
		rs['userID'] =data.get('userID', 0)
		rs['createDate'] =datetime.strptime(data.get('createDate', '0001-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
		rs['startDate'] =datetime.strptime(data.get('startDate', '0001-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
		rs['endDate'] =datetime.strptime(data.get('endDate', '0001-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
		rs['title'] =data.get('title', '')
		rs['rev'] =datetime.strptime(data.get('rev', ''), '%Y-%m-%d %H:%M:%S')
		rs['eventType'] =data.get('eventType', 0)
		rs['userPermissionID'] =data.get('userPermissionID', 0)
		
	return rs
	
	
def errMsg(funcName, action, errMsg):
	return "[synpix.views, %s](%s):%s" %(funcName, action, str(errMsg))
		


# Session Region--------------------------

def sessionIdentifyFunction(req):
	rs =False
	
	if len(req.POST) ==0:
		data =json.loads(req.body)
	else:
		data =req.POST
		
	sess =synpixSession.objects.get(userID_id =data['userID'], session =data['session'], csrfCookie =req['CSRF_COOKIE'])
	rs =sess.check_alive()	# alive or dead
	
	return rs		
	
def sessionRegisterFunction(req):
	from synpix.models import synpixUser
	
	rs ={}
	try:
		if len(req.POST) ==0:
			data =json.loads(req.body)
		else:
			data =req.POST
			
		m = hashlib.md5()
		m.update('---|'+data['userID']+'|'+data['token']+'|---')
		local =m.hexdigest()
		userO =synpixUser.objects.get(userID =data['userID'])
		if local ==data['session']:
			deadline =datetime.utcnow().replace(tzinfo=utc).strftime('%Y-%m-%d %H:%M:%S')+timedelta(minutes =15)
			sess =synpixSession(userID =userO, session =data['session'], csrfCookie =req['CSRF_COOKIE'], userAgent =req['HTTP_USER_AGENT'], deadline =deadline)
			sess.save()
			rs =1
		else:
		# session err when register.
			rs =2
	except ObjectDoesNotExist:
	# User Does Not Exist
		rs =3
	except Exception, e:
		rs['rs'] =0
		rs['msg'] =str(e)
	return rs
	

	