#==================================================================================================================================
#BIBLIOTECAS
#==================================================================================================================================
import streamlit as st
import pandas as pd
import base64
import fpdf
from fpdf import FPDF

#==================================================================================================================================
#INICIO
#==================================================================================================================================
st.set_page_config(layout="wide", page_icon='logo2.jpeg', page_title="Enf_infecciosas")
col1, col2 = st.columns([1,1], gap="large")
with col1:
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 40px; font-weight: bold; text-transform: uppercase;">PREVENCIÓN Y TERAPÉUTICA DE PRECISIÓN</p>'
    st.write(texto,unsafe_allow_html=True)
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 15px; font-weight: bold;">Paula Santamaría Velasco</p>'
    st.write(texto,unsafe_allow_html=True)
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 15px; font-weight: bold;">Aitana Crespo Ferrero</p>'
    st.write(texto,unsafe_allow_html=True)
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 15px; font-weight: bold;">Urko Allí Barrena</p>'
    st.write(texto,unsafe_allow_html=True)
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 15px; font-weight: bold;">Paula Gregorio Losada</p>'
    st.write(texto,unsafe_allow_html=True)
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 15px; font-weight: bold;">Beatriz Alonso Martín</p>'
    st.write(texto,unsafe_allow_html=True)
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 25px; font-weight: bold; text-transform: uppercase;">INFORMACIÓN DEL PACIENTE</p>'
    st.write(texto,unsafe_allow_html=True)
    
    nombre = st.text_input(label="Nombre del paciente")
    apellidos = st.text_input(label="Apellidos del paciente")
    nhi = st.text_input(label="Nº Historia Clínica del paciente")
    sexo = st.selectbox("Sexo del paciente",['Mujer','Hombre','Otro'])
    fecha_n = st.text_input(label="Fecha de nacimiento del paciente", placeholder = "dd-mm-yyyy")
    
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 25px; font-weight: bold; text-transform: uppercase;">INFORMACIÓN CLÍNICA</p>'
    st.write(texto,unsafe_allow_html = True)
    
    enfermedad = st.text_input(label="Enfermedad")
    otras_e = st.text_input(label="Patologías")
    
    texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 25px; font-weight: bold; text-transform: uppercase;">INFORMACIÓN DEL TRATAMIENTO</p>'
    st.write(texto,unsafe_allow_html = True)
    tratamiento = st.text_input(label="Tratamiento", placeholder = "Añada los medicamentos separados por comas")
    farmacos = tratamiento.split(',')
    farmacos = [i.strip().lower() for i in farmacos]
with col2:
    st.image("logo2.jpeg")
    


#==================================================================================================================================
# 2 PARTE
#==================================================================================================================================

# FUNCIONES

def buscarAlelosGen(gen):
    import json
    import requests
    listaAlelos=[]
    url="https://api.cpicpgx.org/v1/allele?genesymbol=eq."+gen
    response = requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    for i in range(len(datos)):
        alelo=datos[i]["name"]
        listaAlelos.append(alelo)
    setAlelos=set(listaAlelos)
    ListaFiltradaAlelos=(list(setAlelos))
    ListaFiltradaAlelos.sort()
    return ListaFiltradaAlelos

def ID_CPIC_Farmaco(nombreFarmaco):
    import json
    import requests
    url="https://api.cpicpgx.org/v1/drug?name=eq."+nombreFarmaco
    response = requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    if len(datos) != 0:
        ID_Farmaco=datos[0]['drugid']
        return ID_Farmaco
    else:
        return ''

def fenotipoSegunAlelos(gen,alelo1,alelo2):
    import json
    import requests
    listaAlelos=[]
    url="https://api.cpicpgx.org/v1/diplotype?genesymbol=eq."+gen+"&diplotype=eq."+alelo1+"/"+alelo2
    response= requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    return datos

def urlGuia(farmaco,ID):
    import json
    import requests
    url = 'https://api.cpicpgx.org/v1/drug?name=eq.'+farmaco+'&select=drugid,name,guideline_for_drug(*)'
    response = requests.get(url)
    json_obtenido = response.json()
    datos = json_obtenido
    for i in datos:
        if i['guideline_for_drug']['id'] == ID:
            return i['guideline_for_drug']['url']
   
