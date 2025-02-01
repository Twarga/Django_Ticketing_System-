from django.contrib import admin
from .models import Ticket, TicketHistory, Feedback, UserProfile

admin.site.register(UserProfile)

admin.site.register(Ticket)
admin.site.register(TicketHistory)
admin.site.register(Feedback)