# tickets/urls.py

from django.urls import path
from . import views

app_name = 'tickets'  # Make sure you have this to namespace the URLs correctly

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('ticket-list/', views.ticket_list, name='ticket_list'),  # Ensure this exists

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('agent-dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
]
