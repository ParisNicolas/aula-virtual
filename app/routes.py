from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from app import db

#from app.models import Carrito, Producto, CarritoProducto, Transaccion
#from app.forms import TarjetaForm

main = Blueprint('main', __name__, template_folder='templates')


#Home para mostrar los cursos a los que tienes acceso
@main.route('/')
def home():
    return render_template('home.html')

#Ruta para crear, editar, eliminar y asignar cursos
@main.route('/gestion_cursos')
def gestion_cursos():
    return render_template('algo.html')

#Crear curso para un determinado profesor (usuario con rol profesor)
@main.route('/gestion_cursos/crear', methods=['POST'])
def crear_curso():
    return render_template('algo.html')

#Editar curso
@main.route('/gestion_cursos/editar/<curso_id>', methods=['POST'])
def editar_curso(curso_id):
    return render_template('algo.html')

#Eliminar curso
@main.route('/gestion_cursos/eliminar/<curso_id>', methods=['DELETE'])
def eliminar_curso(curso_id):
    return render_template('algo.html')

#Asignar curso a un estudiante
@main.route('/gestion_cursos/asignar/<curso_id>/<estudiante_id>', methods=['POST'])
def asignar_curso(curso_id, estudiante_id):
    return render_template('algo.html')



#-----------SECCION 2---------

#Mostrar el contenido de un curso
@main.route('/curso/<curso_id>')
def ver_curso(curso_id):
    return render_template('algo.html')

#Crear un contenido nuevo (solo profesores)
@main.route('/curso/<curso_id>/crear', methods=['POST'])
def crear_contenido(curso_id):
    return render_template('algo.html')

#Eliminar un contenido (solo profesores)
@main.route('/curso/<curso_id>/eliminar', methods=['POST'])
def eliminar_contenido(curso_id):
    return render_template('algo.html')

#Subir una respuesta a una evaluacion
@main.route('/evaluacion/<evaluacion_id>', methods=['POST'])
def subir_respuesta(evaluacion_id):
    return render_template('algo.html')