from googletrans import Translator   
def recomendacionClinica(gen,alelo1,alelo2,farmaco):
    lista = []
    fenotipo = fenotipoSegunAlelos(gen,alelo1,alelo2)
    if len(fenotipo) != 0:
        lookupkey= fenotipo[0]['lookupkey']
        ID_Farmaco=ID_CPIC_Farmaco(farmaco)
        import json
        import requests
        url='https://api.cpicpgx.org/v1/recommendation?drugid=eq.'+ID_Farmaco+'&lookupkey=cs.{"'+list(lookupkey.keys())[0]+'":"'+list(lookupkey.values())[0]+'"}'
        response = requests.get(url)
        json_obtenido = response.json()
        datos=json_obtenido
        if len(datos) != 0:
            translator1 = Translator()
            lista.append((translator1.translate(fenotipo[0]['generesult'], src='en', dest='es')).text)
            translator = Translator()
            lista.append((translator.translate(datos[0]['drugrecommendation'].encode('latin-1','ignore').decode('latin-1'), src='en', dest='es')).text)
    return lista

def BuscarFarmacosRelacionadosGen(gen):
    import json
    import requests
    listaFarmacos=[]
    url="https://api.pharmgkb.org/v1/data/clinicalAnnotation?location.genes.symbol="+gen
    response = requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    if datos['status'] == 'success':
        for i in range(len(datos["data"])):
            farmaco=datos["data"][i]["relatedChemicals"][0]["name"]
            listaFarmacos.append(farmaco)
    setFarmacos=set(listaFarmacos)
    ListaFiltradaFarmacos=(list(setFarmacos))
    ListaFiltradaFarmacos.sort()
    return ListaFiltradaFarmacos

# STREAMLIT

# Título
texto = '<p></p><p style="font-family: \'Times New Roman\'; font-size: 25px; font-weight: bold; text-transform: uppercase;">INFORMACIÓN GENÉTICA</p>'
st.write(texto, unsafe_allow_html=True)

# Selección dinámica del número de genes

num_genes = st.number_input("Número de genes que quieres introducir:", min_value=1, max_value=20, step=1, value=1)

# Inicializar listas para almacenar los datos
genes = []
alelos1 = []
alelos2 = []

# Crear las entradas dinámicamente por filas
for i in range(num_genes):
    st.write(f"### Gen {i+1}")  # Opcional: para etiquetar cada fila
    # Crear una fila con tres columnas: una para el gen y dos para los alelos
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        gen = st.text_input(label=f"Gen {i+1}", placeholder="Introduzca el gen", key=f"gen_{i}")
    with col2:
        lista_alelos = buscarAlelosGen(gen)  # Busca alelos en función del gen ingresado
        alelo_1 = st.selectbox(f"Alelo 1 de Gen {i+1}", ['-'] + lista_alelos, key=f"alelo1_{i}")
    with col3:
        alelo_2 = st.selectbox(f"Alelo 2 de Gen {i+1}", ['-'] + lista_alelos, key=f"alelo2_{i}")
    
    # Guardar los datos en las listas
    genes.append(gen)
    alelos1.append(alelo_1)
    alelos2.append(alelo_2)


#==================================================================================================================================
# RESULTADOS
#==================================================================================================================================

recomendaciones = dict()
for i in farmacos:
    recomendaciones[i] = dict()
    for x, y, z in zip(genes, alelos1, alelos2):
        if y != '-' and z != '-':
            recomendaciones[i][x] = recomendacionClinica(x,y,z,i)
            
relaciones = dict()
for x,y,z in zip(genes, alelos1, alelos2):
    if y != '-' and z != '-':
        relaciones[x] = BuscarFarmacosRelacionadosGen(x)
#====================================================================================================================================
# PDF
#====================================================================================================================================

st.markdown("***")
 
export_as_pdf = st.button("Generar PDF")

report_text = "Hola"

def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

class PDF(FPDF):
    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


