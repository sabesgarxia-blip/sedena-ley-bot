import os
import re
import asyncio
import itertools
import unicodedata
from threading import Thread
import discord
from discord import app_commands
from flask import Flask
from groq import Groq

# ==========================================
# 1. SERVIDOR WEB PARA MANTENER VIVO RENDER
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return 'Bot Código Penal Federal activo 24/7'

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 2. CONFIGURACIÓN DE LA IA (GROQ)
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY.strip())
        print("¡IA Groq configurada exitosamente!")
    else:
        print("Aviso: GROQ_API_KEY no encontrada en variables de entorno.")
        groq_client = None
except Exception as err:
    print(f"Error al configurar Groq: {err}")
    groq_client = None

# CATÁLOGO OFICIAL (ARTÍCULO, NOMBRE LIMPIO, SANCIÓN)
CATALOGO_ARTICULOS = [
    ("1", "Art. 1 - Disposición General del Código Penal", "Aplicable en toda la República Mexicana para delitos de Fuero Común y Federal; es delito toda acción u omisión voluntaria penada por la ley."),
    ("1.1", "Art. 1.1 - Secreto profesional del abogado", "Exento de obligación legal de denunciar el presunto delito conferido por su cliente en servicios jurídico-legales."),
    ("1.2", "Art. 1.2 - Obligatoriedad territorial y mar territorial", "Obligatoria para todos los habitantes de la República, incluidos extranjeros."),
    ("1.3", "Art. 1.3 - Circunstancias atenuantes", "Reducción de gravedad o pena según criterio judicial (obediencia sin oposición, reparar daño, cómplice, confesión o discapacidad/trastorno demostrable)."),
    ("2", "Art. 2 - Circunstancias agravantes", "+11 meses de prisión federal o 5,000 MXN (insulto repetido a funcionario, reincidencia o discriminación)."),
    ("3", "Art. 3 - Equivalencia de plazos de cárcel", "24 meses = 1 día 12h; 18 meses = 1 día 6h; 12 meses = 22h; 9 meses = 12h 30m; 6 meses = 9h; 3 meses = 5h 30m; 1 mes = 2h 30m."),
    ("4", "Art. 4 - Conducción temeraria", "2,000 MXN y/o pérdida de 3 puntos."),
    ("4.1", "Art. 4.1 - Sistema de puntaje de licencia", "Máximo 10 puntos; al llegar a 0 puntos retirada de licencia de 6 a 12 meses."),
    ("5", "Art. 5 - Daño a propiedad privada o pública con vehículo", "2,500 MXN y reparación total (la conciliación extingue el delito)."),
    ("6", "Art. 6 - No cumplir semáforos", "500 MXN por cada semáforo ignorado."),
    ("7", "Art. 7 - Conducir en dirección contraria", "3,000 MXN y/o pérdida de 1 punto."),
    ("8", "Art. 8 - Conducir bajo efectos de alcohol o sustancias ilegales", "2,500 MXN y/o pérdida de 6 puntos."),
    ("9", "Art. 9 - Posesión de arma no autorizada en vehículo", "Art. 48 + 4,000 MXN e incautación temporal del vehículo."),
    ("10", "Art. 10 - Incumplir límites de velocidad", "1,500 MXN y retirada de 2 puntos."),
    ("11", "Art. 11 - Conducir sin licencia", "4,000 MXN e ingreso a prisión preventiva de 24h."),
    ("12", "Art. 12 - Carreras clandestinas sin permiso", "6,500 MXN, suspensión de licencia y 1 mes de prisión."),
    ("13", "Art. 13 - Mal estacionado en zona prohibida", "750 MXN o traslado al depósito (1,000 MXN extra por grúa)."),
    ("14", "Art. 14 - Estacionado obstruyendo la circulación vial", "1,800 MXN o depósito (2,000 MXN por grúa)."),
    ("15", "Art. 15 - No ceder el paso a servicios de emergencia", "1,500 MXN y retirada de licencia por 1 mes."),
    ("16", "Art. 16 - Uso de luces obligatorio entre ocaso y amanecer", "500 MXN."),
    ("17", "Art. 17 - Vehículo con faltas técnicas y/o mecánicas", "900 MXN y retirada de 2 puntos."),
    ("18", "Art. 18 - Arrojar objetos a la vía o inmediaciones", "500 MXN."),
    ("19", "Art. 19 - Incumplimiento general de normas de tráfico", "500 MXN y retirada de 1 punto."),
    ("20", "Art. 20 - Adelantamientos erróneos o peligrosos", "1,200 MXN y retirada de 2 puntos."),
    ("21", "Art. 21 - Ignorar a agente regulando tráfico, evadir control o ignorar escolta", "2,150 MXN y retirada de 2 puntos."),
    ("22", "Art. 22 - Uso de móvil, navegador o auriculares conduciendo", "400 MXN y retirada de 1 punto."),
    ("23", "Art. 23 - Circular por fuera de la calzada", "850 MXN y retirada de 2 puntos."),
    ("24", "Art. 24 - Uso indebido de elementos acústicos (claxon)", "380 MXN."),
    ("25", "Art. 25 - Huir de un accidente sin identificar o socorrer heridos", "4,700 MXN y disposición ante el ministerio público."),
    ("26", "Art. 26 - Causar accidente mayor", "8,000 MXN y retirada de licencia."),
    ("27", "Art. 27 - Circular sin matrícula o con matrícula ilegible", "4,000 MXN y depósito (1,000 MXN de grúa)."),
    ("28", "Art. 28 - Cruzar la calle indebidamente o pararse en el centro por un civil", "600 MXN."),
    ("29", "Art. 29 - Conflicto con agresión física o daños materiales", "2,500 MXN e ingreso inmediato en prisión temporal."),
    ("30", "Art. 30 - Agresión verbal o física", "Agresión verbal: 2,000 MXN / Agresión física: 2 años de prisión e indemnización de 2,000 a 6,000 MXN."),
    ("31", "Art. 31 - Funcionario que no lee derechos al detener", "Suspensión de 1 año y 5,000 MXN (incumplimiento de habeas corpus: 8,000 a 12,000 MXN)."),
    ("32", "Art. 32 - Alterar el orden público con actitudes o palabras", "1 mes de prisión."),
    ("33", "Art. 33 - Comercialización de productos no autorizados", "2,000 MXN y confiscación."),
    ("34", "Art. 34 - Inducción a la alteración pública", "5,000 MXN y 6 meses de prisión."),
    ("35", "Art. 35 - Inducir a realizar acciones ilegales ajenas a la voluntad", "2 años de prisión."),
    ("36", "Art. 36 - Pertenecer a grupo criminal", "2 años de prisión (trabajar o incentivar: 1 año de prisión)."),
    ("37", "Art. 37 - Agresión por color de piel, etnia o nacionalidad", "Sanción de 2 años e indemnización psicológica de 15,000 MXN."),
    ("38", "Art. 38 - Suplantación de identidad", "12,000 MXN y 1 año y 6 meses de prisión (+50% si es autoridad pública)."),
    ("39", "Art. 39 - Acoso reiterado con daños psicológicos", "6,000 MXN y 1 año de prisión."),
    ("40", "Art. 40 - Menoscabo psíquico o lesión leve a cónyuge, expareja o conviviente vulnerable", "5,000 MXN y 2 años de prisión."),
    ("41", "Art. 41 - Allanamiento de morada", "7,000 MXN y 6 meses de prisión temporal."),
    ("42", "Art. 42 - Usurpación", "20,000 MXN y 2 años de prisión."),
    ("43", "Art. 43 - Hurto", "15,000 MXN y 1 año de prisión."),
    ("44", "Art. 44 - Asalto con arma blanca", "10,000 MXN y 1 año y 6 meses de prisión."),
    ("45", "Art. 45 - Asalto con arma de fuego (robo agravado)", "20,000 MXN y 2 años de prisión."),
    ("46", "Art. 46 - Apropiación con fuerza o intimidación con daños", "16,000 MXN y 2 años de prisión."),
    ("47", "Art. 47 - Daños a propiedades del Estado", "25,000 MXN e indemnización obligatoria."),
    ("48", "Art. 48 - Posesión de una o más armas sin licencia o falsificada", "17,000 MXN y 1 año de prisión."),
    ("49", "Art. 49 - Utilizar armas sin licencia con motivo justificado", "25,000 MXN y 1 año y medio de prisión."),
    ("50", "Art. 50 - Comercio ilegal de armas de fuego", "30,000 MXN y 2 años de prisión."),
    ("51", "Art. 51 - Intento de homicidio con extremidades", "2 años de prisión."),
    ("52", "Art. 52 - Intento de homicidio a mano armada", "1 año y medio de prisión."),
    ("53", "Art. 53 - Homicidio con extremidades", "2 años y medio de prisión."),
    ("54", "Art. 54 - Homicidio con arma blanca o de fuego", "3 años de prisión."),
    ("55", "Art. 55 - Homicidio múltiple", "5 años de prisión o 3 años extra por cada víctima adicional."),
    ("56", "Art. 56 - Secuestro", "3 años de prisión."),
    ("57", "Art. 57 - Extorsión", "10,000 MXN y 2 años de prisión."),
    ("58", "Art. 58 - Amenazas", "7,000 MXN y 1 año de prisión (ayudantes: 5,000 MXN y 12 meses)."),
    ("59", "Art. 59 - Falsedad documental", "70,000 a 100,000 MXN y 2 años de prisión."),
    ("60", "Art. 60 - Indebida documentación", "10,000 MXN (conducir sin papeles del auto: 10,000 MXN + retiro y 20,000 MXN)."),
    ("61", "Art. 61 - Estafa", "12,000 MXN e indemnización de daños."),
    ("62", "Art. 62 - Desobedecer orden de autoridad", "20,000 MXN (incumplir resolución judicial: 48,000 MXN y 6 meses de prisión)."),
    ("63", "Art. 63 - Reporte falso a servicios de emergencia", "27,000 MXN y 4 meses de prisión temporal."),
    ("64", "Art. 64 - Invadir instalaciones restringidas", "14,000 MXN y 2 días de detención temporal ERLC."),
    ("65", "Art. 65 - Robo de objeto perteneciente al Estado", "50,000 MXN y 2 años de prisión."),
    ("66", "Art. 66 - Suplantación de identidad de miembro del Estado", "10,000 MXN extra a falsificación y 2 años de prisión."),
    ("67", "Art. 67 - Resistencia a la autoridad", "14,000 MXN."),
    ("68", "Art. 68 - Evasión a la autoridad", "9,600 MXN y 1 mes de prisión."),
    ("69", "Art. 69 - Soborno", "37,000 MXN y 3 años de prisión."),
    ("70", "Art. 70 - Terrorismo", "500,000 MXN y 15 años de prisión."),
    ("71", "Art. 71 - Atentar contra integridad de funcionario público o robar equipo", "2 años de prisión."),
    ("72", "Art. 72 - Dictar resolución arbitraria a sabiendas", "Inhabilitación permanente de cargo público."),
    ("73", "Art. 73 - Nombramiento ilegal a cargo público", "200,000 MXN e inhabilitación permanente."),
    ("74", "Art. 74 - Abandono de misión para no perseguir delitos", "Inhabilitación de cargo y empleo."),
    ("75", "Art. 75 - Dejar intencionadamente de promover persecución de delitos", "Inhabilitación permanente."),
    ("76", "Art. 76 - Calumniar o injuriar públicamente a una institución del Estado", "300,000 MXN y disculpa pública."),
    ("77", "Art. 77 - Negativa abierta de funcionario a cumplir resoluciones judiciales", "230,000 MXN e inhabilitación."),
    ("78", "Art. 78 - No comparecer ante la Suprema Corte u otra autoridad requerida", "90,000 MXN."),
    ("79", "Art. 79 - Sustraer, destruir u ocultar documentos bajo custodia", "50,000 MXN e inhabilitación."),
    ("80", "Art. 80 - Contaminar u obstruir cadena de custodia de evidencia", "155,000 MXN e inhabilitación."),
    ("81", "Art. 81 - Revelar secretos o información reservada de su oficio", "380,000 MXN e inhabilitación."),
    ("82", "Art. 82 - Cohecho (solicitar dádiva/favor para acto contrario a deberes)", "250,000 MXN, 3 años de prisión e inhabilitación."),
    ("83", "Art. 83 - Cohecho por acto propio del cargo", "190,000 MXN, 1 año de prisión e inhabilitación."),
    ("84", "Art. 84 - Recibir regalo u ofrenda en consideración a su cargo", "150,000 MXN."),
    ("85", "Art. 85 - Definición general de cohecho", "Definición de los artículos 82 a 83 como cohecho."),
    ("86", "Art. 86 - Tráfico de influencias", "360,000 MXN, 1 año de prisión e inhabilitación."),
    ("87", "Art. 87 - Malversación", "350,000 MXN y 4 años de prisión."),
    ("88", "Art. 88 - Concertación ilegal en contratación pública con ánimo de lucro", "Sanción por concierto ilegal con ánimo de lucro.")
]

