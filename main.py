import mysql.connector
from flask import jsonify, make_response, Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import database as db  # suponiendo que aquí tienes la conexión db.database

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # página a redirigir si no está autenticado

class User(UserMixin):
    def __init__(self, id, username, password, rol, nombre):
        self.id = id
        self.username = username
        self.password = password
        self.rol = rol
        self.nombre = nombre


@login_manager.user_loader
def load_user(user_id):
    cursor = db.database.cursor()
    cursor.execute("SELECT id, username, password, rol, nombre FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user[0], username=user[1], password=user[2], rol=user[3], nombre=user[4])
    return None



@app.context_processor
def inject_user():
    return dict(current_user=current_user)  # usar current_user de flask_login

@app.route('/', methods=['GET'])
def index_publico():
    return render_template('index_publico.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['contraseña']
        cursor = db.database.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and password == user[3]:  # user[3] es password
            user_obj = user_obj = User(id=user[0], username=user[1], password=user[2], nombre=user[3], rol=user[4])

            login_user(user_obj)  # <-- Esto inicia la sesión en Flask-Login
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('index_admin'))
        else:
            flash("Credenciales incorrectas. Intenta de nuevo.", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "success")
    return redirect(url_for('login'))

@app.route('/index_admin')
@login_required
def index_admin():
    return render_template('index.html', usuario=current_user.username, rol=current_user.rol)




@app.route('/residentes',methods=['GET'])
@login_required
def index_residentes():
    try:
        cursor = db.database.cursor()
        cursor.execute("""
            SELECT id, cedula, nombre, apellido1, apellido2, nacionalidad, telefono_contacto, direccion 
            FROM residentes 
            ORDER BY id DESC LIMIT 20 OFFSET 0
        """)
        datos = cursor.fetchall()
        columnames = [col[0] for col in cursor.description]
        arreglo = [dict(zip(columnames, record)) for record in datos]
    except Exception as e:
        print("ERROR EN RESIDENTES:", e)
        arreglo = []
    finally:
        cursor.close()

    response = make_response(render_template('modulos/clientes/residentes.html', residentes=arreglo))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Ruta para crear un nuevo cliente
@app.route('/create')
@login_required
def index_create():
    return render_template('modulos/clientes/create.html')




@app.route('/edit/<string:id>', methods=['GET'])
@login_required
def index_editar(id):  # Asegúrate de que se reciba `id`
    cursor = db.database.cursor()  # Establecer conexión
    cursor.execute("SELECT * FROM residentes WHERE id = %s", (id,))
    datos = cursor.fetchall() 
    arreglo = []
    columnames = [col[0] for col in cursor.description]
    for record in datos:
         arreglo.append(dict(zip(columnames, record)))
    
    cursor.close()  # Cerrar el cursor
    return render_template('modulos/clientes/edit.html', arreglo=arreglo)


@app.route('/eliminar/<string:id>',methods=['GET', 'POST'])
@login_required
def eliminar_residente(id):
    cursor = db.database.cursor() # Establecer conexión
    cursor.execute("DELETE from RESIDENTES where id= %s", (id,))
    db.database.commit()   
    cursor.close()  # Cerrar el cursor  
    
  
    return redirect(url_for('index_residentes'))




# Ruta para guardar un nuevo cliente
@app.route('/modulos/clientes/create/guardar', methods=['POST'])
@login_required
def btn_cliente_guardar():
   
        nombre = request.form.get('nombre', '').strip().upper()
        apellido1 = request.form.get('apellido1', '').strip().upper()
        apellido2 = request.form.get('apellido2', '').strip().upper()
        cedula = request.form.get('cedula', '').strip()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
        genero = request.form.get('genero', '').strip().upper()
        estado_civil = request.form.get('estado_civil', '').strip().upper()
        nacionalidad = request.form.get('pais_nacimiento', '').strip().upper()
        direccion = request.form.get('direccion', '').strip().upper()
        telefono_contacto = request.form.get('telefono', '').strip()
        contacto_emergencia_nombre = request.form.get('nombre_contacto_emergencia', '').strip().upper()
        contacto_emergencia_parentesco = request.form.get('contacto_emergencia_parentesco', '').strip().upper()
        contacto_emergencia_telefono = request.form.get('telefono_emergencia', '').strip()
        condiciones_medicas = request.form.get('condiciones_medicas', '').strip().upper()
        medicamentos_actuales = request.form.get('medicamentos', '').strip().upper()
        movilidad = request.form.get('movilidad', '').strip().upper()
        estado_mental = request.form.get('estado_mental', '').strip().upper()
        
        # SQL para insertar un nuevo cliente
        sql = """
        INSERT INTO residentes(nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero,
        estado_civil, nacionalidad, direccion, telefono_contacto,
        contacto_emergencia_nombre, contacto_emergencia_parentesco, contacto_emergencia_telefono,
        condiciones_medicas, medicamentos_actuales, movilidad, estado_mental)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero, estado_civil,
            nacionalidad, direccion, telefono_contacto, contacto_emergencia_nombre,contacto_emergencia_parentesco,
            contacto_emergencia_telefono, condiciones_medicas, medicamentos_actuales,
            movilidad, estado_mental  # Estado activo por defecto
        )
        cursor = db.database.cursor()  # Establecer conexión
        
        
        # Verificar si la cédula ya existe
        cursor.execute("SELECT cedula FROM residentes WHERE cedula = %s", (cedula,))
        existente = cursor.fetchone()
        
        if existente:
            mensaje = 'existe'
            return render_template('modulos/clientes/create.html',mensaje=mensaje, cedula=cedula)
        
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()  # Cerrar el cursor  
        
       
        
        mensaje = 'insertado'
        return render_template('modulos/clientes/create.html',mensaje=mensaje, cedula=cedula)



@app.route('/modulos/clientes/create/edit/<string:id>', methods=['POST'])
@login_required
def btn_cliente_editar_guardar(id):
    # Obtener datos del formulario
    nombre = request.form.get('nombre', '').strip().upper()
    apellido1 = request.form.get('apellido1', '').strip().upper()
    apellido2 = request.form.get('apellido2', '').strip().upper()
    cedula = request.form.get('cedula', '').strip()
    fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
    genero = request.form.get('genero', '').strip().upper()
    estado_civil = request.form.get('estado_civil', '').strip().upper()
    nacionalidad = request.form.get('pais_nacimiento', '').strip().upper()
    direccion = request.form.get('direccion', '').strip().upper()
    telefono_contacto = request.form.get('telefono', '').strip()
    contacto_emergencia_nombre = request.form.get('nombre_contacto_emergencia', '').strip().upper()
    contacto_emergencia_parentesco = request.form.get('contacto_emergencia_parentesco', '').strip().upper()
    contacto_emergencia_telefono = request.form.get('telefono_emergencia', '').strip()
    condiciones_medicas = request.form.get('condiciones_medicas', '').strip().upper()
    medicamentos_actuales = request.form.get('medicamentos', '').strip().upper()
    movilidad = request.form.get('movilidad', '').strip().upper()
    estado_mental = request.form.get('estado_mental', '').strip().upper()

    data = (
        nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero, estado_civil, nacionalidad,
        direccion, telefono_contacto, contacto_emergencia_nombre, contacto_emergencia_parentesco,
        contacto_emergencia_telefono, condiciones_medicas, medicamentos_actuales, movilidad,
        estado_mental, id
    )

    cursor = db.database.cursor()

    # ✅ Validar cédula duplicada (excluyendo el mismo registro)
    cursor.execute("SELECT id FROM residentes WHERE cedula = %s AND id != %s", (cedula, id))
    existente = cursor.fetchone()
        
    if existente:
        mensaje = 'existe'
        return render_template('modulos/clientes/create.html',mensaje=mensaje, cedula=cedula)
    # ✅ Intentar guardar cambios
    
    sql = """
            UPDATE residentes
            SET nombre = %s,
                apellido1 = %s,
                apellido2 = %s,
                cedula = %s,
                fecha_nacimiento = %s,
                genero = %s,
                estado_civil = %s,
                nacionalidad = %s,
                direccion = %s,
                telefono_contacto = %s,
                contacto_emergencia_nombre = %s,
                contacto_emergencia_parentesco = %s,
                contacto_emergencia_telefono = %s,
                condiciones_medicas = %s,
                medicamentos_actuales = %s,
                movilidad = %s,
                estado_mental = %s,
                activo = 1
            WHERE id = %s
        """
    cursor.execute(sql, data)
    db.database.commit()    
    cursor.close()
    mensaje = 'no_existe'
    return render_template('modulos/clientes/create.html',mensaje=mensaje, cedula=cedula)



##busqueda por dato ingresado

@app.route('/buscar')
@login_required
def buscar():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    query = query.lower()
    like_query = f"%{query}%"
    sql = """
        SELECT id, cedula, nombre, apellido1, apellido2, nacionalidad, telefono_contacto, direccion
        FROM residentes
        WHERE 
            LOWER(nombre) LIKE %s OR
            LOWER(apellido1) LIKE %s OR
            LOWER(apellido2) LIKE %s OR
            LOWER(nacionalidad) LIKE %s OR
            LOWER(telefono_contacto) LIKE %s OR
            cedula LIKE %s
        LIMIT 20
    """
    cursor = db.database.cursor()
    try:
        cursor.execute(sql, (like_query,) * 6)
        datos = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]
        arreglo = [dict(zip(columnas, registro)) for registro in datos]
    finally:
        cursor.close()

    return jsonify(arreglo)






@app.route('/ver_info/<string:id>', methods=['GET'])
@login_required
def index_ver_info(id):
    cursor = db.database.cursor()  # Establecer conexión
    cursor.execute("SELECT * FROM residentes WHERE id = %s", (id,))
    datos = cursor.fetchall() 
    arreglo = []
    columnames = [col[0] for col in cursor.description]
    for record in datos:
         arreglo.append(dict(zip(columnames, record)))
    
    cursor.close()  # Cerrar el cursor
    return render_template('/modulos/clientes/ver_info.html', arreglo=arreglo)




# MODULO HISTORIAL MEDICO



# Mostrar historial médico
@app.route('/historial_medico/<int:id>')
@login_required
def historial_medico(id):
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM historial_medico WHERE residente_id = %s", (id,))
    historial = cursor.fetchall()
    cursor.execute("SELECT * FROM  medicacion WHERE residente_id = %s", (id,))
    medicacion = cursor.fetchall()
    cursor.close()
    return render_template('/modulos/clientes/historial_medico.html', historial=historial, medicacion=medicacion ,residente_id=id)




# Ruta para actualizar el historial médico
@app.route('/historial_medico/<int:id>/actualizar', methods=['POST'])
@login_required
def actualizar_historial_medico(id):
    # Recibimos los datos del formulario
    fecha = request.form.get('fecha')
    diagnostico = request.form.get('diagnostico', '').strip().upper()
    medico = request.form.get('medico', '').strip().upper()
    notas = request.form.get('notas', '').strip().upper()

    # Usamos la conexión importada
    cursor = database.cursor()

    try:
        # Actualizamos el historial médico en la base de datos
        cursor.execute("""
            UPDATE historial_medico
            SET fecha = %s, diagnostico = %s, medico = %s, notas = %s
            WHERE id = %s
        """, (fecha, diagnostico, medico, notas, id))

        # Hacemos commit para guardar los cambios
        database.commit()
    except Exception as e:
        # Si ocurre algún error, hacemos rollback
        database.rollback()
        print(f"Error: {e}")
        return "Hubo un error al actualizar el registro."

    return redirect(url_for('historial_medico'))  # Redirigir a la lista de historial



@app.route('/historial_medico/<int:residente_id>/nuevo', methods=['POST'])
@login_required
def agregar_historial_medico(residente_id):
    fecha = request.form.get('fecha')
    diagnostico = request.form.get('diagnostico', '').strip()
    observaciones = request.form.get('observaciones', '').strip()

    if not fecha or not diagnostico:
        # Para AJAX devuelve JSON con error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Fecha y diagnóstico son obligatorios'}), 400
        flash('Fecha y diagnóstico son obligatorios', 'danger')
        return redirect(url_for('historial_medico', id=residente_id))

    cursor = db.database.cursor()
    try:
        cursor.execute("""
            INSERT INTO historial_medico (residente_id, fecha, diagnostico, observaciones)
            VALUES (%s, %s, %s, %s)
        """, (residente_id, fecha, diagnostico.upper(), observaciones.upper()))
        db.database.commit()
        nuevo_id = cursor.lastrowid
    except Exception as e:
        db.database.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Error al guardar registro'}), 500
        flash('Error al guardar registro: ' + str(e), 'danger')
        return redirect(url_for('historial_medico', id=residente_id))
    finally:
        cursor.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Devolver datos para actualizar tabla en frontend
        return jsonify({
            'success': True,
            'id': nuevo_id,
            'fecha': fecha,
            'diagnostico': diagnostico.upper(),
            'observaciones': observaciones.upper()
        })

    flash('Registro médico agregado exitosamente', 'success')
    return redirect(url_for('historial_medico', id=residente_id))






@app.route('/historial_medico/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_historial(id):
    cursor = db.database.cursor()
    try:
        cursor.execute("DELETE FROM historial_medico WHERE id = %s", (id,))
        db.database.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.database.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()





if __name__ == '__main__':
    app.run(port=5000, debug=True)


