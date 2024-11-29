from django.contrib import admin
from django.urls import path
from parser import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("",views.upload_resume, name="upload_resume"),
    path("edit_form/",views.parse_resume, name="edit_form"),
     path('save-data/', views.save_data, name='save_data'),

]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
