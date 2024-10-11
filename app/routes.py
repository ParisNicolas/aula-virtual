from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, abort
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from functools import wraps
import os

from app import db
from app.models import Curso, Usuario, Contenido, asignaciones, Evaluacion
from app.forms import LoginForm, RegisterForm, ContentForm, CambiarProfesorForm, AgregarAlumnoForm, CursoForm


main = Blueprint('main', __name__, template_folder='templates')

#Uso: @role_required(['estudiante', 'instructor', 'admin'])
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated and current_user.rol in allowed_roles:
                return f(*args, **kwargs)
            else:
                abort(403)  # Prohibido: el usuario no tiene permiso
        return decorated_function
    return decorator

#Uso: @pertenece_al_curso --> En rutas con el parametro curso_id
def pertenece_al_curso(f):
    @wraps(f)
    def decorated_function(curso_id, *args, **kwargs):
        curso = Curso.query.get(curso_id)
        
        if curso is None:
            abort(404)  # Si el curso no existe, devuelve un error 404
        
        # Verificar si el usuario actual está en la lista de usuarios asignados al curso
        if current_user.rol != "admin" and current_user not in curso.usuarios:
            abort(403)  # Si no pertenece al curso, devuelve un error 403
        
        return f(curso_id, *args, **kwargs)
    
    return decorated_function



#------- HOME ---------
@main.route('/')
@login_required
def home():    
    if current_user.rol == "admin":
        cursos = Curso.query.all()
    else :
        cursos = current_user.cursos_asignados

    return render_template('home.html', cursos=cursos)


#------- CREAR CLASES ---------
# Crear una clase
@main.route('/crear_curso', methods=['GET', 'POST'])
@role_required(['admin'])
def crear_curso():
    form = CursoForm()

    # Filtrar usuarios según su rol
    estudiantes = Usuario.query.filter_by(rol='estudiante').all()
    instructores = Usuario.query.filter_by(rol='instructor').all()

    # Crear las opciones para el SelectMultipleField
    form.usuarios.choices = [(usuario.id, f"{usuario.nombre_usuario} (Estudiante)") for usuario in estudiantes] + \
                            [(usuario.id, f"{usuario.nombre_usuario} (Instructor)") for usuario in instructores]

    if form.validate_on_submit():
        # Crear el nuevo curso con los datos del formulario
        nuevo_curso = Curso(nombre=form.nombre.data, descripcion=form.descripcion.data)

        # Asignar los usuarios seleccionados al curso
        usuarios_seleccionados = Usuario.query.filter(Usuario.id.in_(form.usuarios.data)).all()
        nuevo_curso.usuarios.extend(usuarios_seleccionados)

        db.session.add(nuevo_curso)
        db.session.commit()
        flash('Curso creado con éxito', 'success')
        return redirect(url_for('main.home'))

    return render_template('admin/crear_curso.html', form=form)

@main.route('/curso/eliminar/<int:curso_id>', methods=['GET'])
@role_required(['admin'])
def eliminar_curso(curso_id):
    # Buscar el curso por su ID
    curso = Curso.query.get(curso_id)

    if not curso:
        flash('Curso no encontrado', 'error')
        return redirect(url_for('main.home'))

    # Eliminar el curso de la base de datos
    db.session.delete(curso)
    db.session.commit()

    flash('Curso eliminado con éxito', 'success')
    return redirect(url_for('main.home'))


#------- LOGIN ---------
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


#------- TABLON DE ESTUDIANTES ---------

