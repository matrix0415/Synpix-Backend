from synpix.models import *
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

class SynpixUserInline(admin.StackedInline):
	model =synpixUser
	can_delete =False
	max_num =1
	verbose_name_plural ='Synpix Setting'
	
class SynpixUserAdmin(UserAdmin):
	inlines =(SynpixUserInline, )

class SynpixEventAdmin(admin.ModelAdmin):
	pass

class SynpixEventUserAdmin(admin.ModelAdmin):
	pass
	
class SynpixPhotoSetAdmin(admin.ModelAdmin):
	pass
	
class SynpixPhotoAdmin(admin.ModelAdmin):
	pass
	
class SynpixPhotoInPhotoSetAdmin(admin.ModelAdmin):
	pass

class SynpixContentCategoryAdmin(admin.ModelAdmin):
	list_display =('ccID','ccName', 'ccModel', 'ccRemark')
	
class SynpixContentAdmin(admin.ModelAdmin):
	list_display =('id', 'contentTitle', 'contentType', 'contentRemark','contentCreate', 'contentModified')
	
	
admin.site.unregister(User)
admin.site.register(User, SynpixUserAdmin)
admin.site.register(event, SynpixEventAdmin)
admin.site.register(photoSet, SynpixPhotoSetAdmin)
admin.site.register(photo, SynpixPhotoAdmin)
admin.site.register(photoInPhotoSet, SynpixPhotoInPhotoSetAdmin)
admin.site.register(contentCategory, SynpixContentCategoryAdmin)
admin.site.register(content, SynpixContentAdmin)
