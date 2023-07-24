from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from decimal import Decimal
from .models import *
import json
from datetime import datetime,timedelta
from threading import Timer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view,authentication_classes,permission_classes
# Create your views here.

@api_view(['GET','POST'])
def index(request):
    if request.user.is_authenticated:
        print('Refresh:',request.user)
        returnresponse = {'message':'success'}
        if (Student.objects.filter(user=request.user).exists()):
            returnresponse['role'] = 'Student'
        else:
            returnresponse['role'] = 'Teacher'
        return JsonResponse(returnresponse,status=200)
    returnresponse = {'message':'failed'}
    return JsonResponse(returnresponse,status=401)

def login2(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username,password=password)
    if user is not None:
        token,_ = Token.objects.get_or_create(user=user)
        returnresponse = {'message':'Login Succesful','token':token.key}
        return JsonResponse(returnresponse,status=200)
    else :
        returnresponse = {'message':'Invalid Credentials'}
        return JsonResponse(data=returnresponse,status=401)


class login(APIView):
    def post(self,request):
        data = json.loads(request.body)
        print(data)
        username = data['username']
        password = data['password']
        user = authenticate(username=username,password=password)
        if user is not None:
            token,_ = Token.objects.get_or_create(user=user)
            print("Login:",user)
            returnresponse = {'message':'Login Succesful','token':token.key}
            if(Student.objects.filter(user=user).exists()):
                returnresponse['role'] = 'Student'
            else:
                returnresponse['role'] = 'Teacher'
            return JsonResponse(returnresponse,status=200)
        else :
            returnresponse = {'message':'Invalid Credentials'}
            return JsonResponse(returnresponse,status=401)
        # return JsonResponse({})
        
