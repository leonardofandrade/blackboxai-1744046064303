from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public URLs
    path('', views.index, name='index'),
    path('register/', views.register_request, name='register_request'),
    path('permission-request/', views.permission_request, name='permission_request'),
    
    # AJAX URLs
    path('ajax/features/', views.get_features, name='ajax_features'),
    path('ajax/operations/', views.get_operations, name='ajax_operations'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='management/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Staff URLs
    path('staff/dashboard/', views.StaffDashboardView.as_view(), name='staff_dashboard'),
    path('staff/registration/<int:pk>/process/', views.process_registration, name='process_registration'),
    path('staff/permission/<int:pk>/process/', views.process_permission, name='process_permission'),
    
    # App Management URLs
    path('staff/apps/', views.AppListView.as_view(), name='app_list'),
    path('staff/apps/create/', views.AppCreateView.as_view(), name='app_create'),
    path('staff/apps/<int:pk>/update/', views.AppUpdateView.as_view(), name='app_update'),
    
    # Feature Management URLs
    path('staff/features/', views.FeatureListView.as_view(), name='feature_list'),
    path('staff/features/create/', views.FeatureCreateView.as_view(), name='feature_create'),
    path('staff/features/<int:pk>/update/', views.FeatureUpdateView.as_view(), name='feature_update'),
    
    # Operation Management URLs
    path('staff/operations/', views.OperationListView.as_view(), name='operation_list'),
    path('staff/operations/create/', views.OperationCreateView.as_view(), name='operation_create'),
    path('staff/operations/<int:pk>/update/', views.OperationUpdateView.as_view(), name='operation_update'),
]