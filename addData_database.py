import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendaceface-b73be-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    '124562':{
        'name':'Akshit Sharma',
        'major':'IT',
        'starting_year':2021,
        'total_attendance':5,
        'standing':'G',
        'year':'4',
        'last_attendance_time':'2022-12-11 00:54:34'
    },
    '321654':{
        'name':'Murtaza',
        'major':'Robotics',
        'starting_year':2017,
        'total_attendance':6,
        'standing':'G',
        'year':'4',
        'last_attendance_time':'2022-12-11 00:54:34'
    },
    '852741':{
        'name':'Emily Blunt',
        'major':'Commerce',
        'starting_year':2015,
        'total_attendance':10,
        'standing':'O',
        'year':'2',
        'last_attendance_time':'2022-12-11 00:54:34'
    },
    '963852':{
        'name':'Elon Musk',
        'major':'CSE',
        'starting_year':2014,
        'total_attendance':2,
        'standing':'A',
        'year':'4',
        'last_attendance_time':'2022-12-11 00:54:34'
    }
}

for key,value in data.items():
    ref.child(key).set(value)