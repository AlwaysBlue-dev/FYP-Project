from django.contrib import admin
from django.urls import path
from main_app import views



#Django Admin Customization
admin.site.site_header = "ZUFESTM Admin Panel"
admin.site.site_title = "ZUFESTM Portal Admin Panel"
admin.site.index_title = "Administration"
app_name = 'faculty'

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.user_login, name='user_login'),
    path("login/", views.user_login, name='user_login'),
    path("logout/", views.user_logout, name='user_logout'),
    path('stu_dashboard/', views.stu_dashboard_view, name='stu_dashboard'),
    path('stu_dashboard/stu_profile', views.stu_profile, name='stu_profile'),
    path('hod_dashboard/', views.hod_dashboard_view, name='hod_dashboard'),
    path('fac_dashboard/', views.fac_dashboard_view, name='fac_dashboard'),
    path('fac_dashboard/fac_profile', views.fac_profile, name='fac_profile'),
    path('fac_dashboard/create_classroom', views.fac_create_classroom, name='fac_create_clasroom'),
    path('fac_dashboard/delete_classroom/<int:classroom_id>', views.teacher_delete_classroom, name='delete_classroom'),
    path('fac_dashboard/classroom_dashboard', views.fac_classroom_dashboard, name='fac_classroom_dashboard'),
    path('fac_dashboard/classroom_dashboard/<int:classroom_id>', views.fac_classroom_detail, name='fac_classroom_detail'),
    path('fac_dashboard/classroom_dashboard/<int:classroom_id>/lectures_upload', views.lectures_upload, name='lecture_upload'),
    path('fac_dashboard/delete_lecture/<int:lecture_id>', views.teacher_delete_lecture, name='delete_lecture'),
    path('fac_dashboard/classroom_dashboard/<int:classroom_id>/quiz_upload', views.quiz_upload, name='quiz_upload'),
    path('fac_dashboard/delete_quiz/<int:quiz_id>', views.teacher_delete_quiz, name='delete_quiz'),
    path('fac_dashboard/classroom_dashboard/<int:classroom_id>/assignment_upload', views.assignment_upload, name='assignment_upload'),
    
    path('fac_dashboard/view_assignment_submissions/<int:assign_id>/', views.view_assignment_submission, name='view_assignment_submission'),
    path('fac_dashboard/view_assignment_submissions/<int:assign_id>/assign_assignment_marks', views.assign_assignment_marks, name='assign_assignment_marks'),
   

    path('fac_dashboard/view_quiz_submissions/<int:quiz_id>/', views.view_quiz_submission, name='view_quiz_submission'),
    path('fac_dashboard/view_quiz_submissions/<int:quiz_id>/assign_quiz_marks', views.assign_quiz_marks, name='assign_quiz_marks'),
   
  
   
   
    path('fac_dashboard/delete_assignment/<int:assign_id>', views.teacher_delete_assignment, name='delete_assignment'),
    path('fac_dashboard/classroom_dashboard/<int:classroom_id>/announcement_upload', views.announcement_upload, name='announcement_upload'),
    path('fac_dashboard/delete_announcement/<int:ann_id>', views.teacher_delete_announcement, name='delete_announcement'),
    path('fac_dashboard/joined_students/<int:classroom_id>', views.joined_students, name='joined_students'),

    path('stu_dashboard/classroom_dashboard', views.stu_classroom_dashboard, name='stu_classroom_dashboard'),
    path('stu_dashboard/join_classroom', views.stu_join_classroom, name='stu_join_classroom'),
    path('stu_dashboard/stu_delete_classroom/<int:joined_classroom_id>', views.stu_delete_classroom, name='stu_delete_classroom'),
    path('stu_dashboard/classroom_dashboard/<int:joined_classroom_id>', views.stu_classroom_detail, name='stu_classroom_detail'),
   
    path('stu_dashboard/classroom_dashboard/<int:joined_classroom_id>/lectures_view', views.stu_lectures_view, name='stu_lectures_view'),
    
    path('stu_dashboard/classroom_dashboard/<int:joined_classroom_id>/quiz_view', views.stu_quiz_view, name='stu_quiz_view'),
    path('stu_dashboard/classroom_dashboard/<int:quiz_id>/quiz_submission/<int:joined_classroom_id>', views.stu_quiz_submission, name='stu_quiz_submission'),
    path('stu_dashboard/classroom_dashboard/<int:quiz_id>/quiz_submission/<int:joined_classroom_id>/view_quiz_result', views.stu_view_quiz_result, name='stu_view_quiz_result'),
    path('stu_dashboard/stu_delete_quiz/<int:quiz_id>', views.stu_delete_quiz, name='stu_delete_quiz'),
    
    path('stu_dashboard/classroom_dashboard/<int:joined_classroom_id>/assignment_view', views.stu_assignment_view, name='stu_assignment_view'),
    path('stu_dashboard/classroom_dashboard/<int:assign_id>/assignment_submission/<int:joined_classroom_id>', views.stu_assignment_submission, name='stu_assignment_submission'),
    path('stu_dashboard/classroom_dashboard/<int:assign_id>/assignment_submission/<int:joined_classroom_id>/view_assignment_result', views.stu_view_assignment_result, name='stu_view_assignment_result'),
    path('stu_dashboard/stu_delete_assignment/<int:assignment_id>', views.stu_delete_assignment, name='stu_delete_assignment'),
    
    path('stu_dashboard/classroom_dashboard/<int:joined_classroom_id>/announcement_view', views.stu_announcement_view, name='stu_announcement_view'),

    path('fac_dashboard/attendance/', views.fac_attendance, name='fac_attendance'),

    path('fac_dashboard/attendance/student_list/<int:course_id>', views.student_list, name='student_list'),

    path('fac_dashboard/attendance/submit_attendance', views.submit_attendance, name='submit_attendance'),

    path('fac_dashboard/attendance/view_attendance/<int:course_id>/<int:fac_id>', views.view_attendance, name='view_attendance'),
    path('fac_dashboard/attendance/update_attendance/<int:attendance_id>', views.update_attendance, name='update_attendance'),
    
    path('fac_dashboard/add_clo', views.add_clo, name='add_clo'),

    path('fac_dashboard/map_clo_plo', views.map_clo_plo, name='map_clo_plo'),

    path('fac_dashboard/add_assessment_clos_plos', views.add_assessment_clos_plos, name='add_assessment_clos_plos'),

    path('fac_dashboard/upload_result', views.upload_result, name='upload_result'),

    path('fac_dashboard/view_result', views.view_result, name='view_result'),

    path('fac_dashboard/export_csv', views.export_csv, name='export_csv'),



  
]
