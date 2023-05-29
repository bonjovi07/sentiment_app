from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static

app_name = 'feedback'
urlpatterns = [
    path('',views.index,name='index'),
        #Login
        path('loginview', views.loginview, name='loginview'),
        path('login/process', views.process, name='process'),
        path('logout', views.processlogout, name='processlogout'),

        #Account
        path('home', views.home, name='home'),
        path('adminhome',views.adminhome, name="adminhome"),
        path('accountsearch', views.accountsearch, name='accountsearch'),
        path('adminaddacc', views.adminAddAcc, name="adminaddacc"),
        path('adminaddacc/add_acc', views.add_acc, name="add_acc") ,
        # path('<int:user_id>/delete_acc/', views.delete_acc, name='delete_acc'),
        path('<int:user_id>/deactivate_acc/', views.deactivate_acc, name='deactivate_acc'),
        path('<int:user_id>/activate_acc/', views.activate_acc, name='activate_acc'),
        path('<int:user_id>/edit_acc/', views.edit_acc, name='edit_acc'),
        path('<int:user_id>/process_acc_edit/', views.process_acc_edit, name='process_acc_edit'),

        #User Settings
        path('usersettings', views.usersettings, name="usersettings"),
        path('editusersettings', views.editusersettings, name="editusersettings"),
        path('<int:user_id>/updateusersettings/',views.updateusersettings, name="updateusersettings"),

        #Employee
        path('employeelist', views.employeelist, name="employeelist"),
        path('employeesearch', views.employeesearch, name='employeesearch'),
        path('addemployee', views.addemployee, name='addemployee'),
        path('processaddemployee', views.processaddemployee, name='processaddemployee'),
        path('<int:employee_id>/deactivate_employee/',views.deactivate_employee,name="deactivate_employee"),
        path('<int:employee_id>/activate_employee/',views.activate_employee,name="activate_employee"),
        # path('<int:employee_id>/delete_employee/',views.delete_employee,name="delete_employee"),
        path('<int:employee_id>/edit_employee/',views.edit_employee,name="edit_employee"),
        path('<int:employee_id>/process_edit_employee/', views.process_edit_employee, name='process_edit_employee'),

        #Feedback
        path('generate_feedbackhome', views.generate_feedbackhome, name="generate_feedbackhome"),
        path('generate_client',views.generate_client,name="generate_client"),
        path('client_process', views.client_process, name="client_process"),
        path('client_feedback/<str:token>/<str:encrypt>/', views.client_feedback, name='client_feedback'),
        path('process_feedback',views.process_feedback, name="process_feedback"),
        path('thankyou', views.thankyou, name="thankyou"),

        #reports
        path('reportshome',views.reportshome, name='reportshome'),
        path('report_offices', views.report_offices, name='report_offices'),
        path('report_offices_search', views.report_offices_search, name='report_offices_search'),
        path('<int:user_id>/reports_feedbacks_search',views.reports_feedbacks_search,name='reports_feedbacks_search'),
        path('<int:user_id>/reports_officesummary',views.reports_officesummary,name='reports_officesummary'),
        path('<int:user_id>/reports_feedbacks',views.reports_feedbacks,name='reports_feedbacks'),
        path('<int:user_id>/reports_viewreports',views.reports_viewreports,name='reports_viewreports'),
        path('<int:user_id>/reports_viewreports_search',views.reports_viewreports_search,name='reports_viewreports_search'),
        path('<int:user_id>/reports_staff',views.reports_staff,name='reports_staff'),
        path('<int:user_id>/reports_staff_search',views.reports_staff_search,name='reports_staff_search'),
        path('<int:user_id>/<int:client_id>/reports_single',views.reports_single, name='reports_single'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)