MAPA_ARTICULOS = {num: (nombre, sancion) for num, nombre, sancion in CATALOGO_ARTICULOS}
CODIGO_PENAL_TEXTO = "\n".join(f"{nombre}: {sancion}" for _, nombre, sancion in CATALOGO_ARTICULOS)

MENSAJE_NO_VALIDO = "⚠️ Te has equivocado de mensaje o esa situación no existe en el Código Penal. Describe un delito o infracción válida."

def formatear_respuesta_estructurada(items: list[tuple[str, str]]) -> str:
    vistos = set()
    unicos = []
    for nombre, sancion in items:
        if nombre not in vistos:
            vistos.add(nombre)
            unicos.append((nombre, sancion))

    if not unicos:
        return MENSAJE_NO_VALIDO

    lista_art = "\n".join(f"• {nombre}" for nombre, _ in unicos)
    lista_conc = "\n".join(f"• {nombre}: {sancion}" for nombre, sancion in unicos)
    return (
        f"**Artículos aplicables:**\n{lista_art}\n\n"
        f"**Conclusión:**\nSanciones correspondientes aplicadas:\n{lista_conc}"
    )

def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s\.]", " ", sin_tildes)

def generar_variantes_evasion() -> list[str]:
    verbos = [
        "huir", "huida", "huyendo", "huido", "huirse", "me fui huyendo", "salir huyendo",
        "escapar", "escaparse", "escapando", "escapado", "escape", "me escape", "salir corriendo",
        "evadir", "evadirse", "evadiendo", "evadido", "evasion",
        "fugarse", "fuga", "fugando", "fugado", "fuega", "fuegarse", "fuegando",
        "correr", "corriendo", "pelarse", "pelarme", "abrirse", "abrirme",
        "darse a la fuga", "darme a la fuga", "salir por piernas", "tirarse a la fuga",
        "zafarse", "zafarme", "esquivar", "esquivando", "esquive",
        "salir volando", "pirarse", "pirarme", "largarse", "largarme"
    ]
    conectores = [
        "de", "del", "de la", "de las", "de los", "de lo",
        "a", "al", "a la", "a las", "a los", "a lo",
        "contra", "hacia", "ante"
    ]
    objetivos = [
        "policia", "policias", "policiaas", "policiaz", "policiaa",
        "poli", "polis", "poliz", "poliss",
        "elemento", "elementos", "los elementos", "lo elementos", "del elemento", "de los elementos", "de lo elementos",
        "autoridad", "autoridades", "la autoridad", "las autoridades",
        "arresto", "el arresto", "un arresto",
        "detencion", "la detencion", "una detencion",
        "justicia", "la justicia",
        "patrulla", "patrullas", "la patrulla", "las patrullas",
        "federal", "federales", "los federales", "lo federales",
        "sedena", "militar", "militares", "los militares",
        "guardia", "guardias", "la guardia",
        "agente", "agentes", "los agentes", "lo agentes",
        "funcionario", "funcionarios", "los funcionarios",
        "oficial", "oficiales", "los oficiales",
        "reten", "el reten", "control", "el control", "un control"
    ]

    variantes = set()
    for v, c, o in itertools.product(verbos, conectores, objetivos):
        variantes.add(f"{v} {c} {o}")

    directas = [
        "huir de lo polis", "huir de lo policiaas", "escapar de los elementos",
        "escapar de lo elementos", "escapar de la policia", "escapar de las policias",
        "huir de la policia", "huir de las policias", "huir de los polis",
        "escapar de los polis", "escapar de lo polis", "escapar de policiaas",
        "huir de policiaas", "huir de los elementos", "huir de lo elementos",
        "escapar de la autoridad", "evadir a la policia", "evadir a los polis",
        "evadir a los elementos", "evadir a lo polis", "evadir a lo elementos",
        "evadir el arresto", "evitar el arresto", "evitar arresto", "evitar la detencion",
        "darse a la fuga", "salir huyendo de la policia", "salir huyendo de los polis",
        "salir huyendo de los elementos", "escapar corriendo de la policia",
        "escapar corriendo de los polis", "escapar corriendo de los elementos",
        "me escape de la policia", "me escape de los polis", "me escape de los elementos",
        "me fui huyendo de la policia", "me fui huyendo de los polis",
        "me fui huyendo de los elementos", "huida de la policia", "huida de los polis",
        "huida de los elementos", "fuga de la policia", "fuga de los polis",
        "fuga de los elementos", "escapar de reten", "huir de reten",
        "escapar de un control", "huir de un control", "escapar del reten",
        "fuega ire escapar de la policia", "fuega irme escapar de la policia"
    ]
    for d in directas:
        variantes.add(normalizar_texto(d))

    return list(variantes)

