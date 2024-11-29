from django.urls import path, include
from .views import *

app_name = 'core'
urlpatterns = [
    # Template Views
    path('', LandingView.as_view(), name='landing'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('staff/login/', StaffLoginView.as_view(), name='staff_login'),
    path('executive/login/', ExecutiveLoginView.as_view(), name='executive_login'),
    path('staff/', StaffDashboardView.as_view(), name='staff_dashboard'),
    path('executive/', ExecutiveDashboardView.as_view(), name='executive_dashboard'),
    path('user/login/times/', UserLoginTimeView.as_view(), name='user_login_times'),

    # Api Views
    path('api/signup/', SignupApiView.as_view(), name='signup_api'),
    path('api/staff/login/', StaffLoginApiView.as_view(), name='staff_login_api'),
    path('api/executive/login/', ExecutiveLoginApiView.as_view(), name='executive_login_api'),
    path('api/logout/', LogoutApiView.as_view(), name='logout_api'),
    path('api/user/login/times/', UserLoginTimeApiView.as_view(), name='user_login_times_api'),
    path('api/executive/dashboard/stats/', ExecutiveDashboardStatsApiView.as_view(), name='executive_dashboard_stats_api'),
    path('api/staff/dashboard/stats/', StaffDashboardStatsApiView.as_view(), name='staff_dashboard_stats_api'),
    path('api/notifications/<int:notification_id>/mark-read/', MarkNotificationAsReadApiView.as_view(), name='mark_notification_read'),
    path('api/leave-requests/<int:request_id>/update-status/', 
         UpdateLeaveRequestStatusView.as_view(), 
         name='update_leave_request_status'),
    path('api/hourly-leave-requests/<int:request_id>/update-status/', 
         UpdateHourlyLeaveRequestStatusView.as_view(), 
         name='update_hourly_leave_request_status'),
    path('api/leave-requests/create/', 
         CreateNewLeaveRequestApiView.as_view(), 
         name='create_leave_request'),
    path('api/hourly-leave-requests/create/', 
         CreateNewHourlyLeaveRequestApiView.as_view(), 
         name='create_hourly_leave_request'),
]
