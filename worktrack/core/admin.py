from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline, ModelAdmin
from .models import *



class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'user_type')
    search_fields = ('username', 'email')
    list_filter = ('user_type',)
admin.site.register(User, UserAdmin)


class CompanyInformationAdmin(ModelAdmin):
    list_display = ('work_start_time', 'work_end_time')
    search_fields = ('work_start_time', 'work_end_time')
admin.site.register(CompanyInformation, CompanyInformationAdmin)


class FirstLoginTimeAdmin(ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user', 'created_at')
admin.site.register(FirstLoginTime, FirstLoginTimeAdmin)


class NotificationAdmin(ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'topic', 'is_read', 'created_at')
    search_fields = ('sender', 'receiver', 'message')
admin.site.register(Notification, NotificationAdmin)


class LeaveRequestAdmin(ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'status', 'created_at')
    search_fields = ('user', 'start_date', 'end_date', 'status')
admin.site.register(LeaveRequest, LeaveRequestAdmin)


class HourlyLeaveRequestAdmin(ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'status', 'created_at')
    search_fields = ('user', 'start_time', 'end_time', 'status')
admin.site.register(HourlyLeaveRequest, HourlyLeaveRequestAdmin)

class AnnualLeaveMinutesAdmin(ModelAdmin):
    list_display = ('user', 'annual_leave_minutes')
    search_fields = ('user', 'annual_leave_minutes')
admin.site.register(AnnualLeaveMinutes, AnnualLeaveMinutesAdmin)


class LateToWorkMinutesAdmin(ModelAdmin):
    list_display = ('user', 'late_to_work_minutes', 'created_at', 'is_logined', 'is_full_day')
    search_fields = ('user', 'late_to_work_minutes')
admin.site.register(LateToWorkMinutes, LateToWorkMinutesAdmin)
