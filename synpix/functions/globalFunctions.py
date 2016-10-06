import json
from pytz import timezone
from datetime import datetime

'''
Functions of PhotoSet.
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
		rs['eid'] =data.get('eventID', 0)
		rs['uid'] =data.get('userID', 0)
		rs['date'] =datetime.strptime(data.get('date', '0001-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
		rs['loc'] =data.get('location', '')
		rs['lon'] =data.get('longtitude', '')
		rs['lat'] =data.get('latitude', '')
		rs['title'] =data.get('title', '')
		rs['rev'] =datetime.strptime(data.get('rev', '0001-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
	
	elif catagory =='event':
		rs['id'] =data.get('eventID', 0)	
		rs['uid'] =data.get('userID', 0)
		rs['createDate'] =datetime.strptime(data.get('createDate', '0001-01-01'), '%Y-%m-%d')
		rs['startDate'] =datetime.strptime(data.get('startDate', '0001-01-01'), '%Y-%m-%d')
		rs['endDate'] =datetime.strptime(data.get('endDate', '0001-01-01'), '%Y-%m-%d')
		rs['title'] =data.get('title', '')
		rs['rev'] =datetime.strptime(data.get('rev', ''), '%Y-%m-%d %H:%M:%S')
		rs['eventType'] =data.get('eventType', 0)
		rs['userPermissionID'] =data.get('userPermissionID', 0)
	elif catagory =='eventInvite':
		i =0
		eid =data.get('eventID',0)
		act =data.get('accessToken', '')
		fri =data.getlist('friend')
		for friRow in fri:
			rs[i]['eventID'] =rs['eid']									# eventID
			rs[i]['userPermissionID'] =data.get(['userPermissionID'], 0)		# userPermissionID
			rs[i]['accessToken'] =act	
			fid =data.get(friRow['userID'], 0)
			fbid =data.get(friRow['fbID'], '')
			fphone =data.get(friRow['phone'], '')
			# choosing the available  value.
			# print fid
			# print fbid
			# print fphone
			if fid !=0:
				rs[i]['userID'] =fid										# userID
			elif fbid !='':
				rs[i]['fbID'] =fbid
			elif fphone !='':
				rs[i]['phone'] =fphone
			i =i+1
			
		# rs ={[0, userID, eid, uid, fbID, phone], [1, userID, eid, uid, fbID, phone]}	
		
	return rs
	
	
def errMsg(funcName, action, errMsg):
	return "[synpix.views, %s](%s):\t%s" %(funcName, action, str(errMsg))
		
	