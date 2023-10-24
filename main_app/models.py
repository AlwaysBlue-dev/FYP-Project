from django.db import models

# Create your models here.


class LoginUser(models.Model):
    HeadofDepart = 'HOD'
    Student = 'Student'
    Teacher = 'Teacher'

    YEAR_IN_SCHOOL_CHOICES = [
        (HeadofDepart, 'HOD'),
        (Student, 'Student'),
        (Teacher, 'Teacher'),
    ]
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100, default="")
    user_email = models.CharField(max_length=100, default="")
    user_password = models.CharField(max_length=100, default="")
    user_type = models.CharField(
        max_length=10, choices=YEAR_IN_SCHOOL_CHOICES, default="")

    def __str__(self):
        return self.user_email


class HOD(models.Model):
    hod_id = models.AutoField(primary_key=True)
    hod_name = models.CharField(max_length=100, default="")
    hod_email = models.ForeignKey(LoginUser, on_delete=models.CASCADE)
    hod_img = models.ImageField(upload_to='hod/', default="")
    dep_name = models.CharField(max_length=100, default="")
    user = models.ForeignKey(
        LoginUser, related_name="hod_user", on_delete=models.CASCADE)

    def __str__(self):
        return self.hod_name


class Department(models.Model):
    dep_id = models.AutoField(primary_key=True)
    dep_name = models.CharField(max_length=100, default="")
    hod = models.ForeignKey(HOD, on_delete=models.CASCADE)

    def __str__(self):
        return self.dep_name


class DepartProgramme(models.Model):
    Morning = 'Morning'
    Eveninig = 'Evening'
    Both = 'Morning & Evening'

    shift = [
        (Morning, 'Morning'),
        (Eveninig, 'Evening'),
        (Both, 'Morning & Evening'),

    ]

    id = models.AutoField(primary_key=True)
    prog_name = models.CharField(max_length=100, default="")
    dep = models.ForeignKey(Department, on_delete=models.CASCADE)
    offers_in = models.CharField(max_length=50, choices=shift, default="")

    def __str__(self):
        return self.prog_name


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100, default="")
    course_code = models.CharField(max_length=100, default='')
    dep = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.course_name


class Faculty(models.Model):
    fac_id = models.AutoField(primary_key=True)
    fac_name = models.CharField(max_length=100, default="")
    fac_email = models.ForeignKey(LoginUser, on_delete=models.CASCADE)
    fac_img = models.ImageField(upload_to='faculty/', default="")
    dep = models.ForeignKey(Department, on_delete=models.CASCADE)
    user = models.ForeignKey(
        LoginUser, related_name="user", on_delete=models.CASCADE)

    def __str__(self):
        return self.fac_name


class AssignCourse(models.Model):
    Morning = 'Morning'
    Eveninig = 'Evening'

    shift = [
        (Morning, 'Morning'),
        (Eveninig, 'Evening'),
    ]

    id = models.AutoField(primary_key=True)
    assign_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    dep = models.ForeignKey(Department, on_delete=models.CASCADE)
    depart_prog = models.ForeignKey(DepartProgramme, on_delete=models.CASCADE)
    batch = models.IntegerField(default=0)
    time_shift = models.CharField(max_length=50, choices=shift, default="")
    active = models.BooleanField(max_length=50, default=True)

    def __str__(self):
        return f"{self.faculty.fac_name} assigned {self.assign_course.course_name} of {self.depart_prog} batch {self.batch} ({self.time_shift})"


class Student(models.Model):

    Morning = 'Morning'
    Eveninig = 'Evening'

    shift = [
        (Morning, 'Morning'),
        (Eveninig, 'Evening'),

    ]

    student_id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=100, default="")
    student_email = models.ForeignKey(LoginUser, on_delete=models.CASCADE)
    student_enroll_no = models.CharField(max_length=100, default=0)
    student_batch = models.IntegerField(default=0)
    student_depart = models.ForeignKey(Department, on_delete=models.CASCADE)
    student_depart_prog = models.ForeignKey(
        DepartProgramme, on_delete=models.CASCADE)
    student_time_shift = models.CharField(
        max_length=50, choices=shift, default="")
    student_contact = models.IntegerField(default=0)
    student_img = models.ImageField(upload_to='students/', default="")

    user = models.ForeignKey(
        LoginUser, related_name="stu_user", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student_name} {self.student_enroll_no}"


