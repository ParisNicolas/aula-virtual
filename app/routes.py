from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.utils import secure_filename
import os

from app import db
from app.models import Curso, Usuario
from app.forms import LoginForm, RegisterForm, ContentForm

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def home():
    cursos = Curso.query.all()  # Asumiendo que tienes una clase llamada Curso
    return render_template('home.html', cursos=cursos)


#Logeo
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(nombre_usuario=form.name.data).first()
        if usuario and usuario.check_password(form.password.data):  # Comprueba la contraseña
            login_user(usuario)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('main.home'))  # Redirige a la página de inicio o dashboard
        else:
            flash('Inicio de sesión fallido. Verifica tu nombre de usuario y contraseña.', 'danger')
    return render_template('login.html', form=form)

#Registro
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            nombre_usuario=form.name.data,  # Cambiar aquí a 'name'
            rol=form.rol.data
        )
        nuevo_usuario.set_password(form.password.data)  # Cambiar aquí a 'password'
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Tu cuenta ha sido creada con éxito. ¡Ahora puedes iniciar sesión!', 'success')
        return redirect(url_for('main.login'))  # Redirige al login después del registro
    return render_template('register.html', form=form)

#Registro
@main.route('/logout')
def logout():
    logout_user()
    flash("Has cerrado session.", "success")
    return redirect(url_for("main.home"))

#Crear un contenido nuevo (solo profesores)
@main.route('/curso/<curso_id>/crear', methods=['GET','POST'])
def crear_contenido(curso_id):
    form = ContentForm()
    if form.validate_on_submit():
        archivo = form.archivo.data
        filename = secure_filename(archivo.filename)  # Asegura que el nombre del archivo sea seguro
        archivo.save(os.path.join('static/uploads/', filename))  # Guarda el archivo
        flash('Contenido subido exitosamente', 'success')
        return redirect(url_for('ver_curso'))  # Redirigir a una página relevante
    return render_template('teacher/contentForm.html', form=form)



# Ruta para ver el detalle de un curso (incluye profesor y alumnos)
@main.route('/curso/<int:curso_id>')
def curso_detalle(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    profesor = Usuario.query.filter(Usuario.cursos_asignados.any(id=curso_id), Usuario.rol == 'instructor').all()
    estudiantes = Usuario.query.filter(Usuario.cursos_asignados.any(id=curso_id), Usuario.rol == 'estudiante').all()
    return render_template('admin/class_admin.html',curso=curso, profesor=profesor, estudiantes=estudiantes)

# Ruta para eliminar un profesor
@main.route('/curso/<int:curso_id>/eliminar_profesor', methods=['POST'])
def eliminar_profesor(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    asignacion = db.session.query(Curso).filter_by(curso_id=curso.id, rol_asignado='instructor').first()
    if asignacion:
        db.session.delete(asignacion)
        db.session.commit()
    return redirect(url_for('class_admin', curso_id=curso.id))

# Ruta para cambiar un profesor
@main.route('/curso/<int:curso_id>/cambiar_profesor', methods=['POST'])
def cambiar_profesor(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    # Lógica para cambiar al profesor, podría ser con un select similar a los alumnos
    return redirect(url_for('main.curso_detalle', curso_id=curso.id))

# Ruta para eliminar un alumno
@main.route('/curso/<int:curso_id>/eliminar_alumno/<int:alumno_id>', methods=['POST'])
def eliminar_alumno(curso_id, alumno_id):
    asignacion = db.session.query(Curso).filter_by(curso_id=curso_id, usuario_id=alumno_id, rol_asignado='estudiante').first()
    if asignacion:
        db.session.delete(asignacion)
        db.session.commit()
    return redirect(url_for('main.curso_detalle', curso_id=curso_id))

# Ruta para agregar un alumno
@main.route('/curso/<int:curso_id>/agregar_alumno', methods=['POST'])
def agregar_alumno(curso_id):
    alumno_id = request.form.get('alumno_id')
    asignacion = Curso.insert().values(usuario_id=alumno_id, curso_id=curso_id, rol_asignado='estudiante')
    db.session.execute(asignacion)
    db.session.commit()
    return redirect(url_for('main.curso_detalle', curso_id=curso_id))



#-----------SECCION 2---------

#Mostrar el contenido de un curso
@main.route('/curso/<curso_id>')
def ver_curso(curso_id):
    return render_template('algo.html')


#Eliminar un contenido (solo profesores)
@main.route('/curso/<curso_id>/eliminar', methods=['POST'])
def eliminar_contenido(curso_id):
    return render_template('algo.html')

#Subir una respuesta a una evaluacion
@main.route('/evaluacion/<evaluacion_id>', methods=['POST'])
def subir_respuesta(evaluacion_id):
    return render_template('algo.html')