VARIANTES_EVASION = generar_variantes_evasion()

REGLAS_LOCALES = [
    (["atenuante", "confesar", "cooperar", "complice"], "1.3"),
    (["agravante", "reincidente", "insultar", "discriminar"], "2"),
    (["conduccion temeraria", "manejo temerario", "zig zag"], "4"),
    (["dano a propiedad", "mobiliario urbano", "romper senal"], "5"),
    (["no cumplir semaforo", "pasarse semaforo", "pasarse un alto", "luz roja"], "6"),
    (["direccion contraria", "sentido contrario", "ir en contramano"], "7"),
    (["ebrio", "borracho", "alcoholizado", "conducir ebrio", "manejar ebrio", "bajo efectos del alcohol", "bajo efectos de drogas"], "8"),
    (["arma en vehiculo", "arma en el coche", "arma en el carro", "disparos al aire"], "9"),
    (["exceso de velocidad", "limite de velocidad", "ir a exceso de velocidad"], "10"),
    (["conducir sin licencia", "manejar sin licencia", "sin carnet", "sin carne"], "11"),
    (["carrera clandestina", "carreras ilegales", "correr carreras"], "12"),
    (["mal estacionado", "estacionado en zona prohibida"], "13"),
    (["obstruyendo la circulacion", "bloqueando la circulacion", "estacionado obstruyendo"], "14"),
    (["no ceder el paso", "ceder el paso a ambulancia", "ceder el paso a emergencia"], "15"),
    (["sin luces", "uso de luces"], "16"),
    (["faltas tecnicas", "fallas mecanicas", "vehiculo roto"], "17"),
    (["arrojar objetos", "tirar basura a la via"], "18"),
    (["adelantamiento indebido", "adelantamiento peligroso", "adelantar en curva"], "20"),
    (["ignorar agente", "ignorar escolta", "ignorar convoy"], "21"),
    (["usar el movil", "usar el celular", "auriculares conduciendo"], "22"),
    (["circular por la acera", "circular por el cesped", "fuera de la calzada"], "23"),
    (["uso indebido del claxon", "tocar el claxon sin motivo"], "24"),
    (["huir de un accidente", "huir del accidente", "fuga de accidente", "sin socorrer heridos"], "25"),
    (["causar accidente mayor", "accidente mayor"], "26"),
    (["sin matricula", "matricula ilegible", "sin placa"], "27"),
    (["cruzar indebidamente", "cruzar la calle indebidamente"], "28"),
    (["agresion verbal", "insultar a alguien"], "30"),
    (["agresion fisica", "golpear a alguien", "pegar a alguien"], "30"),
    (["no leer derechos", "no leyo derechos"], "31"),
    (["alterar el orden publico", "alteracion del orden publico"], "32"),
    (["productos no autorizados", "venta de productos ilegales"], "33"),
    (["grupo criminal", "organizacion criminal", "pertenece a un cartel", "pertenece a una banda"], "36"),
    (["discriminacion racial", "agresion por etnia", "agresion por nacionalidad"], "37"),
    (["suplantacion de identidad", "hacerse pasar por otra persona"], "38"),
    (["acoso reiterado", "acosar a alguien"], "39"),
    (["violencia domestica", "violencia familiar", "agredir a su pareja", "agredir a su conyuge"], "40"),
    (["allanamiento de morada", "entrar a propiedad privada sin permiso", "invadir propiedad privada"], "41"),
    (["usurpacion de inmueble", "usurpacion de derecho"], "42"),
    (["hurto", "robo sin violencia", "robar una tienda"], "43"),
    (["asalto con arma blanca", "robo con arma blanca", "amenazar con cuchillo", "amenazar con navaja"], "44"),
    (["asalto con arma de fuego", "robo con arma de fuego", "robo agravado", "atraco a mano armada"], "45"),
    (["robo con fuerza", "robo con intimidacion", "robo a banco"], "46"),
    (["danos a propiedad del estado", "danos a propiedades del estado", "destruir propiedad del estado"], "47"),
    (["arma sin licencia", "arma ilegal", "porte ilegal de arma", "posesion de arma sin licencia", "pistola sin licencia", "arma falsificada"], "48"),
    (["comercio ilegal de armas", "trafico de armas", "vender armas sin permiso", "comprar armas sin permiso"], "50"),
    (["intento de homicidio", "intento de asesinato", "intento de matar"], "52"),
    (["homicidio", "asesinato", "matar a alguien", "homicidio multiple", "masacre"], "54"),
    (["secuestro", "secuestrar", "privacion ilegal de la libertad", "privacion de libertad", "raptar", "rapto"], "56"),
    (["extorsion", "extorsionar", "chantaje", "chantajear"], "57"),
    (["amenaza", "amenazar", "amenazas"], "58"),
    (["falsedad documental", "documento falso", "falsificar documento", "documentos falsos"], "59"),
    (["sin identificacion", "sin papeles", "indebida documentacion", "sin documentos del auto"], "60"),
    (["estafa", "estafar", "fraude", "enganar con lucro"], "61"),
    (["desobedecer orden", "desobediencia a la autoridad", "incumplir resolucion judicial"], "62"),
    (["reporte falso", "llamada falsa a emergencias"], "63"),
    (["zona restringida", "instalaciones restringidas", "invadir base militar"], "64"),
    (["robo de objeto del estado", "robar patrulla", "robar equipo del estado"], "65"),
    (["suplantar funcionario", "suplantar autoridad", "falso policia", "falso militar"], "66"),
    (["resistencia a la autoridad", "resistirse al arresto", "impedir detencion"], "67"),
    (VARIANTES_EVASION, "68"),
    (["soborno", "sobornar", "ofrecer dinero a funcionario"], "69"),
    (["terrorismo", "atentado terrorista", "poner una bomba"], "70"),
    (["atentar contra funcionario", "herir a un policia", "disparar a un policia", "robar equipo policial"], "71"),
    (["resolucion arbitraria", "prevaricacion"], "72"),
    (["nombramiento ilegal"], "73"),
    (["abandono de mision", "abandonar el servicio"], "74"),
    (["calumnia a institucion", "injuria a institucion"], "76"),
    (["ocultar documentos bajo custodia", "destruir documentos bajo custodia"], "79"),
    (["cadena de custodia", "contaminar evidencia"], "80"),
    (["revelacion de secretos", "filtrar informacion reservada"], "81"),
    (["cohecho", "pedir mordida", "pedir dadiva"], "82"),
    (["regalo por el cargo", "ofrenda por el cargo"], "84"),
    (["trafico de influencias"], "86"),
    (["malversacion", "desviar fondos publicos", "robar dinero publico"], "87"),
    (["concertacion ilegal en contratacion publica"], "88")
]

