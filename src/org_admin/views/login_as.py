from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
@login_required
def login_as(request, user_id):

    if not (request.user.is_authenticated and request.user.is_active and request.user.is_superuser):
        raise PermissionDenied

    user = get_object_or_404(User, id=user_id)

    if user:
        login(user)

