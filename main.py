import mysql.connector
from flask import Flask,make_response, redirect, url_for, render_template, request, flash
import database as db

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



# Ruta para ver la lista de clientes
from flask import make_response, render_template

@app.route('/clientes')
def index_clientes():
    try:
        cursor = db.database.cursor()
        cursor.execute("""
            SELECT id, cedula, nombre, apellido1, apellido2, nacionalidad, telefono_contacto, direccion 
            FROM residentes 
            ORDER BY id DESC LIMIT 9 OFFSET 0
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
def index_editar(id):
    cursor = db.database.cursor() # Establecer conexión
    cursor.execute("SELECT * FROM residentes where id= %s", (id,))
    datos= cursor.fetchall() 
    arreglo=[]
    columnames=[colum[0] for colum in cursor.description]
    for record in datos:
         arreglo.append(dict(zip(columnames,record)))
    
    cursor.close()  # Cerrar el cursor  # Cerrar el cursor
    
  # Cerrar la conexión
    return render_template('modulos/clientes/edit.html', arreglo=arreglo)

# Ruta para eliminar un residente

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
   
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        cedula = request.form['cedula']
        fecha_nacimiento = request.form['fecha_nacimiento']
        genero = request.form['genero']
        estado_civil = request.form['estado_civil']
        nacionalidad = request.form['pais_nacimiento']
        direccion = request.form['direccion']
        telefono_contacto = request.form['telefono']
        contacto_emergencia_nombre = request.form['nombre_contacto_emergencia']
        contacto_emergencia_parentesco = request.form['contacto_emergencia_parentesco']
        contacto_emergencia_telefono = request.form['telefono_emergencia']
        condiciones_medicas = request.form['condiciones_medicas']
        medicamentos_actuales = request.form['medicamentos']
        movilidad = request.form['movilidad']
        estado_mental = request.form['estado_mental']
        
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
    # Obtener los datos del formulario
    nombre = request.form['nombre']
    apellido1 = request.form['apellido1']
    apellido2 = request.form['apellido2']
    cedula = request.form['cedula']
    fecha_nacimiento = request.form['fecha_nacimiento']
    genero = request.form['genero']
    estado_civil = request.form['estado_civil']
    nacionalidad = request.form['pais_nacimiento']
    direccion = request.form['direccion']
    telefono_contacto = request.form['telefono']
    contacto_emergencia_nombre = request.form['nombre_contacto_emergencia']
    contacto_emergencia_parentesco = request.form['contacto_emergencia_parentesco']
    contacto_emergencia_telefono = request.form['telefono_emergencia']
    condiciones_medicas = request.form['condiciones_medicas']
    medicamentos_actuales = request.form['medicamentos']
    movilidad = request.form['movilidad']
    estado_mental = request.form['estado_mental']
    
    # SQL para actualizar
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

    data = (
        nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero, estado_civil, nacionalidad,
        direccion, telefono_contacto, contacto_emergencia_nombre, contacto_emergencia_parentesco,
        contacto_emergencia_telefono, condiciones_medicas, medicamentos_actuales, movilidad,
        estado_mental, id  # El ID debe ir al final para el WHERE
    )

    cursor = db.database.cursor()
    cursor.execute(sql, data)
    cursor.execute("SELECT * FROM residentes where id= %s", (id,))
    datos= cursor.fetchall() 
    arreglo=[]
    columnames=[colum[0] for colum in cursor.description]
    for record in datos:
         arreglo.append(dict(zip(columnames,record)))
    
    cursor.close()
    db.database.commit()
    cursor.close()

    mensaje = 'actualizado'
    return render_template('modulos/clientes/edit.html', arreglo=arreglo, mensaje=mensaje, id=id)

   
if __name__ == '__main__':
    app.run(debug=True)
