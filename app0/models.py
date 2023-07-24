from django.db import models
from django.contrib.auth.models import User, auth

# Create your models here.

class Student(models.Model):
    studentId = models.CharField(max_length=10,primary_key=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    # email = models.EmailField
    # mobile = models.PhoneNumberField
    def __str__(self):
        viewname = self.name + " (" + self.studentId + ")"
        return viewname

class Teacher(models.Model):
    teacherId = models.CharField(max_length=10,primary_key=True)
    name = models.CharField(max_length=30)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    def __str__(self):
        viewname = self.name + " (" + self.teacherId + ")"
        return viewname  

class Course(models.Model):
    courseId = models.CharField(max_length=10,primary_key=True)
    name = models.CharField(max_length=30)
    teacherObj = models.ForeignKey(Teacher,on_delete=models.CASCADE)
    totalStudents = models.IntegerField(default=0)
    totalClasses = models.IntegerField(default=0)
    def __str__(self):
        viewname = self.name + " (" + self.courseId + ")"
        return viewname
    
class Enrolment(models.Model):
    enrolmentId = models.AutoField(primary_key=True)
    studentObj = models.ForeignKey(Student,on_delete=models.CASCADE)
    courseObj = models.ForeignKey(Course,on_delete=models.CASCADE)
    classesAttended = models.IntegerField(default=0)
    def __str__(self):
        viewname = "(" + self.studentObj.studentId + ", " + self.courseObj.courseId + ")"
        return viewname


class AttendanceLog(models.Model):
    attendanceLogId = models.AutoField(primary_key=True)
    startTime = models.DateTimeField(auto_created=True)
    #place = models.ManyToManyField(Classrooms,on_delete=models.CASCADE)
    courseObj = models.ForeignKey(Course,on_delete=models.CASCADE)
    presentStudents = models.IntegerField(default=0)
    attendedStudents = models.ManyToManyField(Student)
    latitute = models.DecimalField(decimal_places=10,max_digits=20)
    longitude = models.DecimalField(decimal_places=10,max_digits=20)
    def __str__(self):
        viewname = self.courseObj.name + " (" + self.courseObj.courseId + ", " + self.startTime.strftime('%d/%m/%y %X') + ")"
        return viewname

    
class Proxy(models.Model):
    proxyId = models.AutoField(primary_key=True)
    attendanceLogObj = models.ForeignKey(AttendanceLog,on_delete=models.CASCADE)
    studentObjList = models.ManyToManyField(Student)
    deviceId = models.CharField(max_length=50)
    def __str__(self):
        viewname =  self.attendanceLogObj.courseObj.name + " (" + str(self.attendanceLogObj.attendanceLogId) + ", " + self.deviceId + ")"
        return viewname
    




