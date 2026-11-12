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
    "Art. 71:
