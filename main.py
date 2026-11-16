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

# TEXTO COMPLETO Y OFICIAL DE LOS ARTÍCULOS (1 AL 88)
CODIGO_PENAL_TEXTO = "\n".join([
    "CÓDIGO PENAL FEDERAL",
    "",
    "Título I - De los delitos",
    "Art 1: Disposición General del Código Penal (aplicable en toda la República Mexicana para delitos de Fuero Común y Federal; es delito toda acción u omisión voluntaria penada por la ley).",
    "Art 1.1: Secreto profesional del abogado (sin obligación de denunciar el presunto delito conferido por su cliente en servicios jurídico-legales).",
    "Art 1.2: Obligatoriedad territorial y mar territorial (obligatoria para todos los habitantes de la República, incluidos extranjeros).",
    "Art 1.3: Circunstancias atenuantes (obedecer indicaciones de funcionario sin oposición, reparar daño, ser cómplice, confesar, o discapacidad/trastorno mental demostrable).",
    "Art 2: Circunstancias agravantes (+11 meses de prisión federal o 5,000 MXN; insultar repetidamente a funcionario, reincidencia, o discriminación).",
    "Art 3: Equivalencia de plazos de cárcel (24 meses = 1 día 12h; 18 meses = 1 día 6h; 12 meses = 22h; 9 meses = 12h 30m; 6 meses = 9h; 3 meses = 5h 30m; 1 mes = 2h 30m).",
    "",
    "Título II - De las leyes de circulación",
    "Art 4: Conducción temeraria (2,000 MXN y/o pérdida de 3 puntos).",
    "Art 4.1: Sistema de puntaje de licencia (máximo 10 puntos; a 0 puntos retirada de 6 a 12 meses).",
    "Art 5: Daño a propiedad privada o pública con vehículo (2,500 MXN y reparación total).",
    "Art 6: No cumplir semáforos (500 MXN por cada semáforo ignorado).",
    "Art 7: Conducir en dirección contraria (3,000 MXN y/o pérdida de 1 punto).",
    "Art 8: Conducir bajo efectos de alcohol o sustancias ilegales (2,500 MXN y/o pérdida de 6 puntos).",
    "Art 9: Posesión de arma no autorizada en vehículo (Art. 48 + 4,000 MXN e incautación temporal del vehículo).",
    "Art 10: Incumplir límites de velocidad (1,500 MXN y retirada de 2 puntos).",
    "Art 11: Conducir sin licencia (4,000 MXN e ingreso a prisión preventiva de 24h).",
    "Art 12: Carreras clandestinas sin permiso (6,500 MXN, suspensión de licencia y 1 mes de prisión).",
    "Art 13: Mal estacionado en zona prohibida (750 MXN o depósito; 1,000 MXN extra por grúa).",
    "Art 14: Estacionado obstruyendo la circulación vial (1,800 MXN o depósito; 2,000 MXN por grúa).",
    "Art 15: No ceder el paso a servicios de emergencia (1,500 MXN y retirada de licencia por 1 mes).",
    "Art 16: Uso de luces obligatorio entre ocaso y amanecer (500 MXN).",
    "Art 17: Vehículo con faltas técnicas y/o mecánicas (900 MXN y retirada de 2 puntos).",
    "Art 18: Arrojar objetos a la vía o inmediaciones (500 MXN).",
    "Art 19: Incumplimiento general de normas de tráfico (500 MXN y retirada de 1 punto).",
    "Art 20: Adelantamientos erróneos o peligrosos (1,200 MXN y retirada de 2 puntos).",
    "Art 21: Ignorar a agente regulando tráfico, evadir control policial/militar o ignorar escolta (2,150 MXN y retirada de 2 puntos).",
    "Art 22: Uso de móvil, navegador o auriculares conduciendo sin estar estacionado (400 MXN y retirada de 1 punto).",
    "Art 23: Circular por fuera de la calzada (850 MXN y retirada de 2 puntos).",
    "Art 24: Uso indebido de elementos acústicos / claxon (380 MXN).",
    "Art 25: Huir de un accidente sin identificar o socorrer heridos (4,700 MXN y disposición ante el ministerio público).",
    "Art 26: Causar accidente mayor (8,000 MXN y retirada de licencia).",
    "Art 27: Circular sin matrícula o con matrícula ilegible (4,000 MXN y depósito; 1,000 MXN de grúa).",
    "Art 28: Cruzar la calle indebidamente o pararse en el centro por un civil (600 MXN).",
    "",
    "Título II (Sección 2) - De las agresiones, los disturbios y las conductas erróneas",
    "Art 29: Conflicto con agresión física o daños materiales (2,500 MXN e ingreso inmediato en prisión temporal).",
    "Art 30: Agresión verbal o física (verbal: 2,000 MXN; física: 2 años de prisión e indemnización de 2,000 a 6,000 MXN).",
    "Art 31: Funcionario que no lee derechos al detener (suspensión de 1 año y 5,000 MXN; habeas corpus: 8,000 a 12,000 MXN).",
    "Art 32: Alterar el orden público con actitudes o palabras (1 mes de prisión).",
    "Art 33: Comercialización de productos no autorizados (2,000 MXN y confiscación).",
    "Art 34: Inducción a la alteración pública (5,000 MXN y 6 meses de prisión).",
    "Art 35: Inducir a realizar acciones ilegales ajenas a la voluntad (2 años de prisión).",
    "Art 36: Pertenecer a grupo criminal (2 años de prisión; trabajar o incentivar: 1 año de prisión).",
    "Art 37: Agresión por color de piel, etnia o nacionalidad (sanción de 2 años e indemnización de 15,000 MXN).",
    "Art 38: Suplantación de identidad (12,000 MXN y 1 año y 6 meses de prisión).",
    "Art 39: Acoso reiterado con daños psicológicos (6,000 MXN y 1 año de prisión).",
    "Art 40: Menoscabo psíquico o lesión leve a cónyuge, expareja o persona vulnerable conviviente (5,000 MXN y 2 años de prisión).",
    "",
    "Título III - De los hurtos y los asaltos",
    "Art 41: Allanamiento de morada (7,000 MXN y 6 meses de prisión temporal).",
    "Art 42: Usurpación (20,000 MXN y 2 años de prisión).",
    "Art 43: Hurto (15,000 MXN y 1 año de prisión).",
    "Art 44: Asalto con arma blanca (10,000 MXN y 1 año y 6 meses de prisión).",
    "Art 45: Asalto con arma de fuego / robo agravado (20,000 MXN y 2 años de prisión).",
    "Art 46: Apropiación con fuerza o intimidación con daños (16,000 MXN y 2 años de prisión).",
    "Art 47: Daños a propiedades del Estado (25,000 MXN e indemnización obligatoria).",
    "",
    "Título IV - De las armas de fuego y su porte",
    "Art 48: Posesión de una o más armas sin licencia o falsificada (17,000 MXN y 1 año de prisión).",
    "Art 49: Utilizar armas sin licencia con motivo justificado (25,000 MXN y 1 año y medio de prisión).",
    "Art 50: Comercio ilegal de armas de fuego (30,000 MXN y 2 años de prisión).",
    "",
    "Título V - De los homicidios, secuestros y extorsiones",
    "Art 51: Intento de homicidio con extremidades (2 años de prisión).",
    "Art 52: Intento de homicidio a mano armada (1 año y medio de prisión).",
    "Art 53: Homicidio con extremidades (2 años y medio de prisión).",
    "Art 54: Homicidio con arma blanca o de fuego (3 años de prisión).",
    "Art 55: Homicidio múltiple (5 años de prisión o 3 años extra por víctima adicional).",
    "Art 56: Secuestro (3 años de prisión).",
    "Art 57: Extorsión (10,000 MXN y 2 años de prisión).",
    "Art 58: Amenazas (7,000 MXN y 1 año de prisión; ayudantes: 5,000 MXN y 12 meses).",
    "",
    "Título VI - De los delitos de documentos y licencias",
    "Art 59: Falsedad documental (70,000 a 100,000 MXN y 2 años de prisión).",
    "Art 60: Indebida documentación (10,000 MXN; auto sin papeles: 10,000 MXN + retiro y 20,000 MXN).",
    "Art 61: Estafa (12,000 MXN e indemnización de daños).",
    "",
    "Título VII - De los delitos contra el Estado",
    "Art 62: Desobedecer orden de autoridad (20,000 MXN; resolución judicial: 48,000 MXN y 6 meses de prisión).",
    "Art 63: Reporte falso a servicios de emergencia (27,000 MXN y 4 meses de prisión temporal).",
    "Art 64: Invadir instalaciones restringidas (14,000 MXN y 2 días de detención temporal ERLC).",
    "Art 65: Robo de objeto perteneciente al Estado (50,000 MXN y 2 años de prisión).",
    "Art 66: Suplantación de identidad de miembro del Estado (10,000 MXN extra a falsificación y 2 años de prisión).",
    "Art 67: Resistencia a la autoridad (14,000 MXN).",
    "Art 68: Evasión a la autoridad (9,600 MXN y 1 mes de prisión).",
    "Art 69: Soborno (37,000 MXN y 3 años de prisión).",
    "Art 70: Terrorismo (500,000 MXN y 15 años de prisión).",
    "Art 71: Atentar contra integridad de funcionario público o robar equipo policial/militar (2 años de prisión).",
    "Art 72: Funcionario que dicta resolución arbitraria a sabiendas (inhabilitación permanente de cargo público).",
    "Art 73: Funcionario que nombra ilegalmente a un cargo público (200,000 MXN e inhabilitación permanente).",
    "Art 74: Funcionario que abandona su misión para no perseguir delitos (inhabilitación de cargo y empleo).",
    "Art 75: Funcionario que intencionadamente deja de promover la persecución de delitos (inhabilitación permanente).",
    "Art 76: Funcionario que calumnie o injurie a una institución del Estado (300,000 MXN y disculpa pública).",
    "Art 77: Negativa abierta de funcionario a cumplir resoluciones judiciales (230,000 MXN e inhabilitación).",
    "Art 78: Funcionario que no comparece ante la Suprema Corte u otra autoridad requerida (90,000 MXN).",
    "Art 79: Funcionario que sustrae, destruye u oculta documentos bajo su custodia (50,000 MXN e inhabilitación).",
    "Art 80: Contaminar u obstruir cadena de custodia de evidencia (155,000 MXN e inhabilitación).",
    "Art 81: Funcionario que revela secretos o información reservada de su oficio (380,000 MXN e inhabilitación).",
    "Art 82: Cohecho (250,000 MXN, 3 años de prisión e inhabilitación).",
    "Art 83: Cohecho por acto propio del cargo (190,000 MXN, 1 año de prisión e inhabilitación).",
    "Art 84: Recibir regalo u ofrenda en consideración a su cargo (150,000 MXN).",
    "Art 85: Definición general de los artículos 82 a 83 como cohecho.",
    "Art 86: Tráfico de influencias (360,000 MXN, 1 año de prisión e inhabilitación).",
    "Art 87: Malversación (350,000 MXN y 4 años de prisión).",
    "Art 88: Concertación ilegal en contratación pública con ánimo de lucro."
])

