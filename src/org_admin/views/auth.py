from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render
from commonui.views import check_if_hx
def sign_in(request):
    if request.method == "GET":
        return render(request, "org_admin/sign_in.html", {"hx": check_if_hx(request)})
    
    if request.method == "POST":
            username = request.POST["email"]
            password = request.POST["password"]

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                request.method = "GET"
                return HttpResponseRedirect("/org_admin/")

            else:
                try:
                    #get username from submitted email
                    if username != "" or username != None:
                        user = User.objects.get(email=username)
                        username = user.username
                        user = authenticate(request, username=username, password=password)
                        if user is not None:
                            login(request, user)
                            return HttpResponseRedirect("/org_admin/")
                        else:
                            return render(request, "org_admin/sign_in.html", {"hx": check_if_hx(request), "error": "Incorrect username or password"})
                    if user is not None:
                        login(request, user)
                        return HttpResponseRedirect("/org_admin/")
                    else:
                        return render(request, "org_admin/sign_in.html", {"hx": check_if_hx(request), "error": "Incorrect username or password"})
                except Exception as e:
                    return render(request, "org_admin/sign_in.html", {"hx": check_if_hx(request), "error": e})