class logout(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        # print(request.headers)
        token = Token.objects.get(user=request.user)
        token.delete()
        print("Logout:",request.user)
        returnresponse = {'message':'Logout Succesful'}
        return Response(data=returnresponse)

class studentDetails(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        studentObj = Student.objects.get(user=request.user)
        returnresponse = {'studentId':studentObj.studentId,'name':studentObj.name}
        return JsonResponse(returnresponse,status=200)

@api_view(['POST'])
def registerUser(data):
    username = data['username']
    password = data['password']
    newUser = User.objects.filter(username=username)
    returnresponse = {'user_exists':True}
    if newUser.exists():
        newUser = User.objects.get(username=username)
    else :
        returnresponse['user_exists']=False
        newUser = User.objects.create_user(username=username,password=password)
        newUser.save()
    returnresponse['user'] = newUser
    return returnresponse

@api_view(['POST'])
def register(request):
    data = json.loads(request.body)
    print(data)
    usermsg = registerUser(data)
    returnresponse = {'message':'User exists'}
    if(usermsg['user_exists']):
        return JsonResponse(returnresponse,status=200)
    role = data['role']
    userId = data['userId']
    name = data['name']
    if role == 'Student':
        newUser = Student(studentId=userId,name=name,user=usermsg['user'])
    else:
        newUser = Teacher(teacherId=userId,name=name,user=usermsg['user']) 
    newUser.save()
    returnresponse['message'] = 'User created'
    return JsonResponse(returnresponse,status=200)

@api_view(['POST'])
def home(request):
    curr_user = request.user
    # curr_user = User.objects.get(username=request.GET['username'])   ##############################################################
    if(Student.objects.filter(user=curr_user).exists()):
        curr_student = Student.objects.get(user = curr_user)
        curr_enrolments = Enrolment.objects.filter(studentObj = curr_student).iterator()
        total_courses = []
        for item in curr_enrolments:
            course = {}
            courseObj = item.courseObj
            course['courseId'] = courseObj.courseId
            course['name'] = courseObj.name
            course['totalClasses'] = courseObj.totalClasses
            course['classesAttended'] = item.classesAttended
            total_courses.append(course)
        returnresponse = {'courses':total_courses}
        return JsonResponse(returnresponse)
    curr_Teacher = Teacher.objects.get(user=curr_user)
    curr_courses = Course.objects.filter(teacherObj=curr_Teacher).iterator()
    total_courses = []
    for item in curr_courses:
        total_courses.append({'courseId':item.courseId,'name':item.name,'totalClasses':item.totalClasses,'totalStudents':item.totalStudents})
    returnresponse = {'courses':total_courses}
    return JsonResponse(returnresponse)


@api_view(['POST'])
def enrol(request,courseId):
    curr_user = request.user
    # curr_user = User.objects.get(username=request.GET['username'])   ##############################################################
    studentObj = Student.objects.get(user=curr_user)
    returnresponse = {}; status=200
    if(Course.objects.filter(courseId=courseId).exists()):
        courseObj = Course.objects.get(courseId=courseId)
        if(Enrolment.objects.filter(courseObj=courseObj,studentObj=studentObj).exists()):
            returnresponse['message'] = "Already enrolled in course"
        else:
            newEnrolment = Enrolment(studentObj=studentObj,courseObj=courseObj)
            newEnrolment.save()
            courseObj.totalStudents += 1
            courseObj.save()
            returnresponse['message'] = "Enrolment Succesful"
    else:
        returnresponse['message'] = "Course Not Found"
        status = 404
    return JsonResponse(returnresponse,status=status)

@api_view(['POST'])
def markAttendance(request,attendanceLogId,deviceId):
    curr_user = request.user
    # curr_user = User.objects.get(username=request.GET['username'])   ##############################################################
    studentObj = Student.objects.get(user=curr_user)
    attendanceLogObj = AttendanceLog.objects.get(attendanceLogId=attendanceLogId)
    returnresponse = {}
    if(Proxy.objects.filter(attendanceLogObj=attendanceLogObj,studentObjList=studentObj).exists()):
        returnresponse['message'] = "Attendance already Marked"
    else:
        if(Proxy.objects.filter(attendanceLogObj=attendanceLogObj,deviceId=deviceId)):
            ProxyObj = Proxy.objects.get(attendanceLogObj=attendanceLogObj,deviceId=deviceId)
            ProxyObj.studentObjList.add(studentObj)
            ProxyObj.save()
            returnresponse['message'] = "Proxy detected"
        else:
            newProxy = Proxy(attendanceLogObj=attendanceLogObj,deviceId=deviceId)
            newProxy.save()
            newProxy.studentObjList.add(studentObj)
            newProxy.save()
            returnresponse['message'] = "Attendance Marked"
    return JsonResponse(returnresponse)

def endAttendance(attendanceLogId):
    attendanceLogObj = AttendanceLog.objects.get(attendanceLogId=attendanceLogId)
    # proxyList = attendanceLogObj.proxy_set.all().iterator()
    proxyList = Proxy.objects.filter(attendanceLogObj=attendanceLogObj).iterator()
    for proxyObj in proxyList:
        if proxyObj.studentObjList.all().count()==1:
            attendanceLogObj.presentStudents += 1
            for studentObj in proxyObj.studentObjList.filter().iterator():
                attendanceLogObj.attendedStudents.add(studentObj)
                enrolmentObj = Enrolment.objects.get(studentObj=studentObj,courseObj=attendanceLogObj.courseObj)
                enrolmentObj.classesAttended += 1
                enrolmentObj.save()
                print("Attendance Marked for",studentObj.name,"for attednaceId ",attendanceLogId)
            proxyObj.studentObjList.clear()
            proxyObj.delete()
            attendanceLogObj.save()

@api_view(['POST'])
def startAttendance(request,courseId,latitude,longitude):
    latitude = Decimal(latitude)
    longitude = Decimal(longitude)
    courseObj = Course.objects.get(courseId=courseId)
    if(AttendanceLog.objects.filter(courseObj=courseObj,startTime__lt=datetime.now(),startTime__gt=datetime.now()-timedelta(minutes=(150/60))).exists()):
        returnresponse={'message':'An active Attendance Log exists'}
        return JsonResponse(returnresponse,status=200)
    newAttendanceLog = AttendanceLog(courseObj=courseObj,startTime=datetime.now())
    newAttendanceLog.latitute = latitude
    newAttendanceLog.longitude = longitude
    newAttendanceLog.save()
    courseObj.totalClasses += 1
    courseObj.save()
    returnresponse = {'message':"Attendance Started"}
    attendanceLogId = newAttendanceLog.attendanceLogId
    endAttendanceTimer = Timer(2*60,endAttendance,[attendanceLogId])
    endAttendanceTimer.start()
    return JsonResponse(returnresponse,status=200)

@api_view(['POST'])
def pingAttendance(request,courseId):
    courseObj = Course.objects.get(courseId=courseId)
    status = 404
    returnresponse = {'message':'No Active Attendance Found'}
    if(AttendanceLog.objects.filter(courseObj=courseObj,startTime__lt=datetime.now(),startTime__gt=datetime.now()-timedelta(minutes=(100/60))).exists()):
        AttendanceLogObj = AttendanceLog.objects.get(courseObj=courseObj,startTime__lt=datetime.now(),startTime__gt=datetime.now()-timedelta(minutes=(110/60)))
        status = 200
        returnresponse = {'message':'Ping Successful','attendanceLogId':AttendanceLogObj.attendanceLogId,'latitude':float(AttendanceLogObj.latitute),'longitude':float(AttendanceLogObj.longitude)}
    return JsonResponse(returnresponse,status=status)

@api_view(['POST'])
def attendanceLog(request,courseId):
    courseObj = Course.objects.get(courseId=courseId)
    attendanceLogList = AttendanceLog.objects.filter(courseObj=courseObj,startTime__lt=datetime.now()-timedelta(minutes=(130/60))).order_by('-startTime').iterator()
    totalLog = []
    for item in attendanceLogList:
        newLog = {'attendanceLogId':item.attendanceLogId,'startTime':item.startTime.strftime("%d/%m/%y %X"),'presentStudents':item.presentStudents}
        totalLog.append(newLog)
    returnresponse = {'attendanceLog':totalLog}
    return JsonResponse(returnresponse)

@api_view(['POST'])
def resolveProxy(request,proxyId,studentId):
    proxyObj = Proxy.objects.get(proxyId=proxyId)
    studentObj = Student.objects.get(studentId=studentId)
    attendanceLogObj = proxyObj.attendanceLogObj
    attendanceLogObj.attendedStudents.add(studentObj)
    attendanceLogObj.presentStudents += 1
    attendanceLogObj.save()
    enrolmentObj = Enrolment.objects.get(studentObj=studentObj,courseObj=attendanceLogObj.courseObj)
    enrolmentObj.classesAttended += 1
    enrolmentObj.save()
    proxyObj.studentObjList.remove(studentObj)
    if(proxyObj.studentObjList.all().count()==0):
        proxyObj.delete()
    returnresponse = {'message':'Attendance Marked'}
    return JsonResponse(returnresponse)

class enrolmentList(APIView):
    def post(self,request,courseId):
        courseObj = Course.objects.get(courseId=courseId)
        enrolmentObjList = Enrolment.objects.filter(courseObj=courseObj).order_by('studentObj__studentId').iterator()
        studentList = []
        for item in enrolmentObjList:
            studentObj = item.studentObj
            student = {'studentId':studentObj.studentId,'name':studentObj.name,'classesAttended':item.classesAttended}
            studentList.append(student)
        returnresponse = {'enrolmentList':studentList}
        return JsonResponse(returnresponse,status=200)
    
@api_view(['POST'])
def analysis(request,studentId,courseId):
    print("******",studentId,"*********",courseId)
    courseObj = Course.objects.get(courseId=courseId)
    studentObj = Student.objects.get(studentId=studentId)
    enrolmentObj = Enrolment.objects.get(courseObj=courseObj,studentObj=studentObj)
    attendanceLogList = AttendanceLog.objects.filter(courseObj__courseId=courseId).order_by('-startTime').iterator()
    attendanceList = []
    for item in attendanceLogList:
        verdict = "Absent"
        if(item.attendedStudents.filter(studentId=studentId).exists()) : verdict="Present"
        attendance = {'attendanceLogId':item.attendanceLogId,'startTime':item.startTime.strftime("%d/%m/%y %X"),'verdict':verdict}
        attendanceList.append(attendance)
    returnresponse = {'totalClasses':courseObj.totalClasses,'classesAttended':enrolmentObj.classesAttended,'attendanceList':attendanceList}
    return JsonResponse(returnresponse,status=200)


@api_view(['POST'])
def dayAttendance(request,attendanceLogId):
    attendanceLogObj = AttendanceLog.objects.get(attendanceLogId=attendanceLogId)
    enrolmentObjList = Enrolment.objects.filter(courseObj=attendanceLogObj.courseObj).order_by("studentObj__studentId")
    proxyObjList = attendanceLogObj.proxy_set.all()
    # proxyObjList = Proxy.objects.filter(attendanceLogObj=attendanceLogObj).iterator()
    attended = []; absent=[]; proxy=[]
    for enrolmentObj in enrolmentObjList:
        studentObj = enrolmentObj.studentObj
        student =  {'studentId':studentObj.studentId,'name':studentObj.name}
        if(attendanceLogObj.attendedStudents.filter(studentId=enrolmentObj.studentObj.studentId).exists()):
            attended.append(student)
        else:
            isProxy = False
            for proxyObj in proxyObjList:
                if(proxyObj.studentObjList.filter(studentId=enrolmentObj.studentObj.studentId).exists()):
                    isProxy = True
                    break
            if(not isProxy):
                absent.append(student)
        
    for proxyObj in proxyObjList:
        newproxy = {'proxyId': proxyObj.proxyId, 'deviceId':proxyObj.deviceId,'students':[]}
        for studentObj in proxyObj.studentObjList.all().order_by("studentId").iterator():
            student =  {'studentId':studentObj.studentId,'name':studentObj.name}
            newproxy['students'].append(student)
        proxy.append(newproxy)
    returnresponse = {'dayAttendance': {'attended':attended,'absent':absent,'proxy':proxy}}
    print(returnresponse)
    return JsonResponse(returnresponse,status=200)
        
            








            