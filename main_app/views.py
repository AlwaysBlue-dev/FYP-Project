from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import LoginUser
from .forms import ClassroomForm, LectureUploadForm, QuizUploadForm, AssignmentUploadForm, AnnouncementUploadForm, QuizSubmissionForm, AssignmentSubmissionForm
from .models import Classroom, Faculty, Lecutre, Quiz, Assignment, Announcement, AssignCourse, Course, Student,  StudentJoinedClassroom,  QuizSubmission, AssignmentSubmission, Department, HOD, TotalBatche, StudentAttendance, DepartProgramme, FacultyJobDetail,  StudentRegisterCourse, AddCourseClo, MapCourseCloPlo, AddAssessmentClosPlo, UploadResult, PushNotification 
from django.contrib import messages
import random
import string
from django.conf import settings
import os
from django.http import FileResponse
import mimetypes
from django.views.generic import ListView
from django.db.models import Max
from datetime import datetime, date
import json
from django.http import JsonResponse,  HttpResponseBadRequest
from django.db import connection
import csv

# Create your views here.
def user_login(request):
    if request.method == 'POST':
        # Retrieve the email and password from the form
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Attempt to authenticate the user by filtering the LoginUser model by email and password
        user = LoginUser.objects.filter(user_email=email, user_password=password).first()

        # If a user was found, proceed to render the appropriate dashboard
        if user is not None:
            request.session['user_id'] = user.user_id

            if user.user_type == 'Student':
                return redirect('/stu_dashboard')
            elif user.user_type == 'HOD':
                return redirect('/hod_dashboard')
            elif user.user_type == 'Teacher':
                return redirect('/fac_dashboard')
            elif user.user_type == 'HOD & Teacher':
                context = {'user_id': user.user_id, 
                           'user_type':user.user_type,
                           'user_detail':Faculty.objects.filter(fac_email__user_email=user.user_email).first()}
                return render(request, 'login.html', context)
        # If no user was found, return an error message on the login page
        else:
            error_message = 'Invalid login credentials'
            return render(request, 'login.html', {'error_message': error_message})

    # If the request method is not POST, check if the user is already authenticated
    elif 'user_id' in request.session:
        # If the user id is stored in the session, retrieve the user information from the LoginUser model
        user = LoginUser.objects.filter(user_id=request.session['user_id']).first()

        # If the user was found, render the appropriate dashboard
        if user is not None:
            user_id = request.session.get('user_id')
            if user.user_type == 'Student':
                return redirect('/stu_dashboard')
            elif user.user_type == 'HOD':
                return redirect('/hod_dashboard')
            elif user.user_type == 'Teacher':
                return redirect('/fac_dashboard')
            elif user.user_type == 'HOD & Teacher':
                context = {'user_id': user.user_id, 
                           'user_type':user.user_type,
                           'user_detail':Faculty.objects.filter(fac_email__user_email=user.user_email).first()}
                return render(request, 'login.html', context)

    # If the user id is not stored in the session or none of the conditions are met, render the login page
    return render(request, 'login.html')

def choose_role(request):
    if request.method == 'POST':
        chosen_role = request.POST.get('chosen_role')

        if chosen_role == 'HOD':
            return redirect('/hod_dashboard')
        elif chosen_role == 'Teacher':
            return redirect('/fac_dashboard')

    # Handle invalid or no selection
    error_message = 'Invalid role selection'
    return render(request, 'login.html', {'error_message': error_message})

def user_logout(request):
    # Remove the user id from the session
    if 'user_id' in request.session:
        del request.session['user_id']
    # Redirect the user to the login page
    return redirect('/login')


def stu_dashboard_view(request):
    # Check if the user is logged in
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)

        if stu_data:
            joined_classrooms = StudentJoinedClassroom.objects.filter(
                student=stu_data[0].student_id)

            classrooms = Classroom.objects.filter(
                class_id__in=[jc.classroom.class_id for jc in joined_classrooms])

            student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
            if student_notifications:
                # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
                unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
                # Reverse the order of notifications
                student_notifications = student_notifications.order_by('-created_at')
                if unread_notifications:
                    context = {'stu_data': stu_data, 'classrooms': classrooms, 'notifications':student_notifications, 'unread_notifications':unread_notifications}
                else:
                    context = {'stu_data': stu_data, 'classrooms': classrooms, 'notifications':student_notifications}
               
            else:
                context = {'stu_data': stu_data, 'classrooms': classrooms}

            
        else:
            # Code for rendering the student dashboard
            return render(request, 'student/stu_dashboard.html')

        # Code for rendering the student dashboard
        return render(request, 'student/stu_dashboard.html', context)


def hod_dashboard_view(request):
    # Check if the user is logged in
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')

        hod_data = HOD.objects.filter(user_id=user_id)
        user= LoginUser.objects.filter(user_id=user_id).first()
        user_type = user.user_type

        if hod_data:
            context = {
                'hod_data': hod_data,
                'user_type':user_type,
            }
            return render(request, 'hod/hod_dashboard.html', context)

        else:
            return render(request, 'hod/hod_dashboard.html')


def fac_dashboard_view(request):
    # Check if the user is logged in
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        logged_in_user_id = request.session.get('user_id')
        user= LoginUser.objects.filter(user_id=user_id).first()
        user_type = user.user_type
        # assign_course = AssignCourse.objects.filter(
        #     faculty_id=fac_data[0].fac_id)

        # # Retrieve the course IDs from the AssignCourse queryset
        # course_ids = assign_course.values_list('assign_course', flat=True)

        # # Retrieve courses from the Course model that have matching IDs
        # courses = Course.objects.filter(course_id__in=course_ids)

        # # Retrieve classrooms created by faculty
        # classrooms = Classroom.objects.filter(fac_id=fac_data[0].fac_id)

        # fac_job_detail=FacultyJobDetail.objects.filter(faculty_id__user_id=user_id).first()
        context = {
            'fac_data': fac_data,
            'logged_in_user_id':logged_in_user_id,
            'user_type':user_type,
            # 'classrooms': classrooms,
            # 'courses': courses,
            # 'fac_job_details':fac_job_detail
        }

    # Code for rendering the teacher dashboard
    return render(request, 'faculty/fac_dashboard.html', context)


