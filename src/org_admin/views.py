from django.shortcuts import render
from .models import OrgnaisationAdmin
from commonui.views import check_if_hx
from django.forms import formset_factory
from webpush import send_group_notification
from organisations.models import Location, Video as OrgVideo, Image as OrgImage
from .forms import OrganisationLocationForm
# Create your views here.
def index (request, error=None):
    try:
        orgnaisation = OrgnaisationAdmin.objects.get(user=request.user)
    except OrgnaisationAdmin.DoesNotExist:
        return render(request, 'org_admin/no_admin.html', {'hx' : check_if_hx(request)})
    

    return render(request, 'org_admin/index.html', {'hx' : check_if_hx(request), 'error': error, 'organisation':orgnaisation.organisation, 'admin': request.user})

def media(request):
    if request.method == 'POST':
        data = request.POST
        if 'video' in data:
            video = OrgVideo.objects.create(
                title = data['title'],
                video = data['video'],
                organisation = OrgnaisationAdmin.objects.get(user=request.user).organisation
            )
            video.save()
            return details(request)
        elif 'image' in data:
            image = OrgImage.objects.create(
                title = data['title'],
                image = data['image'],
                organisation = OrgnaisationAdmin.objects.get(user=request.user).organisation
            )
            image.save()
            return details(request)

#Location crud views
def location(request, id=None, delete=False):
    if request.method == 'POST':
        print(request.POST)
        data = request.POST
        print (data['organisation'])
        if data['locationID'] != "":
            location = Location.objects.get(id=data['locationID'])
            if OrgnaisationAdmin.objects.get(user=request.user).organisation.id != location.organisation.id:
                return details(request, error="You do not have permission to edit this location")
            else:
                form = OrganisationLocationForm(data, instance=location)
                if form.is_valid():
                    form.save()
                    return details(request)
                else:
                    return details(request, error=form.errors)
        else:
            form = OrganisationLocationForm(data)
            if form.is_valid():
                form.save()
                return details(request)
            else:
                return details(request, error=form.errors)
                
    if id != None:
        try:
            location = Location.objects.get(id=id)
        except Location.DoesNotExist:
            return details(request, error="Location does not exist")
            
    if delete:
        try:
            location.delete()
            return details(request)
        except Exception as e:
            return details(request, error=e)
    else:
        return render(request, 'org_admin/partials/add_location.html', {'hx' : check_if_hx(request), 'location': location, 'org_id': OrgnaisationAdmin.objects.get(user=request.user).organisation.id})
    

def details(request, error=None):
    try:
        orgnaisation = OrgnaisationAdmin.objects.get(user=request.user)
    except OrgnaisationAdmin.DoesNotExist:
        return render(request, 'org_admin/no_admin.html', {'hx' : check_if_hx(request)})
    
    org_videos = OrgVideo.objects.filter(organisation=orgnaisation.organisation)
    org_images = OrgImage.objects.filter(organisation=orgnaisation.organisation)


    context = {
        'hx' : check_if_hx(request),
        'locations': Location.objects.filter(organisation=orgnaisation.organisation),
        'organisation': orgnaisation.organisation,
        'org_videos': org_videos,
        'org_images': org_images,
        'error': error
    }

    return render(request, 'org_admin/organisation_details_admin.html', context)
