from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O','Others'),
    )
STORAGE_CHOICES=(
("C", "Cemetery"),
("CO", "Columbarium"),
)

Status=(
("P", "Pending"),
("R", "Returned"),
("C", "Completed"),
("Pa", "Paid"),
("O","Ongoing")
)


class Profile(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES) 
	phone = PhoneNumberField()
	def __str__(self):
		return f'{self.user.username} Profile'


class MasterData_Revised(models.Model):
	uid = models.CharField(max_length=50, unique=True)
	place = models.CharField(max_length=60)
	last_name = models.CharField(max_length=60)
	first_name = models.CharField(max_length=60)
	middle_name = models.CharField(max_length=60)
	category = models.CharField(max_length=2, choices=STORAGE_CHOICES) 
	blk = models.CharField(max_length=3)
	street = models.CharField(max_length=12)
	lot = models.CharField(max_length=3)
	def __str__(self):
		return f'{self.uid}'


class User_Place(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	uid = models.ForeignKey(MasterData_Revised,to_field="uid", db_column="uid" ,on_delete=models.CASCADE)
	def __str__(self):
		return f'{self.uid}'


class Order_User(models.Model):
	profile_dead = models.ForeignKey(User_Place, on_delete=models.CASCADE)
	status = models.CharField(max_length=2, choices=Status)
	price = models.CharField(max_length=15)
	services = models.CharField(max_length=15)
	ctime = models.DateTimeField(auto_now_add=True)
	uptime = models.DateTimeField(auto_now=True)







