# hubspot_oauth/urls.py

from django.urls import path
from .views import (
    hubspot_callback,
    get_contacts,
    oauth_home,
    oauth_login,
    get_companies,
    oauth_backend_redirect  
)

urlpatterns = [
    path('', oauth_home),
    path('login/', oauth_login),
    path('callback/', hubspot_callback),
    path('contacts/', get_contacts),
    path('companies/', get_companies),
    path('backend/', oauth_backend_redirect), 
]
