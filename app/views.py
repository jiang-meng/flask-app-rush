from flask import render_template, request, redirect, url_for, flash, json, session
from jinja2  import TemplateNotFound
from sqlalchemy import func
from datetime import datetime

# App modules
from app import app, db
from app.models import Member, Challenge, Tmatch


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

#####-------q1------------
#q1--register
@app.route('/q1register')
def q1register():
    return render_template('q1register.html')

@app.route('/q1registersubmit', methods=['GET','POST'])
def registersubmit():
    # get user input as string (same with input name)
    meid=request.form.get('meid')
    email=request.form.get('email')
    password=request.form.get('password')
    firstname=request.form.get('firstname')
    lastname=request.form.get('lastname')
    phone=request.form.get('phone')
    age=request.form.get('age')
    gender=request.form.get('gender')
    utr=request.form.get('utr')
    
    error=False
    if not meid or not email or not password or not firstname or not lastname or not phone or not age or not gender or not utr:
        flash('The information but lastname is required')
        error=True
    else:
        age=int(age)
        if age < 0:
            flash('age need >=0')
            error=True
    
    if not error:
        member=Member.query.get(meid)  
        if member is None:
            meid=request.form.get('meid')
            meid=int(meid)
            date=datetime.now()
            membership=Member(MEID = meid, FirstName=firstname,LastName=lastname,Email=email, Age=age,UTR=utr,Gender=gender,Phone=phone, MPassword=password, DateOfCreation=date)
            db.session.add(membership)
            db.session.commit()
            db.session.refresh(membership)
            flash('A new member with MEID='+str(membership.MEID)+'has been added')
            return render_template('q1afterregister.html', membership=membership)
        else:
            meid=int(meid)
            membership=Member.query.get(meid)
            membership.FirstName = firstname
            membership.LastName = lastname
            membership.Email = email
            membership.Age = age
            membership.Gender=gender
            membership.UTR=utr
            membership.Phone=phone
            membership.Mpassword=password
            membership.verified=True
            db.session.commit()
            flash("The MEID: "+str(meid)+'has been updated.')
            return render_template('q1afterregister.html', membership=membership)
    else:
        return render_template('q1register.html',meid=meid, firstname=firstname,lastname=lastname,email=email,age=age, gender=gender, utr=utr,phone=phone,password=password )

@app.route('/q1log')
def q1login():
    return render_template('q1login.html')

@app.route('/afterlogin', methods=['GET','POST'])
def afterLogin():
    meid = request.form.get('meid')
    password = request.form.get('password')

    if not meid or not password:
        flash('The MEID and Password are required')
        return render_template('q1login.html',meid=meid,password=password)
        
    else:
        member = Member.query.get(meid)
        if member is None:
            flash('Incorrect MEID or Password')
            return render_template('q1login.html',meid=meid,password=password)
        
        elif password==member.MPassword:
            session['meid'] = meid
            session['password'] = password
            currentHour = datetime.now().hour
            greeting = "morning" if currentHour < 12 else "afternoon"
            return render_template('q1afterlogin.html', greeting=greeting)
        
        else:
            flash('Incorrect MEID or Password')
            return render_template('q1login.html',meid=meid,password=password)
@app.route('/q1modify')
def q1modify():
    return render_template('q1modify.html')

@app.route('/aftermodify', methods=['GET','POST'])
def aftermodify():
    meid=request.form.get('meid')
    email=request.form.get('email')
    password1=request.form.get('password1')
    password2=request.form.get('password2')
    firstname=request.form.get('firstname')
    lastname=request.form.get('lastname')
    phone=request.form.get('phone')
    age=request.form.get('age')
    gender=request.form.get('gender')
    
    if not meid or not email or not password1 or not password2 or not firstname or not lastname or not phone or not age or not gender:
        flash('The information but lastname is required')
        return render_template('q1modify.html')
    
    elif int(age) < 0:
        flash('age need >=0')
        return render_template('q1modify.html')
    
    else:
        meid=int(meid)
        membership=Member.query.get(meid)
        
        if membership is None:
            flash('MEID is not exist')
            return render_template('q1modify.html')
        
        elif password1==membership.MPassword:
            membership.FirstName = firstname
            membership.LastName = lastname
            membership.Email = email
            membership.Age = age
            membership.Gender=gender
            membership.Phone=phone
            membership.Mpassword=password2
            membership.verified=True
            db.session.commit()
            flash("The Information of MEID: "+str(meid)+'has been updated.')
            return render_template('q1aftermodify.html', membership=membership)
        
        else:
            flash('Incorrect MEID or Password')
            return render_template('q1modify.html', meid=meid, password1=password1, password2=password2, age=age, email=email, firstname=firstname, lastname=lastname,gender=gender)
@app.route('/q1delete')
def q1delete():
    return render_template('q1delete.html')

@app.route('/afterdelete', methods=['GET','POST'])
def afterdelete():
    meid = request.form.get('meid')
    password = request.form.get('password')

    if not meid or not password:
        flash('The MEID and Password are required')
        return render_template('q1delete.html',meid=meid,password=password)
        
    else:
        member = Member.query.get(meid)
        if member is None:
            flash('Incorrect MEID or Password')
            return render_template('q1delete.html',meid=meid,password=password)
        
        elif password==member.MPassword:
            meid = request.form.get('meid')
            meid=int(meid)
            member=Member.query.get(meid)
            db.session.delete(member)
            db.session.commit()
            flash('Your Information has been deleted')
            return render_template('base.html')
        else:
            flash('Incorrect MEID or Password')
            return render_template('q1delete.html',meid=meid,password=password)     

