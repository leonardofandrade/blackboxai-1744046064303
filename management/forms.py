from django import forms
from django.contrib.auth.models import User
from .models import RegistrationRequest, PermissionRequest, App, Feature, Operation

class RegistrationRequestForm(forms.ModelForm):
    """
    Form for external users to request registration.
    """
    class Meta:
        model = RegistrationRequest
        fields = ['first_name', 'last_name', 'email', 'organization', 'reason']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your organization'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please explain why you need access to the system'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email already exists in User model
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered in our system.")
        # Check if there's a pending registration request
        if RegistrationRequest.objects.filter(email=email, status='pending').exists():
            raise forms.ValidationError("A registration request with this email is already pending.")
        return email

class PermissionRequestForm(forms.ModelForm):
    """
    Form for requesting permissions for specific features/operations.
    """
    class Meta:
        model = PermissionRequest
        fields = ['app', 'feature', 'operation', 'reason']
        widgets = {
            'app': forms.Select(attrs={'class': 'form-control'}),
            'feature': forms.Select(attrs={'class': 'form-control'}),
            'operation': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please explain why you need this permission'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feature'].queryset = Feature.objects.none()
        self.fields['operation'].queryset = Operation.objects.none()
        
        if 'app' in self.data:
            try:
                app_id = int(self.data.get('app'))
                self.fields['feature'].queryset = Feature.objects.filter(app_id=app_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.app:
            self.fields['feature'].queryset = self.instance.app.features.all()

        if 'feature' in self.data:
            try:
                feature_id = int(self.data.get('feature'))
                self.fields['operation'].queryset = Operation.objects.filter(feature_id=feature_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.feature:
            self.fields['operation'].queryset = self.instance.feature.operations.all()

class RegistrationApprovalForm(forms.ModelForm):
    """
    Form for staff to approve/reject registration requests.
    """
    class Meta:
        model = RegistrationRequest
        fields = ['status', 'comments']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add any comments about this decision'
            }),
        }

class PermissionApprovalForm(forms.ModelForm):
    """
    Form for staff to approve/reject permission requests.
    """
    class Meta:
        model = PermissionRequest
        fields = ['status', 'comments']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add any comments about this decision'
            }),
        }

class AppForm(forms.ModelForm):
    """
    Form for managing applications.
    """
    class Meta:
        model = App
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FeatureForm(forms.ModelForm):
    """
    Form for managing features.
    """
    class Meta:
        model = Feature
        fields = ['app', 'name', 'description', 'is_active']
        widgets = {
            'app': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OperationForm(forms.ModelForm):
    """
    Form for managing operations.
    """
    class Meta:
        model = Operation
        fields = ['feature', 'name', 'description', 'is_active']
        widgets = {
            'feature': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }