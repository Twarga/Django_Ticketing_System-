from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from .models import Ticket, UserProfile
from .forms import SignUpForm, LoginForm
from django.contrib.auth.models import Group
from django.db import IntegrityError

# Custom check functions for user roles
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_agent(user):
    return user.groups.filter(name='Agent').exists()

def is_customer(user):
    return user.groups.filter(name='Customer').exists()

# SignUp View for Customers
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = form.save()

            # Check if the user was successfully created
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)

            # Check if the "Customer" group exists, create it if it doesn't
            customer_group, created = Group.objects.get_or_create(name='Customer')

            # Add the user to the "Customer" group
            user.groups.add(customer_group)

            # Automatically authenticate and log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Account created for {username}!")
                return redirect('tickets:ticket_list')  # Or your desired redirect
            else:
                messages.error(request, "Error during authentication after sign up.")
                return redirect('tickets:signup')
        else:
            # Debug the form errors
            print("Form errors:", form.errors)  # This will log form validation errors
            messages.error(request, "Please correct the errors below.")
            return render(request, 'tickets/signup.html', {'form': form})
    else:
        form = SignUpForm()
    
    return render(request, 'tickets/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate the user if the form is valid
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Successfully logged in!")
                return redirect('tickets:ticket_list')
            else:
                messages.error(request, "Invalid credentials")
                print("Invalid credentials entered")
        else:
            # Print more detailed form errors for debugging
            print("Form errors:", form.errors)  # Print all form errors
            for field, errors in form.errors.items():
                print(f"Field: {field}, Errors: {errors}")  # Detailed error per field
            messages.error(request, "Form is not valid")
    else:
        form = LoginForm()

    return render(request, 'tickets/login.html', {'form': form})

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(customer=request.user)
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

# Customer Dashboard View
@login_required
@user_passes_test(is_customer)
def customer_dashboard(request):
    return render(request, 'tickets/customer_dashboard.html')

# Agent Dashboard View
@login_required
@user_passes_test(is_agent)
def agent_dashboard(request):
    return render(request, 'tickets/agent_dashboard.html')

# Admin Dashboard View
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'tickets/admin_dashboard.html')

# Change Ticket View (Admin/Agent Permission)
@permission_required('tickets.change_ticket', raise_exception=True)
def change_ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    return render(request, 'tickets/change_ticket.html', {'ticket': ticket})
