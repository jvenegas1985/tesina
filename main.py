import mysql.connector
from flask import jsonify, make_response, Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import database as db  # suponiendo que aquí tienes la conexión db.database
from datetime import datetime


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

from flask import session

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']       
        password = request.form['contraseña']    
        
        cursor = db.database.cursor()
        cursor.execute("SELECT id, username, password, rol, nombre FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and password == user[2]:
            user_obj = User(
                id=user[0],
                username=user[1],
                password=user[2],
                rol=user[3],
                nombre=user[4]
            )
            login_user(user_obj)

            # Guardamos el rol en session para que esté disponible en las plantillas
            session['rol'] = user_obj.rol  
            session['nombre'] = user_obj.nombre  # si quieres también el nombre

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
            SELECT id, cedula, nombre, apellido1, apellido2, nacionalidad, telefono_contacto, direccion, activo 
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
    # ———————— Datos obligatorios del formulario ————————
    nombre = request.form.get('nombre', '').strip().upper()
    apellido1 = request.form.get('apellido1', '').strip().upper()
    apellido2 = request.form.get('apellido2', '').strip().upper()
    cedula = request.form.get('cedula', '').strip()
    fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()

    # Estos cuatro campos son ENUM en la BD: no usar .upper(), deben coincidir exactamente
    #   genero  ENUM('Masculino','Femenino','Otro')
    #   estado_civil ENUM('Soltero','Casado','Viudo','Divorciado')
    #   movilidad ENUM('Independiente','Con ayuda','Dependiente')
    #   estado_mental ENUM('Lúcido','Desorientado','Demencia')
    genero = request.form.get('genero', '').strip()
    estado_civil = request.form.get('estado_civil', '').strip()
    movilidad = request.form.get('movilidad', '').strip()
    estado_mental = request.form.get('estado_mental', '').strip()

    # Resto de campos
    nacionalidad = request.form.get('pais_nacimiento', '').strip().upper()
    direccion = request.form.get('direccion', '').strip().upper()
    telefono_contacto = request.form.get('telefono', '').strip()
    contacto_emergencia_nombre = request.form.get('nombre_contacto_emergencia', '').strip().upper()
    contacto_emergencia_parentesco = request.form.get('contacto_emergencia_parentesco', '').strip().upper()
    contacto_emergencia_telefono = request.form.get('telefono_emergencia', '').strip()

    # ———————— Validación: todos los ENUM deben tener valor ————————
    if not genero or not estado_civil or not movilidad or not estado_mental:
        mensaje = 'faltan_campos'
        # Puedes enviar de vuelta los datos que sí se completaron para no obligar a reingresarlos:
        return render_template(
            'modulos/clientes/create.html',
            mensaje=mensaje,
            # Aquí paso los valores recibidos para que el formulario se repueble:
            nombre=nombre,
            apellido1=apellido1,
            apellido2=apellido2,
            cedula=cedula,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            estado_civil=estado_civil,
            pais_nacimiento=nacionalidad,
            direccion=direccion,
            telefono=telefono_contacto,
            nombre_contacto_emergencia=contacto_emergencia_nombre,
            contacto_emergencia_parentesco=contacto_emergencia_parentesco,
            telefono_emergencia=contacto_emergencia_telefono,
            movilidad=movilidad,
            estado_mental=estado_mental
        )

    # ———————— Preparar INSERT ————————
    sql = """
    INSERT INTO residentes(
      nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero,
      estado_civil, nacionalidad, direccion, telefono_contacto,
      contacto_emergencia_nombre, contacto_emergencia_parentesco, contacto_emergencia_telefono,
      movilidad, estado_mental
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero, estado_civil,
        nacionalidad, direccion, telefono_contacto,
        contacto_emergencia_nombre, contacto_emergencia_parentesco, contacto_emergencia_telefono,
        movilidad, estado_mental
    )

    cursor = db.database.cursor()

    # ———————— Verificar si la cédula ya existe ————————
    cursor.execute("SELECT cedula FROM residentes WHERE cedula = %s", (cedula,))
    existente = cursor.fetchone()
    if existente:
        cursor.close()
        mensaje = 'existe'
        return render_template(
            'modulos/clientes/create.html',
            mensaje=mensaje,
            cedula=cedula
        )

    # ———————— Intentar INSERT/commit ————————
    try:
        cursor.execute(sql, data)
        db.database.commit()
    except mysql.connector.Error as err:
        db.database.rollback()
        cursor.close()
        # Si hay algún otro problema de ENUM mal enviado, err.msg lo detalla.
        mensaje = 'error_insercion'
        return render_template(
            'modulos/clientes/create.html',
            mensaje=mensaje,
            error_detalle=err.msg,
            cedula=cedula
        )
    finally:
        cursor.close()

    # ———————— Éxito ————————
    mensaje = 'insertado'
    return render_template('modulos/clientes/create.html', mensaje=mensaje, cedula=cedula)

from flask import request, jsonify

@app.route('/historial_medico/<int:id>/editar', methods=['POST'])
def editar_historial(id):
    # Validar y actualizar en base a request.form
    fecha = request.form.get('fecha')
    diagnostico = request.form.get('diagnostico')
    observaciones = request.form.get('observaciones')

    # Aquí actualizas la base de datos y guardas los cambios

    # Simular respuesta exitosa
    return jsonify({
        'success': True,
        'id': id,
        'fecha': datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y'),  # para mostrar en la tabla
        'fecha_backend': fecha,  # para rellenar input date
        'diagnostico': diagnostico,
        'observaciones': observaciones
    })



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

    # Validar cédula duplicada (excluyendo el mismo registro)
    cursor.execute("SELECT id FROM residentes WHERE cedula = %s AND id != %s", (cedula, id))
    existente = cursor.fetchone()
        
    if existente:
        mensaje = 'existe'
        return render_template('modulos/clientes/create.html', mensaje=mensaje, cedula=cedula)

    # Intentar guardar cambios
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
        WHERE id = %s
    """
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    mensaje = 'no_existe'
    return render_template('modulos/clientes/create.html', mensaje=mensaje, cedula=cedula)





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
        SELECT id, cedula, nombre, apellido1, apellido2, nacionalidad, telefono_contacto, direccion, activo
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

@app.route('/toggle_estado/<int:residente_id>', methods=['POST'])
@login_required
def toggle_estado_residente(residente_id):
    data = request.get_json()
    nuevo_estado = data.get('estado')

    if nuevo_estado is None:
        return jsonify({'success': False, 'error': 'Estado no proporcionado'}), 400

    estado_db = 1 if nuevo_estado in [True, 'true', 'activo', 1] else 0

    cursor = db.database.cursor()
    try:
        cursor.execute("UPDATE residentes SET activo = %s WHERE id = %s", (estado_db, residente_id))
        db.database.commit()
        return jsonify({'success': True, 'estado': estado_db})
    except Exception as e:
        db.database.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()



# MODULO HISTORIAL MEDICO



# Mostrar historial médico
@app.route('/historial_medico/<int:id>')
@login_required
def historial_medico(id):
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM historial_medico WHERE residente_id = %s", (id,))
    historial = cursor.fetchall()
    cursor.execute("""
    SELECT CONCAT(nombre, ' ', apellido1, ' ', apellido2) AS nombre_completo 
    FROM residentes 
    WHERE id = %s
""", (id,))
    residente = cursor.fetchone() 
    cursor.close()
    return render_template('/modulos/clientes/historial_medico.html', historial=historial, residente=residente ,residente_id=id)


@app.route('/medicacion/<int:id>')
@login_required
def medicacion(id):
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM  medicacion WHERE residente_id = %s", (id,))
    medicacion = cursor.fetchall()
    cursor.close()
    return render_template('/modulos/clientes/medicacion.html', medicacion=medicacion ,residente_id=id)


@app.route('/medicacion/nueva/<int:residente_id>', methods=['POST'])
@login_required
def agregar_medicacion(residente_id):
    medicamento = request.form.get('medicamento')
    dosis = request.form.get('dosis')
    frecuencia = request.form.get('frecuencia')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    # Validar campos obligatorios
    if not medicamento or not dosis or not frecuencia or not fecha_inicio:
        flash('Por favor completa todos los campos obligatorios.', 'danger')
        return redirect(url_for('medicacion', id=residente_id))

    try:
        cursor = db.database.cursor()
        sql = """
            INSERT INTO medicacion (residente_id, medicamento, dosis, frecuencia, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (residente_id, medicamento, dosis, frecuencia, fecha_inicio, fecha_fin))
        db.database.commit()
        cursor.close()
        flash('Medicamento agregado correctamente.', 'success')
    except Exception as e:
        flash('Error al agregar el medicamento.', 'danger')
        print(f"Error al insertar medicación: {e}")

    # Redirigir a la página que muestra la medicación del residente
    return redirect(url_for('medicacion', id=residente_id))



# RUTA PARA ELIMINAR UN MEDICAMENTO
@app.route('/medicacion/<int:id>/eliminar', methods=['POST', 'GET'])
@login_required
def eliminar_medicacion(id):
    cursor = db.database.cursor(dictionary=True)
    # Primero obtenemos el residente_id para luego redirigir correctamente
    cursor.execute("SELECT residente_id FROM medicacion WHERE id = %s", (id,))
    medicamento = cursor.fetchone()
    
    if medicamento is None:
        cursor.close()
        flash('Medicamento no encontrado.', 'danger')
        return redirect(url_for('dashboard'))  # o donde consideres
    
    residente_id = medicamento['residente_id']

    try:
        cursor.execute("DELETE FROM medicacion WHERE id = %s", (id,))
        db.database.commit()
        flash('Medicamento eliminado correctamente.', 'success')
    except Exception as e:
        flash('Error al eliminar el medicamento.', 'danger')
        print(f"Error eliminando medicacion: {e}")
    finally:
        cursor.close()

    return redirect(url_for('medicacion', id=residente_id))




@app.route('/historial_medico/<int:registro_id>/editar', methods=['POST'])
def editar_registro_medico(registro_id):
    if not request.is_xhr:  # o usa: if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return jsonify({'error': 'Acceso no permitido'}), 403

    registro = RegistroMedico.query.get_or_404(registro_id)

    try:
        fecha = request.form['fecha']
        diagnostico = request.form['diagnostico']
        observaciones = request.form.get('observaciones', '')

        registro.fecha = datetime.strptime(fecha, '')
        registro.diagnostico = diagnostico
        registro.observaciones = observaciones

        db.session.commit()

        return jsonify({
            'success': True,
            'id': registro.id,
            'fecha': registro.fecha.strftime('%d/%m/%Y'),
            'fechaISO': registro.fecha.strftime('%Y-%m-%d'),
            'diagnostico': registro.diagnostico,
            'observaciones': registro.observaciones
        })
    except Exception as e:
        return jsonify({'error': 'No se pudo actualizar el registro'}), 400





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



# Listar usuarios
@app.route('/admin/usuarios')
def admin_usuarios():
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('modulos/usuarios/admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/crear', methods=['POST'])
def crear_usuario():
    f = request.form
    cursor = db.database.cursor()
    sql = """
        INSERT INTO usuarios (username, correo, password, nombre, apellido, telefono, rol, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    valores = (
        f['username'], f['correo'], f['password'], f['nombre'], f['apellido'],
        f['telefono'], f['rol'], 1 if 'activo' in f else 0
    )
    cursor.execute(sql, valores)
    db.database.commit()
    cursor.close()
    flash("Usuario creado exitosamente")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/editar/<int:id>', methods=['POST'])
def editar_usuario(id):
    f = request.form
    cursor = db.database.cursor()
    sql = """
        UPDATE usuarios
        SET username=%s, correo=%s, nombre=%s, apellido=%s,
            telefono=%s, rol=%s, activo=%s
        WHERE id=%s
    """
    valores = (
        f['username'], f['correo'], f['nombre'], f['apellido'],
        f['telefono'], f['rol'], 1 if 'activo' in f else 0, id
    )
    cursor.execute(sql, valores)
    db.database.commit()
    cursor.close()
    flash("Usuario actualizado correctamente")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    db.database.commit()
    cursor.close()
    flash("Usuario eliminado")
    return redirect(url_for('admin_usuarios'))



if __name__ == '__main__':
    app.run(port=5000, debug=True)