if export_as_pdf:
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.set_margins(left = 20.0, top = 25.0, right = 20.0)
    pdf.add_page()
    pdf.set_font('Times', 'I', 20)
    pdf.cell(40, 10, 'Información del paciente', ln = 1)
    
    pdf.set_fill_color(r = 255, g = 255, b = 255)
    pdf.set_draw_color(r = 255, g = 255, b = 255)
    
    pdf.multi_cell(w = 170, h = 30, border = 1, fill = True)
    pdf.set_font('Times', '', 12)
    pdf.set_y(pdf.get_y()-25)
    pdf.cell(w = 0, txt = f'Nombre del paciente: {nombre}', align = 'L')
    pdf.set_x(-90)
    pdf.cell(w = 0, txt = f'Sexo del paciente: {sexo}', align = 'L')
    pdf.ln(9)
    pdf.cell(w = 0, txt = f'Apellidos del paciente: {apellidos}', align = 'L')
    pdf.set_x(-90)
    pdf.cell(w = 0, txt = f'Fecha de nacimiento del paciente: {fecha_n}', align = 'L')
    pdf.ln(9)
    pdf.cell(w = 0, txt = f'Nº Historia Clínica del paciente: {nhi}', align = 'L', ln = 1)
    pdf.ln(9)
    
    pdf.set_font('Times', 'I', 20)
    pdf.cell(40, 10, 'Información clínica', ln = 1)
    pdf.set_font('Times', '', 12)
    pdf.multi_cell(w = 170, h = 10, txt = f'Enfermedad: {enfermedad}\nPatologías: {otras_e}\nTratamiento: {tratamiento}', border = 1, fill = True)
    pdf.ln(3)
    
    pdf.set_font('Times', 'I', 20)
    pdf.cell(40, 10, 'Fenotipo y recomendación de dosis', ln = 1)
    texto = ''
    for i in recomendaciones:
        texto += 'En relación con el fármaco ' + i + ':\n'       
        for x in recomendaciones[i]:
            if len(recomendaciones[i][x]) == 0:
                texto += 'No hay información sobre interacciones con '+ x +' para esos alelos.\n'
            else:
                texto += 'El fenotipo para '+ x +' es '+ recomendaciones[i][x][0] + '. Recomendación clínica: ' + recomendaciones[i][x][1]+'.\n'
        texto += '\n'
    pdf.set_font('Times', '', 12)
    pdf.multi_cell(w = 170, h = 6, txt = texto, border = 1, fill = True, align = 'L')
    pdf.ln(3)
    
    pdf.set_font('Times', 'I', 20)
    pdf.cell(40,10,'Interacciones con fármacos',ln=1)
    texto = ''
    for i in relaciones:
        texto += 'Fármacos metabolizados por ' + i + ': ' + str(', '.join(relaciones[i]))+'.\n\n'
    pdf.set_font('Times', '', 12)
    pdf.multi_cell(w = 170, h = 6, txt = texto, border = 1, fill = True, align = 'L')
        
    
    html = create_download_link(pdf.output(dest="S").encode('latin-1'), f"Informe paciente {nhi}")

    st.markdown(html, unsafe_allow_html=True)
    
#==================================================================================================================================
# MOSTRAR RESULTADOS
#==================================================================================================================================   
texto = '<center><p style="font-family: \'Times New Roman\'; font-weight: bold; text-transform: uppercase; font-size: 35px;">Informe final</p></center>'
st.write(texto,unsafe_allow_html = True)
#--------------------------------------------------------------------------------------------------------------------------
texto = '<p style="font-family: \'Times New Roman\'; font-weight: bold; text-transform: uppercase; font-size: 22px;">Fenotipo y recomendación de dosis</p>'
st.write(texto,unsafe_allow_html = True)

for i in recomendaciones:
    texto = '<p style="text-indent: 30px; font-family: \'Times New Roman\'; font-size: 18px;">En relación con el fármaco <b>'+i+'</b>:</p>'
    st.write(texto,unsafe_allow_html = True)          
    for x in recomendaciones[i]:
        if len(recomendaciones[i][x]) == 0:
            texto = '<p style="text-indent: 50px; font-family:Cambria; font-size: 15px;">No hay información sobre interacciones con <b>'+x+'</b> para esos alelos.</p>'
            st.write(texto,unsafe_allow_html = True)
        else:
            texto = '<p style="text-indent: 50px; font-family: \'Times New Roman\'; font-size: 15px;">El fenotipo para <b>'+x+'</b> es '+recomendaciones[i][x][0]+'</a></p>'
            st.write(texto,unsafe_allow_html = True)
            texto='<p style="text-indent: 50px; font-family: \'Times New Roman\'; font-size: 15px;">Recomendación clínica: '+recomendaciones[i][x][1]+'</a></p>'
            st.write(texto,unsafe_allow_html = True)
#--------------------------------------------------------------------------------------------------------------------------   
texto = '<p style="font-family: \'Times New Roman\'; font-weight: bold; text-transform: uppercase; font-size: 22px;">Interacciones con otros fármacos</p>'
st.write(texto,unsafe_allow_html = True)

for i in relaciones:
    texto = '<p style="text-indent: 30px; font-family: \'Times New Roman\'; font-size: 15px;">Fármacos metabolizados por <b>'+i+'</b>: '+str(', '.join(relaciones[i]))+'.'+'</p>'
    st.write(texto,unsafe_allow_html = True)