def extraer_numeros_articulo(situacion: str) -> list[str]:
    s_low = normalizar_texto(situacion)
    if not s_low:
        return []
    # Detecta si el usuario pide artículos por número ("son estos articulos 1, 2, 6", "los articulos son ...", "art 6", "1, 2, 6")
    es_consulta_lista = bool(
        re.search(r"\b(?:son estos articulos|los articulos son|articulos?|art\.?)\b", s_low)
        or re.search(r"^\s*[\d\.\s,]+$", situacion.strip())
    )
    if not es_consulta_lista:
        return []

    candidatos = re.findall(r"\b\d+(?:\.\d+)?\b", situacion)
    validos = []
    vistos = set()
    for c in candidatos:
        if c in MAPA_ARTICULOS and c not in vistos:
            vistos.add(c)
            validos.append(c)
    return validos

def motor_local_rapido(situacion: str) -> str:
    if not situacion or len(situacion.strip()) < 2:
        return MENSAJE_NO_VALIDO

    nums_art = extraer_numeros_articulo(situacion)
    if nums_art:
        items = [MAPA_ARTICULOS[n] for n in nums_art]
        return formatear_respuesta_estructurada(items)

    s = normalizar_texto(situacion)
    items = []
    for palabras_clave, num_art in REGLAS_LOCALES:
        for k in palabras_clave:
            k_norm = normalizar_texto(k)
            if not k_norm:
                continue
            patron = r"(?:^|\s)" + re.escape(k_norm) + r"(?:$|\s)"
            if re.search(patron, s):
                if num_art == "54" and "intento de homicidio" in s and s.count("homicidio") == 1:
                    continue
                if num_art in MAPA_ARTICULOS:
                    items.append(MAPA_ARTICULOS[num_art])
                break

    if not items:
        return MENSAJE_NO_VALIDO

    return formatear_respuesta_estructurada(items)

