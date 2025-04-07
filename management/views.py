from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from .models import (
    App, Feature, Operation, 
    RegistrationRequest, PermissionRequest
)
from .forms import (
    RegistrationRequestForm, PermissionRequestForm,
    RegistrationApprovalForm, PermissionApprovalForm,
    AppForm, FeatureForm, OperationForm
)

def index(request):
    """Landing page view."""
    return render(request, 'management/index.html')

def register_request(request):
    """Handle external user registration requests."""
    if request.method == 'POST':
        form = RegistrationRequestForm(request.POST)
        if form.is_valid():
            registration_request = form.save()
            messages.success(
                request,
                'Your registration request has been submitted successfully. '
                'You will be notified via email once it has been processed.'
            )
            return redirect('index')
    else:
        form = RegistrationRequestForm()
    
    return render(request, 'management/registration_request.html', {'form': form})

@login_required
def permission_request(request):
    """Handle permission requests for features/operations."""
    if request.method == 'POST':
        form = PermissionRequestForm(request.POST)
        if form.is_valid():
            permission_request = form.save(commit=False)
            permission_request.requesting_user = request.user
            permission_request.save()
            messages.success(
                request,
                'Your permission request has been submitted successfully.'
            )
            return redirect('index')
    else:
        form = PermissionRequestForm()
    
    return render(request, 'management/permission_request.html', {'form': form})

def get_features(request):
    """AJAX view to get features for a specific app."""
    app_id = request.GET.get('app_id')
    features = Feature.objects.filter(app_id=app_id).values('id', 'name')
    return JsonResponse(list(features), safe=False)

def get_operations(request):
    """AJAX view to get operations for a specific feature."""
    feature_id = request.GET.get('feature_id')
    operations = Operation.objects.filter(feature_id=feature_id).values('id', 'name')
    return JsonResponse(list(operations), safe=False)

# Staff Views
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is staff."""
    def test_func(self):
        return self.request.user.is_staff

class StaffDashboardView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Dashboard for staff users."""
    template_name = 'management/staff/dashboard.html'
    context_object_name = 'registration_requests'
    
    def get_queryset(self):
        return RegistrationRequest.objects.filter(status='pending')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permission_requests'] = PermissionRequest.objects.filter(status='pending')
        return context

@login_required
def process_registration(request, pk):
    """Process (approve/reject) registration requests."""
    if not request.user.is_staff:
        raise PermissionDenied
    
    reg_request = get_object_or_404(RegistrationRequest, pk=pk)
    if request.method == 'POST':
        form = RegistrationApprovalForm(request.POST, instance=reg_request)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.processed_by = request.user
            registration.processed_at = timezone.now()
            registration.save()
            messages.success(request, f'Registration request has been {registration.status}.')
            return redirect('staff_dashboard')
    else:
        form = RegistrationApprovalForm(instance=reg_request)
    
    return render(request, 'management/staff/process_registration.html', {
        'form': form,
        'registration_request': reg_request
    })

@login_required
def process_permission(request, pk):
    """Process (approve/reject) permission requests."""
    if not request.user.is_staff:
        raise PermissionDenied
    
    perm_request = get_object_or_404(PermissionRequest, pk=pk)
    if request.method == 'POST':
        form = PermissionApprovalForm(request.POST, instance=perm_request)
        if form.is_valid():
            permission = form.save(commit=False)
            permission.processed_by = request.user
            permission.processed_at = timezone.now()
            permission.save()
            messages.success(request, f'Permission request has been {permission.status}.')
            return redirect('staff_dashboard')
    else:
        form = PermissionApprovalForm(instance=perm_request)
    
    return render(request, 'management/staff/process_permission.html', {
        'form': form,
        'permission_request': perm_request
    })

# App Management Views
class AppListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = App
    template_name = 'management/staff/app_list.html'
    context_object_name = 'apps'

class AppCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = App
    form_class = AppForm
    template_name = 'management/staff/app_form.html'
    success_url = reverse_lazy('app_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Application created successfully.')
        return super().form_valid(form)

class AppUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = App
    form_class = AppForm
    template_name = 'management/staff/app_form.html'
    success_url = reverse_lazy('app_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Application updated successfully.')
        return super().form_valid(form)

# Feature Management Views
class FeatureListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Feature
    template_name = 'management/staff/feature_list.html'
    context_object_name = 'features'

class FeatureCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Feature
    form_class = FeatureForm
    template_name = 'management/staff/feature_form.html'
    success_url = reverse_lazy('feature_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Feature created successfully.')
        return super().form_valid(form)

class FeatureUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Feature
    form_class = FeatureForm
    template_name = 'management/staff/feature_form.html'
    success_url = reverse_lazy('feature_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Feature updated successfully.')
        return super().form_valid(form)

# Operation Management Views
class OperationListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Operation
    template_name = 'management/staff/operation_list.html'
    context_object_name = 'operations'

class OperationCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Operation
    form_class = OperationForm
    template_name = 'management/staff/operation_form.html'
    success_url = reverse_lazy('operation_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Operation created successfully.')
        return super().form_valid(form)

class OperationUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Operation
    form_class = OperationForm
    template_name = 'management/staff/operation_form.html'
    success_url = reverse_lazy('operation_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Operation updated successfully.')
        return super().form_valid(form)
