import os
import asyncio
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
CODIGO_PENAL_TEXTO = (
    "CÓDIGO PENAL FEDERAL\n\n"
    "Título I - De los delitos\n"
    "Art 1: Este Código penal aplicará en toda la República Mexicana para los delitos de Fuero Común y Federal.\n"
    "Fracción I: Es delito toda acción u omisión voluntaria penada por la ley, el que cometiere delito será responsable de él e incurrirá en la pena que la ley señale.\n"
    "Art. 1.1: Todo aquel abogado que tenga conocimiento del presunto delito que le confiere a su cliente, en el desempeño de sus servicios jurídicos-legal, no tiene ninguna obligación legal de denunciar el delito al que se le profiere a su cliente.\n"
    "Fracción I: Todo aquel que cumpla el artículo 2 estará exento de responsabilidad criminal, procesal, condenatoria o cualesquiera que dañen la inocencia y el trabajo del abogado.\n"
    "Art. 1.2: La ley penal mexicana es obligatoria para todos los habitantes de la República, incluso los extranjeros. Los delitos cometidos dentro del mar territorial o adyacente quedan sometidos a las prescripciones de la Suprema Corte Suprema de México.\n"
    "Art. 1.3: Son circunstancias atenuantes las situaciones que disminuyen la gravedad o la intensidad de un delito: obedece indicaciones de funcionario sin oposición, reparar el daño físico o psicológico, ser cómplice, confesar ante autoridad, o sufrir discapacidad/trastorno mental demostrable.\n"
    "Art. 2: Son circunstancias agravantes las situaciones que aumentan la gravedad o la intensidad de un delito. Se aplicarán 11 meses al total de la condena si hay prisión federal, y en caso de que no la hubiera, 5,000 MXN. Agravantes: insultar repetidamente a un funcionario en ejercicio, reincidencia, o discriminar por color de piel, procedencia, sexo, identidad u orientación sexual.\n"
    "Art. 3: Los períodos de cárcel se regirán en base a los siguientes plazos: 24 meses = 1 día y 12 horas; 18 meses = 1 día y 6 horas; 12 meses = 22 horas; 9 meses = 12 horas y 30 minutos; 6 meses = 9 horas; 3 meses = 5 horas y 30 minutos; 1 mes = 2 horas y 30 minutos.\n\n"
    "Título II - De las leyes de circulación\n"
    "Art. 4: Conducción temeraria que pone en peligro la vida de viandantes o la vía/funcionario: sanción de 2,000 MXN y/o pérdida de 3 puntos.\n"
    "Art. 4.1: Licencias de conducción con puntaje máximo de 10. Al llegar a 0 puntos se retira la licencia de 6 a 12 meses. Se recuperan conduciendo bien (ej. 7 días = 2 puntos, respetar semáforos = 1 punto; al suspender se reinician a 10).\n"
    "Art. 5: Daño a propiedad privada o pública con vehículo: 2,500 MXN y reparación total. La conciliación extingue el delito.\n"
    "Art. 6: No cumplir semáforos: 500 MXN por cada semáforo ignorado.\n"
    "Art. 7: Conducir en dirección contraria: 3,000 MXN y/o pérdida de 1 punto.\n"
    "Art. 8: Conducir bajo efectos de alcohol o sustancias ilegales (incluye estar en el interior del vehículo con pruebas): 2,500 MXN y/o pérdida de 6 puntos.\n"
    "Art. 9: Posesión de arma no autorizada en vehículo: Art. 48 + 4,000 MXN e incautación temporal del vehículo (retirable solo por juez).\n"
    "Art. 10: Incumplir límites de velocidad: 1,500 MXN y retirada de 2 puntos.\n"
    "Art. 11: Conducir sin licencia: 4,000 MXN e ingreso a prisión preventiva de 24h.\n"
    "Art. 12: Carreras clandestinas sin permiso: 6,500 MXN, suspensión de licencia y 1 mes de prisión.\n"
    "Art. 13: Mal estacionado en zona prohibida: 750 MXN o traslado al depósito (1,000 MXN extra por grúa).\n"
    "Art. 14: Estacionado obstruyendo la circulación vial: 1,800 MXN o depósito (2,000 MXN por grúa).\n"
    "Art. 15: No ceder el paso a servicios de emergencia: 1,500 MXN y retirada de licencia por 1 mes.\n"
    "Art. 16: Uso de luces obligatorio entre ocaso y amanecer: 500 MXN.\n"
    "Art. 17: Vehículo con faltas técnicas y/o mecánicas: 900 MXN y retirada de 2 puntos.\n"
    "Art. 18: Arrojar objetos a la vía o inmediaciones: 500 MXN.\n"
    "Art. 19: Incumplimiento general de normas de tráfico: 500 MXN y retirada de 1 punto.\n"
    "Art. 20: Adelantamientos erróneos o peligrosos (en curva, línea continua, paso a nivel/peatonal): 1,200 MXN y retirada de 2 puntos.\n"
    "Art. 21: Ignorar a agente regulando tráfico, evadir control policial/militar o ignorar escolta en convoy: 2,150 MXN y retirada de 2 puntos.\n"
    "Art. 22: Uso de móvil, navegador o auriculares conduciendo sin estar estacionado: 400 MXN y retirada de 1 punto.\n"
    "Art. 23: Circular por fuera de la calzada (aceras, césped, arcenes): 850 MXN y retirada de 2 puntos.\n"
    "Art. 24: Uso indebido de elementos acústicos (claxon) en la vía pública: 380 MXN.\n"
    "Art. 25: Huir de un accidente sin identificar o socorrer heridos: 4,700 MXN y disposición ante el ministerio público. Exento si no hubo mala voluntad y se avisó a emergencias.\n"
    "Art. 26: Causar accidente mayor: 8,000 MXN y retirada de licencia (determinado por juez). Víctimas justificadas quedan exentas.\n"
    "Art. 27: Circular sin matrícula o con matrícula ilegible: 4,000 MXN y depósito (1,000 MXN de grúa).\n"
    "Art. 28: Cruzar la calle indebidamente o pararse en el centro por un civil: 600 MXN. (Exentos servicios de emergencia).\n\n"
    "Título II (Sección 2) - De las agresiones, los disturbios y las conductas erróneas\n"
    "Art. 29: Conflicto con agresión física o daños materiales: 2,500 MXN e ingreso inmediato en prisión temporal. Heridos bajo custodia en hospital.\n"
    "Art. 30: Agresión verbal (2,000 MXN) / Agresión física (2 años de prisión e indemnización médica de 2,000 a 6,000 MXN).\n"
    "Art. 31: Funcionario que no lee derechos al detener: suspensión de 1 año y 5,000 MXN. Incumplimiento de habeas corpus: 8,000 a 12,000 MXN.\n"
    "Art. 32: Alterar el orden público con actitudes o palabras: 1 mes de prisión.\n"
    "Art. 33: Comercialización de productos no autorizados: 2,000 MXN y confiscación.\n"
    "Art. 34: Inducción a la alteración pública: 5,000 MXN y 6 meses de prisión.\n"
    "Art. 35: Inducir a realizar acciones ilegales ajenas a la voluntad: 2 años de prisión.\n"
    "Art. 36: Pertenecer a grupo criminal: 2 años de prisión. Trabajar o incentivar al grupo: 1 año de prisión.\n"
    "Art. 37: Agresión por color de piel, etnia o nacionalidad: multa/sanción de 2 años e indemnización psicológica de 15,000 MXN.\n"
    "Art. 38: Suplantación de identidad: 12,000 MXN y 1 año y 6 meses de prisión (agravante 50% extra si es a autoridad pública).\n"
    "Art. 39: Acoso reiterado con daños psicológicos (constatados por informe médico): 6,000 MXN y 1 año de prisión.\n"
    "Art. 40: Menoscabo psíquico o lesión leve a cónyuge, expareja o persona vulnerable conviviente: 5,000 MXN y 2 años de prisión.\n\n"
    "Título III - De los hurtos y los asaltos\n"
    "Art. 41: Allanamiento de morada (invasión de propiedad privada sin consentimiento): 7,000 MXN y 6 meses de prisión temporal. (Requiere orden escrita y sellada de juez de la Suprema Corte para policías/militares).\n"
    "Art. 42: Usurpación (apoderarse violentamente de un inmueble o derecho): 20,000 MXN y 2 años de prisión.\n"
    "Art. 43: Hurto (apropiación no violenta de posesiones ajenas): 15,000 MXN y 1 año de prisión.\n"
    "Art. 44: Asalto con arma blanca: 10,000 MXN y 1 año y 6 meses de prisión.\n"
    "Art. 45: Asalto con arma de fuego (robo agravado): 20,000 MXN y 2 años de prisión.\n"
    "Art. 46: Apropiación con fuerza o intimidación con daños físicos/mentales/materiales: 16,000 MXN y 2 años de prisión.\n"
    "Art. 47: Daños a propiedades del Estado: 25,000 MXN e indemnización obligatoria por especialista.\n\n"
    "Título IV - De las armas de fuego y su porte\n"
    "Art. 48: Posesión de una o más armas sin licencia o falsificada: 17,000 MXN y 1 año de prisión.\n"
    "Art. 49: Utilizar armas sin licencia con motivo justificado: 25,000 MXN y 1 año y medio de prisión. (Exenta legítima defensa probada y funcionarios autorizados).\n"
    "Art. 50: Comercio ilegal de armas de fuego: 30,000 MXN y 2 años de prisión (sanciona a compradores y vendedores sin permiso).\n\n"
    "Título V - De los homicidios, secuestros y extorsiones\n"
    "Art. 51: Intento de homicidio con extremidades (víctima en estado crítico pero viva): 2 años de prisión. (Exenta legítima defensa).\n"
    "Art. 52: Intento de homicidio a mano armada (arma blanca o fuego, víctima crítica viva): 1 año y medio de prisión. (Exenta legítima defensa).\n"
    "Art. 53: Homicidio con extremidades (víctima fallece): 2 años y medio de prisión. (Exenta legítima defensa).\n"
    "Art. 54: Homicidio con arma blanca o de fuego (víctima fallece): 3 años de prisión. (Exenta legítima defensa).\n"
    "Art. 55: Homicidio múltiple (a más de una persona en corto tiempo): 5 años de prisión o 3 años extra por cada víctima adicional (juicio especial).\n"
    "Art. 56: Secuestro (privación ilegal de la libertad): 3 años de prisión. Agravante: amenazas, armas, daños. Atenuante: liberación sin daños y sin rescate.\n"
    "Art. 57: Extorsión (obtener algo mediante violencia o intimidación): 10,000 MXN y 2 años de prisión.\n"
    "Art. 58: Amenazas (mal en persona, bienes u honor, o impedir derecho): 7,000 MXN y 1 año de prisión. Ayudantes: 5,000 MXN y 12 meses.\n\n"
    "Título VI - De los delitos de documentos y licencias\n"
    "Art. 59: Falsedad documental (crear, vender o usar documentos falsos): 70,000 a 100,000 MXN y 2 años de prisión. (Agravante si es oficial del gobierno/tribunal/policía; atenuante aceptar y entregar documento).\n"
    "Art. 60: Indebida documentación (transitar sin identificación oficial: 10,000 MXN; conducir sin papeles del auto: 10,000 MXN + retiro de auto y multa de 20,000 MXN; cazar sin licencia de armas: 10,000 MXN).\n"
    "Art. 61: Estafa (engaño con ánimo de lucro para perjuicio ajeno): 12,000 MXN e indemnización de daños.\n\n"
    "Título VII - De los delitos contra el Estado\n"
    "Art. 62: Desobedecer orden de autoridad judicial/policial/militar: 20,000 MXN. Incumplir resolución judicial: 48,000 MXN y 6 meses de prisión.\n"
    "Art. 63: Reporte falso a servicios de emergencia: 27,000 MXN y 4 meses de prisión temporal.\n"
    "Art. 64: Invadir instalaciones catalogadas como restringidas: 14,000 MXN y 2 días de detención temporal ERLC.\n"
    "Art. 65: Robo de objeto perteneciente al Estado: 50,000 MXN y 2 años de prisión.\n"
    "Art. 66: Suplantación de identidad de miembro del Estado: 10,000 MXN extra a falsificación y 2 años de prisión. (Agravante alto funcionario/Gobierno).\n"
    "Art. 67: Resistencia a la autoridad (impedir detención por fuerza/amenazas/acoso): 14,000 MXN.\n"
    "Art. 68: Evasión a la autoridad (evitar arresto): 9,600 MXN y 1 mes de prisión.\n"
    "Art. 69: Soborno (incentivar a funcionario público para beneficio propio): 37,000 MXN y 3 años de prisión.\n"
    "Art. 70: Terrorismo (actos contra ciudadanía/Estado para inestabilidad nacional): 500,000 MXN y 15 años de prisión (juicio en Tribunal Federal).\n"
    "Art. 71: Atentar contra integridad de funcionario público o robar equipo policial/militar: 2 años de prisión.\n"
    "Art. 72: Funcionario que dicta resolución arbitraria a sabiendas: inhabilitación permanente de cargo público.\n"
    "Art. 73: Funcionario que nombra ilegalmente a un cargo público: 200,000 MXN e inhabilitación permanente (igual sanción para quien acepta sabiendo que no cumple requisitos).\n"
    "Art. 74: Funcionario que abandona su misión para no perseguir delitos: inhabilitación de cargo y empleo.\n"
    "Art. 75: Funcionario que intencionadamente deja de promover la persecución de delitos: inhabilitación permanente.\n"
    "Art. 76: Funcionario que calumnie o injurie a una institución del Estado públicamente: 300,000 MXN y disculpa pública.\n"
    "Art. 77: Negativa abierta de funcionario a cumplir resoluciones judiciales: 230,000 MXN e inhabilitación. (Exento si el mandato es infracción manifiesta de ley).\n"
    "Art. 78: Funcionario que no comparece ante la Suprema Corte u otra autoridad requerida: 90,000 MXN.\n"
    "Art. 79: Funcionario que sustrae, destruye u oculta documentos bajo su custodia: 50,000 MXN e inhabilitación.\n"
    "Art. 80: Contaminar u obstruir cadena de custodia de evidencia: 155,000 MXN e inhabilitación.\n"
    "Art. 81: Funcionario que revela secretos o información reservada de su oficio: 380,000 MXN e inhabilitación.\n"
    "Art. 82: Cohecho (solicitar dádiva/favor para acto contrario a deberes): 250,000 MXN, 3 años de prisión e inhabilitación.\n"
    "Art. 83: Cohecho por acto propio del cargo: 190,000 MXN, 1 año de prisión e inhabilitación.\n"
    "Art. 84: Recibir regalo u ofrenda en consideración a su cargo: 150,000 MXN.\n"
    "Art. 85: Definición general de los artículos 82 a 83 como cohecho.\n"
    "Art. 86: Tráfico de influencias (influir en otro funcionario para beneficio propio o ajeno): 360,000 MXN, 1 año de prisión e inhabilitación.\n"
    "Art. 87: Malversación (sustraer o consentir sustracción de caudales públicos con ánimo de lucro): 350,000 MXN y 4 años de prisión.\n"
    "Art. 88: Concertación ilegal en contratación pública con ánimo de lucro."
)

