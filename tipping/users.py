from app import db, app
from models import User

USERS = {
    "samjr.bradshaw@gmail.com": {
        
        
        "first_name": "Sam",
        "last_name": "Bradshaw",
    },
    "fiona@nimbus.financial": {
        
        
        "first_name": "Fiona",
        "last_name": "Bradshaw",
    },
    "kim@nimbus.financial": {
        
        
        "first_name": "Kim",
        "last_name": "Bradshaw",
    },
    "tash?": {
        
        
        "first_name": "Tash",
        "last_name": "Bradshaw",
    },
    "nan?": {
        
        
        "first_name": "Nan",
        "last_name": "Morland",
    },
    
    "barbee?": {
        
        "first_name": "Barbee",
        "last_name": "Morland",
    },
}

def createUsers():
    with app.app_context():
        users = User.query.all()
        users = [u.email for u in users]
        for u in USERS:
            if u not in users:
                user = User(**USERS[u], email=u)
                db.session.add(user)
        db.session.commit()
