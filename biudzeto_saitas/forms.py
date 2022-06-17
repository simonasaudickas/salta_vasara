from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo
import app

class RegistracijosForma(FlaskForm):
    user_name = StringField('nickas', [DataRequired()])
    vardas = StringField('vardas', [DataRequired()])
    pavarde = StringField('pavarde', [DataRequired()])
    el_pastas = StringField('el.pastas', [DataRequired()])
    slaptazodis = PasswordField ('slaptazodis', [DataRequired()])
    patvirtintas_slaptazodis = PasswordField ('pakartokite slaptazodi',[EqualTo('slaptazodis', "Slaptazodis turi sutapti.")] )
    submit = SubmitField('Registruotis')

    def tikrinti_varda(self, user_name):
        vartotojas = app.Vartotojas.query.filter_by(user_name = user_name.data).first()
        if vartotojas:
            raise ValidationError ('Sis nickas panaudotas. Pasirinkite kita')

    def tikrinti_emaila(self,el_pastas):
        vartotojas = app.Vartotojas.query.filter_by(el_pastas = el_pastas.data).first()
        if vartotojas:
            raise ValidationError('Sis el.pastas uzimtas. Pasirinkite kita')


class PrisijungimoForma(FlaskForm):
    el_pastas = StringField('Jusu el.pastas', [DataRequired()])
    slaptazodis = PasswordField('Jusu slaptazodis', [DataRequired()])
    submit = SubmitField('Prisijungit')






class IrasasForm(FlaskForm):
    pajamos = BooleanField('Pajamos')
    kiekis = FloatField('kiekis', [DataRequired()])
    submit = SubmitField('Įvesti')