@main.route('/tablon/<int:curso_id>')
@login_required
@pertenece_al_curso
def tablon(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    contenidos = Contenido.query.filter_by(curso_id=curso_id).all()
    evaluaciones = Evaluacion.query.filter_by(curso_id=curso_id).all()
    return render_template('tablon.html',curso=curso , contenidos=contenidos, evaluaciones=evaluaciones)


#------- TABLON DE INSTRUCTORES ---------

@main.route('/curso/<curso_id>/crear_contenido', methods=['GET', 'POST'])
@role_required(['instructor', 'admin'])
@pertenece_al_curso
def crear_contenido(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    form = ContentForm()
    if form.validate_on_submit():
        archivo = form.archivo.data
        filename = secure_filename(archivo.filename)
        
        # Ruta absoluta para la carpeta 'static/uploads/'
        upload_folder = os.path.join(current_app.root_path, 'static/uploads/')
        
        # Guarda el archivo usando la ruta absoluta
        archivo.save(os.path.join(upload_folder, filename))

        # Crea un nuevo contenido en la base de datos
        nuevo_contenido = Contenido(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            tipo='archivo',
            archivo=filename,
            enlace_externo=form.enlace_externo.data or None,
            curso_id=curso.id
        )
        db.session.add(nuevo_contenido)
        db.session.commit()

        flash('Contenido subido exitosamente', 'success')
        return redirect(url_for('main.tablon', curso_id=curso.id))

    return render_template('teacher/contentForm.html', form=form, curso=curso)


#------- TABLON DE ADMIN ---------

# Contenido de un curso (incluye profesor y alumnos)
@main.route('/curso/<int:curso_id>', methods=['GET', 'POST'])
@role_required(['admin'])
def curso_detalle(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    # Obtener los usuarios asignados y no asignados
    profesores_asignados = Usuario.query.filter(Usuario.cursos_asignados.any(id=curso_id), Usuario.rol == 'instructor').all()
    estudiantes_asignados = Usuario.query.filter(Usuario.cursos_asignados.any(id=curso_id), Usuario.rol == 'estudiante').all()
    
    profesores_no_asignados = Usuario.query.filter(~Usuario.cursos_asignados.any(id=curso_id), Usuario.rol == 'instructor').all()
    estudiantes_no_asignados = Usuario.query.filter(~Usuario.cursos_asignados.any(id=curso_id), Usuario.rol == 'estudiante').all()

    formProfe = CambiarProfesorForm()
    formProfe.profesor.choices = [(profesor.id, profesor.nombre_usuario) for profesor in profesores_no_asignados]
    
    # Crear una instancia del formulario para agregar alumnos
    formAlumn = AgregarAlumnoForm()
    formAlumn.alumno_id.choices = [(alumno.id, alumno.nombre_usuario) for alumno in estudiantes_no_asignados]

    if formAlumn.validate_on_submit():
        alumno_id = formAlumn.alumno_id.data
        curso.usuarios.append(Usuario.query.get(alumno_id))
        db.session.commit()
        flash('Alumno agregado exitosamente', 'success')
        return redirect(url_for('main.curso_detalle', curso_id=curso.id))
    
    if formProfe.validate_on_submit():
        profe_id = formProfe.profesor.data

        curso.usuarios.append(Usuario.query.get(profe_id))
        db.session.commit()
        flash('Profesor agregado exitosamente', 'success')
        return redirect(url_for('main.curso_detalle', curso_id=curso.id))

    return render_template('admin/class_admin.html', 
                           curso=curso, 
                           profesores=profesores_asignados,
                           estudiantes=estudiantes_asignados, 
                           formAlumn=formAlumn,
                           formProfe=formProfe,
                           )

@main.route('/curso/<int:curso_id>/cambiar_profesor', methods=['GET', 'POST'])
@role_required(['admin'])
def cambiar_profesor(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    form = CambiarProfesorForm()

    # Obtener la lista de usuarios que son profesores
    profesores = Usuario.query.filter_by(rol='instructor').all()
    form.profesor.choices = [(profesor.id, profesor.nombre_usuario) for profesor in profesores]

    if form.validate_on_submit():
        usuario_id = form.profesor.data  # Obtener el ID del profesor seleccionado
        asignacion = db.session.query(asignaciones).filter_by(curso_id=curso.id, usuario_id=usuario_id).first()

        if asignacion:
            asignacion.rol_asignado = 'instructor'  # Cambiar el rol a instructor
        else:
            nueva_asignacion = asignaciones.insert().values(usuario_id=usuario_id, curso_id=curso.id, rol_asignado='instructor')
            db.session.execute(nueva_asignacion)

        db.session.commit()
        flash('Profesor asignado exitosamente', 'success')
        return redirect(url_for('main.curso_detalle', curso_id=curso.id))

    return render_template('admin/profForm.html', form=form, curso=curso)


# Eliminar un profesor de un curso
@main.route('/curso/<int:curso_id>/eliminar_profesor/<int:profe_id>', methods=['POST'])
@role_required(['admin'])
def eliminar_profesor(curso_id, profe_id):
    curso = Curso.query.get_or_404(curso_id)
    instructor = Usuario.query.filter_by(id=profe_id, rol='instructor').first()

    if not instructor:
        flash('Instructor no encontrado', 'error')
        return redirect(url_for('main.curso_detalle', curso_id=curso_id))
    
    if instructor in curso.usuarios:
        curso.usuarios.remove(instructor)
        db.session.commit()
        flash('Instructor eliminado del curso con éxito', 'success')
    else:
        flash('El instructor no está asignado a este curso', 'error')

    return redirect(url_for('main.curso_detalle', curso_id=curso.id))


@main.route('/curso/<int:curso_id>/agregar_alumno', methods=['GET', 'POST'])
@role_required(['admin'])
def agregar_alumno_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    form = AgregarAlumnoForm()

    # Obtener la lista de estudiantes disponibles
    estudiantes = Usuario.query.filter_by(rol='estudiante').all()
    form.alumno_id.choices = [(estudiante.id, estudiante.nombre_usuario) for estudiante in estudiantes]

    if form.validate_on_submit():
        alumno_id = form.alumno_id.data
        # Lógica para agregar al alumno al curso
        curso.usuarios.append(Usuario.query.get(alumno_id))
        db.session.commit()
        flash('Alumno agregado exitosamente', 'success')
        return redirect(url_for('main.curso_detalle', curso_id=curso.id))

    return render_template('admin/studForm.html', curso=curso, form=form)


# Ruta para eliminar un alumno
@main.route('/curso/<int:curso_id>/eliminar_alumno/<int:alumno_id>', methods=['POST'])
@role_required(['admin'])
def eliminar_alumno(curso_id, alumno_id):
    # Elimina el registro de la tabla intermedia
    db.session.execute(asignaciones.delete().where(
        asignaciones.c.curso_id == curso_id,
        asignaciones.c.usuario_id == alumno_id
    ))
    db.session.commit()
    flash('Alumno eliminado exitosamente', 'success')
    return redirect(url_for('main.curso_detalle', curso_id=curso_id))



#-----------SECCION 2---------

#Subir una respuesta a una evaluacion
@main.route('/evaluacion/<evaluacion_id>', methods=['POST'])
def subir_respuesta(evaluacion_id):
    return render_template('algo.html')