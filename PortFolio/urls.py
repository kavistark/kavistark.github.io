from django.urls import path
from . import views
from .views import ProfileView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('student/', views.student, name='student'),
    path('delete_profile_image/', views.delete_profile_image, name='delete_profile_image'),
    
    path('dashboard/',views.dashboard,name='dashboard'),
    path('activity/',views.activity,name='activity'),
    path('resume/',views.resume,name='resume'),

    path('waiting/', views.waiting_page, name='waiting_page'),
    path('home/', views.home, name='homepage'),
    
    # staff
    path('adminpage/', views.admin, name='adminpage'),
    path('decline/', views.decline_page, name='decline_page'),
    path('approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('decline/<int:request_id>/', views.decline_request, name='decline_request'),
    path('student_access_list/',views.student_list,name='student_list'),
    path('student/<int:student_id>/', views.student_details, name='student_details'),
    
    path("folder/<int:folderid>/",views.folder, name="folder"),
    path("addFolder/", views.addfolder, name="addfolder"),
    path("delete_folder/<int:folder_id>/", views.delete_folder, name="delete_folder"),
    path("delete_file/<int:file_id>/", views.delete_file, name="delete_file"),
    path('get_folder_file_data/', views.get_folder_file_data, name='get_folder_file_data'),
    path('get_folder_data/', views.get_folder_data, name='get_folder_data'),

    path('profile_visits/', views.profile_visits1, name='profile_visits1'),

    path('generate_qr_code/<str:generated_link>/', views.generate_qr_code, name='generate_qr_code'),
    path('logout/', views.logout_view, name='logout_view'),
    path('generate_link/', views.generate_visit_link, name='generate_visit'),
    path('profile_visits/<str:generated_link>/', views.profile_visits, name='profile_visits'),
    
 ]

    