@app.route('/q1chart')
def q1charts():
    result=db.session.query(Member.Gender.label('label'), func.count(Member.MEID).label('value')).group_by('Gender')
    chartData1 = [row._asdict() for row in result]
    chartData1 = json.dumps(chartData1)
    
    result=db.session.query(Member.Age.label('label'), func.count(Member.MEID).label('value')).group_by('Age')
    chartData2 = [row._asdict() for row in result]
    chartData2 = json.dumps(chartData2)
    
    return render_template('q1chart.html', chartData1 = chartData1, chartData2=chartData2)





# ---------q2----------
#after log
@app.route('/q2logsubmit')
def q2logSubmit():

            currentHour = datetime.now().hour
            greeting = "morning" if currentHour < 12 else "afternoon"
            filtered_challenges = Challenge.query.filter(Challenge.ChallengedMEID==int(session['meid'])).all()
            return render_template('challenge_afterlog.html', greeting=greeting, filtered_challenges = filtered_challenges)
                
# afterlog -- create a new challenge
@app.route('/q2create')
def create():
    return render_template('create_challenge.html')

## afterlog -- address challenge request
@app.route('/q2address')
def address():
    filtered_challenges = Challenge.query.filter(Challenge.ChallengedMEID==int(session['meid'])).all()
    return render_template('address_challenge.html', filtered_challenges = filtered_challenges)
## afterlog -- show chart
@app.route('/q2graph', methods=['GET', 'POST'])
def graph():
    c_meid = session.get('meid')
    result_win = db.session.query(Tmatch.WinnerMEID.label('Wins'), 
                                  func.count(Tmatch.WinnerMEID).label('value')).filter(Tmatch.WinnerMEID==c_meid)
    result_lose = db.session.query(Tmatch.LoserMEID.label('Loses'), 
                                   func.count(Tmatch.LoserMEID).label('value')).filter(Tmatch.LoserMEID==c_meid)
    
    chartData1 = [row._asdict() for row in result_win]
    chartData2 = [row._asdict() for row in result_lose]
    chartData = chartData1 + chartData2
    chartData = json.dumps(chartData)
    return render_template('challenge_graph.html', chartData=chartData)


## address request -- delete row in database
@app.route('/delete', methods=['GET', 'POST'])
def requestSubmit():
    delete_cid = request.form.get('cid')
    if not delete_cid:
        flash("if you want to delete a challenge, please input a CID")
    else:
        delete_challenge = Challenge.query.get(delete_cid)
        if not delete_challenge:
            flash('You input wrong CID')
        else:
            db.session.delete(delete_challenge)
            db.session.commit()
            return render_template('address_challenge.html')

@app.route('/allcha', methods=['GET', 'POST'])
def challengerinfo():
    filtered_challenges = Challenge.query.filter(Challenge.ChallengedMEID==int(session['meid'])).all()
    return render_template('challenge_info.html', filtered_challenges = filtered_challenges)

#create new challenge information
@app.route('/createchallenge', methods=['GET', 'POST'])
def challengeFormSubmit():
    # get user input values
    c_id = request.form.get('cid')
    challenger_meid = request.form.get('challengerID')
    challenged_meid = request.form.get('challengedID')
    c_date = request.form.get('date')
    c_note = request.form.get('note')
    
    
    #check error
    error = False
    if not c_id:
        flash('The CID is required')
        error = True
    else:
        if Challenge.query.get(c_id):
            flash('The CID has already exists, please change another CID')
            error = True
    
    if not challenger_meid:
        flash('The challenger id is required')
        error = True
    else:
        challenger_member = Member.query.get(challenger_meid)
        if not challenger_member:
            flash('The Challenger MEID does not exist')
            error = True
        
    if not challenged_meid:
        flash('The challenged id is required')
        error = True
    else:
        challenged_member = Member.query.get(challenged_meid)
        if not challenged_member:
            flash('The Challenger MEID does not exist')
            error = True
            
    if not c_date:
        flash('The challenge date is required')
        error = True
        
    
    if not error:
        challenge = ''
        if not challenge:
            challenge=Challenge(CID = c_id, ChallengerMEID=challenger_meid, ChallengedMEID=challenged_meid, DateOfChallenge=c_date, Notes=c_note)
            db.session.add(challenge)
            db.session.commit()
            db.session.refresh(challenge)
            flash('A new challenge with CID='+str(challenge.CID)+'has been added')
            return render_template('challenge_info.html', challenge=challenge)
        else:
            c_id=int(c_id)
            challenge=Challenge.query.get(c_id)
            challenge.CID = c_id
            challenge.ChallenderMEID=challenger_meid
            challenge.ChallendedMEID=challenged_meid
            challenge.DateOfChallenge=c_date
            challenge.Notes=c_note
            challenge.verified=True
            db.session.commit()
            flash("You update Challenging information.The challenge with CID"+str(c_id)+'has been updated.')
            return render_template('create_info.html', challenge=challenge)
    else:
        return render_template('create_challenge.html',error=error, cid=c_id, challengerID=challenger_meid, challengedID=challenged_meid, date=c_date, note=c_note)

 


