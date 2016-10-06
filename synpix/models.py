from django.db import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserChangeForm
from django.contrib.contenttypes.models import ContentType

from datetime import datetime
from django.core import serializers
from django.utils.timezone import utc

from synpix.globalFunctions import errMsg

class contentCategory(models.Model):				# content type table, can save all content type info.
	ccID =models.AutoField(primary_key =True)
	ccName =models.CharField(max_length =30)
	ccModel =models.CharField(max_length =30, db_index =True)
	ccRemark =models.CharField(max_length =50, db_index =True)
	
	def __unicode__(self):
		return self.ccModel+'.'+self.ccName
		
class content(models.Model):					# content table, can save some info.
	contentType =models.ForeignKey(contentCategory, db_index =True)
	contentTitle =models.CharField(max_length =50)
	content =models.TextField()
	contentRemark =models.CharField(max_length =50, blank =True, null =True)
	contentCreate =models.DateTimeField(auto_now_add =True)
	contentModified =models.DateTimeField(auto_now =True)
	
	def __unicode__(self):
		return self.contentTitle
	
	class Meta:
		ordering =['-contentModified']
	
class event(models.Model):						# event table
	eventID =models.AutoField(primary_key =True)
	createDate =models.DateTimeField()
	startDate =models.DateTimeField()
	endDate =models.DateTimeField()
	eventType =models.ForeignKey(contentCategory)
	title =models.CharField(max_length =50)
	rev =models.DateTimeField(db_index =True)
	
	def updateRev(self):			# update rev to now.
		try:
			newRev =datetime.utcnow().replace(tzinfo=utc).strftime('%Y-%m-%d %H:%M:%S')
			self.rev =newRev
			self.save()
			return [True, ]
		except Exception, e:
			return [False, e]
		
	def compareRev(self, rev):
		rev =str(rev)
		clientRev =datetime.strptime(rev, '%Y-%m-%d %H:%M:%S')
		if self.rev >clientRev:	# need sync
			rs =1
		elif self.rev <clientRev:	# new version
			rs =3
		elif self.rev ==clientRev: 	# synced
			rs =2
		return rs
	
	def __unicode__(self):
		return self.eventID

class photoSet(models.Model):					# photo set table 
	photoSetID =models.AutoField(primary_key =True)
	eventID =models.ForeignKey(event, db_index =True)
	createDate =models.DateTimeField(db_index =True) 			
	title =models.CharField(max_length =50, null =True, blank =True)
	location =models.CharField(max_length =150)
	lat =models.CharField(max_length =10, null =True, db_index =True)
	lon =models.CharField(max_length =10, null =True, db_index =True)
	rev =models.DateTimeField(db_index =True)
	
	def updateRev(self):			# update rev to now.
		try:
			newRev =datetime.utcnow().replace(tzinfo=utc).strftime('%Y-%m-%d %H:%M:%S')
			self.rev =newRev
			self.save()
			return [True, ]
		except Exception, e:
			return [False, e]
	
	def compareRev(self, rev):
		rs ={}
		rev =str(rev)
		clientRev =datetime.strptime(rev, '%Y-%m-%d %H:%M:%S')
		if self.rev >clientRev:	# need sync, server>client, server newer than client.
			try:
				phoID =photoInPhotoSet.objects.values('photoID').filter(photoSetID =self.photoSetID, enable =True)
				phoObj =photo.objects.values().filter(photoID__in =phoID)
				rs['rs'] =1
				rs['rev'] =str(psObj.rev)
				rs['msg'] =list(phoObj)
			except Exception, e:
				rs['rs'] =0
				rs['msg'] =errMsg('compareRev', 'select photoID',e)
				
		elif self.rev <clientRev:	# new version, server<client, client newer than server.
			rs['rs'] =3
		elif self.rev ==clientRev: 	# synced, same.
			rs['rs'] =2
		return rs
		
	def __unicode__(self):
		return self.photoSetID
		
class photo(models.Model):						# photo table
	photoID =models.CharField(max_length =50, primary_key =True)
	title =models.CharField(max_length =100, null =True)
	thumb =models.CharField(max_length =40, null =True)
	location =models.CharField(max_length =150, null =True)
	lat =models.CharField(max_length =10, null =True)
	lon =models.CharField(max_length =10, null =True)
	createDate =models.DateTimeField()
	
	def disable_photo(self):
		try:
			self.enable =False
			self.save()
			return [True, ]
		except Exception, e:
			return [False, e]
			
	def __unicode__(self):
		return self.photoID

class synpixUser(models.Model):					# service user object	
	userID =models.AutoField(primary_key =True)
	authUser =models.OneToOneField(User, blank =True, null =True)
	name =models.CharField(max_length =10)
	fbID =models.CharField(max_length =30, null =True, blank =True, db_index =True)
	phoneNumber =models.CharField(max_length =20, null =True, blank =True, db_index =True)
	headPhotoID =models.ForeignKey(photo, blank =True, null =True)

	class Meta:
		unique_together = ("fbID", "phoneNumber")
	
	def __unicode__(self):
		return self.userID
	
class eventUser(models.Model):					# who can access this event.
	eventID =models.ForeignKey(event, db_index =True)
	userID =models.ForeignKey(synpixUser, db_index =True)
	userPermissionID =models.ForeignKey(contentCategory, db_index =True)	
	userReadedOrNot =models.BooleanField(default =False, db_index =True)
	userAcceptOrNot =models.BooleanField(default =False, db_index =True)
	enable =models.BooleanField(default =True, db_index =True)
	
	def make_status(self, alternative):
		try:
			self.enable =alternative
			self.save()
			effRow =photoInPhotoSet.objects.filter(eventUserID =self.id).update(enable =False)
			return [True,]
		except Exception, e:
			return [False, e]
			
	def make_accept(self, alternative):
		try:	
			self.userReadedOrNot =True
			self.userAcceptOrNot =alternative
			self.save()
			return [True,]
		except Exception, e:
			return [False, e]
			
	def __unicode__(self):
		return self.id

class photoInPhotoSet(models.Model):				# photo relationship with photo set
	photoSetID =models.ForeignKey(photoSet, db_index =True)
	photoID =models.ForeignKey(photo, db_index =True)
	eventUserID =models.ForeignKey(eventUser, db_index =True)
	enable =models.BooleanField(default =True, db_index =True)
	
	def __unicode__(self):
		return self.id

class synpixSession(models.Model):
	userID =models.ForeignKey(synpixUser, db_index =True)
	session =models.CharField(max_length =70, db_index =True)
	csrfCookie =models.CharField(max_length =70, db_index =True)
	userAgent =models.CharField(max_length =70)
	deadline =models.DateTimeField()
				
	def check_alive(self):
		rs =False
		now =datetime.utcnow().replace(tzinfo=utc).strftime('%Y-%m-%d %H:%M:%S')
		if self.deadline >=now:
		# alive
			rs =True
		else:
		# dead
			rs =False
		return rs
		
	def __unicode__(self):
		return self.deadline
	
	
