from re import X
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import (
    CreateUserForm,
    ProfileForm,
    Order_UserForm,
    EventForm,
)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .decorators import unathenticated_user, allowed_users
from django.contrib.auth.models import Group
from .models import (
    FlowerTaker_Task,
    Prayer,
    Prayer_Task,
    Profile,
    User_Place,
    MasterData_Revised,
    CareTaker,
    Order_User,
    Caretaker_Task,
    FlowerShopItems,
    FlowerTaker,
)
from .resources import MasterData_RevisedResource
from django.core.exceptions import ObjectDoesNotExist
import sweetify
from django.core.mail import send_mail, BadHeaderError
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from lapida.settings import EMAIL_HOST_USER
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
import datetime
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from .serializer import FlowerShopItemsSerializer


def index(request):
    if request.user.is_authenticated:
        group = request.user.groups.all()[0].name
        if "caretaker" in group:
            return redirect("dashboard")
        elif "flowershop" in group:
            return redirect("flowershop_dashboard")
        elif "prayer" in group:
            return redirect("prayer_dashboard")
    return render(request, "lapida_app/index.html")


@unathenticated_user
def loginPage(request):
    message_error = ""
    message_error_1 = ""
    if request.user.is_authenticated:
        return redirect("home-view")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("home-view")
                else:
                    message_error_1 = None
                    sweetify.error(
                        request,
                        "Your account is not activated yet please check your email for the verification link",
                        persistent=":(",
                    )
            else:
                message_error = messages.info(
                    request, "Username or Password is incorrect"
                )
                message_error_1 = "Username or Password is incorrect"
        context = {"message_error": message_error_1}
        return render(request, "lapida_app/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


@unathenticated_user
def register(request):
    if request.user.is_authenticated:
        return redirect("home-view")
    else:
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            form_1 = ProfileForm(request.POST)
            gender = request.POST.get("gender")
            form_1.gender = gender
            if form.is_valid() and form_1.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                form_1 = form_1.save(commit=False)
                group = Group.objects.get(name="customer")
                user.groups.add(group)
                form_1.user = user
                form_1.save()
                current_site = get_current_site(request)
                mail_subject = "Activate your account."
                message = render_to_string(
                    "lapida_app/verification.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": account_activation_token.make_token(user),
                    },
                )
                to_email = form.cleaned_data.get("email")
                send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
                message_error_1 = None
                sweetify.error(
                    request,
                    "You need to verify your account via email that we sent in order to login.",
                    persistent=":)",
                )
                context = {"message_error": message_error_1}
                return render(request, "lapida_app/login.html", context)
                # # Auto login and once authenticated then redirect to register dead page
                # user = authenticate(
                #     request,
                #     username=form.cleaned_data["username"],
                #     password=form.cleaned_data["password1"],
                # )
                # if user is not None:
                #     login(request, user)
                #     return redirect("create-dead")
        else:
            form = CreateUserForm()
            form_1 = ProfileForm()
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
        context = {"form": form, "form_1": form_1}
        return render(request, "lapida_app/register.html", context)


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        message_error_1 = None
        user.save()
        sweetify.error(
            request,
            "Your account is activated go log in your account now!",
            persistent=":)",
        )
        context = {"message_error": message_error_1}
        return render(request, "lapida_app/login.html", context)
    else:
        return HttpResponse("Activation link is invalid!")


