from flask import Flask,render_template,redirect,request,session,flash,url_for
from flask_bcrypt import bcrypt
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO
from flask import send_file
import cv2
import glob


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///POV.db'

db=SQLAlchemy(app)

#creating a table to store user's information
class User(db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name=name
        self.email=email
        self.password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

#table to store event details
class Event_details(db.Model):
    event_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    event_name=db.Column(db.String(200),nullable=False)
    end_date=db.Column(db.DateTime,nullable=False)
    photos_per_person=db.Column(db.Integer,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow())

    def __init__(self,event_name,end_date,photos_per_person,created_at):
        #self.user_id=user_id
        self.event_name=event_name
        self.end_date=end_date
        self.photos_per_person=photos_per_person
        self.created_at=created_at


#table to store the relationship between user and events
#many to many relationship
class user_event(db.Model):
    user_event_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False)
    event_id=db.Column(db.Integer,db.ForeignKey('event_details.event_id'), nullable=False)
    photos_left=db.Column(db.Integer)

    def __init__(self,user_id,event_id):
        self.user_id=user_id
        self.event_id=event_id
        event=Event_details.query.filter_by(event_id=event_id).first()
        if event:
            self.photos_left=event.photos_per_person



#creating tables
with app.app_context():
    #db.drop_all()
    db.create_all()


app.secret_key = 'WORK_IT_OUT'



@app.route('/')
def index():
    return render_template('signup.html')