def fac_profile(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        assign_course = AssignCourse.objects.filter(
            faculty_id=fac_data[0].fac_id)

        assign_course = AssignCourse.objects.filter(
            faculty_id=fac_data[0].fac_id, active=True)

        # # Retrieve the course IDs from the AssignCourse queryset
        # course_ids = assign_course.values_list('assign_course', flat=True)

        # # Retrieve courses from the Course model that have matching IDs
        # courses = Course.objects.filter(course_id__in=course_ids)

        # Retrieve classrooms created by faculty
        classrooms = Classroom.objects.filter(fac_id=fac_data[0].fac_id)

        fac_job_detail = FacultyJobDetail.objects.filter(
            faculty_id__user_id=user_id).first()
        context = {
            'fac_data': fac_data,
            'classrooms': classrooms,
            # 'courses': courses,
            'fac_job_details': fac_job_detail,
            'assign_course': assign_course

        }

    # Code for rendering the teacher dashboard
    return render(request, 'faculty/fac_profile.html', context)


def stu_profile(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)

        course_register_data = StudentRegisterCourse.objects.filter(batch_year=stu_data[0].student_batch,
                                                                    time_shift=stu_data[0].student_time_shift, depart_programme=stu_data[0].student_depart_prog)

        if course_register_data[0].active == True:
            context = {
                'course_register_data': course_register_data,
                'stu_data': stu_data,
            }

        else:
            context = {
                'stu_data': stu_data,
            }

        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})


    # Code for rendering the teacher dashboard
    return render(request, 'student/stu_profile.html', context)