@login_required(login_url="login")
def create_dead(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cemetery = request.POST.get("cemetery")
        dead_profile = []
        query_results = User_Place.objects.filter(user=request.user)
        for dead in query_results:
            dead_profile.append(MasterData_Revised.objects.get(uid=dead))
        try:
            person = MasterData_Revised.objects.get(
                place=cemetery,
                first_name=form.cleaned_data.get("first_name"),
                middle_name=form.cleaned_data.get("middle_name"),
                last_name=form.cleaned_data.get("last_name"),
                birthdate=form.cleaned_data.get("birth_date"),
            )
            if person in dead_profile:
                sweetify.error(
                    request,
                    "The person you inputted is already registered to your account.",
                    persistent=":(",
                )
                return redirect("create-dead")
        except MasterData_Revised.DoesNotExist:
            sweetify.error(
                request,
                "The person you inputted was not found in our database please try again.",
                persistent=":(",
            )
            return redirect("create-dead")
        instance = User_Place(uid=person)
        instance.user = request.user
        instance.save()
        return redirect("profile")
    else:
        form = EventForm()
    context = {"form": form}
    return render(request, "lapida_app/register_dead.html", context)


@allowed_users(allowed_roles=["caretaker"])
@login_required(login_url="login")
def dashboard(request):
    caretaker_profile = CareTaker.objects.get(user=request.user)
    caretaker_task = Caretaker_Task.objects.filter(caretaker=caretaker_profile)
    tasks = []
    for task in caretaker_task:
        if Order_User.objects.get(caretaker_task=task).gravesite_status not in (
            "NP",
            "NA",
        ):
            tasks.append(Order_User.objects.get(caretaker_task=task))
    caretaker_task_none = Caretaker_Task.objects.filter(caretaker=None)
    for task in caretaker_task_none:
        if Order_User.objects.get(caretaker_task=task).gravesite_status not in (
            "NP",
            "NA",
        ):
            tasks.append(Order_User.objects.get(caretaker_task=task))
    context = {"form": tasks}
    return render(request, "lapida_app/dashboard.html", context)


@allowed_users(allowed_roles=["prayer"])
@login_required(login_url="login")
def prayer_dashboard(request):
    prayer_profile = Prayer.objects.get(user=request.user)
    prayer_task = Prayer_Task.objects.filter(prayer=prayer_profile)
    tasks = []
    for task in prayer_task:
        if Order_User.objects.get(prayer_task=task).prayer_status not in (
            "NP",
            "NA",
        ):
            tasks.append(Order_User.objects.get(prayer_task=task))
    prayer_task_none = Prayer_Task.objects.filter(prayer=None)
    for task in prayer_task_none:
        if Order_User.objects.get(prayer_task=task).prayer_status not in (
            "NP",
            "NA",
        ):
            tasks.append(Order_User.objects.get(prayer_task=task))
    context = {"form": tasks}
    return render(request, "lapida_app/dashboard_prayer.html", context)


@allowed_users(allowed_roles=["flowershop"])
@login_required(login_url="login")
def flowershop_dashboard(request):
    flower_taker_profile = FlowerTaker.objects.get(user=request.user)
    flower_taker_task = FlowerTaker_Task.objects.filter(
        flower_taker=flower_taker_profile
    )
    tasks = []
    for task in flower_taker_task:
        if task.order.floral_status not in ("Ca", "NP"):
            tasks.append(task.order)
    context = {"form": tasks}
    return render(request, "lapida_app/dashboard_flowershop.html", context)


@allowed_users(allowed_roles=["flowershop"])
@login_required(login_url="login")
def create_new_flower(request):
    context = {"new_item": True}
    serializer_class = FlowerShopItemsSerializer
    if request.method == "POST":
        data = dict(request.POST.items())
        data.pop("csrfmiddlewaretoken")
        data["price"] = int(data["price"])
        serializer = serializer_class(data=data)
        if serializer.is_valid():
            flower_name = serializer.data.get("flower_name")
            price = serializer.data.get("price")
            description = serializer.data.get("description")
            flower_taker_profile = FlowerTaker.objects.get(user=request.user)
            flower = FlowerShopItems(
                flower_taker=flower_taker_profile,
                flower_name=flower_name,
                price=price,
                description=description,
            )
            flower.image = (
                request.FILES["image"]
                if request.FILES.get("image") is not None
                else "image/upload_default_flower.png"
            )
            flower.save()
            return redirect("flowershop_items")
    return render(request, "lapida_app/create_new_flower.html", context)


@allowed_users(allowed_roles=["flowershop"])
@login_required(login_url="login")
def edit_flower(request, id):
    flower_item = FlowerShopItems.objects.get(id=id)
    flower_item.new_item = False
    context = {"flower_item": flower_item, "new_item": False}
    if request.method == "POST":
        serializer_class = FlowerShopItemsSerializer
        data = dict(request.POST.items())
        data.pop("csrfmiddlewaretoken")
        data["price"] = int(data["price"])
        serializer = serializer_class(data=data)
        if serializer.is_valid():
            flower_name = serializer.data.get("flower_name")
            price = serializer.data.get("price")
            description = serializer.data.get("description")
            flower_item.flower_name = flower_name
            flower_item.price = price
            flower_item.description = description
            if request.FILES.get("image"):
                flower_item.image = request.FILES["image"]
            flower_item.save()
            return redirect("flowershop_items")
    return render(request, "lapida_app/create_new_flower.html", context)


@allowed_users(allowed_roles=["flowershop"])
@login_required(login_url="login")
def flowershop_items(request):
    flowertaker_profile = FlowerTaker.objects.get(user=request.user)
    flowertaker_items = FlowerShopItems.objects.filter(flower_taker=flowertaker_profile)
    items = []
    for item in flowertaker_items:
        items.append(item)
    context = {"form": items}
    return render(request, "lapida_app/flowershop_items.html", context)


def creating_order_tasks(instance, services_dict):
    # Creating Caretaker Task
    if services_dict["gravesite_service"]:
        profile_dead = MasterData_Revised.objects.get(uid=instance.profile_dead.uid)
        dead_place = get_cemetery(profile_dead.place)
        caretaker_profile = CareTaker.objects.filter(cemetery=dead_place)
        caretaker_p = []
        for i in caretaker_profile:
            caretaker_p.append(i)
        caretaker_task_instance = Caretaker_Task(caretaker=None)
        # User = get_user_model()
        # user = User.objects.get(pk=caretaker_p[0].user.id)
        # user_email = user.email
        # current_site = get_current_site(request)
        # mail_subject = "New Task"
        # message = render_to_string(
        #     "lapida_app/verification.html",
        #     {
        #         "user": user,
        #         "domain": current_site.domain,
        #         "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        #         "token": account_activation_token.make_token(user),
        #     },
        # )
        # to_email = user_email
        # send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
        caretaker_task_instance.order = instance
        caretaker_task_instance.save()
        instance.gravesite_status = "NP"

    # Creating FlowerTaker Tasks
    if services_dict["floral_service"]:
        flower_taker_profile = FlowerTaker.objects.get(
            flower_shops=instance.flower_shop
        )
        flower_taker_task_instance = FlowerTaker_Task(flower_taker=flower_taker_profile)
        flower_taker_task_instance.order = instance
        flower_taker_task_instance.save()
        instance.floral_status = "NP"
    # Creating PrayerTaker Tasks
    if services_dict["prayer_service"]:
        profile_dead = MasterData_Revised.objects.get(uid=instance.profile_dead.uid)
        dead_place = get_cemetery(profile_dead.place)
        prayer_profile = Prayer.objects.filter(cemetery=dead_place)
        prayer_P = []
        for i in prayer_profile:
            prayer_P.append(i)
        prayer_task_instance = Prayer_Task(prayer=None)
        prayer_task_instance.order = instance
        prayer_task_instance.save()
        instance.prayer_status = "NP"


def menu_submission(request, form, context):
    uid = request.POST.get("uid")
    instance = Order_User(
        profile_dead=User_Place.objects.get(user=request.user, uid=uid)
    )
    if form.is_valid():
        id_to_check = {
            "graveCheck": "gravesite_service",
            "flowerCheck": "floral_service",
            "prayerCheck": "prayer_service",
        }
        services_dict = {
            "gravesite_service": False,
            "floral_service": False,
            "prayer_service": False,
        }
        options = []
        for id, service in id_to_check.items():
            if request.POST.get(id):
                services_dict[service] = True
                value = get_value_of_user_choices(request, id)
                if service == "floral_service":
                    flower_shape_decoder = {
                        "citifora": "CF",
                        "gertudes": "GF",
                        "raphael": "RG",
                        "larose": "LR",
                    }
                    flower = request.POST.get("flowerSelect")
                    setattr(instance, "flower_shop", flower_shape_decoder[flower])
                setattr(instance, service, value)
        totalpay = request.POST.get("cat_id")
        order_date = form.cleaned_data.get("order_date")
        instance.order_date = order_date
        note = request.POST.get("Note")
        instance.status = "NP"
        instance.price = totalpay
        instance.note = note
        instance.save()
        creating_order_tasks(instance, services_dict)
        instance.save()
        return redirect("summary", instance.id)
    else:
        return render(request, "lapida_app/menu.html", context)


@login_required(login_url="login")
def menu(request):
    query_results = User_Place.objects.filter(user=request.user)
    form = Order_UserForm(request.POST)
    dead_profile = []
    cemeteries = []
    flower_shop_names = [
        "CF",
        "GF",
        "RG",
        "LR",
    ]
    flower_shape_decoder = {
        "CF": "citifora",
        "GF": "gertudes",
        "RG": "raphael",
        "LR": "larose",
    }
    flowers_dict = {}
    flower_summary_list = []
    for flower_shop in flower_shop_names:
        flowertaker_profile = FlowerTaker.objects.get(flower_shops=flower_shop)
        flowertaker_items = FlowerShopItems.objects.filter(
            flower_taker=flowertaker_profile
        )
        flower_list = []
        for counter, flower in enumerate(flowertaker_items):
            flower_id = "".join([str(flower.flower_taker.user), "_", str(flower.id)])
            radio_value = "".join([str(flower.price), ",", flower.flower_name])
            flower_html = """<li class="list-group-item rounded-0 d-flex align-items-center justify-content-between">
                <div class="custom-control custom-radio">
                    <input class="custom-control-input" id="{id}" type="radio" name="{flower_shop_name}" value="{radio_value}" {checked} flower_price="{flower_price}" flower_name="{flower_name}">
                    <label class="custom-control-label" for="{id}">
                        <p class="mb-0">{flower_name} - ₱{flower_price}.00</p><span class="small font-italic text-muted">{flower_description}</span>
                    </label>
                </div>
                <label for="{id}"><img src="{image_source}" alt="" width="60"></label>
            </li>""".format(
                id=flower_id,
                flower_shop_name=flower_shape_decoder[flower_shop],
                radio_value=radio_value,
                flower_name=flower.flower_name,
                flower_price=str(flower.price),
                image_source=flower.image.url,
                flower_description=flower.description,
                checked="checked" if counter == 0 else "",
            )
            flower_list.append(flower_html)
            flower_id_summary = "".join([flower_id, "_", "summary"])
            flower_summary_html = """<div id="{flower_id}" hidden>
                    <li class='list-group-item d-flex justify-content-between align-items-center border-0 px-0 pb-0 tab'>{flower_name}<span>₱{flower_price}.00</span></li>
                    </div>""".format(
                flower_id=flower_id_summary,
                flower_name=flower.flower_name,
                flower_price=str(flower.price),
            )
            flower_summary_list.append(flower_summary_html)
        flowers_dict[flower_shop] = flower_list
    for dead in query_results:
        person_dead = MasterData_Revised.objects.get(uid=dead)
        dead_profile.append(person_dead)
        cemeteries.append(person_dead.place)
    if not dead_profile:
        messages.error(request, "Please register a profile of your loved one first.")
        return redirect("create-dead")
    context = {
        "form": dead_profile,
        "order": form,
        "cemeteries": cemeteries,
        "flowers": flowers_dict,
        "flowers_summary": flower_summary_list,
    }
    if request.method == "POST":
        summary_form = menu_submission(request, form, context)
        return summary_form
    return render(request, "lapida_app/menu.html", context)


def get_value_of_user_choices(request, id):
    if id == "graveCheck":
        final_gravesite_html = ""
        grave_site_html = """<div id="{div_id}">
                    <li class='list-group-item d-flex justify-content-between align-items-center border-0 px-0 pb-0 tab'>{gravesite_service} Care<span>₱1000.00</span></li>
                </div>"""
        if request.POST.get("gravecareCheck"):
            div_id = "gravestoneprice"
            gravesite_service = "Gravestone"
            final_gravesite_html += grave_site_html.format(
                div_id=div_id, gravesite_service=gravesite_service
            )
        if request.POST.get("landscapeCheck"):
            div_id = "landscapeprice"
            gravesite_service = "Landscape"
            final_gravesite_html += grave_site_html.format(
                div_id=div_id, gravesite_service=gravesite_service
            )
        return final_gravesite_html
    elif id == "flowerCheck":
        flower_summary_html = """<div id="flower_summary">
                <li class='list-group-item d-flex justify-content-between align-items-center border-0 px-0 pb-0 tab'>{flower_name}<span>₱{flower_price}.00</span></li>
                </div>"""
        flower = request.POST.get("flowerSelect")
        if flower:
            if flower == "citifora":
                flower_arrangement = request.POST.get("citifora")
            elif flower == "gertudes":
                flower_arrangement = request.POST.get("gertudes")
            elif flower == "raphael":
                flower_arrangement = request.POST.get("raphael")
            elif flower == "larose":
                flower_arrangement = request.POST.get("larose")
            if flower_arrangement:
                flower_list = flower_arrangement.split(",")
                final_flower_summary_html = flower_summary_html.format(
                    flower_name=flower_list[1], flower_price=flower_list[0]
                )
            return final_flower_summary_html
    elif id == "prayerCheck":
        prayer_service_html = """<div id="prayer_service">
                    <li class='list-group-item d-flex justify-content-between align-items-center border-0 px-0 pb-0 tab'>Prayer Service and Candle Lighting<span>₱1500.00</span></li>
                </div>"""
        return prayer_service_html


def get_cemetery(place):
    if place == "Manila North C":
        final_place = "MN"
    elif place == "Manila South C":
        final_place = "MS"
    elif place == "La Loma C":
        final_place = "L"
    elif place == "Manila Chinese C":
        final_place = "MC"
    return final_place


def get_options(x):
    if x == 6:
        option = "Service includes grass-trimming, watering the entire site, and proper cleaning the gravestone. Photos of before and after proof of service will be sent to your email."
    elif x == 8:
        option = "Placing of candle lights for the ones you love as an act of an extension for your prayers.Photos of before and after proof of service will be sent to your email."
    elif x == 9:
        option = "Haven's Memory will offer 'The Eternal Rest prayer' which is offered at any time during business hours for those who have departed in this life. "
    return option


def get_flower(flower):
    if flower == "Wreath":
        option = "Floral Arrangement: Wreath"
    elif flower == "Classic":
        option = "Floral Arrangement: Classic"
    elif flower == "Elegant":
        option = "Floral Arrangement: Elegant"
    return option


@login_required(login_url="login")
def delete_record(request, uid):
    dead_profile = User_Place.objects.get(user=request.user, uid=uid)
    dead_profile.delete()


@login_required(login_url="login")
def profile(request):
    query_results = User_Place.objects.filter(user=request.user)
    dead_profile = []
    order_user = []
    order_query = []
    for dead in query_results:
        dead_profile.append(MasterData_Revised.objects.get(uid=dead))
        order_query += Order_User.objects.filter(profile_dead=dead)
    for order in order_query:
        try:
            order_user.append(Order_User.objects.get(id=order.id))
        except ObjectDoesNotExist:
            pass
    if not dead_profile:
        messages.error(request, "Please register a profile of your loved one first.")
        return redirect("create-dead")
    context = {"form": dead_profile, "order_user": order_user}
    return render(request, "lapida_app/profile.html", context)


@login_required(login_url="login")
def summary(request, id):
    order = Order_User.objects.get(id=id)
    profile = Profile.objects.get(user=order.profile_dead.user)
    group = request.user.groups.all()[0].name
    if "customer" not in group:
        if order.before_gravesite_image == "image/default_client.png":
            order.before_gravesite_image = "image/default_before_employee.png"
        if order.after_gravesite_image == "image/default_client.png":
            order.after_gravesite_image = "image/default_employee.png"
        if order.floral_image == "image/default_client.png":
            order.floral_image = "image/default_employee.png"
        if order.prayer_link == "":
            order.prayer_image = "image/default_employee.png"
    else:
        if order.before_gravesite_image == "image/default_client.png":
            order.before_gravesite_image = "image/default_before_client.png"
        if order.prayer_link == "":
            order.prayer_image = "image/default_client.png"
    context = {"form": order, "profile": profile}
    return render(request, "lapida_app/summary.html", context)


def approve_payment(request, id):
    order = Order_User.objects.get(id=id)
    order.status = "Pa"
    order.gravesite_status = "NT" if order.gravesite_status != "NA" else "NA"
    order.floral_status = "P" if order.floral_status != "NA" else "NA"
    order.prayer_status = "NT" if order.prayer_status != "NA" else "NA"
    order.save()
    context = {"form": order}
    return render(request, "lapida_app/summary.html", context)


def no_permission(request):
    return render(request, "lapida_app/no_permission.html")


def update_over_all_status(order):
    complete = [False, False, False]
    if order.gravesite_status != "NA":
        if order.gravesite_status == "C":
            complete[0] = True
    else:
        complete[1] = True
    if order.floral_status != "NA":
        if order.floral_status == "C":
            complete[1] = True
    else:
        complete[1] = True
    if order.prayer_status != "NA":
        if order.prayer_status == "C":
            complete[2] = True
    else:
        complete[2] = True
    if complete[0:3] == [True, True, True]:
        return "C"
    else:
        return "P"


def complete_task(order, group):
    if "caretaker" in group:
        if (
            order.before_gravesite_image != "image/default_client.png"
            and order.gravesite_status == "P"
        ):
            order.gravesite_status = "O"
        if (
            order.after_gravesite_image != "image/default_client.png"
            and order.gravesite_status == "O"
        ):
            order.gravesite_status = "C"
    elif "flowershop" in group:
        if (
            order.floral_image != "image/default_client.png"
            and order.floral_status == "P"
        ):
            order.floral_status = "C"
    elif "prayer" in group:
        if order.prayer_link != "" and order.prayer_status == "P":
            order.prayer_status = "C"
    order.status = update_over_all_status(order)


def update_image_url(request, order):
    group = request.user.groups.all()[0].name
    if "caretaker" in group:
        if (
            order.before_gravesite_image == "image/default_client.png"
            and order.gravesite_status == "P"
        ):
            order.before_gravesite_image = request.FILES["image"]
        if (
            order.after_gravesite_image == "image/default_client.png"
            and order.gravesite_status == "O"
        ):
            order.after_gravesite_image = request.FILES["image"]
    elif "flowershop" in group:
        if (
            order.floral_image == "image/default_client.png"
            and order.floral_status == "P"
        ):
            order.floral_image = request.FILES["image"]
    elif "prayer" in group:
        if order.prayer_link == "" and order.prayer_status == "P":
            order.prayer_link = request.POST.get("prayer_link")
    complete_task(order, group)


def update_prayer_link(request, id):
    if request.method == "POST":
        order = Order_User.objects.get(id=id)
        order.prayer_link = request.POST.get("prayer_link")
        order.prayer_status = "C"
        order.status = update_over_all_status(order)
        order.save()
        context = {"form": order}
        return render(request, "lapida_app/summary.html", context)


def update_picture(request, id):
    if request.method == "POST":
        order = Order_User.objects.get(id=id)
        update_image_url(request, order)
        order.save()
        context = {"form": order}
        return render(request, "lapida_app/summary.html", context)


def update_status(request, id):
    order = Order_User.objects.get(id=id)
    if order.status == "Pa":
        order.status = "O"
    elif order.status == "O":
        order.status = "C"
    order.save()
    context = {"form": order}


def reserve_task(request, id):
    order = Order_User.objects.get(id=id)
    order_date = datetime.datetime.strftime(order.order_date, "%Y-%m-%d")
    employee_role = request.user.groups.all()[0].name
    employee_model = CareTaker if employee_role == "caretaker" else Prayer
    employee_profile = employee_model.objects.get(user=request.user)
    employee_task_model = (
        Caretaker_Task if employee_role == "caretaker" else Prayer_Task
    )
    emplyoee_tasks = (
        employee_task_model.objects.filter(caretaker=employee_profile)
        if employee_role == "caretaker"
        else employee_task_model.objects.filter(prayer=employee_profile)
    )
    if employee_role == "caretaker":
        order_date_to_be_checked = []
        for x in emplyoee_tasks:
            if x:
                past_order = x.order
                order_date_to_be_checked.append(
                    datetime.datetime.strftime(past_order.order_date, "%Y-%m-%d")
                )
        if order_date in order_date_to_be_checked:
            sweetify.error(
                request,
                "YOU HAVE REACHED YOUR DAILY QUOTA",
                persistent=":(",
            )
            return redirect("summary", order.id)
    tasks_status_name = (
        "gravesite_status" if employee_role == "caretaker" else "prayer_status"
    )
    tasks_employee_name = "caretaker" if employee_role == "caretaker" else "prayer"
    setattr(order, tasks_status_name, "P")
    employee_task_instance = employee_task_model.objects.get(order=order)
    setattr(employee_task_instance, tasks_employee_name, employee_profile)
    order.save()
    employee_task_instance.save()
    User = get_user_model()
    user = User.objects.get(pk=employee_profile.user.id)
    user_email = user.email
    current_site = get_current_site(request)
    mail_subject = "New Task"
    message = render_to_string(
        "lapida_app/email_notification.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        },
    )
    to_email = user_email
    send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
    return redirect("summary", order.id)


@receiver(post_save, sender=reserve_task)
def clear_cache(sender, instance, **kwargs):
    cache.clear()
    # call cache clear here


def cancel_request(request, id):
    order = Order_User.objects.get(id=id)
    if order.status == "NT":
        order.delete()
    else:
        order.status = "Ca"
        order.save()
        context = {"form": order}


def export(request):
    member_resource = MasterData_RevisedResource()
    dataset = member_resource.export()
    # response = HttpResponse(dataset.csv, content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="member.csv"'
    # response = HttpResponse(dataset.json, content_type='application/json')
    # response['Content-Disposition'] = 'attachment; filename="persons.json"'
    response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="persons.xls"'
    return response


def handle404(request, exception):
    return render(request, "lapida_app/404.html", status=404)


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "lapida_app/password_message.html"
                    c = {
                        "email": user.email,
                        "domain": "127.0.0.1:8000",
                        "site_name": "Website",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email,
                            "admin@example.com",
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="lapida_app/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )


# Create your views here.
