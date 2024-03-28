"""claudecn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from claudecn.view.Views import *
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('cnaude/assistant/', assistant),
    path('cnaude/login/', login),
    path('cnaude/latest_session/', latest_session),
    path('cnaude/list_session/', list_session),
    path('cnaude/member_info/', member_info),
    path('cnaude/del_session/', del_session),
    path('cnaude/get_captcha/', get_captcha),
    path('cnaude/generate_session/', generate_session),
    path('cnaude/register/', register),
    path('cnaude/member_edit/', member_edit),
    path('cnaude/del_conversation/', del_conversation),

]
