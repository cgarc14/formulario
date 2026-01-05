import streamlit as st
import gspread
import pandas as pd
from datetime import datetime, date 

st.set_page_config(
    page_title="(Dev) Formulario",
    layout="centered"
)


def extraer_sheet():
    credenciales = st.secrets["gspread_creds"]
    gc = gspread.service_account_from_dict(credenciales)

    sheet = gc.open_by_url(st.secrets["spreadsheet"]["url"])
    return sheet.get_worksheet(0)

datos = extraer_sheet()


st.title("Draft Formulario")

st.info("Los comentarios de este borrador aparecerán así. \n Te dará un contexto de cómo funcionan algunos espacios más adelante. Si todo va bien, después los sacamos.")

st.subheader("Datos de Contacto")

st.info("**(Esto está pensado para la persona de contacto del paciente)**")

st.write("A continuación, te pedimos responder las siguientes preguntas.")


nombres_contacto = st.text_input("Nombres:")
apellido_paterno_contacto = st.text_input("Apellido Paterno:")
apellido_materno_contacto = st.text_input("Apellido Materno (Opcional):")
rut_contacto = st.text_input("RUT:")
telefono_contacto = st.text_input("Teléfono de Contacto:")
correo_contacto = st.text_input("Correo Electrónico (Opcional):")
relacion_check_contacto = st.checkbox("¿Eres familiar del paciente?")


st.info("Quizás el paciente no está siendo ingresado por un familiar, o puede ser el mismo paciente quien se ingresa a sí mismo. Si es un familiar, entonces se habilita el espacio para que especifique su relación con el paciente.")

relacion_contacto = st.text_input("Parentesco con Paciente (Ej: Hijo/a, Hermano/a, etc):", disabled= not relacion_check_contacto)


st.subheader("Datos del Paciente")

st.info("Si el paciente se está ingresando por cuenta propia, entonces omitimos preguntarle nuevamente por su nombre y rut. Si es otra persona, entonces le pedimos esa info sobre el paciente.")
contacto_paciente_check = st.checkbox("¿Tú eres el paciente?")

if contacto_paciente_check:
    st.write("Estos datos ya los llenaste en la sección anterior. Por favor continua con las siguientes preguntas.")

nombres_paciente = st.text_input("Nombres:", key="npac", disabled= contacto_paciente_check)
apellido_paterno_paciente = st.text_input("Apellido Paterno:", key="appac", disabled= contacto_paciente_check)
apellido_materno_paciente = st.text_input("Apellido Materno (Opcional):", key="ampac", disabled= contacto_paciente_check)
rut_paciente = st.text_input("RUT:", key="rpac", disabled= contacto_paciente_check)

fecha_nacimiento_paciente = st.date_input("Fecha de Nacimiento:", min_value="1900-01-01", max_value="today", format="DD-MM-YYYY", value="1900-01-31")

st.info("Podemos incluir más preguntas o modificar las que están. En algunas preguntas, si la persona responde **Sí**, se habilita una sección para que detalle sobre esa pregunta.")

check_remedios = st.checkbox("¿Toma medicamentos?")
remedios = st.text_area("Lista todos los medicamentos consumidos:", disabled= not check_remedios)

check_discapacidad = st.checkbox("¿Tiene alguna discapacidad?")
discapacidades = st.text_area("¿Qué discapacidad/es tiene?", disabled= not check_discapacidad)

check_enfermedad = st.checkbox("¿Tiene alguna enfermedad crónica? (Ej: Diabetes, Hipertensión, Artritis, Alzheimer)")
enfermedades = st.text_area("¿Qué enfermedad/es tiene?", disabled= not check_enfermedad)

check_reaccion = st.checkbox("¿Tiene alguna alergia o es intolerante a algún alimento? (Ej: Lactosa, Gluten, Nueces)")
reacciones = st.text_area("Cuéntanos qué tiene:", disabled= not check_reaccion)

check_baño = st.checkbox("¿Necesita ayuda para ir al baño?")
check_comida = st.checkbox("¿Necesita ayuda para comer?")

st.info("Esto está pensado por si alguna persona necesita dejar instrucciones más específicas o particulares para el cuidado del paciente.")
info_adicional = st.text_area("Indicaciones Adicionales (Opcional):")

if st.button("Enviar"):
    if not nombres_contacto or not apellido_paterno_contacto or not rut_contacto or not telefono_contacto:
        st.warning("¡Por favor revisa que todos los campos obligatorios estén completados!")

    else:
 
        st.success("¡El formulario se llenó correctamente!")
        #   Creación ID para entrada

        ids_existentes = datos.col_values(1)
        num_ids = [int(i) for i in ids_existentes if i.isdigit()]
        if num_ids:
            next_id = max(num_ids) + 1
        else:
            next_id = 1


        contacto = {
            "nombres_contacto": nombres_contacto,
            "apellido_paterno_contacto": apellido_paterno_contacto,
            "apellido_materno_contacto": apellido_materno_contacto,
            "rut_contacto": rut_contacto,
            "telefono_contacto": telefono_contacto,
            "correo_contacto": correo_contacto,
            "familiar": "Si" if relacion_check_contacto == True else "No",
            "parentesco": relacion_contacto
        }

        st.info("Esto es la info del contacto")
        contacto

        st.info("La fila en el registro tendrá esta forma.")
        data_contacto = pd.DataFrame([contacto])
        st.dataframe(data_contacto, hide_index=True)


        paciente = {
            "id": next_id,
            "nombres_paciente": nombres_paciente if contacto_paciente_check == False else nombres_contacto,
            "apellido_paterno_paciente": apellido_paterno_paciente if contacto_paciente_check == False else apellido_paterno_contacto,
            "apellido_materno_paciente": apellido_materno_paciente if contacto_paciente_check == False else apellido_materno_contacto,
            "rut_paciente": rut_paciente if contacto_paciente_check == False else rut_contacto,
            "fecha_nacimiento": fecha_nacimiento_paciente.strftime("%d-%m-%Y"),
            "edad": f"{str((date.today().year - fecha_nacimiento_paciente.year))}a{str((date.today().month - fecha_nacimiento_paciente.month))}m",
            "check_medicamentos": "Si" if check_remedios == True else "No",
            "medicamentos": remedios,
            "check_discapacidad": "Si" if check_discapacidad == True else "No",
            "discapacidad": discapacidades,
            "check_enfermedad": "Si" if check_enfermedad == True else "No",
            "enfermedad": enfermedades,
            "check_alergias": "Si" if check_reaccion == True else "No",
            "alergias": reacciones,
            "check_baño": "Si" if check_baño == True else "No",
            "check_comida": "Si" if check_comida == True else "No",
            "info_adicional": info_adicional,
            "fecha_creacion": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        st.info("Esto es la info del paciente.")
        paciente

        st.info("La fila en el registro tendrá esta forma.")
        data_paciente = pd.DataFrame([paciente])
        st.dataframe(data_paciente, hide_index=True)

        st.info("El registro final se vería así.")
        data_total = pd.concat([data_paciente, data_contacto], axis=1, sort=False)
        st.dataframe(data_total, hide_index=True)
        
        data_nueva = data_total.values.tolist()

        # datos.append_rows(data_nueva)

    
