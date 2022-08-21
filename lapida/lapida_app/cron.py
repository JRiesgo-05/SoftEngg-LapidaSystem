from django_cron import CronJobBase, Schedule
from .models import (
    Order_User,
)
from datetime import date, datetime, timedelta
from django.db.models import Q


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 0.002  # every 1 min
    RETRY_AFTER_FAILURE_MINS = 1
    schedule = Schedule(
        run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS
    )
    code = "lapida.my_cron_job"  # a unique code

    def do(self):
        orders = Order_User.objects.filter(
            Q(gravesite_status__in=["P", "NT", "O"])
            | Q(floral_status__in=["P"])
            | Q(prayer_status__in=["P", "NT"])
        )
        today = date.today()
        yesterday = today - timedelta(days=1)
        for order in orders:
            changes = False
            order_date_converted = order.order_date.date() + timedelta(days=1)
            gravesite_leftover_days = (order_date_converted - yesterday).days
            leftover_days = (order_date_converted - today).days
            if order.gravesite_status in ["P", "NT", "O"]:
                if gravesite_leftover_days < 1:
                    order.gravesite_status = "OV"
                    changes = True
            if order.floral_status in ["P"]:
                if leftover_days < 0:
                    order.floral_status = "OV"
                    changes = True
            if order.prayer_status in ["P", "NT", "O"]:
                if leftover_days < 0:
                    order.floral_status = "OV"
                    changes = True
            if changes:
                order.save()
