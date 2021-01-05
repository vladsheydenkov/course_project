from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.mail import send_mail

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models
from . import forms

# Create your views here.

TEMPLATE = ("{title} at {uri} \n\n {name} asks you to review"
            "Comment:\n\n {comment}")


class MaterialListView(LoginRequiredMixin, ListView):
    queryset = models.Material.objects.all()
    context_object_name = 'materials'
    template_name = 'materials/all_materials.html'


@login_required
def all_materials(request):
    materials = models.Material.objects.all()
    return render(request,
                  'materials/all_materials.html',
                  {'materials': materials})


def material_details(request, year, month, day, slug):
    material = get_object_or_404(models.Material,
                                 slug=slug,
                                 publish__year=year,
                                 publish__month=month,
                                 publish__day=day)
    if request.method == 'POST':
        comment_form = forms.CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.material = material
            new_comment.save()
            return redirect(material)
    else:
        comment_form = forms.CommentForm()
    return render(request,
                  'materials/detail.html',
                  {'material': material,
                   'form': comment_form})


def share_material(request, material_id):
    material = get_object_or_404(models.Material,
                                 id=material_id,
                                 )
    sent = False
    if request.method == 'POST':
        form = forms.EmailMaterialForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            material_uri = request.build_absolute_uri(
                material.get_absolute_url()
            )

            subject = "{} asks you to review: {}". format(
                cd['name'],
                material.title,
            )

            body = TEMPLATE.format(
                title=material.title,
                uri=material_uri,
                name=cd['name'],
                comment=cd['comment'],
            )

            send_mail(subject,
                      body,
                      'supersiteadmin@mysote.com',
                      [cd['to_email'], ])
            sent = True
    else:
        form = forms.EmailMaterialForm()

    return render(request,
                  'materials/share.html',
                  {'material': material, 'form': form, 'sent': sent})


def create_form(request):
    if request.method == 'POST':
        material_form = forms.MaterialForm(request.POST)
        if material_form.is_valid():
            new_material = material_form.save(commit=False)
            new_material.author = User.objects.first()
            new_material.slug = new_material.title.replace(' ', '-')
            new_material.save()
            created = True
            return render(request,
                          'materials/create.html',
                          {'material': new_material, 'created': created})
    else:
        material_form = forms.MaterialForm()
        return render(request,
                      'materials/create.html',
                      {'form': material_form})


def user_login(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['login'],
                password=cd['password'],
            )
            if user is None:
                return HttpResponse('BAD CREDS')
            else:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Auth success')
                else:
                    return HttpResponse('user inactive')
    else:
        form = forms.LoginForm()
        return render(request,
                      'login.html',
                      {'form': form})


@login_required
def view_profile(request):
    return render(request, 'profile.html', {'user': request.user})
