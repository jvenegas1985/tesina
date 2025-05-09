from faker import Faker
import random

faker = Faker('en_US')  # Localización en español

# Función para generar un INSERT por cada residente
def generar_insert_residentes(n=1000):
    inserts = []
    for i in range(n):
        nombre = faker.first_name()
        apellido1 = faker.last_name()
        apellido2 = faker.last_name()
        cedula = faker.random_number(digits=7, fix_len=True)
        fecha_nacimiento = faker.date_of_birth(minimum_age=60, maximum_age=95).strftime('%Y-%m-%d')
        genero = random.choice(['Masculino', 'Femenino', 'Otro'])
        estado_civil = random.choice(['Soltero', 'Casado', 'Viudo', 'Divorciado','Otro'])
        nacionalidad = faker.country()
        direccion = faker.address().replace("\n", ", ")
        telefono_contacto = faker.phone_number()
        contacto_emergencia_nombre = faker.name()
        contacto_emergencia_parentesco = random.choice(['Hijo', 'Hija', 'Nieto', 'Sobrino', 'Hermano', 'Esposo'])
        contacto_emergencia_telefono = faker.random_number(digits=7, fix_len=True)
        condiciones_medicas = random.choice(['Diabetes', 'Hipertensión', 'Alzheimer', 'Artritis', 'Sano'])
        medicamentos_actuales = random.choice(['Metformina', 'Losartán', 'Paracetamol', 'Ibuprofeno', 'Ninguno'])
        movilidad = random.choice(['Independiente', 'Con ayuda', 'Dependiente'])
        estado_mental = random.choice(['Lúcido', 'Desorientado', 'Demencia'])
        activo = 1

        insert = f"""INSERT INTO `proyecto`.`residentes`
(nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero, estado_civil, nacionalidad, direccion,
telefono_contacto, contacto_emergencia_nombre, contacto_emergencia_parentesco, contacto_emergencia_telefono,
condiciones_medicas, medicamentos_actuales, movilidad, estado_mental, activo)
VALUES ('{nombre}', '{apellido1}', '{apellido2}', '{cedula}', '{fecha_nacimiento}', '{genero}', '{estado_civil}',
'{nacionalidad}', '{direccion}', '{telefono_contacto}', '{contacto_emergencia_nombre}', '{contacto_emergencia_parentesco}',
'{contacto_emergencia_telefono}', '{condiciones_medicas}', '{medicamentos_actuales}', '{movilidad}', '{estado_mental}', {activo});"""
        
        inserts.append(insert)
    return inserts

# Generar los inserts
inserts_sql = generar_insert_residentes(50)

# Ruta de guardado en Windows (ajusta según tu usuario si quieres)
ruta_archivo = "C:\\Users\\Public\\insert_residentes.sql"
with open(ruta_archivo, "w", encoding="utf-8") as f:
    f.write("\n\n".join(inserts_sql))

print(f"Archivo generado en: {ruta_archivo}")
