"""
URL configuration for volunteeringSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.i18n import JavaScriptCatalog
from django.conf import  settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib.auth.models import User
from volunteer.models import Volunteer, VolunteerAddress, EmergencyContacts, VolunteerConditions, VolunteerInterest
from organisations.models import Organisation, Image as OrganisationImage, Location as OrganisationLocation, thematicCategory as OrganisationTheme, organisationnThematicLink as OrganisationThematicLink
js_info_dict = {
    'packages': ('recurrence', ),
}

urlpatterns = [
    path("supervisor/", include("rota.urls")),
    path("organisations/", include("organisations.urls")),
    path("opportunities/", include("opportunities.urls")),
    path("volunteer/", include("volunteer.urls")),
    path("explore/", include("explore.urls")),
    path("forms/", include("forms.urls")),
    path("", include("commonui.urls")),
    path('admin/', admin.site.urls),
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(), js_info_dict),
    path('', include('pwa.urls')),  # You MUST use an empty string as the URL prefix
    path('org_admin/', include('org_admin.urls')),
    path('webpush/', include('webpush.urls')),
    path('communications/', include('communications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