# ==========================================
# 3. MOTOR LOCAL DE RESPALDO RÁPIDO AMPLIADO
# ==========================================
def motor_local_rapido(situacion):
    s = situacion.lower()
    articulos = []

    # Tránsito y Circulación
    if "temeraria" in s or "peligro" in s or "zig-zag" in s:
        articulos.append(("Art. 4 - Conducción temeraria", "2,000 MXN y/o pérdida de 3 puntos."))
    if "daño" in s and ("propiedad" in s or "mobiliario" in s or "choca" in s):
        articulos.append(("Art. 5 - Daño a la propiedad", "2,500 MXN y reparación total."))
    if "semáforo" in s or "stop" in s or "roja" in s or "rojo" in s:
        articulos.append(("Art. 6 - No cumplir semáforos", "500 MXN por infracción."))
    if "dirección contraria" in s or "contraria" in s:
        articulos.append(("Art. 7 - Dirección contraria", "3,000 MXN y/o pérdida 1 punto."))
    if "alcohol" in s or "ebrio" in s or "sustancias" in s or "drogas" in s:
        articulos.append(("Art. 8 - Conducir bajo efectos de alcohol/sustancias", "2,500 MXN y/o pérdida 6 puntos."))
    if "velocidad" in s or "rápido" in s:
        articulos.append(("Art. 10 - Exceso de velocidad", "1,500 MXN y retirada 2 puntos."))
    if ("licencia" in s or "carné" in s or "sin carnet" in s) and "arma" not in s:
        articulos.append(("Art. 11 - Conducir sin licencia", "4,000 MXN e ingreso a prisión preventiva de 24h."))
    if "carrera" in s:
        articulos.append(("Art. 12 - Carreras clandestinas", "6,500 MXN, suspensión de licencia y 1 mes de prisión."))
    if "mal estacionado" in s:
        articulos.append(("Art. 13 - Mal estacionado", "750 MXN o depósito (1,000 MXN grúa)."))
    if "obstruyendo" in s or "bloquea" in s:
        articulos.append(("Art. 14 - Estacionado obstruyendo circulación", "1,800 MXN o depósito (2,000 MXN grúa)."))
    if "ambulancia" in s or "emergencia" in s or "ceder el paso" in s:
        articulos.append(("Art. 15 - No ceder el paso a emergencias", "1,500 MXN y retirada de licencia por 1 mes."))
    if "luces" in s:
        articulos.append(("Art. 16 - Uso de luces obligatorio", "500 MXN."))
    if "mecánica" in s or "faltas técnicas" in s:
        articulos.append(("Art. 17 - Faltas técnicas/mecánicas", "900 MXN y retirada 2 puntos."))
    if "arrojar" in s or "tirar objetos" in s:
        articulos.append(("Art. 18 - Arrojar objetos a la vía", "500 MXN."))
    if "adelant" in s:
        articulos.append(("Art. 20 - Adelantamiento erróneo", "1,200 MXN y retirada 2 puntos."))
    if "ignora" in s or "control" in s or "convoy" in s:
        articulos.append(("Art. 21 - Ignorar agente o control", "2,150 MXN y retirada 2 puntos."))
    if "movil" in s or "móvil" in s or "auriculares" in s:
        articulos.append(("Art. 22 - Uso de móvil/auriculares", "400 MXN y retirada 1 punto."))
    if "acera" in s or "césped" in s or "fuera de la calzada" in s:
        articulos.append(("Art. 23 - Circular fuera de la calzada", "850 MXN y retirada 2 puntos."))
    if "claxon" in s or "acústico" in s:
        articulos.append(("Art. 24 - Uso indebido de claxon", "380 MXN."))
    if "huir" in s or "huyendo" in s or "accidente" in s:
        articulos.append(("Art. 25 - Huir de un accidente", "4,700 MXN y disposición ante ministerio público."))
    if "accidente mayor" in s:
        articulos.append(("Art. 26 - Causar accidente mayor", "8,000 MXN y retirada de licencia."))
    if "matrícula" in s:
        articulos.append(("Art. 27 - Circular sin matrícula", "4,000 MXN y depósito."))
    if "cruzar" in s and "calle" in s:
        articulos.append(("Art. 28 - Cruzar indebidamente la calle", "600 MXN."))

    # Agresiones, Orden Público y Agravantes
    if "insult" in s or "reincidente" in s:
        articulos.append(("Art. 2 - Agravantes generales", "11 meses de prisión federal o 5,000 MXN."))
    if "agresión" in s or "empujones" in s or "golpe" in s:
        articulos.append(("Art. 30 - Agresión verbal/física", "2,000 MXN (verbal) o 2 años prisión + indemnización (física)."))
    if "orden público" in s or "gritos" in s or "disturbio" in s:
        articulos.append(("Art. 32 - Alterar el orden público", "1 mes de prisión."))
    if "grupo criminal" in s or "banda" in s:
        articulos.append(("Art. 36 - Pertenencia a grupo criminal", "2 años de prisión."))
    if "discrimin" in s or "color de piel" in s or "etnia" in s:
        articulos.append(("Art. 37 - Agresión por discriminación", "Multa/sanción de 2 años e indemnización de 15,000 MXN."))
    if "suplant" in s:
        articulos.append(("Art. 38 - Suplantación de identidad", "12,000 MXN y 1 año y 6 meses de prisión."))
    if "acoso" in s:
        articulos.append(("Art. 39 - Acoso reiterado", "6,000 MXN y 1 año de prisión."))

    # Hurtos, Armas, Homicidios y Delitos contra el Estado
    if "allanamient" in s or "rompiendo la puerta" in s or "propiedad privada" in s:
        articulos.append(("Art. 41 - Allanamiento de morada", "7,000 MXN y 6 meses prisión temporal."))
    if "usurpación" in s:
        articulos.append(("Art. 42 - Usurpación", "20,000 MXN y 2 años prisión."))
    if "hurto" in s or "robar" in s or "robo" in s:
        articulos.append(("Art. 43 - Hurto", "15,000 MXN y 1 año prisión."))
    if "arma blanca" in s or "cuchillo" in s or "navaja" in s:
        articulos.append(("Art. 44 - Asalto con arma blanca", "10,000 MXN y 1 año y 6 meses prisión."))
    if "arma de fuego" in s or "pistola" in s or "dispar" in s:
        articulos.append(("Art. 45 - Asalto con arma de fuego", "20,000 MXN y 2 años prisión."))
        articulos.append(("Art. 48 - Posesión de arma sin licencia", "17,000 MXN y 1 año prisión."))
    if "comercio" in s and "arma" in s:
        articulos.append(("Art. 50 - Comercio ilegal de armas", "30,000 MXN y 2 años prisión."))
    if "homicidio" in s or "matar" in s or "asesin" in s:
        articulos.append(("Art. 54 - Homicidio", "3 años prisión."))
    if "secuestr" in s:
        articulos.append(("Art. 56 - Secuestro", "3 años prisión."))
    if "extorsi" in s:
        articulos.append(("Art. 57 - Extorsión", "10,000 MXN y 2 años prisión."))
    if "amenaz" in s:
        articulos.append(("Art. 58 - Amenazas", "7,000 MXN y 1 año prisión."))
    if "falsedad" in s or "documento" in s or "falsific" in s:
        articulos.append(("Art. 59 - Falsedad documental", "70,000 a 100,000 MXN y 2 años prisión."))
    if "estafa" in s or "engaño" in s:
        articulos.append(("Art. 61 - Estafa", "12,000 MXN e indemnización."))
    if "desobed" in s:
        articulos.append(("Art. 62 - Desobediencia a la autoridad", "20,000 MXN."))
    if "reporte falso" in s or "llamada falsa" in s:
        articulos.append(("Art. 63 - Reporte falso a emergencias", "27,000 MXN y 4 meses prisión temporal."))
    if "restringid" in s:
        articulos.append(("Art. 64 - Invadir zona restringida", "14,000 MXN y 2 días detención temporal ERLC."))
    if "estado" in s or "objetos del estado" in s:
        articulos.append(("Art. 65 - Robo de objeto del Estado", "50,000 MXN y 2 años prisión."))
    if "resistencia" in s:
        articulos.append(("Art. 67 - Resistencia a la autoridad", "14,000 MXN."))
    if "evasión" in s or "evadir" in s or "escap" in s:
        articulos.append(("Art. 68 - Evasión a la autoridad", "9,600 MXN y 1 mes prisión."))
    if "soborn" in s or "dinero a un policía" in s:
        articulos.append(("Art. 69 - Soborno a funcionario público", "37,000 MXN y 3 años prisión."))
    if "terroris" in s:
        articulos.append(("Art. 70 - Terrorismo", "500,000 MXN y 15 años prisión."))
    if ("policía" in s or "policia" in s or "funcionario" in s or "agente" in s) and ("atentar" in s or "integridad" in s or "herir" in s or "equipo" in s):
        articulos.append(("Art. 71 - Atentar contra integridad de funcionario público", "2 años prisión."))
    if "secretos" in s or "revela" in s:
        articulos.append(("Art. 81 - Revelación de secretos", "380,000 MXN e inhabilitación."))
    if "cohecho" in s:
        articulos.append(("Art. 82/85 - Cohecho", "250,000 MXN, 3 años de prisión e inhabilitación."))
    if "tráfico de influencias" in s:
        articulos.append(("Art. 86 - Tráfico de influencias", "360,000 MXN, 1 año prisión e inhabilitación."))
    if "malversación" in s or "fondos" in s:
        articulos.append(("Art. 87 - Malversación", "350,000 MXN y 4 años prisión."))

    if not articulos:
        articulos.append(("Art. 1 - Disposición General del Código Penal", "Sujeto a revisión de los hechos por la autoridad competente."))

    # Ordenar y eliminar duplicados manteniendo orden
    vistos = set()
    articulos_unicos = []
    for item in articulos:
        if item[0] not in vistos:
            vistos.add(item[0])
            articulos_unicos.append(item)

    lista_art = [f"• {item[0]}" for item in articulos_unicos]
    lista_conc = [f"• {item[0]}: {item[1]}" for item in articulos_unicos]

    return f"**Artículos aplicables:**\n" + "\n".join(lista_art) + "\n\n**Conclusión:**\nSanciones correspondientes aplicadas:\n" + "\n".join(lista_conc)

def obtener_respuesta_ia(situacion):
    if not situacion or len(situacion.strip()) < 3:
        return motor_local_rapido(situacion)

    if not groq_client:
        return motor_local_rapido(situacion)

    system_prompt = (
        "Eres un asistente legal experto del Código Penal Federal de México. "
        "Lee la situación y extrae TODOS los artículos aplicables del siguiente código completo, sin omitir ninguno:\n\n"
        f"{CODIGO_PENAL_TEXTO}\n\n"
        "FORMATO OBLIGATORIO:\n"
        "**Artículos aplicables:**\n"
        "• Art. XX - Nombre del delito\n\n"
        "**Conclusión:**\n"
        "Sanciones correspondientes aplicadas:\n"
        "• Art. XX - Nombre del delito: [Multa y Prisión]"
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'SITUACIÓN: "{situacion}"'}
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        res = completion.choices[0].message.content
        if res and res.strip():
            return res
    except Exception as e:
        print(f"Aviso IA: {e}")

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
