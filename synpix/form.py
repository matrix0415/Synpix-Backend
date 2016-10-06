from synpix.models import *
from django.forms import ModelForm


class contentCategoryForm(ModelForm):
	class Meta:
		model =contentCategory

class eventForm(ModelForm):
	class Meta:
		model =event
		
class photoSetForm(ModelForm):
	class Meta:
		model =photoSet
		
class photoForm(ModelForm):
	class Meta:
		model =photo

class synpixUserForm(ModelForm):
	class Meta:
		model =synpixUser

class eventUserForm(ModelForm):
	class Meta:
		model =eventUser
'''
class photoInPhotoSet(ModelForm):
	class Meta:
		model =photoSetUserRelation
'''		
	