class Classroom(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100, default="")
    class_desc = models.TextField(blank=True)
    class_code = models.CharField(max_length=50, default=0)
    fac = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    user = models.ForeignKey(LoginUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.class_name


class Lecutre(models.Model):
    lec_id = models.AutoField(primary_key=True)
    lec_name = models.CharField(max_length=100, default="")
    lec_desc = models.TextField(blank=True)
    lec_file = models.FileField(upload_to='lectures/')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.lec_name


class Assignment(models.Model):
    assign_id = models.AutoField(primary_key=True)
    assign_name = models.CharField(max_length=100, default="")
    assign_desc = models.TextField(blank=True)
    assign_file = models.FileField(upload_to='assignments/')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    assign_deadline = models.DateField()
    assign_marks = models.FloatField(max_length=100, default="0")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assign_name} of {self.classroom.class_name}"


class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    quiz_name = models.CharField(max_length=100, default="")
    quiz_desc = models.TextField(blank=True)
    quiz_file = models.FileField(upload_to='quizzes/')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    quiz_deadline = models.DateField()
    quiz_marks = models.FloatField(max_length=100, default="0")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_name} of {self.classroom.class_name}"


class Announcement(models.Model):
    ann_id = models.AutoField(primary_key=True)
    ann_name = models.CharField(max_length=100, default="")
    ann_desc = models.TextField(blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ann_name


class QuizSubmission(models.Model):
    sub_id = models.AutoField(primary_key=True)
    quiz_name = models.TextField(blank=True)
    quiz_file = models.FileField(upload_to='submissions/quiz/')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    quiz_total_marks = models.FloatField(max_length=100, default=0)
    quiz_marks_obtained = models.FloatField(max_length=100, default=0)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Quiz Due")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    uploaded_at = models.DateField(auto_now_add=True)
    quiz_submission_date = models.DateField()

    def __str__(self):
        return f"{self.student.student_name} submitted {self.quiz_name} of {self.classroom.class_name}"


class AssignmentSubmission(models.Model):
    sub_id = models.AutoField(primary_key=True)
    assign_name = models.CharField(max_length=100, default="")
    assign_file = models.FileField(upload_to='submissions/assignments/')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    assign_total_marks = models.FloatField(max_length=100, default=0)
    assign_marks_obtained = models.FloatField(max_length=100, default=0)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Quiz Due")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    uploaded_at = models.DateField(auto_now_add=True)
    assignment_submission_date = models.DateField(default="2022-04-05")

    def __str__(self):
        return f"{self.student.student_name} submitted {self.assign_name} of {self.classroom.class_name}"


class StudentJoinedClassroom(models.Model):
    id = models.AutoField(primary_key=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_code = models.CharField(max_length=50, default=0)

    def __str__(self):
        return f"{self.student} joined {self.classroom}"


class TotalBatche(models.Model):
    Morning = 'Morning'
    Eveninig = 'Evening'

    shift = [
        (Morning, 'Morning'),
        (Eveninig, 'Evening'),
    ]

    id = models.AutoField(primary_key=True)
    batch = models.IntegerField(default=0)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    depart_programme = models.ForeignKey(DepartProgramme, on_delete=models.CASCADE , default='')
    time_shift = models.CharField(max_length=50, choices=shift, default="")

    def __str__(self):
        return f"{self.depart_programme.prog_name} batch {self.batch} ({self.time_shift})"


class StudentAttendance(models.Model):
    id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=100, default="")
    student_enroll_no = models.CharField(max_length=100, default="")
    student_depart = models.CharField(max_length=100, default="")
    student_enrolled_programme = models.CharField(max_length=100, default="")
    student_batch = models.IntegerField(default=0)
    student_time_shift = models.CharField(max_length=20, default="")
    student_img = models.ImageField(
        upload_to='students_attendance/', default="")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default="")
    attendance_week = models.IntegerField(default=0)
    attendance_date = models.DateField()
    attendance_status = models.CharField(max_length=5, default="")
    fac = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.student_name


