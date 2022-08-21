from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime


User._meta.get_field("email")._unique = True


STORAGE_CHOICES = (
    ("C", "Cemetery"),
    ("CO", "Columbarium"),
)

Status = (
    ("P", "Pending"),
    ("Ca", "Cancelled"),
    ("C", "Completed"),
    ("Pa", "Paid"),
    ("O", "Ongoing"),
    ("NT", "Not taken"),
    ("NA", "Did Not Avail"),
    ("NP", "Not Paid"),
    ("OV", "Overdue"),
)

cemeteries = (
    ("MN", "Manila North"),
    ("MS", "Manila South"),
    ("L", "La Loma"),
    ("MC", "Manila Chinese"),
)

flower_shops = (
    ("CF", "Citfora Flowers"),
    ("GF", "Gertudes Flowershop"),
    ("RG", "Raphael's Gifts"),
    ("LR", "La Rose"),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=60)
    phone = PhoneNumberField()

    def __str__(self):
        return f"{self.user.username} Profile"


class CareTaker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField()
    cemetery = models.CharField(max_length=2, choices=cemeteries)

    def __str__(self):
        return f"{self.user.username} Profile"


class MasterData_Revised(models.Model):
    uid = models.CharField(max_length=50, unique=True)
    place = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    first_name = models.CharField(max_length=60)
    middle_name = models.CharField(max_length=60)
    birthdate = models.DateField(blank=True)
    category = models.CharField(max_length=2, choices=STORAGE_CHOICES)
    blk = models.CharField(max_length=3)
    street = models.CharField(max_length=12)
    lot = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.uid}"


class User_Place(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uid = models.ForeignKey(
        MasterData_Revised,
        to_field="uid",
        db_column="uid",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.uid}"


class Order_User(models.Model):
    profile_dead = models.ForeignKey(User_Place, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=Status)
    gravesite_status = models.CharField(max_length=2, choices=Status, default="NA")
    floral_status = models.CharField(max_length=2, choices=Status, default="NA")
    prayer_status = models.CharField(max_length=2, choices=Status, default="NA")
    price = models.CharField(max_length=15)
    gravesite_service = models.CharField(max_length=1200, blank=True)
    floral_service = models.CharField(max_length=1200, blank=True)
    prayer_service = models.CharField(max_length=1200, blank=True)
    flower_shop = models.CharField(max_length=2, choices=flower_shops, blank=True)
    note = models.CharField(max_length=180, blank=True)
    order_date = models.DateTimeField(default=datetime.now, blank=True)
    before_gravesite_image = models.ImageField(
        upload_to="image", blank=True, default="image/default_client.png"
    )
    after_gravesite_image = models.ImageField(
        upload_to="image", blank=True, default="image/default_client.png"
    )
    floral_image = models.ImageField(
        upload_to="image", blank=True, default="image/default_client.png"
    )
    prayer_link = models.CharField(
        max_length=1200,
        blank=True,
        # default="This section is gonna be updated once the link is provided.",
    )
    ctime = models.DateTimeField(auto_now_add=True)
    uptime = models.DateTimeField(auto_now=True)


class Caretaker_Task(models.Model):
    caretaker = models.ForeignKey(
        CareTaker, on_delete=models.SET_NULL, blank=True, null=True
    )
    order = models.ForeignKey(Order_User, on_delete=models.CASCADE)


class FlowerTaker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField()
    flower_shops = models.CharField(max_length=2, choices=flower_shops, unique=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class FlowerTaker_Task(models.Model):
    flower_taker = models.ForeignKey(
        FlowerTaker, on_delete=models.SET_NULL, blank=True, null=True
    )
    order = models.ForeignKey(Order_User, on_delete=models.CASCADE)


class FlowerShopItems(models.Model):
    flower_taker = models.ForeignKey(
        FlowerTaker, on_delete=models.SET_NULL, blank=True, null=True
    )
    flower_name = models.CharField(max_length=150)
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=150)
    image = models.ImageField(
        upload_to="image", blank=True, default="image/upload_default_flower.png"
    )


class Prayer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField()
    cemetery = models.CharField(max_length=2, choices=cemeteries)

    def __str__(self):
        return f"{self.user.username} Profile"


class Prayer_Task(models.Model):
    prayer = models.ForeignKey(Prayer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order_User, on_delete=models.CASCADE)
