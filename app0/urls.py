from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('login2', views.login2, name='login2'),
    path('login', views.login.as_view(), name='login'),
    path('logout', views.logout.as_view(), name="logout"),
    path('studentDetails', views.studentDetails.as_view(),name='studentDetails'),
    path('register', views.register, name='register'),
    path('home', views.home, name='home'),
    path('enrol/<str:courseId>', views.enrol, name='enrol'),
    path('markAttendance/<int:attendanceLogId>/<str:deviceId>', views.markAttendance, name='markAttendance'),
    path('startAttendance/<str:courseId>/<str:latitude>/<str:longitude>', views.startAttendance, name='startAttendance'),
    path('pingAttendance/<str:courseId>', views.pingAttendance, name='pingAttendance'),
    path('resoveProxy/<int:proxyId>/<str:studentId>', views.resolveProxy, name='resolveProxy'),
    path('enrolmentList/<str:courseId>', views.enrolmentList.as_view(), name='enrolmentList'),
    path('attendanceLog/<str:courseId>', views.attendanceLog, name='attendanceLog'),
    path('dayAttendance/<int:attendanceLogId>', views.dayAttendance, name="dayAttendance"),
    # path('enrolmentList/<str:courseId>', views.enrolmentList, name='enrolmentList'),
    path('analysis/<str:courseId>/<str:studentId>', views.analysis, name='analysis'),
]
