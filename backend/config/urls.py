
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the HubSpot OAuth App!")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('oauth/', include('hubspot_oauth.urls')),  

]