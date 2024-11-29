from celery import shared_task
from celery.utils.log import get_task_logger
import logging
logger = logging.getLogger('celery_info')

@shared_task
def check_user_attendance():
    from .models import FirstLoginTime, LateToWorkMinutes, CompanyInformation
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import datetime, time
    
    User = get_user_model()
    
    today = timezone.localdate()
    today_start = timezone.make_aware(datetime.combine(today, time.min))
    today_end = timezone.make_aware(datetime.combine(today, time.max))
    user_logined_today = FirstLoginTime.objects.filter(
        created_at__gte=today_start,
        created_at__lte=today_end
    ).values_list('user', flat=True)

    users_not_logined_today = User.objects.exclude(id__in=user_logined_today)

    company_information = CompanyInformation.objects.all()

    full_day_minutes = company_information[0].get_full_day_minutes()

    if len(company_information) == 0:
        logger.error("No company information found. Please create a company information first.")
        return

    for user in users_not_logined_today:
        logger.info(f"The check user activity task just ran for {user.username}.")
        executives = User.objects.filter(user_type='executive')
        for executive in executives:
            LateToWorkMinutes.objects.create(
                user=executive,
                late_to_work_minutes=full_day_minutes,
                is_logined=False,
                is_full_day=True
            )