def fac_create_classroom(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            classroom_name = request.POST.get('classroom_name')
            classroom_desc = request.POST.get('classroom_desc')
            # Generate a unique random code
            while True:
                classroom_code = random.randint(10000, 99999)
                if not Classroom.objects.filter(class_code=classroom_code).exists():
                    break
            faculty_data = Faculty.objects.get(
                user_id=request.session['user_id'])
            faculty_id = faculty_data.fac_id
            user_id = request.session['user_id']
            classroom = Classroom(
                class_name=classroom_name,
                class_desc=classroom_desc,
                class_code=classroom_code,
                fac_id=faculty_id,
                user_id=user_id
            )
            classroom.save()
            return redirect('/fac_dashboard/classroom_dashboard')
        else:
            user_id = request.session.get('user_id')
            fac_data = Faculty.objects.filter(user_id=user_id)
            # Retrieve classrooms created by faculty
            classrooms = Classroom.objects.filter(fac_id=fac_data[0].fac_id)
            context = {
                'fac_data': fac_data,
                'classrooms': classrooms
            }
            return render(request, 'faculty/create_classroom.html', context)


def fac_classroom_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        assign_course = AssignCourse.objects.filter(
            faculty_id=fac_data[0].fac_id)

        # Retrieve the course IDs from the AssignCourse queryset
        course_ids = assign_course.values_list('assign_course', flat=True)

        # Retrieve courses from the Course model that have matching IDs
        courses = Course.objects.filter(course_id__in=course_ids)
        # Retrieve classrooms created by faculty
        classrooms = Classroom.objects.filter(fac_id=fac_data[0].fac_id)

        fac_job_detail = FacultyJobDetail.objects.filter(
            faculty_id__user_id=user_id).first()

        if classrooms:
            context = {'classrooms': classrooms,
                       'fac_data': fac_data,  'courses': courses, 'fac_job_details': fac_job_detail}
            return render(request, 'faculty/classroom_dashboard.html', context)
        else:
            # No Classroom found
            context = {'classrooms': classrooms,
                       'fac_data': fac_data, 'fac_job_details': fac_job_detail}
            return render(request, 'faculty/classroom_dashboard.html', context)


def fac_classroom_detail(request, classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        classrooms = Classroom.objects.filter(class_id=classroom_id)
        # classroom = get_object_or_404(Classroom, pk=classroom_id, fac_id=fac_data[0].fac_id)
        # classrooms = Classroom.objects.filter(fac_id=fac_data[0].fac_id)
        # lectures = Lecutre.objects.filter(lec_id=classrooms[0].class_id)
        # Get all StudentJoinedClassrooms created by the logged-in faculty
        student_joined_classrooms = StudentJoinedClassroom.objects.filter(
            classroom=classrooms[0])
        num_student_joined_classrooms = student_joined_classrooms.count()

        lectures = Lecutre.objects.filter(classroom_id=classroom_id)
        quiz = Quiz.objects.filter(classroom_id=classroom_id)
        assignment = Assignment.objects.filter(classroom_id=classroom_id)
        announcement = Announcement.objects.filter(classroom_id=classroom_id)
        context = {'classrooms': classrooms, 'fac_data': fac_data,
                   'lectures': lectures, 'quiz': quiz, 'assignment': assignment, 'announcement': announcement, 'num_student_joined_classrooms': num_student_joined_classrooms}
        return render(request, 'faculty/classroom_detail.html', context)


def view_assignment_submission(request, assign_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        assignment = get_object_or_404(Assignment, pk=assign_id)

        submissions = AssignmentSubmission.objects.filter(
            assignment=assignment)

        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)

        context = {
            'fac_data': fac_data,
            'assignment': assignment,
            'submissions': submissions,
        }
        return render(request, 'faculty/view_assignment_submission.html', context)


def assign_assignment_marks(request, assign_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        assignment = get_object_or_404(Assignment, pk=assign_id)

        if request.method == 'POST':
            submission_ids = request.POST.getlist('submission_ids[]')

            for sub_id in submission_ids:
                assignment_obtained_marks = request.POST.get('assignment_assign_marks_{}'.format(sub_id))
                assignment_total_marks = request.POST.get('assignment_total_marks')

                if float(assignment_obtained_marks) < 0:
                    return HttpResponse("Error: you cannot assign negative marks.")
                elif float(assignment_obtained_marks) > float(assignment_total_marks):
                    return HttpResponse("Error: you cannot assign more than total marks.")

                submission = AssignmentSubmission.objects.get(sub_id=sub_id)
                submission.assign_total_marks = assignment_total_marks
                submission.assign_marks_obtained = assignment_obtained_marks
                submission.save()

        context = {
            'assignment': assignment,
            'fac_data': fac_data,
            'submissions': AssignmentSubmission.objects.filter(assignment=assignment),
        }
        return render(request, 'faculty/view_assignment_submission.html', context)




def view_quiz_submission(request, quiz_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        submissions = QuizSubmission.objects.filter(quiz=quiz)

        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)

        context = {
            'fac_data': fac_data,
            'quiz': quiz,
            'submissions': submissions,
        }
        return render(request, 'faculty/view_quiz_submission.html', context)


def assign_quiz_marks(request, quiz_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        if request.method == 'POST':
            submission_ids = request.POST.getlist('submission_ids[]')

            for sub_id in submission_ids:
                quiz_obtained_marks = request.POST.get('quiz_marks_{}'.format(sub_id))
                quiz_total_marks = request.POST.get('quiz_total_marks')

                if float(quiz_obtained_marks) < 0:
                    return HttpResponse("Error: you cannot assign negative marks.")

                elif float(quiz_obtained_marks) > float(quiz_total_marks):
                    return HttpResponse("Error: you cannot assign more than total marks.")

                submission = QuizSubmission.objects.get(sub_id=sub_id)
                submission.quiz_total_marks = quiz_total_marks
                submission.quiz_marks_obtained = quiz_obtained_marks
                submission.save()

        context = {
            'quiz': quiz,
            'submissions': QuizSubmission.objects.filter(quiz=quiz),
            'fac_data': fac_data,
        }

        return render(request, 'faculty/view_quiz_submission.html', context)


def lectures_upload(request, classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')

    classroom = get_object_or_404(Classroom, pk=classroom_id)
    lectures = Lecutre.objects.filter(classroom_id=classroom_id)
    user_id = request.session.get('user_id')
    fac_data = Faculty.objects.filter(user_id=user_id)

    if request.method == 'POST':
        form = LectureUploadForm(request.POST, request.FILES)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.classroom = classroom
            lecture.save()
            # messages.success(request, 'Lecture uploaded successfully!')

            # Get the list of students in the classroom
            student_classrooms = StudentJoinedClassroom.objects.filter(classroom=classroom)
            
            # Assuming you want to use all students who joined the classroom
            students = student_classrooms.values_list('student', flat=True)

            # Create notification entries for each student
            for student_id in students:
                student = get_object_or_404(Student, pk=student_id)
                PushNotification.objects.create(
                    student=student,
                    content_type='lecture', 
                    content_id=lectures.first().lec_id,
                    classroom_id = classroom
                )
            messages.success(request, 'Lecture uploaded successfully!')
    else:
        form = LectureUploadForm()

    context = {
        'fac_data': fac_data,
        'classroom': classroom,
        'lectures': lectures,
        'form': form,
    }
    return render(request, 'faculty/lectures_upload.html', context)


def quiz_upload(request, classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')

    classroom = get_object_or_404(Classroom, pk=classroom_id)
    quiz = Quiz.objects.filter(classroom_id=classroom_id).first()
    user_id = request.session.get('user_id')
    fac_data = Faculty.objects.filter(user_id=user_id)

    if request.method == 'POST':
        form = QuizUploadForm(request.POST, request.FILES)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.classroom = classroom
            quiz.save()
            # messages.success(request, 'Quiz uploaded successfully!')

            # Get the list of students in the classroom
            student_classrooms = StudentJoinedClassroom.objects.filter(classroom=classroom)
            
            # Assuming you want to use all students who joined the classroom
            students = student_classrooms.values_list('student', flat=True)

            # Create notification entries for each student
            for student_id in students:
                student = get_object_or_404(Student, pk=student_id)
                PushNotification.objects.create(
                    student=student,
                    content_type='quiz', 
                    content_id=Quiz.objects.filter(classroom_id=classroom_id).first().quiz_id,
                    classroom_id = classroom_id
                )
    else:
        form = QuizUploadForm()

    context = {
        'fac_data': fac_data,
        'classroom': classroom,
        'quizzes': Quiz.objects.filter(classroom_id=classroom_id),
        'form': form,
    }
    return render(request, 'faculty/quiz_upload.html', context)


def assignment_upload(request, classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')

    classroom = get_object_or_404(Classroom, pk=classroom_id)
    assignment = Assignment.objects.filter(assign_id=classroom_id).first()
    user_id = request.session.get('user_id')
    fac_data = Faculty.objects.filter(user_id=user_id)

    if request.method == 'POST':
        form = AssignmentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom = classroom
            assignment.save()
            # messages.success(request, 'Assignment uploaded successfully!')

             # Get the list of students in the classroom
            student_classrooms = StudentJoinedClassroom.objects.filter(classroom=classroom)
            
            # Assuming you want to use all students who joined the classroom
            students = student_classrooms.values_list('student', flat=True)

            # Create notification entries for each student
            for student_id in students:
                student = get_object_or_404(Student, pk=student_id)
                PushNotification.objects.create(
                    student=student,
                    content_type='assignment', 
                    content_id=Assignment.objects.filter(assign_id=classroom_id).first().assign_id,
                    classroom_id = classroom
                )
    else:
        form = AssignmentUploadForm()

    context = {
        'fac_data': fac_data,
        'classroom': classroom,
        'assignments': Assignment.objects.filter(classroom_id=classroom_id),
        'form': form,
    }
    return render(request, 'faculty/assignment_upload.html', context)


def announcement_upload(request, classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')

    classroom = get_object_or_404(Classroom, pk=classroom_id)
    announcement = Announcement.objects.filter(ann_id=classroom_id).first()
    user_id = request.session.get('user_id')
    fac_data = Faculty.objects.filter(user_id=user_id)

    if request.method == 'POST':
        form = AnnouncementUploadForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.classroom = classroom
            announcement.save()
            # messages.success(request, 'Announcement uploaded successfully!')

             # Get the list of students in the classroom
            student_classrooms = StudentJoinedClassroom.objects.filter(classroom=classroom)
            
            # Assuming you want to use all students who joined the classroom
            students = student_classrooms.values_list('student', flat=True)

            # Create notification entries for each student
            for student_id in students:
                student = get_object_or_404(Student, pk=student_id)
                PushNotification.objects.create(
                    student=student,
                    content_type='announcement', 
                    content_id=Announcement.objects.filter(ann_id=classroom_id).first().ann_id,
                    classroom_id = classroom
                )
    else:
        form = AssignmentUploadForm()

    context = {
        'fac_data': fac_data,
        'classroom': classroom,
        'announcements': Announcement.objects.filter(classroom_id=classroom_id),
        'form': form,
    }
    return render(request, 'faculty/announcement_upload.html', context)


def joined_students(request, classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)

        students = StudentJoinedClassroom.objects.filter(
            classroom_id=classroom_id)

        context = {'fac_data': fac_data,
                   'students': students}

        return render(request, 'faculty/joined_students.html', context)


def teacher_delete_classroom(request, classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        classroom = get_object_or_404(Classroom, class_id=classroom_id)
        classroom.delete()
        # messages.success(request, f'{classroom.class_name} has been deleted.')
        return redirect('/fac_dashboard/classroom_dashboard')


def teacher_delete_lecture(request, lecture_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        lecture = get_object_or_404(Lecutre, lec_id=lecture_id)
        lecture.delete()
        # messages.success(request, f'{lecture.lec_name} has been deleted.')
        # Get the referer URL from the request headers
        referer_url = request.META.get('HTTP_REFERER')
        # If there is no referer URL, redirect to the homepage
        if not referer_url:
            return redirect('/fac_dashboard/classroom_dashboard')
        # Otherwise, redirect to the referer URL
        return redirect(referer_url)


def teacher_delete_quiz(request, quiz_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
        quiz.delete()
        # messages.success(request, f'{quiz.quiz_name} has been deleted.')
        # Get the referer URL from the request headers
        referer_url = request.META.get('HTTP_REFERER')
        # If there is no referer URL, redirect to the homepage
        if not referer_url:
            return redirect('/fac_dashboard/classroom_dashboard')
        # Otherwise, redirect to the referer URL
        return redirect(referer_url)


def teacher_delete_assignment(request, assign_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        assignment = get_object_or_404(Assignment, assign_id=assign_id)
        assignment.delete()
        # messages.success(
        #     request, f'{assignment.assign_name} has been deleted.')
        # Get the referer URL from the request headers
        referer_url = request.META.get('HTTP_REFERER')
        # If there is no referer URL, redirect to the homepage
        if not referer_url:
            return redirect('/fac_dashboard/classroom_dashboard')
        # Otherwise, redirect to the referer URL
        return redirect(referer_url)


def teacher_delete_announcement(request, ann_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        announcement = get_object_or_404(Announcement, ann_id=ann_id)
        announcement.delete()
        # messages.success(
        #     request, f'{announcement.ann_name} has been deleted.')
        # Get the referer URL from the request headers
        referer_url = request.META.get('HTTP_REFERER')
        # If there is no referer URL, redirect to the homepage
        if not referer_url:
            return redirect('/fac_dashboard/classroom_dashboard')
        # Otherwise, redirect to the referer URL
        return redirect(referer_url)


def stu_classroom_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)

        joined_classrooms = StudentJoinedClassroom.objects.filter(
            student=stu_data[0].student_id)

        classrooms = Classroom.objects.filter(
            class_id__in=[jc.classroom.class_id for jc in joined_classrooms])

        context = {'stu_data': stu_data, 'joined_classrooms': joined_classrooms,
                   'classrooms': classrooms, }

        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/classroom_dashboard.html', context)


def stu_join_classroom(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            code = request.POST.get('classroom_code')
            try:
                user_id = request.session.get('user_id')
                student = Student.objects.get(user_id=user_id)
                classroom = Classroom.objects.get(class_code=code)
                # Check if the student has already joined this classroom
                if StudentJoinedClassroom.objects.filter(student=student, classroom=classroom).exists():
                    messages.warning(
                        request, 'You have already joined this class.')
                else:
                    joined_classroom = StudentJoinedClassroom(
                        student=student, classroom=classroom, class_code=code)
                    joined_classroom.save()
                    # messages.success(
                    #     request, 'You have successfully joined the class.')
                return redirect('/stu_dashboard/classroom_dashboard')
            except Classroom.DoesNotExist:
                messages.error(request, 'Invalid Class Code')
                return redirect('/stu_dashboard/classroom_dashboard')
        else:
            student_id = request.session['user_id']
            StudentJoinedClassroom.objects.create(
                student_id=student_id, classroom_id=classroom.class_id, class_code=code)
            classrooms = Classroom.objects.filter(
                studentjoinedclassroom__student_id=request.session['user_id'])
            context = {'classrooms': classrooms}
            return render(request, 'stu_dashboard/classroom_dashboard.html', context)


def stu_delete_classroom(request, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        student = Student.objects.filter(user_id=user_id).first()
        classroom = Classroom.objects.filter(
            class_id=joined_classroom_id).first()

        # Check if the student is joined to the classroom
        joined_classroom = StudentJoinedClassroom.objects.filter(
            student=student, classroom=classroom).first()
        if joined_classroom:
            joined_classroom.delete()
            # messages.success(request, 'Classroom removed successfully!')
        else:
            # messages.error(request, 'You are not joined to this classroom.')
            return redirect('/stu_dashboard/classroom_dashboard')

        return redirect('/stu_dashboard/classroom_dashboard')


def stu_classroom_detail(request, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)
        classrooms = Classroom.objects.filter(class_id=joined_classroom_id)

        # classroom = get_object_or_404(Classroom, pk=classroom_id, fac_id=fac_data[0].fac_id)
        # classrooms = Classroom.objects.filter(fac_id=fac_data[0].fac_id)
        # lectures = Lecutre.objects.filter(lec_id=classrooms[0].class_id)
        lectures = Lecutre.objects.filter(classroom_id=joined_classroom_id)
        quiz = Quiz.objects.filter(classroom_id=joined_classroom_id)
        assignment = Assignment.objects.filter(
            classroom_id=joined_classroom_id)
        announcement = Announcement.objects.filter(
            classroom_id=joined_classroom_id)

        joined_classrooms = StudentJoinedClassroom.objects.filter(
            classroom_id=classrooms[0].class_id)

        fac_name = Faculty.objects.get(fac_name=classrooms[0].fac)

        context = {'classrooms': classrooms, 'stu_data': stu_data,
                   'lectures': lectures, 'quiz': quiz, 'assignment': assignment, 'announcement': announcement,
                   'joined_classrooms': joined_classrooms, 'fac_name': fac_name}
        
        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/classroom_detail.html', context, )


def stu_lectures_view(request, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        classroom = get_object_or_404(Classroom, pk=joined_classroom_id)
        lectures = Lecutre.objects.filter(classroom_id=joined_classroom_id)
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)
        context = {
            'stu_data': stu_data,
            'classroom': classroom,
            'lectures': lectures
        }
        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/lectures_view.html', context)


def stu_quiz_view(request, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        quizzes = Quiz.objects.filter(classroom_id=joined_classroom_id)
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)

        context = {'stu_data': stu_data,
                   'quizzes': quizzes}
        
        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/quiz_view.html', context)


def stu_view_quiz_result(request, quiz_id, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        student = Student.objects.get(user_id=request.session['user_id'])
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)
        try:
            quiz_submissions = QuizSubmission.objects.get(
                quiz_id=quiz_id, student=student, classroom=joined_classroom_id)
            context = {
                'stu_data': stu_data,
                'quiz_submissions': quiz_submissions,
            }
        except QuizSubmission.DoesNotExist:
            context = {
                'stu_data': stu_data,
                'error_msg': 'You have not submitted the quiz yet.',
            }

        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})


    return render(request, 'student/stu_quiz_result.html', context)


def stu_quiz_submission(request, quiz_id, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        student = Student.objects.filter(user=user_id).first()
        stu_data = Student.objects.filter(user_id=user_id)

        classroom = get_object_or_404(Classroom, pk=joined_classroom_id)
        quiz = Quiz.objects.filter(quiz_id=quiz_id).first()

        if not quiz:
            # handle the case where there are no assignments in the classroom
            return HttpResponse('There are no quiz for this classroom.')

        if request.method == 'POST':
            form = QuizSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                user_id = request.session['user_id']
                student = Student.objects.get(user_id=user_id)
                quiz_submission_exists = QuizSubmission.objects.filter(
                    classroom_id=joined_classroom_id,
                    quiz_id=quiz.quiz_id,
                    student=student).exists()
                if quiz_submission_exists:
                    messages.warning(request, 'Delete old one to submit again')
                    return redirect(request.META.get('HTTP_REFERER'))

                quiz_submission = form.save(commit=False)
                quiz_submission.classroom = classroom
                quiz_submission.quiz = quiz
                quiz_submission.student = student
                quiz_submission.status = 'Quiz Submitted'
                quiz_submission.quiz_submission_date = date.today()

                quiz_submission.save()
                # messages.success(request, 'Quiz submitted successfully!')
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            form = QuizSubmissionForm()

        context = {
            'stu_data': stu_data,
            'classroom': classroom,
            'quizzes_submission': QuizSubmission.objects.filter(classroom_id=joined_classroom_id, quiz=quiz_id, student=student),
            'form': form,
        }
        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/quiz_submission.html', context)


def stu_delete_quiz(request, quiz_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        quiz_submission = QuizSubmission.objects.filter(
            quiz_id=quiz_id).first()
        quiz_submission.delete()
        # messages.success(request, f'{quiz.quiz_name} has been deleted.')
        # Get the referer URL from the request headers
        referer_url = request.META.get('HTTP_REFERER')
        # If there is no referer URL, redirect to the homepage
        if not referer_url:
            return redirect('/stu_dashboard/classroom_dashboard')
        # Otherwise, redirect to the referer URL
        return redirect(referer_url)


def stu_assignment_view(request, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        assignments = Assignment.objects.filter(
            classroom_id=joined_classroom_id)
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)
        context = {'stu_data': stu_data,
                   'assignments': assignments}
        
        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/assignment_view.html', context)


def stu_view_assignment_result(request, assign_id, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        student = Student.objects.get(user_id=request.session['user_id'])
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)
        try:
            assignment_submissions = AssignmentSubmission.objects.get(
                assignment=assign_id, student=student, classroom=joined_classroom_id)

            context = {
                'stu_data': stu_data,
                'assignment_submissions': assignment_submissions,
            }
        except AssignmentSubmission.DoesNotExist:
            context = {
                'stu_data': stu_data,
                'error_msg': 'You have not submitted the quiz yet.',
            }

        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})


    return render(request, 'student/stu_assignment_result.html', context)


def stu_assignment_submission(request, assign_id, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:

        user_id = request.session.get('user_id')
        student = Student.objects.filter(user=user_id).first()
        stu_data = Student.objects.filter(user_id=user_id)

        classroom = get_object_or_404(Classroom, pk=joined_classroom_id)
        assignment = Assignment.objects.filter(assign_id=assign_id).first()

        if not assignment:
            # handle the case where there are no assignments in the classroom
            return HttpResponse('There are no assignments for this classroom.')

        if request.method == 'POST':
            form = AssignmentSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                student_id = request.session['user_id']
                student = Student.objects.get(user_id=student_id)
                assignment_submission_exists = AssignmentSubmission.objects.filter(
                    classroom_id=joined_classroom_id,
                    assignment_id=assignment.assign_id,
                    student=student).exists()
                if assignment_submission_exists:
                    messages.warning(request, 'Delete old one to submit again')
                    return redirect(request.META.get('HTTP_REFERER'))

                assignment_submission = form.save(commit=False)
                assignment_submission.classroom = classroom
                assignment_submission.assignment = assignment
                assignment_submission.student = student
                assignment_submission.status = 'Assignment Submitted'
                assignment_submission.assignment_submission_date = date.today()
                assignment_submission.save()
                # messages.success(request, 'Assignment uploaded successfully!')
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            form = AssignmentSubmissionForm()

        context = {
            'stu_data': stu_data,
            'classroom': classroom,
            'assignments_submission': AssignmentSubmission.objects.filter(classroom_id=joined_classroom_id, assignment=assign_id, student=student),
            'form': form,
        }
        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/assignment_submission.html', context)


def stu_delete_assignment(request, assignment_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        assignment_submission = AssignmentSubmission.objects.filter(
            assignment_id=assignment_id).first()
        assignment_submission.delete()
        # messages.success(request, f'{quiz.quiz_name} has been deleted.')
        # Get the referer URL from the request headers
        referer_url = request.META.get('HTTP_REFERER')
        # If there is no referer URL, redirect to the homepage
        if not referer_url:
            return redirect('/stu_dashboard/classroom_dashboard')
        # Otherwise, redirect to the referer URL
        return redirect(referer_url)


def stu_announcement_view(request, joined_classroom_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:

        announcements = Announcement.objects.filter(
            classroom=joined_classroom_id)
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)
        context = {
            'stu_data': stu_data,
            'announcements': announcements,
        }
        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/announcement_view.html', context)


# # # # Faculty Attendance Section # # # #

def fac_attendance(request, faculty_id=None):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)

        assign_course = AssignCourse.objects.filter(
            faculty_id=fac_data[0].fac_id, active=True)
        

        # # Retrieve the course IDs from the AssignCourse queryset
        # course_ids = assign_course.values_list('assign_course', flat=True)

        # # Retrieve courses from the Course model that have matching IDs
        # courses = Course.objects.filter(course_id__in=course_ids)

        # Retrieve classrooms created by faculty
        classrooms = Classroom.objects.filter(fac_id=fac_data[0].fac_id)

        fac_job_detail = FacultyJobDetail.objects.filter(
            faculty_id__fac_id=fac_data[0].fac_id).first()
        context = {
            'fac_data': fac_data,
            'classrooms': classrooms,
            # 'courses': courses,
            'fac_job_details': fac_job_detail,
            'assign_course': assign_course
        }

        return render(request, 'faculty/fac_attendance.html', context)


def student_list(request, course_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        course = get_object_or_404(Course, course_id=course_id)
        fac_data = Faculty.objects.filter(user_id=user_id)
        fac_data_attendance_list = Faculty.objects.filter(user_id=user_id).first()
        departments = Department.objects.all()
        programmes = DepartProgramme.objects.all()
        batches = TotalBatche.objects.all().values('batch').distinct()
        students = Student.objects.all()
        fac_job_details = FacultyJobDetail.objects.filter(
            faculty__user_id=user_id)
        department = request.GET.get('department')
        batch = request.GET.get('batch')
        programme = request.GET.get('programme')
        shift = request.GET.get('shift')

        attendance_list = StudentAttendance.objects.filter(
            course=course_id, fac=fac_data_attendance_list.fac_id)
        latest_week = attendance_list.aggregate(Max('attendance_week'))[
            'attendance_week__max']

        # check if form has been submitted and apply filters
        if department and batch and programme and shift:
            students = students.filter(student_depart__dep_name=department, student_batch=batch,
                                       student_time_shift=shift, student_depart_prog__prog_name=programme)
        elif department or batch or programme:
            messages.warning(request, 'Please select all the filter options.')

        # check if filters have been applied and return appropriate context
        if department and batch and programme and shift:
            if not students:
                messages.warning(request, 'No student found')

            context = {
                'course': course,
                'departments': departments,
                'programmes': programmes,
                'batches': batches,
                'students': students,
                'selected_department': department,
                'selected_batch': batch,
                "fac_data": fac_data,
                'fac_job_details': fac_job_details,
                'latest_week': latest_week
            }
        else:
            context = {
                'course': course,
                'departments': departments,
                'programmes': programmes,
                'batches': batches,
                "fac_data": fac_data,
                'fac_job_details': fac_job_details,
                'latest_week': latest_week
            }

        return render(request, 'faculty/student_list.html', context)


def submit_attendance(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            input_date = request.POST.get('inputDate')
            input_week = request.POST.get('inputWeek')
            student_names = request.POST.getlist('student_name')
            student_enroll_nos = request.POST.getlist('student_enroll')
            student_departs = request.POST.getlist('student_depart')
            student_depart_programmes = request.POST.getlist(
                'student_depart_prog')
            student_batches = request.POST.getlist('student_batch')
            student_images = request.POST.getlist('student_img')
            course_id = request.POST.get('course_id')
            attendance_statuses = request.POST.getlist('attendance_status')
            fac_id = request.POST.get('fac_id')

            new_attendance_list = []
            updated_attendance_list = []

            for i in range(len(student_names)):
                # Check if attendance entry already exists for the given date, week, course id, fac_id and student enrollment number
                existing_attendance = StudentAttendance.objects.filter(
                    attendance_date=input_date,
                    attendance_week=input_week,
                    course_id=course_id,
                    fac_id=fac_id,
                    student_enroll_no=student_enroll_nos[i]
                ).first()

                if existing_attendance:
                    # If an attendance entry already exists, update the attendance status instead of creating a new entry
                    if existing_attendance.attendance_status != attendance_statuses[i]:
                        existing_attendance.attendance_status = attendance_statuses[i]
                        existing_attendance.save()
                        updated_attendance_list.append(existing_attendance)
                else:
                    # If no attendance entry exists, create a new entry
                    student_attendance = StudentAttendance(
                        student_name=student_names[i],
                        student_enroll_no=student_enroll_nos[i],
                        student_depart=student_departs[i],
                        student_enrolled_programme=student_depart_programmes[i],
                        student_batch=student_batches[i],
                        course_id=course_id,
                        attendance_week=input_week,
                        attendance_date=input_date,
                        attendance_status=attendance_statuses[i],
                        student_img=student_images[i],
                        fac_id=fac_id,
                    )
                    new_attendance_list.append(student_attendance)

            if not new_attendance_list and not updated_attendance_list:
                messages.warning(request, 'No new record(s) to save/update.')
            else:
                if new_attendance_list:
                    StudentAttendance.objects.bulk_create(new_attendance_list)
                    messages.success(
                        request, 'New attendance record(s) saved successfully.')

                if updated_attendance_list:
                    messages.success(
                        request, 'Attendance record(s) updated successfully.')

            return redirect(request.META.get('HTTP_REFERER', 'faculty/student_list.html'))
        else:
            return render(request, 'faculty/student_list.html')


def view_attendance(request, course_id, fac_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        course_data = Course.objects.filter(course_id=course_id).first()
        attendance_data = StudentAttendance.objects.filter(
            course_id=course_data, fac_id=fac_id)
        # attendance_weeks = attendance_data.values_list('attendance_week', flat=True).distinct().order_by('attendance_week')

        week = request.GET.get('week')

        if week:
            if week == 'All':
                attendance_data = attendance_data
            else:
                attendance_data = attendance_data.filter(
                    attendance_week=week, fac_id=fac_id)

        context = {
            'attendance_data': attendance_data,
            'fac_data': fac_data,
            'course_data': course_data,
            # 'attendance_weeks': attendance_weeks
        }

        return render(request, 'faculty/view_attendance.html', context)


def update_attendance(request, attendance_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            # Handle edit form submission

            attendance_status = request.POST.get('attendance_status')
            attendance = StudentAttendance.objects.filter(
                id=attendance_id).first()
            if attendance:
                attendance.attendance_status = attendance_status
                attendance.save()

            return redirect(request.META.get('HTTP_REFERER', 'view_attendance.html'))


# # # # Faculty Upload Result Section # # # #

def add_clo(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        assign_courses = AssignCourse.objects.filter(faculty__user_id=user_id)
        if request.method == 'POST':
            course = request.POST.get('course')
            total_clos = int(request.POST.get('num_clos', 0))
            for i in range(1, total_clos+1): 
                clo_cover = request.POST.get(f'clo_{i}')
                clo_objective = request.POST.get(f'clo_objective_{i}')
          
                AddCourseClo.objects.create(
                    course=course,
                    fac=Faculty.objects.filter(user_id=user_id).first(), 
                    total_clos=total_clos, 
                    clos=clo_cover, 
                    clos_objective=clo_objective
                )

            context = {
                'fac_data': fac_data,
                'assign_courses':assign_courses,
            }

            return render(request, 'faculty/add_clo.html', context)

        context = {
            'fac_data': fac_data,
            'assign_courses':assign_courses,
        }

        return render(request, 'faculty/add_clo.html', context)


        

def map_clo_plo(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        assign_courses = AssignCourse.objects.filter(faculty__user_id=user_id)
        course = request.GET.get('course')
      
        clo_data=None
        if course:
            clo_data = AddCourseClo.objects.filter(course=course, fac=fac_data[0].fac_id)
            if not clo_data:
                messages.error(request, f"Please first add the CLO's for {course}")

        if request.method == 'POST':
            total_mapped_clos_plos = int(request.POST.get('num_mapping', 0))

            if not (course and total_mapped_clos_plos):
                messages.error(request, "Please fill all the fields")
                return redirect('/fac_dashboard/map_clo_plo')
            
            for i in range(1,  total_mapped_clos_plos+1): 
                mapped_clos_plos = request.POST.get(f'map_clo_plo_{i}')

                if not (mapped_clos_plos):
                    messages.error(request, "Please fill all the fields")
                    return redirect('/fac_dashboard/map_clo_plo')
            
                MapCourseCloPlo.objects.create(
                    course=course,
                    fac=Faculty.objects.filter(user_id=user_id).first(), 
                    total_mapped_clos_plos = total_mapped_clos_plos, 
                    mapped_clos_plos = mapped_clos_plos,
                 
                )
            messages.success(request, "Submitted successfully")

            context = {
                'fac_data': fac_data,
                'assign_courses':assign_courses,
                'clo_data':clo_data,
                'selected_course':course,
                }
            
            return redirect('/fac_dashboard/map_clo_plo')

        context = {
            'fac_data': fac_data,
            'assign_courses':assign_courses,
            'clo_data':clo_data,
            'selected_course':course,
        }
        
        return render(request, 'faculty/map_clo_plo.html', context)
    
def add_assessment_clos_plos(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        assign_courses = AssignCourse.objects.filter(faculty__user_id=user_id)
        course = request.GET.get('course')
      
        mapped_data=None
        if course:
            mapped_data = MapCourseCloPlo.objects.filter(course=course, fac=fac_data[0].fac_id)
            if not mapped_data:
                messages.error(request, f"Please first map the CLO's PLO's for {course}")

        if request.method == 'POST':
            assessment_type = request.POST.get('assessment_type')
            assessment_name = request.POST.get('assessment_name')
            mapped_clos_plos = request.POST.get('mapped_clos_plos')
            total_marks = request.POST.get('total_marks')
            total_questions = int(request.POST.get('num_question', 0))

            if not (course and assessment_type and assessment_name and total_marks and mapped_clos_plos and total_questions):
                messages.error(request, "Please fill all the fields")
                return redirect('/fac_dashboard/add_assessment_clos_plos')

            # Concatenate question numbers and clo plo values
            question_wise_map_clos_plos = ""
            for i in range(1, total_questions + 1): 
                question_num = request.POST.get(f'question_num_{i}')
                clo_plo = request.POST.get(f'map_clos_plos_cover_{i}')

                if not (question_num and clo_plo):
                    messages.error(request, "Please fill all the fields")
                    return redirect('/fac_dashboard/add_assessment_clos_plos')

                question_wise_map_clos_plos += f"{question_num}: {clo_plo}, "

            # Remove the trailing comma and space
            question_wise_map_clos_plos = question_wise_map_clos_plos.rstrip(", ")

            # Save a single entry with concatenated values
            AddAssessmentClosPlo.objects.create(
                course=course,
                fac=Faculty.objects.filter(user_id=user_id).first(),
                assessment_type=assessment_type,
                assessment_name=assessment_name,
                mapped_clos_plos=mapped_clos_plos,
                total_questions=total_questions,
                total_marks=total_marks,
                question_wise_map_clos_plos=question_wise_map_clos_plos,
            )

            messages.success(request, "Submitted successfully")

            context = {
                'fac_data': fac_data,
                'assign_courses': assign_courses,
                'mapped_data': mapped_data,
                'selected_course': course,
            }

            return redirect('/fac_dashboard/add_assessment_clos_plos')

        context = {
            'fac_data': fac_data,
            'assign_courses': assign_courses,
            'mapped_data': mapped_data,
            'selected_course': course,
        }

        return render(request, 'faculty/add_assessment_clos_plos.html', context)


def upload_result(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        department = request.GET.get('department')
        batch = request.GET.get('batch')
        programme = request.GET.get('programme')
        shift = request.GET.get('shift')
        course_id = request.GET.get('course')
        assessment_type_id = request.GET.get('assessment_type')
        assign_courses = AssignCourse.objects.filter(faculty__user_id=user_id)
        departments = Department.objects.all()
        programmes = DepartProgramme.objects.all()
        batches = TotalBatche.objects.all().values('batch').distinct()
        fac_job_details = FacultyJobDetail.objects.filter(
            faculty__user_id=user_id)
     
        # print( onChangeValue, 'HELLO')
            
        # assessment_data = AddAssessmentClosPlo.objects.filter(fac=Faculty.objects.filter(user_id=user_id)[0].fac_id, course=course_id, assessment_type=assessment_type_id)
        # print(assessment_data)
        # assessment_name = assessment_data.values('assessment_name').distinct()
        # print(assessment_name)
    
        
        # fetch students based on the selected filters
        students = Student.objects.all()
        if department and batch and programme and shift:
            students = students.filter(student_depart__dep_name=department, student_batch=batch,
                                       student_time_shift=shift, student_depart_prog__prog_name=programme)
            if not students:
                messages.warning(request, 'No student found')

        # fetch course and assessment type based on the selected filters
        assessment_data = None
        assessment_name = None
        mapped_clos_plos = None
        total_assessment = None
        onChangeAssessmentName = request.GET.get('onChangeAssessmentName_value')
        onChangeCourseName = request.GET.get('onChangeCourseName_value')
        onChangeAssessmentType= request.GET.get('onChangeAssessmentType_value')

        assessment_data = AddAssessmentClosPlo.objects.filter(fac=Faculty.objects.filter(user_id=user_id)[0].fac_id, course=onChangeCourseName, assessment_type=onChangeAssessmentType)
        if onChangeAssessmentName:
            mapped_clos_plos = assessment_data.filter(assessment_name=onChangeAssessmentName).values('mapped_clos_plos').distinct()
            mapped_clos_plos_list = list(mapped_clos_plos)
            return JsonResponse({'mapped_clos_plos': mapped_clos_plos_list})
            # print(onChangeAssessmentName,'HELLO1')
            # print (onChangeCourseName, 'HELLO2')
            # print( onChangeAssessmentType,'HELLO3')
            # print(mapped_clos_plos, 'HELLO4')
            # print(mapped_clos_plos_list, 'HELLO5')
            
        if course_id and assessment_type_id:
            try:
                assessment_data = AddAssessmentClosPlo.objects.filter(fac=Faculty.objects.filter(user_id=user_id)[0].fac_id, course=course_id, assessment_type=assessment_type_id)
                assessment_name = assessment_data.values('assessment_name').distinct()
                # mapped_clos_plos = ';'.join([str(item['mapped_clos_plos']) for item in assessment_data.values('mapped_clos_plos').distinct()])
                total_assessment = assessment_data.values('assessment_name').distinct().count()
                # print(mapped_clos_plos, 'HELLO2')
                # print(assessment_name,'HELLO3')
               
             

            except AddAssessmentClosPlo.DoesNotExist:
                messages.warning(request, f'Please add {assessment_type_id} assessment first.')

            if not assessment_data:
                messages.warning(request, f'Please add {assessment_type_id} assessment first.')

       
        if request.method == 'POST':
            assessment_name = request.POST.get('assessment_name')
            mapped_plos_clos_cover = request.POST.get('mapped_clos_plos')
            total_marks = request.POST.get('total_marks')
            marks_obtained = request.POST.getlist('marks_obtained')

            # Save or update the result data
            for i, student in enumerate(students):
                # Check if an entry already exists for the given parameters
                existing_result = UploadResult.objects.filter(
                    student_name=student.student_name,
                    student_enroll_no=student.student_enroll_no,
                    department=student.student_depart.dep_name,
                    programme=student.student_depart_prog.prog_name,
                    batch=student.student_batch,
                    time_shift=student.student_time_shift,
                    course=course_id,
                    fac=Faculty.objects.get(user_id=user_id),
                    assessment_type=assessment_type_id,
                    assessment_name = assessment_name,
                ).first()

                if existing_result:
                    # Entry already exists, update it
                    existing_result.assessment_name = assessment_name
                    existing_result.mapped_plos_clos_cover = mapped_plos_clos_cover
                    existing_result.total_marks = total_marks
                    existing_result.obtained_marks = marks_obtained[i]
                    existing_result.save()
                else:
                    # Entry does not exist, create a new one
                    UploadResult.objects.create(
                        student_name=student.student_name,
                        student_enroll_no=student.student_enroll_no,
                        department=student.student_depart.dep_name,
                        programme=student.student_depart_prog.prog_name,
                        batch=student.student_batch,
                        time_shift=student.student_time_shift,
                        course=course_id,
                        fac=Faculty.objects.get(user_id=user_id),
                        assessment_type=assessment_type_id,
                        assessment_name=assessment_name,
                        mapped_plos_clos_cover=mapped_plos_clos_cover,
                        total_marks=total_marks,
                        obtained_marks=marks_obtained[i],
                    )

        context = {
            'departments': departments,
            'programmes': programmes,
            'batches': batches,
            'students': students,
            "fac_data": fac_data,
            'fac_job_details': fac_job_details,
            'assign_courses': assign_courses,
            'assessment_data': assessment_data,
            'selected_department': department,
            'selected_batch': batch,
            'selected_programme': programme,
            'selected_shift': shift,
            'selected_course_id': course_id,
            'selected_assessment_type_id': assessment_type_id,
            'mapped_clos_plos': mapped_clos_plos,
            'total_assessment': total_assessment,
            'assessment_name': assessment_name,
        }

        return render(request, 'faculty/upload_result.html', context)
    

def view_result(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)

        assigned_courses = AssignCourse.objects.filter(
            faculty_id=fac_data[0].fac_id, active=True)
        
        # Fetch upload_result data for the logged-in user
        upload_result_data = UploadResult.objects.filter(fac_id=fac_data[0].fac_id,
                             course__in=[assigned_course.assign_course.course_name for assigned_course in assigned_courses])

        context = {
            'fac_data': fac_data,
            'upload_result_data': upload_result_data,
        }
        return render(request, 'faculty/view_result.html', context)

def export_csv(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        fac_data = Faculty.objects.filter(user_id=user_id)
        
        # Fetch upload_result data for the logged-in user
        upload_result_data = UploadResult.objects.filter(fac_id=fac_data[0].fac_id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="result_data.csv"'

        writer = csv.writer(response)
        writer.writerow(['Student', 'Course', 'Assessment Type', 'Assessment Name', 'CLO\'s PLO\'s', 'Total Marks', 'Obtained Marks'])

        for result in upload_result_data:
            writer.writerow([result.student_name, result.course, result.assessment_type, result.assessment_name, result.mapped_plos_clos_cover, result.total_marks, result.obtained_marks])

        return response
    
# # # # Student View Result Section # # # #
def stu_view_result(request):   
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)
       
        user_name = stu_data[0].student_name
        
        # Get the registered courses for the student
        course_register_data = StudentRegisterCourse.objects.filter(
            batch_year=stu_data[0].student_batch,
            time_shift=stu_data[0].student_time_shift,
            depart_programme=stu_data[0].student_depart_prog 
        )
        stu_semester = course_register_data[0].semester
       
        # Extract the course names from the queryset
        course_names = course_register_data.values_list('courses__course_name', flat=True)

        # print("Course Names:", course_names)  # Debug print

         # Specify the columns you want to include
        selected_columns = ['StudentName', 'EnrollmentNumber', 'CourseName', 'Grade', 'CH', 'QP', 'Status']
        # Fetch results using raw SQL query
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT *
                FROM student_result_view
                WHERE StudentName = %s AND CourseName IN %s
                ''',
                [user_name, tuple(course_names)]
            )
            columns = [desc[0] for desc in cursor.description if desc[0] in selected_columns]
            result_data = cursor.fetchall()

        # print("Result Data:", result_data)  # Debug print
        context = {
            'columns': columns,
            'stu_data': stu_data,
            'course_register_data': course_register_data,
            'result_data': result_data,
            'stu_semester':stu_semester,
        }

        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})

        return render(request, 'student/result_view.html', context)

# # # # Student Attendance View Section # # # #
def stu_view_attendance(request):   
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session.get('user_id')
        stu_data = Student.objects.filter(user_id=user_id)

        # Get the registered courses for the student
        course_register_data = StudentRegisterCourse.objects.filter(
            batch_year=stu_data[0].student_batch,
            time_shift=stu_data[0].student_time_shift,
            depart_programme=stu_data[0].student_depart_prog 
        )

        user_name = stu_data[0].student_name
        # print(user_name)
         # Extract the course names from the queryset
        course_names = course_register_data.values_list('courses__course_name', flat=True)
        # print(course_names)

        # Define context outside of the if statement
        context = {
            'stu_data': stu_data,
            'course_register_data': course_register_data,
        }

        if course_register_data and course_register_data[0].active:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT *
                    FROM student_attendance_view
                    WHERE Student = %s AND Course IN %s
                    ''',
                    [user_name, tuple(course_names)]
                )
                columns = [desc[0] for desc in cursor.description]
                result_data = cursor.fetchall()
                
                context.update({
                    'columns': columns,
                    'result_data': result_data,
                })

                print(result_data)
        else:
            print("Not Hello")

        
        student_notifications = PushNotification.objects.filter(student_id=stu_data[0].student_id)
        if student_notifications:
            # noti_classrooms = Classroom.objects.filter(class_id = student_notificaitons[0].classroom_id)
            unread_notifications = [noti for noti in student_notifications if noti.is_read == False]
            # Reverse the order of notifications
            student_notifications = student_notifications.order_by('-created_at')
            if unread_notifications:
                context.update({'notifications':student_notifications, 'unread_notifications':unread_notifications})
        
        return render(request, 'student/attendance_view.html', context)


