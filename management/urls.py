from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name= 'index'),
    path('addmission/', views.addmission, name='addmission'),
    path('save_confirmation/', views.save_confirmation, name='save_confirmation'),
    path('cancel_confirmation/', views.cancel_confirmation, name='cancel_confirmation'),
    path('statement/<int:pk>/', views.statement, name= 'statement'),
    path('manage-database/', views.manage_database, name= 'manage-database'),
    path('addmission/payment-method/', views.payment_method, name= 'payment-method'),
    path('search-statement/', views.search_statement, name= 'search-statement'),
    path('search-view/', views.search_view, name= 'search-statement'),
    path('search-student/', views.search_student, name= 'search-view'),
    path('pre-search-deposite/', views.pre_search_deposit, name= 'pre-search-deposit'),
    path('fee-deposite/<int:pk>/', views.fee_deposite, name= 'fee_deposite'),
    path('confirm_deposit/', views.confirm_deposit, name='confirm_deposit'),
    path('show_deposit_information/', views.show_deposit_information, name='show_deposit_information'),
    path('search/', views.search_by_admission_year, name='search_by_admission_year'),
    path('level_up/', views.level_up_students, name='level_up_students'),
    path('level_up_success/', views.level_up_success, name='level_up_success'),
    path('search_report/', views.search_report, name='search_report'),
    path('pre_report_view/', views.pre_report, name='pre_report_view'),
    # path('see_student_report/<int:pk>/', views.see_student_report, name='see_student_report'),
    path('upload/', views.upload_file, name='upload_file'),
    path('upload_installment/', views.upload_installments, name='upload_installments'), 
    path('upload/success/', views.upload_success, name='upload_success'),
    path('upload/failed/', views.upload_failed, name='upload_failed'),
    path('select_period/', views.select_period, name='select_period'),
     path('download-student-info-demo/', views.download_student_info_demo, name='download_student_info_demo'),
    path('download-student-installment-demo/', views.download_student_installment_demo, name='download_student_installment_demo'),

]