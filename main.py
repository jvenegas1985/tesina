import mysql.connector
from flask import jsonify, Flask,make_response, redirect, url_for, render_template, request, flash, session
import database as db
import bcrypt

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Función para obtener la conexión a la base de datos
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Usuario1',
        database='proyecto'
    )
    return connection

# Ruta principal (home)
@app.route('/', methods=['GET', 'POST'])
def home():
    cursor = db.database.cursor()
    cursor.execute("""
            SELECT id, cedula, nombre, apellido1, apellido2, nacionalidad, telefono_contacto, direccion 
            FROM residentes 
            ORDER BY id DESC LIMIT 9 OFFSET 0
        """)
    datos = cursor.fetchall()
    return render_template('index.html')





@app.route('/clientes')
def index_clientes():
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
    finally:
        cursor.close()
        

    response = make_response(render_template('modulos/clientes/index.html', residentes=arreglo))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Ruta para crear un nuevo cliente
@app.route('/create')
def index_create():
    return render_template('modulos/clientes/create.html')




@app.route('/edit/<string:id>', methods=['GET'])
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
def eliminar_residente(id):
    cursor = db.database.cursor() # Establecer conexión
    cursor.execute("DELETE from RESIDENTES where id= %s", (id,))
    db.database.commit()   
    cursor.close()  # Cerrar el cursor  
    
  
    return redirect(url_for('index_clientes'))




# Ruta para guardar un nuevo cliente
@app.route('/modulos/clientes/create/guardar', methods=['POST'])
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
def buscar():
    query = request.args.get('q')
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
    cursor = db.database.cursor()  # Establecer conexión
    cursor.execute(sql, (like_query,) * 6)
    datos = cursor.fetchall()
    arreglo = []
    columnames = [col[0] for col in cursor.description]
    for record in datos:
        arreglo.append(dict(zip(columnames, record)))
    
    cursor.close()
    return jsonify(arreglo)





@app.route('/ver_info/<string:id>', methods=['GET'])
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


#pagina de login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.form['usuario']
        password = request.form['contraseña']
        
        # Conexión a la base de datos
        
        cursor=db.database.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and password == user[4]:  # Comparación directa (índice 4 = contraseña)
            session['usuario'] = user[2]  # Nombre
            session['rol'] = user[6]      # Rol (admin o usuario)
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('/'))
        else:
            flash("Credenciales incorrectas. Intenta de nuevo.", "danger")

    return render_template('login.html')

# MODULO HISTORIAL MEDICO



# Mostrar historial médico
@app.route('/historial_medico/<string:id>', methods=['GET'])
def ver_historial_medico(id):
    cursor = db.database.cursor()

    # Obtener los datos del residente
    cursor.execute("SELECT nombre FROM residentes WHERE id = %s", (id,))
    residente = cursor.fetchone()  # Esto devuelve una tupla como ('Juan Pérez',)

    # Obtener historial médico
    cursor.execute("SELECT * FROM historial_medico WHERE residente_id = %s ORDER BY fecha DESC", (id,))
    historial = cursor.fetchall()

    cursor.close()

    return render_template(
        'modulos/clientes/historial_medico.html',
        historial=historial,
        id=id,
        residente_nombre=residente[0] if residente else "Desconocido"
    )

# Agregar nueva entrada
@app.route('/historial_medico/agregar', methods=['POST'])
def agregar_historial_medico():
    residente_id = request.form.get('residente_id')
    fecha = request.form.get('fecha')
    diagnostico = request.form.get('diagnostico')
    medico = request.form.get('medico')
    notas = request.form.get('notas')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO historial_medico (residente_id, fecha, diagnostico, medico, notas)
        VALUES (%s, %s, %s, %s, %s)
    """, (residente_id, fecha, diagnostico, medico, notas))
    conn.commit()
    conn.close()

    flash('Registro guardado correctamente.', 'success')
    return redirect(url_for('ver_historial_medico', id=id))



if __name__ == '__main__':
    app.run(debug=True)


