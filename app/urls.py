"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings as s
from django.conf.urls.static import static
from django.views.generic.base import TemplateView


urlpatterns = [
    path('politika/', TemplateView.as_view(template_name='quizzes/politika.html'), name='politika'),
    path('theory/', TemplateView.as_view(template_name='quizzes/theory.html'), name='theory'),
    path('theory/road-markings/', TemplateView.as_view(template_name='quizzes/road_markings.html'), name='road_markings'),
    path('theory/road-signs/', TemplateView.as_view(template_name='quizzes/road_signs.html'), name='road_signs'),
    path('theory/fines/', TemplateView.as_view(template_name='quizzes/theory_fines.html'), name='theory_fines'),
    path('theory/traffic-light/', TemplateView.as_view(template_name='quizzes/theory_traffic_light.html'), name='theory_traffic_light'),
    path('theory/regulator/', TemplateView.as_view(template_name='quizzes/theory_regulator.html'), name='theory_regulator'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('quizzes.urls')),
]

if s.DEBUG:
    urlpatterns += static(s.MEDIA_URL, document_root=s.MEDIA_ROOT)