def is_strong(password):
    upper=False
    for i in password:
        if i.isupper():
            upper=True
            break
    lower=False
    for i in password:
        if i.islower():
            lower=True
            break

    digit=False
    for i in password:
        if i.isdigit():
            digit=True
            break

    character=False
    for i in password:
        if i in ('$','#','@'):
            character=True
            break
    if len(password)>=6 and len(password)<=12 and upper and lower and digit and character:
        return True
    else:
        return False

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        password=request.form['password'] 

        if User.query.filter_by(name=name).first():
            flash('username is already taken')
            return render_template('signup.html')

        elif User.query.filter_by(email=email).first():
            flash('user already exists')
            return render_template('signup.html')
        if is_strong(password): 
            new_user=User(name=name,email=email,password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Your account is created successfully.')
            return redirect('/login')
        else:
            flash('enter a strong password')
            return render_template('signup.html')
        
    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']

        user=User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['name']=user.name
            session['email']=user.email
            session['password']=user.password
            return redirect('/eventgen')
        else:
            flash('Invalid credentials')
            return render_template('login.html')
        
    return render_template('login.html')

@app.route('/profile',methods=['GET','POST'])
def profile():
    email=session.get('email')
    user=User.query.filter_by(email=email).first()
    return render_template('profile.html',id=user.user_id,name=user.name,email=user.email)


@app.route('/logout')
def logout():
    session.pop('name',None)
    return redirect('/login')



def delete_event():
    current_datetime = datetime.utcnow()
    delete_event=Event_details.query.filter(Event_details.end_date<current_datetime).all()

    for event in delete_event:
        db.session.delete(event)
    db.session.commit()

        


@app.route('/eventgen',methods=['GET','POST'])
def eventgen():
    if request.method=='POST' :
       data_from_form= request.form['data_from_form']
       if session['name']:
           session['data_from_form']=data_from_form
           return render_template('setDate.html',data_from_form=data_from_form)
       else:
           return render_template('eventgen.html')
    delete_event()
    return render_template('eventgen.html')


    

from datetime import datetime

@app.route('/setDate', methods=['GET', 'POST'])
def setDate():
    global end_date, photos_per_person
   

    today = datetime.today().strftime('%Y-%m-%d')
    
    
    if request.method == 'POST':
        end_date = request.form['end_date']
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        photos_per_person = int(request.form['photos_per_person'])
    
    event_name=session['data_from_form']
    email=session.get('email')
    user=User.query.filter_by(email=email).first()
    if user is None:
        flash('User with the provided email does not exist')
    else:
            new_event=Event_details(event_name=event_name,end_date=end_date,photos_per_person=photos_per_person,created_at=datetime.utcnow())
            db.session.add(new_event)
            db.session.commit()
            new_event = db.session.query(Event_details).filter_by(event_name=event_name).first()
            if new_event is not None:
                new_user_event=user_event(user_id=user.user_id,event_id=new_event.event_id)
                db.session.add(new_user_event)
                db.session.commit()
            else:
                return "event not found"
            return redirect(url_for('allEvents'))
    #delete_event()
    return render_template('setDate.html', end_date=end_date, photos_per_person=photos_per_person,today=today)
            
@app.route('/camera/<int:id>',methods=['GET','POST'])
def camera(id):
    email=session.get('email')
    user=User.query.filter_by(email=email).first()
    if user is not None:

        data = f"http://127.0.0.1:5000/allEvents_qr/{user.user_id}/{id}"

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
    

        qr_img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        qr_img.save(f"qr_code_{user.user_id}_{id}.png")
        img_buffer.seek(0)
        
        return send_file(img_buffer, mimetype='image/png')
    else:
        return "User not found", 404
    

@app.route('/allEvents_qr/<int:id>/<int:eventid>',methods=['GET','POST'])
def allEvents_qr(id,eventid):
    user=User.query.filter_by(user_id=id).first() 
    new_user_events = user_event.query.filter_by(user_id=id,event_id=eventid).all()
    if new_user_events is not None:

        events = Event_details.query.filter_by(event_id=eventid).first()
        email=session.get('email')
        user=User.query.filter_by(email=email).first()
        new_event= db.session.query(Event_details).filter_by(event_name=events.event_name).first()
        if new_event is not None:
            new_user_event=user_event(user_id=user.user_id,event_id=new_event.event_id)
            db.session.add(new_user_event)
            db.session.commit()
    return render_template('qrEvent.html', events=events)

@app.route('/allEvents',methods=['GET','POST'])
def allEvents():
    email=session.get('email')
    user=User.query.filter_by(email=email).first()
      
    if user:
        new_user_events = user_event.query.filter_by(user_id=user.user_id).all()
        if new_user_events:
            event_ids = [event.event_id for event in new_user_events]  # Extract event IDs from the list of new_user_events
            events = Event_details.query.filter(Event_details.event_id.in_(event_ids)).all()
            return render_template('allEvents.html', events=events)
        else:
            return 'User has no associated events'
    else:
        return 'User not found'

import os
@app.route('/click/<int:eid>',methods=['GET','POST'])
def capture_photos_with_key(eid):
    email=session.get('email')
    user=User.query.filter_by(email=email).first()
    
    if user:
            new_user_event=user_event.query.filter_by(user_id=user.user_id,event_id=eid).first()
            
            events = Event_details.query.filter_by(event_id=eid).first()
    # Access the default camera (index 0)
            camera = cv2.VideoCapture(0)

            # Check if the camera is opened successfully
            if not camera.isOpened():
                print("Error: Unable to access the camera")
                return "Error: Unable to access the camera"
            
            #num_photos = events.photos_per_person
            num_photos=new_user_event.photos_left
            #return f'{new_user_event.event_id} left'
            if num_photos==0:
               return 'photos limit reached'
            else:
                while num_photos>0:
                    # Capture a frame from the camera
                    ret, frame = camera.read()

                    # Display the frame
                    cv2.imshow('click photo', frame)

                    # Wait for the 's' key to be pressed
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('s'):
                        # Save the captured photo
                        static = os.path.join(os.getcwd(), 'static')
                        filename = f'{events.event_name}_{user.user_id}_{eid}_{num_photos}.jpg'
                        filepath = os.path.join(static, filename)
                        cv2.imwrite(filepath, frame)
                        #cv2.imwrite(filename, frame)
                        print(f"Photo captured successfully: {filename}")
                        num_photos-=1
                    
                    if key == ord('q'):
                        break

                new_user_event.photos_left=num_photos
                db.session.commit()

            # Release the camera and close OpenCV windows
            camera.release()
            cv2.destroyAllWindows()
            return redirect(url_for('allEvents'))
    
@app.route('/gallary/<int:eventid>',methods=['GET','POST'])
def gallary(eventid):
    event=Event_details.query.filter_by(event_id=eventid).first()
    if event:
        photos = glob.glob(f'static/{event.event_name}_*_{eventid}_[0-9].jpg')
        final=[]
        for photo in photos:
            final.append(photo[7:])
            print(photo)
        
        return render_template('gallary.html', photos=final)
    else:
        return "no photos"
    

if __name__=='__main__':
  
    app.run(debug=True)