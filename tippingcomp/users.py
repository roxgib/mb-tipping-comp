from .models import User

USERS = {
    "samjr.bradshaw@gmail.com": {
        
        "password": "tillymay",
        "first_name": "Sam",
        "last_name": "Bradshaw",
    },
    "fiona@nimbus.financial": {
        
        "password": "tillymay",
        "first_name": "Fiona",
        "last_name": "Bradshaw",
    },
    "kim@nimbus.financial": {
        
        "password": "tillymay",
        "first_name": "Kim",
        "last_name": "Bradshaw",
    },
    "tash?": {
        
        "password": "tillymay",
        "first_name": "Tash",
        "last_name": "Bradshaw",
    },
    "nan?": {
        
        "password": "tillymay",
        "first_name": "Nan",
        "last_name": "Morland",
        "email": "morland?",
    },
    
    "barbee?": {
        
        "password": "tillymay",
        "first_name": "Barbee",
        "last_name": "Morland",
    },
}

def createUsers():
    users = User.objects.all()
    for u in USERS:
        if u['first_name'] not in users:
            user = User(**u)
            user.save()
