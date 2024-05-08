from io import BytesIO
from django.urls import reverse_lazy
from django.shortcuts import render
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo
from organisations.models import Image as OrgImage, Video as OrgVideo, Organisation
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from .common import check_ownership
from ..models import OrganisationAdmin
from .views import details
from .opportunity_details import opportunity_details
from PIL import Image as PImage
import os
import cv2
from django.core.files.base import ContentFile


def opportunity_gallery(request, id):
    opportunity = Opportunity.objects.get(id=id)
    opp_images = OppImage.objects.filter(opportunity=opportunity)
    opp_videos = OppVideo.objects.filter(opportunity=opportunity)
    print(len(opp_images))
    context = {
        "hx": check_if_hx(request),
        "opportunity": opportunity,
        "opp_images": opp_images,
        "opp_videos": opp_videos,
    }
    
    return render(request, "org_admin/partials/opportunity_gallery.html", context=context)
    
    


def delete_media(request, id, location, media_type):
    
    return_id = None
    
    if location == "opportunity_media":
        media = OppImage.objects.get(id=id)
        return_id = media.opportunity.id
    
    if media_type == "image" and location == "org_media":
        media = OrgImage.objects.get(id=id)
    elif media_type == "video" and location == "org_media":
        media = OrgVideo.objects.get(id=id)
    elif media_type == "image" and location == "opportunity_media":
        media = OppImage.objects.get(id=id)
    elif media_type == "video" and location == "opportunity_media":
        media = OppVideo.objects.get(id=id)
    else:
        return details(request, error="Media type not found")
    
    if check_ownership(request, media):
        media.delete()
    else:
        return details(
            request, error="You do not have permission to delete this media"
        )

    if location == "org_media" and request.user.is_superuser:
        return HTTPResponseHXRedirect('/org_admin/organisations/{}/'.format(media.organisation.id))
    if location == "org_media": return HTTPResponseHXRedirect('/org_admin/details/')
    elif location == "opportunity_media": return HTTPResponseHXRedirect('/org_admin/opportunities/{}/gallery/'.format(return_id))

def upload_media(request, location, id=None, organisation_id=None):
    if request.method == "GET":
        if request.user.is_superuser and organisation_id and location == "org_media":
            organisation = Organisation.objects.get(id=organisation_id)
            url = "/org_admin/upload_media/organisation_image/{}/".format(organisation_id)
        elif request.user.is_superuser and location == "org_media":
            return details(request, error="Organisation not found")
        elif location == "org_media":
            url = reverse_lazy("upload_media_organisation")
        elif location == "opportunity_media":
            url = reverse_lazy("upload_media_opportunity", args=[id])
            
        return render(
            request,
            "org_admin/partials/file_upload.html",
            {"hx": check_if_hx(request), "upload_url": url},
        )

    elif request.method == "POST":
        data = request.POST
        file = request.FILES["file"]
        file_type = file.content_type.split("/")[1]
        print(file_type)
        #generate_thumbnails_optimise()

        # emergency_contact = emergency_contact_form.save(commit=False)
        # emergency_contact.volunteer = volunteer
        try:
            if file_type in ["jpeg", "png", "jpg"]:
                print("image")
                if location == "org_media":
                    
                    if request.user.is_superuser and organisation_id:
                        organisation = Organisation.objects.get(id=organisation_id)
                    elif request.user.is_superuser:
                        return details(request, error="Organisation not found")
                    else:
                        organisation = OrganisationAdmin.objects.get(user=request.user).organisation
                    
                    image_instance = OrgImage.objects.create(
                        image=file,
                        organisation=organisation,
                    )
                    
                    pil_photo = PImage.open(image_instance.image.path)
                    pil_photo.thumbnail((300, 300))
                    file = BytesIO()
                    pil_photo.save(file, file_type.upper())
                    image_instance.thumbnail_image.save(image_instance.image.name,  ContentFile(file.getvalue()), save=False)
                    image_instance.save()
                    
                elif location == "opportunity_media":
                    image_instance = OppImage.objects.create(
                        image=file,
                        opportunity=Opportunity.objects.get(id=id),
                    )
                    print
                    pil_photo = PImage.open(image_instance.image.path)
                    pil_photo.thumbnail((300, 300))
                    file = BytesIO()
                    pil_photo.save(file, file_type.upper())
                    image_instance.thumbnail_image.save(image_instance.image.name,  ContentFile(file.getvalue()), save=False)
                    image_instance.save()
                    
            elif file_type == "mp4":
                if location == "org_media":
                    if request.user.is_superuser and organisation_id:
                        organisation = Organisation.objects.get(id=organisation_id)
                    elif request.user.is_superuser:
                        return details(request, error="Organisation not found")
                    else:
                        organisation = OrganisationAdmin.objects.get(user=request.user).organisation
                      
                      
                        
                    video = OrgVideo.objects.create(
                    video=file,
                    organisation=organisation,
                        )
                    video.save()
                    save_video_thumbnail(video)
                
                elif location == "opportunity_media":
                    video = OppVideo.objects.create(
                        video=file,
                        opportunity=Opportunity.objects.get(id=id),
                    )
                    save_video_thumbnail(video)

            if location == "org_media" and organisation_id:
                return HTTPResponseHXRedirect('/org_admin/organisations/{}/'.format(organisation_id))
            elif location == "org_media":
                return HTTPResponseHXRedirect('/org_admin/details/')
            elif location == "opportunity_media":
                return HTTPResponseHXRedirect(
                    '/org_admin/opportunities/{}/gallery/'.format(id)
                )
        except Exception as e:
            print("Something went wrong: ",e)
            if location == "org_media":
                return HTTPResponseHXRedirect('/org_admin/details/')
            elif location == "opportunity_media":
                return HTTPResponseHXRedirect(
                    '/org_admin/opportunities/{}/gallery/'.format(id)
                )
                
def generate_thumbnails_optimise():
    images = OrgImage.objects.all()
    for image in images:
        pil_photo = PImage.open(image.image.path)
        pil_photo.thumbnail((300, 300))
        file = BytesIO()
        pil_photo.save(file, "JPEG")
        image.thumbnail_image.save(image.image.name,  ContentFile(file.getvalue()), save=False)
        image.save()
        print("Optimised")
        
    print("Done")
    
    
def get_video_thumbnail(video):
    video = cv2.VideoCapture(video)
    #fix colours 
    
    print("video cv2")
    success, image = video.read()
    coloured = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print(success, "stage 2")
    if success:
        
        pil_image = PImage.fromarray(coloured)
        print("pil_image")
        pil_image.thumbnail((1920, 1080))
        file = BytesIO()
        pil_image.save(file, "JPEG")
        return file
    return None

def save_video_thumbnail(video_model):
    filename_without_extension = os.path.splitext(video_model.video.name)[0].strip('videos/')[1]+".jpg"
    print(filename_without_extension)
    video_content_file = ContentFile(get_video_thumbnail(video_model.video.path).getvalue())
    video_model.video_thumbnail.save(filename_without_extension, video_content_file, save=False)
    video_model.save()