MENSAJE_NO_VALIDO = "⚠️ Te has equivocado de mensaje o esa situación no existe en el Código Penal. Describe un delito o infracción válida."

def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s\.]", " ", sin_tildes)

def generar_variantes_evasion() -> list[str]:
    """Genera miles de combinaciones de huida/escape de policías, polis, elementos y autoridades."""
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

# ==========================================
# 3. MOTOR LOCAL DE RESPALDO INFALIBLE
# ==========================================
REGLAS_LOCALES = [
    (["atenuante", "confesar", "cooperar", "complice"], "Art. 1.3 - Circunstancias atenuantes", "Disminución de gravedad/pena según criterio judicial."),
    (["agravante", "reincidente", "insultar", "discriminar"], "Art. 2 - Circunstancias agravantes", "+11 meses de prisión federal o 5,000 MXN."),
    (["conduccion temeraria", "manejo temerario", "zig zag"], "Art. 4 - Conducción temeraria", "2,000 MXN y/o pérdida de 3 puntos."),
    (["dano a propiedad", "mobiliario urbano", "romper senal"], "Art. 5 - Daño a propiedad privada o pública con vehículo", "2,500 MXN y reparación total."),
    (["no cumplir semaforo", "pasarse semaforo", "pasarse un alto", "luz roja"], "Art. 6 - No cumplir semáforos", "500 MXN por cada semáforo ignorado."),
    (["direccion contraria", "sentido contrario", "ir en contramano"], "Art. 7 - Conducir en dirección contraria", "3,000 MXN y/o pérdida de 1 punto."),
    (["ebrio", "borracho", "alcoholizado", "conducir ebrio", "manejar ebrio", "bajo efectos del alcohol", "bajo efectos de drogas"], "Art. 8 - Conducir bajo efectos de alcohol o sustancias", "2,500 MXN y/o pérdida de 6 puntos."),
    (["arma en vehiculo", "arma en el coche", "arma en el carro", "disparos al aire"], "Art. 9 - Posesión de arma no autorizada en vehículo", "Art. 48 + 4,000 MXN e incautación temporal del vehículo."),
    (["exceso de velocidad", "limite de velocidad", "ir a exceso de velocidad"], "Art. 10 - Incumplir límites de velocidad", "1,500 MXN y retirada de 2 puntos."),
    (["conducir sin licencia", "manejar sin licencia", "sin carnet", "sin carne"], "Art. 11 - Conducir sin licencia", "4,000 MXN e ingreso a prisión preventiva de 24h."),
    (["carrera clandestina", "carreras ilegales", "correr carreras"], "Art. 12 - Carreras clandestinas", "6,500 MXN, suspensión de licencia y 1 mes de prisión."),
    (["mal estacionado", "estacionado en zona prohibida"], "Art. 13 - Mal estacionado", "750 MXN o traslado al depósito (1,000 MXN grúa)."),
    (["obstruyendo la circulacion", "bloqueando la circulacion", "estacionado obstruyendo"], "Art. 14 - Estacionado obstruyendo circulación vial", "1,800 MXN o depósito (2,000 MXN grúa)."),
    (["no ceder el paso", "ceder el paso a ambulancia", "ceder el paso a emergencia"], "Art. 15 - No ceder el paso a servicios de emergencia", "1,500 MXN y retirada de licencia por 1 mes."),
    (["sin luces", "uso de luces"], "Art. 16 - Uso de luces obligatorio", "500 MXN."),
    (["faltas tecnicas", "fallas mecanicas", "vehiculo roto"], "Art. 17 - Vehículo con faltas técnicas/mecánicas", "900 MXN y retirada de 2 puntos."),
    (["arrojar objetos", "tirar basura a la via"], "Art. 18 - Arrojar objetos a la vía", "500 MXN."),
    (["adelantamiento indebido", "adelantamiento peligroso", "adelantar en curva"], "Art. 20 - Adelantamientos erróneos o peligrosos", "1,200 MXN y retirada de 2 puntos."),
    (["ignorar agente", "ignorar escolta", "ignorar convoy"], "Art. 21 - Ignorar agente o evadir control", "2,150 MXN y retirada de 2 puntos."),
    (["usar el movil", "usar el celular", "auriculares conduciendo"], "Art. 22 - Uso de móvil o auriculares conduciendo", "400 MXN y retirada de 1 punto."),
    (["circular por la acera", "circular por el cesped", "fuera de la calzada"], "Art. 23 - Circular por fuera de la calzada", "850 MXN y retirada de 2 puntos."),
    (["uso indebido del claxon", "tocar el claxon sin motivo"], "Art. 24 - Uso indebido de claxon", "380 MXN."),
    (["huir de un accidente", "huir del accidente", "fuga de accidente", "sin socorrer heridos"], "Art. 25 - Huir de un accidente sin socorrer", "4,700 MXN y disposición ante ministerio público."),
    (["causar accidente mayor", "accidente mayor"], "Art. 26 - Causar accidente mayor", "8,000 MXN y retirada de licencia."),
    (["sin matricula", "matricula ilegible", "sin placa"], "Art. 27 - Circular sin matrícula", "4,000 MXN y depósito (1,000 MXN grúa)."),
    (["cruzar indebidamente", "cruzar la calle indebidamente"], "Art. 28 - Cruzar la calle indebidamente", "600 MXN."),
    (["agresion verbal", "insultar a alguien"], "Art. 30 - Agresión verbal", "2,000 MXN."),
    (["agresion fisica", "golpear a alguien", "pegar a alguien"], "Art. 30 - Agresión física", "2 años de prisión e indemnización de 2,000 a 6,000 MXN."),
    (["no leer derechos", "no leyo derechos"], "Art. 31 - Funcionario que no lee derechos al detener", "Suspensión de 1 año y 5,000 MXN."),
    (["alterar el orden publico", "alteracion del orden publico"], "Art. 32 - Alterar el orden público", "1 mes de prisión."),
    (["productos no autorizados", "venta de productos ilegales"], "Art. 33 - Comercialización de productos no autorizados", "2,000 MXN y confiscación."),
    (["grupo criminal", "organizacion criminal", "pertenece a un cartel", "pertenece a una banda"], "Art. 36 - Pertenecer a grupo criminal", "2 años de prisión (1 año por trabajar/incentivar)."),
    (["discriminacion racial", "agresion por etnia", "agresion por nacionalidad"], "Art. 37 - Agresión por discriminación", "Multa/sanción de 2 años e indemnización de 15,000 MXN."),
    (["suplantacion de identidad", "hacerse pasar por otra persona"], "Art. 38 - Suplantación de identidad", "12,000 MXN y 1 año y 6 meses de prisión."),
    (["acoso reiterado", "acosar a alguien"], "Art. 39 - Acoso reiterado", "6,000 MXN y 1 año de prisión."),
    (["violencia domestica", "violencia familiar", "agredir a su pareja", "agredir a su conyuge"], "Art. 40 - Menoscabo o lesión a cónyuge/pareja", "5,000 MXN y 2 años de prisión."),
    (["allanamiento de morada", "entrar a propiedad privada sin permiso", "invadir propiedad privada"], "Art. 41 - Allanamiento de morada", "7,000 MXN y 6 meses de prisión temporal."),
    (["usurpacion de inmueble", "usurpacion de derecho"], "Art. 42 - Usurpación", "20,000 MXN y 2 años de prisión."),
    (["hurto", "robo sin violencia", "robar una tienda"], "Art. 43 - Hurto", "15,000 MXN y 1 año de prisión."),
    (["asalto con arma blanca", "robo con arma blanca", "amenazar con cuchillo", "amenazar con navaja"], "Art. 44 - Asalto con arma blanca", "10,000 MXN y 1 año y 6 meses de prisión."),
    (["asalto con arma de fuego", "robo con arma de fuego", "robo agravado", "atraco a mano armada"], "Art. 45 - Asalto con arma de fuego", "20,000 MXN y 2 años de prisión."),
    (["robo con fuerza", "robo con intimidacion", "robo a banco"], "Art. 46 - Apropiación con fuerza o intimidación", "16,000 MXN y 2 años de prisión."),
    (["danos a propiedad del estado", "danos a propiedades del estado", "destruir propiedad del estado"], "Art. 47 - Daños a propiedades del Estado", "25,000 MXN e indemnización obligatoria."),
    (["arma sin licencia", "arma ilegal", "porte ilegal de arma", "posesion de arma sin licencia", "pistola sin licencia", "arma falsificada"], "Art. 48 - Posesión de arma sin licencia", "17,000 MXN y 1 año de prisión."),
    (["comercio ilegal de armas", "trafico de armas", "vender armas sin permiso", "comprar armas sin permiso"], "Art. 50 - Comercio ilegal de armas de fuego", "30,000 MXN y 2 años de prisión."),
    (["intento de homicidio", "intento de asesinato", "intento de matar"], "Art. 51/52 - Intento de homicidio", "2 años de prisión (extremidades) / 1 año y medio (mano armada)."),
    (["homicidio", "asesinato", "matar a alguien", "homicidio multiple", "masacre"], "Art. 54 - Homicidio", "3 años de prisión (2 años y medio si es con extremidades)."),
    (["secuestro", "secuestrar", "privacion ilegal de la libertad", "privacion de libertad", "raptar", "rapto"], "Art. 56 - Secuestro", "3 años de prisión."),
    (["extorsion", "extorsionar", "chantaje", "chantajear"], "Art. 57 - Extorsión", "10,000 MXN y 2 años de prisión."),
    (["amenaza", "amenazar", "amenazas"], "Art. 58 - Amenazas", "7,000 MXN y 1 año de prisión."),
    (["falsedad documental", "documento falso", "falsificar documento", "documentos falsos"], "Art. 59 - Falsedad documental", "70,000 a 100,000 MXN y 2 años de prisión."),
    (["sin identificacion", "sin papeles", "indebida documentacion", "sin documentos del auto"], "Art. 60 - Indebida documentación", "10,000 MXN (+20,000 MXN y retiro si es auto)."),
    (["estafa", "estafar", "fraude", "enganar con lucro"], "Art. 61 - Estafa", "12,000 MXN e indemnización de daños."),
    (["desobedecer orden", "desobediencia a la autoridad", "incumplir resolucion judicial"], "Art. 62 - Desobedecer orden de autoridad", "20,000 MXN (48,000 MXN y 6 meses si es resolución judicial)."),
    (["reporte falso", "llamada falsa a emergencias"], "Art. 63 - Reporte falso a servicios de emergencia", "27,000 MXN y 4 meses de prisión temporal."),
    (["zona restringida", "instalaciones restringidas", "invadir base militar"], "Art. 64 - Invadir instalaciones restringidas", "14,000 MXN y 2 días de detención temporal ERLC."),
    (["robo de objeto del estado", "robar patrulla", "robar equipo del estado"], "Art. 65 - Robo de objeto perteneciente al Estado", "50,000 MXN y 2 años de prisión."),
    (["suplantar funcionario", "suplantar autoridad", "falso policia", "falso militar"], "Art. 66 - Suplantación de identidad de miembro del Estado", "10,000 MXN extra a falsificación y 2 años de prisión."),
    (["resistencia a la autoridad", "resistirse al arresto", "impedir detencion"], "Art. 67 - Resistencia a la autoridad", "14,000 MXN."),
    (VARIANTES_EVASION, "Art. 68 - Evasión a la autoridad", "9,600 MXN y 1 mes de prisión."),
    (["soborno", "sobornar", "ofrecer dinero a funcionario"], "Art. 69 - Soborno", "37,000 MXN y 3 años de prisión."),
    (["terrorismo", "atentado terrorista", "poner una bomba"], "Art. 70 - Terrorismo", "500,000 MXN y 15 años de prisión."),
    (["atentar contra funcionario", "herir a un policia", "disparar a un policia", "robar equipo policial"], "Art. 71 - Atentar contra integridad de funcionario público o robar equipo", "2 años de prisión."),
    (["resolucion arbitraria", "prevaricacion"], "Art. 72 - Dictar resolución arbitraria", "Inhabilitación permanente de cargo público."),
    (["nombramiento ilegal"], "Art. 73 - Nombramiento ilegal a cargo público", "200,000 MXN e inhabilitación permanente."),
    (["abandono de mision", "abandonar el servicio"], "Art. 74 - Abandono de misión para no perseguir delitos", "Inhabilitación de cargo y empleo."),
    (["calumnia a institucion", "injuria a institucion"], "Art. 76 - Calumniar o injuriar institución del Estado", "300,000 MXN y disculpa pública."),
    (["ocultar documentos bajo custodia", "destruir documentos bajo custodia"], "Art. 79 - Sustraer, destruir u ocultar documentos bajo custodia", "50,000 MXN e inhabilitación."),
    (["cadena de custodia", "contaminar evidencia"], "Art. 80 - Contaminar u obstruir cadena de custodia", "155,000 MXN e inhabilitación."),
    (["revelacion de secretos", "filtrar informacion reservada"], "Art. 81 - Revelación de secretos oficiales", "380,000 MXN e inhabilitación."),
    (["cohecho", "pedir mordida", "pedir dadiva"], "Art. 82/83 - Cohecho", "250,000 MXN, 3 años de prisión e inhabilitación."),
    (["regalo por el cargo", "ofrenda por el cargo"], "Art. 84 - Recibir regalo en consideración a su cargo", "150,000 MXN."),
    (["trafico de influencias"], "Art. 86 - Tráfico de influencias", "360,000 MXN, 1 año de prisión e inhabilitación."),
    (["malversacion", "desviar fondos publicos", "robar dinero publico"], "Art. 87 - Malversación", "350,000 MXN y 4 años de prisión."),
    (["concertacion ilegal en contratacion publica"], "Art. 88 - Concertación ilegal en contratación pública", "Sanción por concierto ilegal con ánimo de lucro.")
]

