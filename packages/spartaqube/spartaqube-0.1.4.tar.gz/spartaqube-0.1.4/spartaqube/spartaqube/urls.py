from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_cd458aa7f0.sparta_4b302aecd6.qube_1483045b8e.sparta_4014f099df'
handler500='project.sparta_cd458aa7f0.sparta_4b302aecd6.qube_1483045b8e.sparta_28d467558e'
handler403='project.sparta_cd458aa7f0.sparta_4b302aecd6.qube_1483045b8e.sparta_ebee8659ef'
handler400='project.sparta_cd458aa7f0.sparta_4b302aecd6.qube_1483045b8e.sparta_a504cb6ddc'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]