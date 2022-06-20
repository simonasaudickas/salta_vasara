import os
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
#from slaptazodziai import postgres
from datetime import datetime
import forms
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
#from flask_admin import Admin
#from flask_admin.contrib.sqla import ModelView
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema

#basedir = os.path.abspath(os.path.dirname(__file__))
app= Flask(__name__)


#db configuration
app.config['SECRET_KEY'] = '4654f5dfadsrfasdr54e6rae'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/kursas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)

login_manager = LoginManager(app)
login_manager.login_view = 'prisijungti'
login_manager.login_message = 'info'
login_manager.login_message = 'Prisijunkite, jei norite matyti puslapi'
#admin = Admin(app, name='Panele')
#create tables

class Vartotojas(db.Model, UserMixin):
    __table_args__ = {"schema":"biudzetas"}
    __tablename__ = "useris"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column('nickas', db.String(20), unique=True, nullable=True)
    vardas = db.Column('vardas', db.String(20), unique=False, nullable=False)
    pavarde = db.Column('pavarde', db.String(30), unique=False, nullable=False)
    el_pastas = db.Column('email', db.String(50), unique=True, nullable=False)
    slaptazodis = db.Column('slaptazodis', db.String(60), unique=True, nullable=False)



class Irasai(db.Model):
    __table_args__= {"schema":"biudzetas"}
    __tablename__ = "biudzeto_irasai"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column("dt", DateTime, default=datetime.now())
    pajamos = db.Column("pajamos", db.Boolean)
    suma = db.Column("kiekis", db.Integer)
    vartotojas_id = db.Column(db.Integer, db.ForeignKey('biudzetas.useris.id'))
    vartotojas = db.relationship("Vartotojas", lazy=True)

"""class Darbuotojas(db.Model):
    __table_args__ = {"schema": "biudzetas"}
    __tablename__ = "darbuotojai"
    id = db.Column(db.Integer, primary_key=True)
    darbuotojas= db.Column('darbuotojas', db.Boolean, default=False)
    #vartotojo_id = db.Column('user_id',db.Integer)
    vartotojas_id = db.Column(db.Integer, db.ForeignKey('biudzetas.useris.id'))
    vartotojas = db.relationship("Vartotojas", lazy=True)"""


class RecordSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Irasai
        include_fk = True

record_schema =RecordSchema()
records_schema = RecordSchema(many=True)



@login_manager.user_loader
def load_user(id):
    try:
        return Vartotojas.query.get(id)
    except:
        return None

#routes in site
@app.route('/')
def index():
    menus = [{'url': 'prisijungti', 'menu_title': 'Prisijungti', 'parameters': {'param1': 'test'}},
             {'url': 'registracija', 'menu_title': 'Registruotis', 'parameters': {'param1': 'test'}},
             {'url': 'atsijungti', 'menu_title': 'Atsijungti', 'parameters': {'param1': 'test'}}]
    return render_template('home.html', menus=menus)



@app.route('/registruotis', methods=['GET', 'POST'])
def registracija():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    forma = forms.RegistracijosForma()
    if forma.validate_on_submit():
        koduotas_slaptazodis = bcrypt.generate_password_hash(forma.slaptazodis.data).decode('utf-8')
        vartotojas = Vartotojas(user_name = forma.user_name.data, vardas=forma.vardas.data, pavarde=forma.pavarde.data, el_pastas=forma.el_pastas.data, slaptazodis=koduotas_slaptazodis)
        db.session.add(vartotojas)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('registruotis.html', form=forma)


@app.route('/prisijungti', methods=['GET', 'POST'])
def prisijungti():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.PrisijungimoForma()
    if form.validate_on_submit():
        user = Vartotojas.query.filter_by(el_pastas=form.el_pastas.data).first()
        if user and bcrypt.check_password_hash(user.slaptazodis, form.slaptazodis.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('sekmingai prisijungete', 'info')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('ivalid username or password', 'danger')

    return render_template('prisijungti.html', form=form, title = 'Prisijungti')

@app.route("/atsijungti")
def atsijungti():
    logout_user()
    return redirect(url_for('index'))

@app.route('/naujas_irasas', methods=['GET', 'POST'])
def new_record():
    db.create_all()
    forma = forms.IrasasForm()
    if forma.validate_on_submit():
        naujas_irasas = Irasai(pajamos= forma.pajamos.data, suma=forma.kiekis.data, vartotojas_id=current_user.id)
        db.session.add(naujas_irasas)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('prideti_irasa.html', form=forma)

@app.route('/paskyra')
@login_required
def profile():
    return render_template('profile.html')



@app.route('/<slaptazodis>/api', methods=['GET'])
def api(slaptazodis):
    user = Vartotojas.query(slaptazodis)
    all_records = Irasai.query.filter_by(vartotojas_id = user.id).all()
    res = records_schema.dump(all_records)
    return jsonify(res)


@app.route('/user', methods=['GET'])
def api(slaptazodis):
    user = Vartotojas.query.all()
    #all_records = Irasai.query.filter_by(vartotojas_id = user.id).all()
    res = records_schema.dump(user)
    return jsonify(res)




@app.route('/irasai')
def records():
    db.create_all()
    try:
        visi_irasai= Irasai.query.filter_by(vartotojas_id = current_user.id).all()
    except:
        visi_irasai = []
        print(visi_irasai)
    return render_template('irasai.html', visi_irasai=visi_irasai, datetime=datetime)

@app.route('/balansas')
@login_required
def balansas():
    try:
        visi_irasai= Irasai.query.filter_by(vartotojas_id=current_user.id)
    except:
        visi_irasai = []
    balansas=0
    for irasas in visi_irasai:
        if irasas.pajamos:
            balansas += irasas.suma
        else:
            balansas -=irasas.suma
    date_string = "2012-12-12 10:10:10"
    time_past = datetime.fromisoformat(date_string) - datetime.now()
    return render_template('balansas.html', balansas=balansas, laikas = time_past, title = 'Balansas')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    irasas = Irasai.query.get(id)
    db.session.delete(irasas)
    db.session.commit()
    return redirect(url_for('records'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    forma = forms.IrasasForm()
    irasas = Irasai.query.get(id)
    if forma.validate_on_submit():
        irasas.pajamos = forma.pajamos.data
        irasas.suma = forma.kiekis.data
        db.session.commit()
        return redirect(url_for('records'))
    return render_template("update.html", form=forma, irasas=irasas)




if __name__== '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)
