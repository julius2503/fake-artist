from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    is_Gamemaster = db.Column(db.Boolean, unique=False, default=False)
    is_Faker = db.Column(db.Boolean, unique=False, default=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))

app.app_context().push()
db.create_all()
#

@app.route("/", methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        if "usernameAdd" in request.form:
            username = request.form['usernameAdd']
            new_user = User(
                name = username
            )
            db.session.add(new_user)
            db.session.commit()
            print("Added User " + username)
        if "usernameDelete" in request.form:
            userId = request.form['usernameDelete']
            username = db.session.query(User).filter(User.id==userId).one()
            username = str(username.name)
            db.session.query(User).filter(User.id==userId).delete()
            db.session.commit()
            print("Deleted User " + username)
        if "beginGame" in request.form:
            if db.session.query(User).count() <= 3:
                flash('YOU NEED TO BE AT LEAST 4 PLAYERS')
                print('not enough players')
            else:
                gamemaster = db.session.query(User).filter(User.is_Gamemaster == True).all()
                faker = db.session.query(User).filter(User.is_Faker == True).all()
                for gm in gamemaster:
                    gm.is_Gamemaster = False
                for fake in faker:
                    fake.is_Faker = False
                db.session.commit()
                randG = 0
                randF = 0
                while randF == randG:
                    randG = random.randrange(0, db.session.query(User).count())
                    randF = random.randrange(0, db.session.query(User).count())
                for usr in db.session.query(User).all():
                    if randG  == 0:
                        usr.is_Gamemaster = True
                        break
                    randG-=1
                for usr in db.session.query(User).all():
                    if randF  == 0:
                        usr.is_Faker = True
                        break
                    randF-=1    
                db.session.commit()
                print("Start Game")
    users = User.query.order_by(User.created_at).all()
    return  render_template("index.html", users=users)

@app.route("/<id>", methods=['GET', 'POST'])
def playGame(id):
    user = db.session.query(User).filter(User.id == id).first()
    gamemaster = db.session.query(User).filter(User.is_Gamemaster == True).first()
    faker = db.session.query(User).filter(User.is_Faker == True).first()
    if user.is_Gamemaster == True:
        return render_template("gamemaster.html", user=user)
    if user.is_Faker == True:
        return render_template("faker.html", user=user, gamemaster=gamemaster)
    else:
        return render_template("general.html", user=user, gamemaster=gamemaster)
    


if __name__ == "__main__":
    app.run(debug=True, port=8082)