def obtener_respuesta_ia(situacion: str) -> str:
    if not situacion or len(situacion.strip()) < 2:
        return MENSAJE_NO_VALIDO

    # Si el usuario pasa números de artículos explícitamente, garantizamos el formato exacto y completo
    nums_art = extraer_numeros_articulo(situacion)
    if nums_art:
        return formatear_respuesta_estructurada([MAPA_ARTICULOS[n] for n in nums_art])

    if not groq_client:
        return motor_local_rapido(situacion)

    system_prompt = (
        "Eres un juez y experto legal del Código Penal Federal para un servidor de roleplay.\n"
        "REGLAS ESTRICTAS:\n"
        "1. Si el mensaje NO tiene sentido legal, es una pregunta cotidiana o fuera de tema (por ejemplo: '¿cuál es el tiempo de hoy?', 'hola', 'qué tal', 'cuánto es 2+2', bromas sin delito o texto incoherente), responde ÚNICAMENTE con esta frase exacta:\n"
        f"{MENSAJE_NO_VALIDO}\n"
        "2. Si SÍ describe una situación o delito, interpreta su intención real aunque tenga faltas graves de ortografía, abreviaturas o jerga (ej. 'polis', 'elementos', 'fuega', 'fierro', 'plomear', 'darse a la fuga') y extrae TODOS los artículos aplicables.\n"
        "3. En **Artículos aplicables:** pon ÚNICAMENTE el número y nombre del artículo (sin dinero, multas, puntos ni prisión).\n"
        "4. En **Conclusión:** pon SIEMPRE el encabezado 'Sanciones correspondientes aplicadas:' y el detalle de cada artículo con su sanción.\n"
        "5. NUNCA uses el Art. 1 como relleno o respuesta por defecto.\n\n"
        f"{CODIGO_PENAL_TEXTO}\n\n"
        "FORMATO OBLIGATORIO:\n"
        "**Artículos aplicables:**\n"
        "• Art. XX - Nombre del artículo\n\n"
        "**Conclusión:**\n"
        "Sanciones correspondientes aplicadas:\n"
        "• Art. XX - Nombre del artículo: [Multa y/o Prisión]"
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'SITUACIÓN A ANALIZAR: "{situacion}"'}
            ],
            temperature=0.1,
            max_tokens=3500,
        )
        res = completion.choices[0].message.content
        if res and res.strip():
            texto_limpio = res.strip()
            if texto_limpio == MENSAJE_NO_VALIDO:
                return texto_limpio
            if "**Conclusión:**" not in texto_limpio:
                return motor_local_rapido(situacion)
            return texto_limpio
    except Exception as e:
        print(f"ERROR GROQ: {e}")

    return motor_local_rapido(situacion)

