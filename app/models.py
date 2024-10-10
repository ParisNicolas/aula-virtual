from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

from app import db

class Usuario(UserMixin,db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(80), unique=True, nullable=False)
    contraseña_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='estudiante')  # 'admin', 'instructor', 'estudiante'
    cursos_asignados = db.relationship('Curso', secondary='asignaciones', back_populates='usuarios')

    def set_password(self, contraseña):
        self.contraseña_hash = generate_password_hash(contraseña)

    def check_password(self, contraseña):
        return check_password_hash(self.contraseña_hash, contraseña)

    # Método para asignar un curso a un instructor
    def asignar_como_instructor(self, curso):
        asignacion = db.session.query(asignaciones).filter_by(usuario_id=self.id, curso_id=curso.id).first()
        if asignacion:
            asignacion.rol_asignado = 'instructor'
        else:
            asignacion = asignaciones.insert().values(usuario_id=self.id, curso_id=curso.id, rol_asignado='instructor')
            db.session.execute(asignacion)
        db.session.commit()

    # Método para asignar un curso a un estudiante
    def asignar_como_estudiante(self, curso):
        asignacion = db.session.query(asignaciones).filter_by(usuario_id=self.id, curso_id=curso.id).first()
        if asignacion:
            asignacion.rol_asignado = 'estudiante'
        else:
            asignacion = asignaciones.insert().values(usuario_id=self.id, curso_id=curso.id, rol_asignado='estudiante')
            db.session.execute(asignacion)
        db.session.commit()

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario} ({self.rol})>'


# Modelo para Cursos (Creado y gestionado por Admin, accesible según rol)
class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuarios = db.relationship('Usuario', secondary='asignaciones', back_populates='cursos_asignados', cascade="all, delete")
    contenidos = db.relationship('Contenido', backref='curso', lazy=True, cascade='all, delete-orphan')
    evaluaciones = db.relationship('Evaluacion', backref='curso', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Curso {self.nombre}>'

# Tabla intermedia para la relación muchos a muchos entre Usuarios y Cursos (Asignaciones)
asignaciones = db.Table('asignaciones',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('curso_id', db.Integer, db.ForeignKey('cursos.id'), primary_key=True),
    db.Column('rol_asignado', db.String(20), nullable=False)  # 'instructor', 'estudiante', 'admin'
)

# Modelo para Contenidos
class Contenido(db.Model):
    __tablename__ = 'contenidos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    tipo = db.Column(db.String(50), nullable=False)  # 'pdf', 'video', 'enlace'
    archivo = db.Column(db.String(200), nullable=True)  # Ruta al archivo si es un PDF o video
    enlace_externo = db.Column(db.String(200), nullable=True)  # Enlace si es material 'externo'
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contenido {self.titulo}>'

# Modelo para Evaluaciones
class Evaluacion(db.Model):
    __tablename__ = 'evaluaciones'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    intentos = db.relationship('Entrega', backref='evaluacion', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Evaluacion {self.titulo}>'

# Modelo para Intentos de Evaluaciones (Respuestas de estudiantes)
class Entrega(db.Model):
    __tablename__ = 'Entregas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones.id'), nullable=False)
    respuestas = db.Column(db.Text, nullable=False)  # Respuestas de los estudiantes
    calificacion = db.Column(db.Float, nullable=True)  # Calificación de la evaluación (automática o manual)
    fecha_intento = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Entrega Usuario: {self.usuario_id}, Evaluacion: {self.evaluacion_id}>'
