from django.shortcuts import render

def reporting(request):
    return render(request, 'org_admin/reporting.html')

