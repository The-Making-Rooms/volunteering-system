from django.shortcuts import render
from organisations.models import thematicCategory, organisationnThematicLink
# Create your views here.

#get theme in software
def get_themes():
    themes = thematicCategory.objects.filter()
    print (themes)
    return themes

def index(request):
    context = {
        'themes' : get_themes(),
    }
    return render(request, 'explore/index.html', context=context)