# ==========================================
# 4. CONFIGURACIÓN DEL CLIENTE Y COMANDOS
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

class BotClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents, status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="el Código Penal Federal"))
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Comandos slash sincronizados correctamente.")

client = BotClient()

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="el Código Penal Federal"))
    print(f"Bot conectado exitosamente y en línea con luz verde como {client.user}")

@client.tree.command(
    name="codigo-penal",
    description="Analiza una situación y busca los artículos y sanciones.",
)
@app_commands.describe(
    situacion="Describe detalladamente los hechos ocurridos."
)
async def codigo_penal(interaction: discord.Interaction, situacion: str):
    await interaction.response.defer(thinking=True, ephemeral=False)
    try:
        resultado = await asyncio.to_thread(obtener_respuesta_ia, situacion)
        embed = discord.Embed(description=resultado.strip()[:4090], color=0xFFFFFF)
        await interaction.followup.send(embed=embed, ephemeral=False)
    except Exception as e:
        await interaction.followup.send(f"❌ Error al procesar: `{str(e)}`", ephemeral=False)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!codigo"):
        situacion = message.content[len("!codigo"):].strip()
        if not situacion:
            await message.channel.send("⚠️ Escribe una situación. Ej: `!codigo exceso de velocidad`")
            return

        msg_proceso = await message.channel.send("🔍 Analizando situación...")
        try:
            resultado = await asyncio.to_thread(obtener_respuesta_ia, situacion)
            embed = discord.Embed(description=resultado.strip()[:4090], color=0xFFFFFF)
            await msg_proceso.edit(content=None, embed=embed)
        except Exception as e:
            await msg_proceso.edit(content=f"❌ Error al procesar: `{str(e)}`")
        return

# ==========================================
# 5. INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    keep_alive()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN.strip())
    else:
        print("ERROR: No se encontró la variable DISCORD_TOKEN.")
