from rest_framework import status, views
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from .models import *
from django.views import generic
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, time
from django.core.paginator import Paginator
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ValidationError

# Template Views

class LogoutView(generic.View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('core:landing')


class LandingView(generic.View):
    template_name = 'core/landing.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.user_type == 'staff':
                return redirect('core:staff_dashboard')
            elif request.user.user_type == 'executive':
                return redirect('core:executive_dashboard')
        return render(request, self.template_name)


class StaffDashboardView(generic.View):
    template_name = 'core/staff_dashboard.html'
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('core:landing')
        if request.user.user_type != 'staff':
            return redirect('core:executive_dashboard')
        return render(request, self.template_name)


class ExecutiveDashboardView(generic.View):
    template_name = 'core/executive_dashboard.html'
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('core:landing')
        if request.user.user_type != 'executive':
            return redirect('core:staff_dashboard')
        return render(request, self.template_name)


# Login Views
class StaffLoginView(generic.View):
    template_name = 'core/staff_login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.user_type == 'staff':
                return redirect('core:staff_dashboard')
            elif request.user.user_type == 'executive':
                return redirect('core:executive_dashboard')
        return render(request, self.template_name)


class ExecutiveLoginView(generic.View):
    template_name = 'core/executive_login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.user_type == 'staff':
                return redirect('core:staff_dashboard')
            elif request.user.user_type == 'executive':
                return redirect('core:executive_dashboard')
        return render(request, self.template_name)


class UserLoginTimeView(generic.View):
    template_name = 'core/user_login_times.html'
    paginate_by = 10
    
    def get_today_login_times(self):
        """Get first login time for each user for the current day"""
        today = timezone.localdate()
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        today_end = timezone.make_aware(datetime.combine(today, time.max))
        
        users = User.objects.all()
        user_login_times = []
        
        for user in users:
            # Get first login time from FirstLoginTime model
            first_login = FirstLoginTime.objects.filter(
                user=user,
                login_time__gte=today_start,
                login_time__lte=today_end
            ).first()
            
                
            user_login_times.append({
                'username': user.username,
                'user_type': user.user_type,
                'first_login': first_login.login_time if first_login else None,
                'last_login': user.last_login if user.last_login else None
            })
            
        return user_login_times
    
    def get(self, request):
        user_login_times = self.get_today_login_times()
        paginator = Paginator(user_login_times, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'user_login_times': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
        }
        return render(request, self.template_name, context)

# Api Views
class SignupApiView(views.APIView):

    @extend_schema(request=UserSerializer, responses=UserSerializer)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(username=serializer.validated_data['username']).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.validated_data['password'] != serializer.validated_data['repeat_password']:
                return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            user = User.objects.get(username=serializer.validated_data['username'])
            user.set_password(serializer.validated_data['password'])
            user.save()
            token = Token.objects.create(user=user) 
            return Response({'message': 'User created successfully', 'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


class StaffLoginApiView(views.APIView):

    @extend_schema(request=UserLoginSerializer, responses=UserSerializer)
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            
            if user and user.user_type == 'staff':
                login(request, user)
                first_login_time, is_login_created = FirstLoginTime.objects.get_or_create(user=user)  # Create first login time
                token, is_token_created = Token.objects.get_or_create(user=user)

                return Response(
                    {
                        'message': 'Login successful as staff',
                        'token': token.key,
                        'first_login': first_login_time.created_at,
                        'last_login': user.last_login if user.last_login else None
                    }, 
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {'error': 'Invalid credentials or not authorized'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExecutiveLoginApiView(views.APIView):

    @extend_schema(request=UserLoginSerializer, responses=UserSerializer)
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            
            if user and user.user_type == 'executive':
                login(request, user)
                first_login_time, is_login_created = FirstLoginTime.objects.get_or_create(user=user)  # Create first login time
                token, is_token_created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        'message': 'Login successful as executive',
                        'token': token.key,
                        'first_login': first_login_time.created_at,
                        'last_login': user.last_login if user.last_login else None
                    }, 
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {'error': 'Invalid credentials or not authorized'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutApiView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserSerializer)
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})


class UserLoginTimeApiView(views.APIView):
    # Add pagination settings
    pagination_class = PageNumberPagination
    page_size = 10

    @extend_schema(
        description='List all user login times with pagination',
        parameters=[
            OpenApiParameter(
                name='page',
                description='Page number',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='page_size',
                description='Number of items per page',
                required=False,
                type=int
            )
        ],
        responses={200: {'type': 'object', 'properties': {
            'count': {'type': 'integer'},
            'next': {'type': 'string', 'format': 'uri', 'nullable': True},
            'previous': {'type': 'string', 'format': 'uri', 'nullable': True},
            'results': {'type': 'array'}
        }}}
    )
    def get(self, request):
        today = timezone.localdate()
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        today_end = timezone.make_aware(datetime.combine(today, time.max))
        
        users = User.objects.all()
        user_login_times = []
        
        for user in users:
            # Get first login time from FirstLoginTime model
            first_login = FirstLoginTime.objects.filter(
                user=user,
                login_time__gte=today_start,
                login_time__lte=today_end
            ).first()
            
            user_login_times.append({
                'username': user.username,
                'user_type': user.user_type,
                'first_login': first_login.login_time if first_login else None,
                'last_login': user.last_login if user.last_login else None
            })
        
        # Initialize paginator
        paginator = self.pagination_class()
        paginated_times = paginator.paginate_queryset(user_login_times, request)

        return paginator.get_paginated_response(paginated_times)


class ExecutiveDashboardStatsApiView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    @extend_schema(responses=UserSerializer)
    def get(self, request):
        context = {}
        context['staff_count'] = User.objects.filter(user_type='staff').count()
        context['executive_count'] = User.objects.filter(user_type='executive').count()

        leave_requests = LeaveRequest.objects.filter(status='pending')
        context['leave_requests'] = LeaveRequestSerializer(leave_requests, many=True).data

        hourly_leave_requests = HourlyLeaveRequest.objects.filter(status='pending')
        context['hourly_leave_requests'] = HourlyLeaveRequestSerializer(hourly_leave_requests, many=True).data

        notifications = Notification.objects.filter(is_read=False, receiver=request.user)
        context['notifications'] = NotificationSerializer(notifications, many=True).data

        today = timezone.localdate()
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        today_end = timezone.make_aware(datetime.combine(today, time.max))
        
        first_login_count = FirstLoginTime.objects.filter(
            created_at__gte=today_start,
            created_at__lte=today_end
        ).count()
        
        context['first_login_count'] = first_login_count

        return Response(context)


class MarkNotificationAsReadApiView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}})
    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateLeaveRequestStatusView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        try:
            leave_request = LeaveRequest.objects.get(id=request_id)
            new_status = request.data.get('status')
            
            if new_status not in ['approved', 'rejected']:
                return Response(
                    {'error': 'Invalid status'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            leave_request.status = new_status
            leave_request.save()
            
            # Create notification for the staff member
            Notification.objects.create(
                sender=request.user,
                receiver=leave_request.user,
                message=f'Your leave request for {leave_request.start_date.strftime("%d/%m/%Y")} - {leave_request.end_date.strftime("%d/%m/%Y")} has been {new_status}',
                is_read=False
            )
            
            return Response({
                'success': True,
                'message': f'Leave request {new_status} successfully'
            })
            
        except LeaveRequest.DoesNotExist:
            return Response(
                {'error': 'Leave request not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateHourlyLeaveRequestStatusView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        try:
            hourly_leave_request = HourlyLeaveRequest.objects.get(id=request_id)
            new_status = request.data.get('status')
            
            if new_status not in ['approved', 'rejected']:
                return Response(
                    {'error': 'Invalid status'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            hourly_leave_request.status = new_status
            hourly_leave_request.save()
            
            # Create notification for the staff member
            Notification.objects.create(
                sender=request.user,
                receiver=hourly_leave_request.user,
                message=f'Your hourly leave request for {hourly_leave_request.start_time} - {hourly_leave_request.end_time} has been {new_status}',
                is_read=False
            )
            
            return Response({
                'success': True,
                'message': f'Hourly leave request {new_status} successfully'
            })
            
        except HourlyLeaveRequest.DoesNotExist:
            return Response(
                {'error': 'Hourly leave request not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class StaffDashboardStatsApiView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    @extend_schema(responses=UserSerializer)
    def get(self, request):
        context = {}

        # Leave Request
        leave_requests = LeaveRequest.objects.filter(user=request.user)
        context['leave_requests'] = LeaveRequestSerializer(leave_requests, many=True).data
        

        # Hourly Leave Request
        hourly_leave_requests = HourlyLeaveRequest.objects.filter(user=request.user)
        context['hourly_leave_requests'] = HourlyLeaveRequestSerializer(hourly_leave_requests, many=True).data


        # Late to work minutes
        late_to_work_minutes = LateToWorkMinutes.objects.filter(user=request.user)
        context['late_to_work_minutes'] = LateToWorkMinutesSerializer(late_to_work_minutes, many=True).data

        return Response(context)


class CreateNewLeaveRequestApiView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=LeaveRequestSerializer, responses=LeaveRequestSerializer)
    def post(self, request):
        # Create a mutable copy of request.data and add the user
        data = request.data.copy()
        serializer = LeaveRequestSerializer(data=data)
        try:
            if serializer.is_valid():
                # Save with the current user
                serializer.save(user=request.user)

                executives = User.objects.filter(user_type='executive')

                for executive in executives:
                    Notification.objects.create(
                        sender=request.user,
                        receiver=executive,
                        message=f'{request.user.username} has created a new leave request for {serializer.data["start_date"]} - {serializer.data["end_date"]}',
                        is_read=False
                    )
                return Response(
                    {'message': 'Leave request created successfully'}, 
                    status=status.HTTP_201_CREATED
                )
        except ValidationError as e:
            return Response(
                {'error': e.message_dict}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class CreateNewHourlyLeaveRequestApiView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=HourlyLeaveRequestSerializer, responses=HourlyLeaveRequestSerializer)
    def post(self, request):
        data = request.data.copy()
        serializer = HourlyLeaveRequestSerializer(data=data)
        try:
            if serializer.is_valid():
                instance = serializer.save(user=request.user)
                instance.full_clean()
                instance.save()

                executives = User.objects.filter(user_type='executive')

                for executive in executives:
                    Notification.objects.create(
                        sender=request.user,
                        receiver=executive,
                        message=f'{instance.user.username} has created a new hourly leave request for {instance.start_time} - {instance.end_time}',
                        is_read=False
                    )
                
                return Response(
                    {'message': 'Hourly leave request created successfully'}, 
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(
                {'error': e.message_dict}, 
                status=status.HTTP_400_BAD_REQUEST
            )