class FacultyJobDetail(models.Model):
    Permanent = 'Permanent'
    Visiting = 'Vsiting'

    fac_type = [
        (Permanent, 'Permanenet'),
        (Visiting, 'Vsiting'),

    ]

    Morning = 'Morning'
    Eveninig = 'Evening'
    Both = 'Morning & Evening'

    shift = [
        (Morning, 'Morning'),
        (Eveninig, 'Evening'),
        (Both, 'Morning & Evening'),

    ]

    id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    faculty_type = models.CharField(
        max_length=50, choices=fac_type, default="")
    time_shift = models.CharField(max_length=50, choices=shift, default="")

    def __str__(self):
        return f"{self.faculty.fac_name} job details"
    
class StudentRegisterCourse(models.Model):
     
    Morning = 'Morning'
    Eveninig = 'Evening'
    

    shift = [
        (Morning, 'Morning'),
        (Eveninig, 'Evening'),

    ]

    Semester01 = 'Semester 01'
    Semester02 = 'Semester 02'
    Semester03 = 'Semester 03'
    Semester04 = 'Semester 04'
    Semester05 = 'Semester 05'
    Semester06 = 'Semester 06'
    Semester07 = 'Semester 07'
    Semester08 = 'Semester 08'
    
    sem = [
        (Semester01, 'Semester01'),
        (Semester02, 'Semester02'),
        (Semester03, 'Semester03'),
        (Semester04, 'Semester04'),
        (Semester05, 'Semester05'),
        (Semester06, 'Semester06'),
        (Semester07, 'Semester07'),
        (Semester08, 'Semester08'),
    ]

    id = models.AutoField(primary_key=True)
    courses = models.ManyToManyField(Course)
    time_shift = models.CharField(max_length=20, choices=shift, default="")
    batch_year = models.IntegerField(default=0)
    depart_programme = models.ForeignKey(DepartProgramme, on_delete=models.CASCADE)
    semester = models.CharField(max_length=50, choices=sem, default="")
    batch= models.ForeignKey(TotalBatche, on_delete=models.CASCADE)
    active = models.BooleanField(max_length=50, default=True)
    
    def __str__(self):
        return f"{self.depart_programme} Batch {self.batch_year}"
    
class AddCourseClo(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.CharField(max_length=100, default="")
    fac = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    clos = models.CharField(max_length=50, default="")
    clos_objective = models.CharField(max_length=200, default="")
    total_clos = models.CharField(max_length=50, default="")

    def __str__(self):
        return f"{self.fac.fac_name} add clo's of {self.course}"
    
class MapCourseCloPlo(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.CharField(max_length=100, default="")
    fac = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    mapped_clos_plos = models.CharField(max_length=50, default="")
    total_mapped_clos_plos = models.CharField(max_length=50, default="")

    def __str__(self):
        return f"{self.fac.fac_name} mapped clos and plos of {self.course}"
    
class AddAssessmentClosPlo (models.Model):
    id = models.AutoField(primary_key=True)
    course = models.CharField(max_length=100, default="")
    fac = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=50, default="")
    assessment_name = models.CharField(max_length=50, default="")
    mapped_clos_plos =models.CharField(max_length=100, default="")
    question_num = models.CharField(max_length=50, default="")
    total_questions = models.CharField(max_length=50, default="" )
    total_marks = models.FloatField(default=0)
    question_wise_map_clos_plos = models.CharField(max_length=50, default="")

    def __str__(self):
        return f"{self.fac.fac_name} added {self.assessment_type} assessment of {self.course}"
    
class UploadResult(models.Model):
    Morning = 'Morning'
    Eveninig = 'Evening'
    

    shift = [
        (Morning, 'Morning'),
        (Eveninig, 'Evening'),

    ]
    id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=100, default="")
    student_enroll_no = models.CharField(max_length=100, default="")
    department = models.CharField(max_length=100, default="")
    programme = models.CharField(max_length=100, default="")
    batch =  models.IntegerField(default="")
    time_shift = models.CharField(max_length=50, choices=shift, default="")
    course = models.CharField(max_length=100, default="")
    fac = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=50, default="")
    assessment_name = models.CharField(max_length=50, default="")
    mapped_plos_clos_cover = models.CharField(max_length=100, default="")
    total_marks = models.FloatField(default=0)
    obtained_marks = models.FloatField(default=0)

    def __str__(self):
        return f"{self.fac.fac_name} upload {self.assessment_type} result of {self.course}"