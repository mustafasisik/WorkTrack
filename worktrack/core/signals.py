from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import *
import json
from .serializers import NotificationSerializer
from .models import User
from datetime import timedelta

def send_websocket_notification(notification_serializer_data, receiver_id):
    channel_layer = get_channel_layer()
    
    # Send message to the specific user's notification group
    async_to_sync(channel_layer.group_send)(
        f"notifications_{receiver_id}",  # User specific group name
        {
            "type": "send_notification",
            "notification": notification_serializer_data
        }
    )

@receiver(post_save, sender=Notification)
def notify_executive(sender, instance, created, **kwargs):
    
    if created and instance.can_be_sent:
        notification_serializer_data = NotificationSerializer(instance, many=False).data
        # Send to the specific user's channel
        send_websocket_notification(notification_serializer_data, instance.receiver.id)


@receiver(post_save, sender=User)
def define_annual_leave_days(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'staff':
            company_information = CompanyInformation.objects.all()
            
            if len(company_information) > 0:
                company_information = company_information[0]

                work_minutes_per_day = timedelta(hours=company_information.work_end_time.hour - company_information.work_start_time.hour).total_seconds() / 60

                AnnualLeaveMinutes.objects.create(
                    user=instance,
                    annual_leave_minutes=company_information.vacation_days * work_minutes_per_day
                )
        

@receiver(post_save, sender=LateToWorkMinutes)
def notify_late_to_work(sender, instance, created, **kwargs):
    if created:

        executives = User.objects.filter(user_type='executive')
    
        topic = 'not_attendance'
        can_be_sent = False
        if instance.is_logined:
            topic = 'late_attendance'
            can_be_sent = True
        for executive in executives:
            Notification.objects.create(
                sender=instance.user,
                receiver=executive,
                message=f"{instance.user.username} is late to work for {instance.late_to_work_minutes} minutes",
                topic=topic,
                can_be_sent=can_be_sent
            )


@receiver(post_save, sender=FirstLoginTime)
def notify_first_login(sender, instance, created, **kwargs):
    if created:
        company_information = CompanyInformation.objects.all()

        if len(company_information) > 0:
            company_information = company_information[0]

            if instance.created_at.time() > company_information.work_start_time:

                time_in_minutes = instance.created_at.hour * 60 + instance.created_at.minute
                datetime_in_minutes = company_information.work_start_time.hour * 60 + company_information.work_start_time.minute

                # Calculate the difference in minutes
                difference_in_minutes = time_in_minutes - datetime_in_minutes

                LateToWorkMinutes.objects.create(
                    user=instance.user,
                    late_to_work_minutes=difference_in_minutes,
                    is_logined=True
                )

