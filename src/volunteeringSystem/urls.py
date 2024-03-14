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

from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

class VolunteerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Volunteer
        fields = ['url', 'user', 'avatar', 'date_of_birth', 'phone_number', 'bio', 'CV']

class VolunteerAddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VolunteerAddress
        fields = ['url', 'first_line', 'second_line', 'postcode', 'city', 'volunteer']

class EmergencyContactsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmergencyContacts
        fields = ['url', 'name', 'relation', 'phone_number', 'email', 'volunteer']

class VolunteerConditionsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VolunteerConditions
        fields = ['url', 'name', 'disclosures', 'volunteer']

class VolunteerInterestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VolunteerInterest
        fields = ['url', 'tag', 'volunteer']


class OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organisation
        fields = ['url', 'name', 'description']

class OrganisationImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OrganisationImage
        fields = ['url', 'image', 'organisation']

class OrganisationLocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OrganisationLocation
        fields = ['url', 'name', 'description', 'first_line', 'second_line', 'postcode', 'city', 'organisation']

class OrganisationThemeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OrganisationTheme
        fields = ['url', 'hex_colour', 'name', 'image']
    
class OrganisationThematicLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OrganisationThematicLink
        fields = ['url', 'organisation', 'theme']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class VolunteerViewSet(viewsets.ModelViewSet):
    queryset = Volunteer.objects.all()
    serializer_class = VolunteerSerializer

class VolunteerAddressViewSet(viewsets.ModelViewSet):
    queryset = VolunteerAddress.objects.all()
    serializer_class = VolunteerAddressSerializer

class EmergencyContactsViewSet(viewsets.ModelViewSet):
    queryset = EmergencyContacts.objects.all()
    serializer_class = EmergencyContactsSerializer

class VolunteerConditionsViewSet(viewsets.ModelViewSet):
    queryset = VolunteerConditions.objects.all()
    serializer_class = VolunteerConditionsSerializer

class VolunteerInterestViewSet(viewsets.ModelViewSet):
    queryset = VolunteerInterest.objects.all()
    serializer_class = VolunteerInterestSerializer

class OrganisationViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer

class OrganisationImageViewSet(viewsets.ModelViewSet):
    queryset = OrganisationImage.objects.all()
    serializer_class = OrganisationImageSerializer

class OrganisationLocationViewSet(viewsets.ModelViewSet):
    queryset = OrganisationLocation.objects.all()
    serializer_class = OrganisationLocationSerializer

class OrganisationThemeViewSet(viewsets.ModelViewSet):
    queryset = OrganisationTheme.objects.all()
    serializer_class = OrganisationThemeSerializer

class OrganisationThematicLinkViewSet(viewsets.ModelViewSet):
    queryset = OrganisationThematicLink.objects.all()
    serializer_class = OrganisationThematicLinkSerializer



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'volunteers', VolunteerViewSet)
router.register(r'volunteeraddresses', VolunteerAddressViewSet)
router.register(r'emergencycontacts', EmergencyContactsViewSet)
router.register(r'volunteerconditions', VolunteerConditionsViewSet)
router.register(r'volunteerinterests', VolunteerInterestViewSet)
router.register(r'organisations', OrganisationViewSet)
router.register(r'organisationimages', OrganisationImageViewSet)
router.register(r'organisationlocations', OrganisationLocationViewSet)
router.register(r'organisationthemes', OrganisationThemeViewSet)
router.register(r'organisationthematiclinks', OrganisationThematicLinkViewSet)

urlpatterns = [
    path("organisations/", include("organisations.urls")),
    path("opportunities/", include("opportunities.urls")),
    path("volunteer/", include("volunteer.urls")),
    path("explore/", include("explore.urls")),
    path("", include("commonui.urls")),
    path('admin/', admin.site.urls),
    path('djrichtextfield/', include('djrichtextfield.urls')),
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(), js_info_dict),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('pwa.urls')),  # You MUST use an empty string as the URL prefix
    path('org_admin/', include('org_admin.urls')),
    path('webpush/', include('webpush.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