def motor_local_rapido(situacion):
    s = normalizar_texto(situacion)
    if not s or len(s.strip()) < 2:
        return MENSAJE_NO_VALIDO

    numeros_detectados = re.findall(r"\b\d+(?:\.\d+)?\b", s)
    if numeros_detectados and (
        any(p in s for p in ["art", "articulo", "los articulos", ","])
        or len(s.split()) <= 4
    ):
        lineas_codigo = CODIGO_PENAL_TEXTO.splitlines()
        encontrados = []
        vistos_num = set()
        for num in numeros_detectados:
            if num in vistos_num:
                continue
            vistos_num.add(num)
            for linea in lineas_codigo:
                low = linea.lower()
                if low.startswith(f"art. {num}:") or low.startswith(f"art {num}:"):
                    encontrados.append(linea)
                    break
        if encontrados:
            lista_art = []
            lista_conc = []
            for linea in encontrados:
                cuerpo = linea.split(":", 1)[1].strip() if ":" in linea else linea
                if "(" in cuerpo and cuerpo.endswith(")"):
                    nombre = cuerpo[:cuerpo.rfind("(")].strip()
                    sancion = cuerpo[cuerpo.rfind("(")+1:-1].strip()
                else:
                    nombre = cuerpo
                    sancion = "Sin sanción monetaria o de prisión especificada."
                num_art = linea.split(":", 1)[0].strip()
                lista_art.append(f"• {num_art} - {nombre}")
                lista_conc.append(f"• {num_art} - {nombre}: {sancion}")
            return (
                "**Artículos aplicables:**\n"
                + "\n".join(lista_art)
                + "\n\n**Conclusión:**\nSanciones correspondientes aplicadas:\n"
                + "\n".join(lista_conc)
            )

    articulos = []
    for palabras_clave, titulo, sancion in REGLAS_LOCALES:
        for k in palabras_clave:
            k_norm = normalizar_texto(k)
            if not k_norm:
                continue
            patron = r"(?:^|\s)" + re.escape(k_norm) + r"(?:$|\s)"
            if re.search(patron, s):
                if titulo.startswith("Art. 54") and "intento de homicidio" in s and s.count("homicidio") == 1:
                    continue
                articulos.append((titulo, sancion))
                break

    if not articulos:
        return MENSAJE_NO_VALIDO

    vistos = set()
    articulos_unicos = []
    for item in articulos:
        if item[0] not in vistos:
            vistos.add(item[0])
            articulos_unicos.append(item)

    lista_art = [f"• {item[0]}" for item in articulos_unicos]
    lista_conc = [f"• {item[0]}: {item[1]}" for item in articulos_unicos]

    return "**Artículos aplicables:**\n" + "\n".join(lista_art) + "\n\n**Conclusión:**\nSanciones correspondientes aplicadas:\n" + "\n".join(lista_conc)

