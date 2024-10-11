from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, FileField, SelectField, TextAreaField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from flask_wtf.file import FileAllowed, FileRequired
from app.models import Usuario

class LoginForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class RegisterForm(FlaskForm):
    name = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirmar_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    rol = SelectField('Rol', choices=[('estudiante', 'Estudiante'), ('instructor', 'Instructor'), ('admin', 'Admin')], validators=[DataRequired()])  # Elige el rol: estudiante o instructor
    submit = SubmitField('Registrarse')

    # Validación personalizada para asegurar que el nombre de usuario es único
    def validate_name(self, name):
        usuario = Usuario.query.filter_by(nombre_usuario=name.data).first()
        if usuario:
            raise ValidationError('Ese nombre de usuario ya existe. Por favor, elige otro.')


class CursoForm(FlaskForm):
    nombre = StringField('Nombre del Curso', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    usuarios = SelectMultipleField('Asignar Usuarios', coerce=int)  # Para asignar usuarios (estudiantes/instructores)
    submit = SubmitField('Guardar')

class ContentForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    archivo = FileField('Archivo', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'mp4', 'mov', 'avi', 'jpg', 'png', 'mp3'], 'Solo se permiten archivos PDF, videos o imágenes.')
    ])
    enlace_externo = StringField('Enlace', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Subir contenido')


class EVAForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    fecha_entrega = DateField('Fecha de Entrega', format='%Y-%m-%d')
    submit = SubmitField('Subir evaluacion')

class CambiarProfesorForm(FlaskForm):
    profesor = SelectField('Profesor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Asignar Profesor')

class AgregarAlumnoForm(FlaskForm):
    alumno_id = SelectField('Seleccionar Alumno', validators=[DataRequired()])
    submit = SubmitField('Agregar Alumno')