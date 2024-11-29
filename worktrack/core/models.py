from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import datetime
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('staff', 'Staff'),
        ('executive', 'Executive'),
    )
    
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES,
        default='staff'
    )
    
    class Meta:
        db_table = 'core_user'
        swappable = 'AUTH_USER_MODEL'


class AnnualLeaveMinutes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    annual_leave_minutes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.annual_leave_minutes} minutes"


class CompanyInformation(models.Model):
    work_start_time = models.TimeField(default=datetime.time(8, 0))
    work_end_time = models.TimeField(default=datetime.time(18, 0))
    weekend_days = models.CharField(max_length=255, default='Saturday, Sunday')
    vacation_days = models.IntegerField(default=15)

    def __str__(self):
        return "Company Information"

    def save(self, *args, **kwargs):
        if not self.pk and CompanyInformation.objects.exists():
            raise ValidationError("Only one instance of Company Information data is allowed.")
        super().save(*args, **kwargs)

    class Meta:
        abstract = False  # Change to True if you want to make this a base class

    def get_full_day_minutes(self):
        return (self.work_end_time.hour - 1 - self.work_start_time.hour) * 60 + self.work_end_time.minute + 60 - self.work_start_time.minute
    

    def get_minutes_until_work_start(self):
        now = timezone.now().time()
        work_start = self.work_start_time
        
        # Convert times to datetime for comparison
        today = timezone.now().date()
        now_datetime = timezone.datetime.combine(today, now)
        work_start_datetime = timezone.datetime.combine(today, work_start)
        
        # Calculate time difference
        time_difference = work_start_datetime - now_datetime
        
        # Convert to minutes
        minutes_difference = time_difference.total_seconds() / 60
        
        return int(minutes_difference)


class FirstLoginTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at} - {self.updated_at}"


class LeaveRequest(models.Model):
    LEAVE_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=LEAVE_STATUS,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date}"

    class Meta:
        ordering = ['-created_at']


class HourlyLeaveRequest(models.Model):
    LEAVE_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=LEAVE_STATUS, 
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Fetch company information
        try:
            company_info = CompanyInformation.objects.first()
            if not company_info:
                raise ValidationError("Company information not set up.")
        except CompanyInformation.DoesNotExist:
            raise ValidationError("Company information not found.")

        # Validate start and end times
        if self.start_time and self.end_time:
            # Ensure start time is before end time
            if self.start_time >= self.end_time:
                raise ValidationError("Start time must be before end time.")

            # Validate start time is within work hours
            if self.start_time < company_info.work_start_time or self.start_time > company_info.work_end_time:
                raise ValidationError(f"Start time must be between {company_info.work_start_time} and {company_info.work_end_time}.")
            
            # Validate end time is within work hours
            if self.end_time < company_info.work_start_time or self.end_time > company_info.work_end_time:
                raise ValidationError(f"End time must be between {company_info.work_start_time} and {company_info.work_end_time}.")

    def save(self, *args, **kwargs):
        # Run full clean before saving
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - Leave Request from {self.start_time} to {self.end_time}"


class Notification(models.Model):
    TOPIC_CHOICES = (
        ('leave_request', 'Leave Request'),
        ('late_attendance', 'Late Attendance'),
        ('not_attendance', 'Not Attendance'),
        ('leave_expiring', 'Leave expiring'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    message = models.TextField()
    topic = models.CharField(max_length=255, choices=TOPIC_CHOICES, default='')
    is_read = models.BooleanField(default=False)
    can_be_sent = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.receiver.username} - {self.message}"

    class Meta:
        ordering = ["is_read", '-created_at']


class LateToWorkMinutes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    late_to_work_minutes = models.IntegerField(default=0)
    is_logined = models.BooleanField(default=False)
    is_full_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.late_to_work_minutes} minutes"