def obtener_respuesta_ia(situacion):
    if not situacion or len(situacion.strip()) < 2:
        return MENSAJE_NO_VALIDO

    if not groq_client:
        return motor_local_rapido(situacion)

    system_prompt = (
        "Eres un juez y experto legal del Código Penal Federal para un servidor de roleplay.\n"
        "REGLAS ESTRICTAS DE FORMATO:\n"
        "1. En la sección **Artículos aplicables:** escribe ÚNICAMENTE el número de artículo y su nombre corto (NUNCA pongas dinero, multas, puntos ni años de prisión ahí).\n"
        "2. En la sección **Conclusión:** escribe las sanciones correspondientes aplicadas (multa en MXN, puntos, prisión o inhabilitación según el código).\n"
        "3. Si el mensaje NO tiene sentido legal, es una pregunta cotidiana o fuera de tema (por ejemplo: '¿cuál es el tiempo de hoy?', 'hola', 'qué tal', 'cuánto es 2+2', bromas sin delito o texto incoherente), responde ÚNICAMENTE con esta frase exacta:\n"
        f"{MENSAJE_NO_VALIDO}\n"
        "4. Si SÍ describe una situación o delito, interpreta su intención real aunque tenga faltas graves de ortografía, abreviaturas o jerga (ej. 'polis', 'elementos', 'fuega', 'fierro', 'plomear', 'darse a la fuga') y extrae TODOS los artículos aplicables sin omitir ninguno.\n"
        "5. Distingue bien:\n"
        "   - Huir o escapar de policías/elementos/autoridad = Art. 68 (Evasión a la autoridad).\n"
        "   - Huir de un accidente sin ayudar = Art. 25.\n"
        "   - Evadir un retén o control de tráfico = Art. 21.\n"
        "   - Intento de homicidio (queda vivo/crítico) = Art. 51 o 52 / Homicidio (fallece) = Art. 53 o 54.\n"
        "   - Conducir sin licencia = Art. 11 / Arma sin licencia = Art. 48.\n"
        "6. NUNCA uses el Art. 1 como relleno o respuesta por defecto.\n\n"
        f"{CODIGO_PENAL_TEXTO}\n\n"
        "EJEMPLO OBLIGATORIO DE ESTRUCTURA:\n"
        "**Artículos aplicables:**\n"
        "• Art. 6 - No cumplir semáforos\n"
        "• Art. 68 - Evasión a la autoridad\n\n"
        "**Conclusión:**\n"
        "Sanciones correspondientes aplicadas:\n"
        "• Art. 6 - No cumplir semáforos: 500 MXN por cada semáforo ignorado\n"
        "• Art. 68 - Evasión a la autoridad: 9,600 MXN y 1 mes de prisión"
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
            return res.strip()
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
