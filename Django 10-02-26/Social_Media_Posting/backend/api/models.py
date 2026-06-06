from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

#---------------- AI Image ----------------#
#------------------------------------------#
class AIImage(models.Model):
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='ai_generated/')
    created_at = models.DateTimeField(auto_now_add=True)

#-------------- Custom User ----------------#
#-------------------------------------------#
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("SuperAdmin", "SuperAdmin"),
        ("Admin", "Admin"),
        ("User", "User"),
    )

    name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="User"
    )

    def __str__(self):
        return self.email


    def __str__(self):
        return self.email

    
#----------------- Product ------------------#
#--------------------------------------------#
class Product(models.Model):
    name = models.CharField(max_length=40)
    price = models.FloatField()
    quantity = models.IntegerField()
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


#------------- Email Automation -------------#
#--------------------------------------------#
class EmailAutomationAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_automation_account",
    )
    email = models.EmailField()
    app_password = models.CharField(max_length=255)
    is_reading = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} email automation"



#------------------ Admin -------------------#
#--------------------------------------------#
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AIImage, EmailAutomationAccount

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # This controls which columns show up in the user list
    list_display = ('email', 'name', 'is_staff', 'is_active')
    
    # This ensures the "Edit User" page includes your custom fields
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('name', 'phone', 'profile_image')}),
    )
    
    # This ensures the "Add User" page includes your custom fields
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('name', 'email', 'phone', 'profile_image')}),
    )

# Don't forget to register your AIImage model too!
admin.site.register(AIImage)
admin.site.register(EmailAutomationAccount)
