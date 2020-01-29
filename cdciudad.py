# -*- coding: utf-8 -*-

from __future__ import print_function
#from botocore.vendored import requests
import requests
from unicodedata import normalize
from datetime import datetime, timedelta
import json,urllib,os,time
import re
from random import randint

baseURL = "https://newapp.matchapp.es/matchapp/app/"
team_name = "C.D. CIUDAD"

#COPIAR A PARTIR DE AQUI


meses = {
        "01" : "enero",
        "02" : "febrero",
        "03" : "marzo",
        "04" : "abril",
        "05" : "mayo",
        "06" : "junio",
        "07" : "julio",
        "08" : "agosto",
        "09" : "septiembre",
        "10" : "octubre",
        "11" : "noviembre",
        "12" : "diciembre"
}

posicion = {
    "2" : "segundo",
    "3" : "tercero",
    "4" : "cuarto",
    "5" : "quinto",
    "6" : "sexto",
    "7" : "septimo",
    "8" : "octavo",
    "9" : "noveno",
    "10" : "decimo",
    "11" : "decimoprimero",
    "12" : "decimosegundo",
    "13" : "decimotercero",
    "14" : "decimocuarto",
    "15" : "decimoquinto",
    "16" : "decimosexto",
    "17" : "decimoseptimo",
    "18" : "decimo octavo",
    "19" : "decimo noveno",
    "20" : "vigesimo",
}

torneos = {
		"ALEVIN" : "ALEVIN F-8 PRIMERA GALICIA",
        "ABSOLUTA" : "TERCERA GALICIA",
        "JUVENIL"  : "JUVENIL SEGUNDA AUTONÓMICA",
        "ALEVINB"  : "ALEVIN F-8 TERCERA GALICIA",
        "BENJAMIN" : "BENJAMIN F-8 - TERCERA GALICIA",
        "PREBENJAMIN" : "PREBENJAMIN F-8 - TERCERA GALICIA",
        "VETERANO" : "VETERANOS - PRIMERA GALICIA",
        "CADETE" : "CADETE SEGUNDA AUTONOMICA"
 	}

alias = {
		"ALEVIN" : "equipo alevín",
        "ABSOLUTA" : "Deportivo Ciudad",
        "JUVENIL"  : "equipo juvenil",
        "ALEVINB"  : "equipo alevín B",
        "BENJAMIN" : "equipo benjamín",
        "PREBENJAMIN" : "equipo prebenjamin",
        "VETERANO" : "equipo de veteranos",
        "CADETE" : "equipo cadete"
 	}


def quita_acentos(s):
    trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
    s = normalize('NFKC', normalize('NFKD', s).translate(trans_tab))
    return s

s = requests.session()

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title':  title,
            'content':  output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            }
        },
        'shouldEndSession': should_end_session
    }

def on_intent(intent_request, session, result,s):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent_name = intent_request['intent']['name']
    try:
        categoria = intent_request['intent']['slots']['categoria']["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]["name"].upper() 
    except:
        categoria = "ABSOLUTA"
        
    # Dispatch to your skill's intent handers
    if intent_name == "proximo_partido":
        response = proximo_partido_response (categoria)
    elif intent_name == "ultimo_resultado":
        response = ultimo_resultado_response(categoria)
    elif intent_name == "clasificacion":
        response = clasificacion_response(categoria)
    elif intent_name == "mejoresjugadores":
        response = jugadores_destacados_response()
    elif intent_name == "AMAZON.HelpIntent":
        response = status_intent_response()
    else:
        response = status_intent_response()
        
    card_title = "DEPORTIVO CIUDAD"
    speech_output = response["response"]
    reprompt_text = ""
    session_attributes = {}
    should_end_session = response["end_session"]

    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def get_group(categoria):
    listado_equipos = baseURL + "/getTeams?nameTeam=" + team_name + "&idSport=1"
    info_equipo = baseURL + "/getTeamByIdTeam.jsonp?_dc=1578927295607&page=1&start=0&limit=25&idTeam="
    obj = s.get(listado_equipos)
    get_result = json.loads (normalize( 'NFC',obj.text))
    results = get_result["listTeamsVO"]
    for i in results:
        # RECUPERAMOS LOS IDs de los EQUIPOS 
        # RECUPERAMOS LOS IDs de los GRUPO 
        if i["category"] == torneos[categoria]:
            equipo = dict()
            obj = s.get(info_equipo+str(i["idTeam"]))
            get_result = json.loads (normalize( 'NFC',obj.text.replace('callback(','').replace('})','}')))
            equipo["idGroup"] = get_result["idGroup"]
            equipo["idTeam"] =  i["idTeam"]
            equipo["torneo"] = torneos[categoria]
            equipo["categoria"] = categoria
    return equipo

def status_intent_response():
    result = dict()
    respuesta = "Desde esta aplicacion puedes saber toda la informacion de tu equipo preferido "
    respuesta = respuesta + "como resultados, proximos partidos o las noticias mas importantes de nuestro club. "
    respuesta = respuesta + "puedes usarla diciendo: 'alexa, preguntale al deportivo ciudad como quedo el equipo alevin "
    respuesta = respuesta + "o 'alexa, preguntale al deportivo ciudad cual es el proximo partido del equipo alevin "
    respuesta = respuesta + "Vamos Rojillos!"
    result["response"] = respuesta
    result["end_session"] = False
    return result 

def convierte_estadio(estadio):
    if estadio == "Sin Determinar":
        return " Se jugará en un estadio sin confirmar"
    else:
        result = estadio.replace('Nº','Número ').replace("."," ").replace("TORRE","de la torre")
        return  " Se jugará en el campo " + result

def convierte_hora(fecha):
    if str(fecha.time()) == "00:00:00":
        return " la hora no está confirmada "
    else:
        hora=fecha.hour
        minutos=fecha.minute
        if minutos == 45:
            hora = hora + 1
            min_texto = " menos cuarto"
        elif minutos == 30:
            min_texto = " y media"
        elif minutos == 00:
            min_texto = " en punto"
        elif minutos == 15:
            min_texto = " y cuarto "
        
        if hora > 12:
            hora = hora - 12
            hora_texto = str(hora) + " de la tarde "
        else:
            hora_texto = str(hora)

        if hora == 1:
            hora_texto = " a la " + hora_texto
        else:
            hora_texto = " a las " + hora_texto
        return  hora_texto + min_texto

def convertir_equipo(equipo,categoria):
    if equipo == team_name:
        team = "Deportivo Ciudad " + categoria
    else:
        team = equipo.replace('C.F.','').replace("S.D.","").replace('  ',' ')
    return team

def jugadores_destacados_response():
    result = dict()
    jugadores = {
        "1" : "En el equipo alevín juega Pedrito Pedreira, nacido en el 2008, es una de las promesas de la cantera rojilla.",
        "2" : "En el equipo benjamín destaca David Pedreira, un defensa con estilo propio que puede marcar una época .",
        "3" : "La universidad de La Coruña nos ha anunciado que va a analizar el misterio de los brazos del portero Raul, que son capaces de estirarse hasta cualquier hueco del arco para evitar que le marquen gol",
        "4" : 'Santi Alonso, defensa duro con una potente pegada, tiene una maxima "o pasa el balon, o pasa el jugador, pero los dos juntos no".',
        "5" : "Mateo Rodriguez, este jugador me recuerda las subidas de Capdevila en la banda del SuperDepor.",
        "6" : "El entrenador Fernando, tras su buena temporada,esta pensando en dar el salto a los banquillos del deportivo de La Coruña",
        "7" : "No se pierdan a Teo Samaniego, estén atentos a este jugador porque es tan rapido que si parpadean se lo pierden",
        "8" : "Gonzalo Ortiz, sobrio y rapido al corte, muy elegante sacando el balon",
        "9" : "Amilcar, un cerrojo en la retaguardia del equipo. Nunca pierde la posicion.",
        "10" : "Bamba, jugador de dibujos animados, es capaz de hacer diabluras con la pelota.",
        "11" : "Mateo Vizcaino, con una progresión en ascenso cada vez se encuentra más comodo en la banda izquierda.",
        "12" : "Luis Mercadal puede jugar en cualquier posicion, si bien donde más cómodo se encuentra es en la retaguardia.",
        "13" : "Diego Lopez incansable trotador, es un ancla en el ataque sobre el que pivotan todas las jugadas.",
        "14" : "Pedro Pedreira, si el flequillo no le limita la visión, este chico va a llegar muy lejos",
        "15" : "Javi Garcia, rápido con la pelota tiene una definición brutal delante del arco contrario.",
        "16" : "Tom, centrocampista rapido y habilidoso, va a dar mucho que hablar en este final de temporada.",
        "17" : "Anton, el jugador con más criterio de este equipo, siempre con la cabeza levantada es capaz de dar pases definitivos a sus compañeros.",
        "18" : "Gabriel está siendo el portero más seguro de esta liga, con paradas decisivas que dan mucha confianza a su equipo.",
        "19" : "Iago Sessa es el lider de la defensa, sobrio, potente y con una visión de juego que le permiten sacar la pelota con mucho peligro desde atrás.",
        "20" : "No le llamen Roque! LLamenle correcaminos! Que velocidad tiene este jugador!",
        "21" : "Iago Vaamonde, letal con la pelota en sus piernas, es el pichichi histórico de este equipo.",
        "22" : "Un defensa muy rápido siempre atento al corte es Gabi Rivera, que se ha convertido en titular indiscutible",
        "23" : "Cuando Alex Gonzalez no está sobre el terreno de juego, el equipo lo echa en falta. Y su entrenador lo sabe.",
        "24" : "Sergio Zas siempre atento a echar una mano a sus compañeros, es el pulmon del equipo en el mediocampo.",
        "25" : "Hector Guzman hace que lo dificil parezca facil.",
        "26" : "Un jugador que hay ido de menos a mas es Caleb Reynaga, que este año figura en el equipo titular de cada jornada.",
        "27" : "Con la progresion actual Rayan promete ser un futuro jugador de la seleccion marroquí absoluta",
        "28" : "El reciente fichaje bruno seoane se ha adaptado a la perfeccion y ha cubierto los pequeños defectos que el equipo tenía",
        "29" : "Oscar Pinchi, exjugador del Deportivo de la Coruña y que actualmente en el Extremadura, jugó en la cantera rojilla durante la decada pasada.",
    }   
    
    result["response"] = jugadores [str(randint(1,29))]
    result["end_session"] = True
    return result

def ultimo_resultado_response(categoria):
    resultados_equipo = baseURL + "/getResultsByTeamAndGroup?idGroup="
    equipo = get_group(categoria)
    result = dict()
    obj = s.get(resultados_equipo + str(equipo["idGroup"]))
    get_result = json.loads (normalize( 'NFC',obj.text))
    resultados = get_result["listJornadaData"]
    ultima_jornada = 0
    ultimo_partido = 0
    for i in resultados:
        for j in i["dataJornada"]:
            if j["resultado"]!= '':
                if ((j["localName"] == team_name) or (j["visitanteName"] == team_name )):
                    if i["idNumJornada"] > ultima_jornada:
                        ultima_jornada = i["idNumJornada"]
                        ultimo_partido = j
    if ultimo_partido == 0:
        return "Todavia no ha jugado ningun partido"
    else:
        score = ultimo_partido["resultado"].split()
        if ultimo_partido["localName"] == team_name:
            rival = convertir_equipo (ultimo_partido["visitanteName"],categoria)
            condicion = "local"
            diferencia = int(score[0]) - int(score[2])
            if diferencia > 0:
                if diferencia > 2:
                    resultado = "ha goleado"
                else:
                    resultado = "ha ganado"
            else:
                if diferencia == 0:
                    resultado = "ha empatado"
                else:
                    resultado = "ha perdido"
        else:
            rival = convertir_equipo (ultimo_partido["localName"],categoria)
            diferencia = int(score[0]) - int(score[2])
            condicion = "visitante"
            if  diferencia > 0 :
                resultado = "ha perdido"
            else:
                if diferencia == 0:
                    resultado = "ha empatado"
                else:
                    if diferencia < -2:
                        resultado = "ha goleado"
                    else:
                        resultado = "ha ganado"            
        if resultado == "ha ganado" or resultado == "ha goleado":
            texto = "Nuestro " + alias[categoria] + " " + resultado +  " como " + condicion + " " + str(score[0]) + " a " + " " + str(score[2]) +" al " + rival
        else:
            texto = "Nuestro " + alias[categoria] + " " + resultado +  " como " + condicion + " " + str(score[0]) + " a " + " " + str(score[2]) + " contra el " + rival
        result["response"] = texto.replace("  "," ")
        result["end_session"] = True
        return result 

def clasificacion_response(categoria):
    primero = dict()
    segundo = dict()
    result = dict()
    cdciudad = dict()
    clasificacion = baseURL + "/getClasification?idGroup="
    equipo = get_group(categoria)
    obj = s.get(clasificacion + str(equipo["idGroup"]))
    get_result = json.loads (normalize( 'NFC',obj.text))
    clasificacion = get_result["listClasificationVO"]
    primero["idTeam"] = clasificacion[0]["nameTeam"]
    primero["Puntos"] = clasificacion[0]["puntos"]
    segundo["idTeam"] = clasificacion[1]["nameTeam"]
    segundo["Puntos"] = clasificacion[1]["puntos"]
    for equipo in clasificacion:
        if equipo["nameTeam"] == team_name:
            cdciudad["Puntos"] = equipo["puntos"]
            cdciudad["idPosition"] = equipo["idPosition"]
    if cdciudad["idPosition"] != 1:
        diferencia = primero["Puntos"] - cdciudad["Puntos"]

        texto = "Nuestro " + alias[categoria] + " va " + posicion[str(equipo["idPosition"])] + " a " + str(diferencia) + " puntos del primero"
    else:
        diferencia = cdciudad["Puntos"] - segundo["Puntos"] 
        texto = "Nuestro "+ alias[categoria] +" va lider a " + str(diferencia) + " puntos del segundo"
    result["response"] = texto.replace("  "," ")
    result["end_session"] = True
    return result


def proximo_partido_response(categoria):
    calendario_equipo = baseURL + "/getNumJornadas?"
    equipo = get_group(categoria)
    result = dict()
    obj = s.get(calendario_equipo + "idGroup=" + str(equipo["idGroup"]) + "&idTeam=" + str(equipo["idTeam"]))
    get_result = json.loads (normalize( 'NFC',obj.text))
    jornadas = get_result["listJornadaData"]
    proxima_jornada = jornadas[0]
    fecha =  datetime.strptime(proxima_jornada["matchDay"], '%d/%m/%y %H:%M:%S')
    mes = meses[str(fecha.strftime("%m"))]
    dia = str(fecha.strftime("%d"))
    convierte_hora(fecha)
    estadio = proxima_jornada["nameField"]
    if proxima_jornada["localName"] == team_name:
        
        rival = convertir_equipo (proxima_jornada["visitanteName"],categoria)      
    else:
        rival = convertir_equipo (proxima_jornada["localName"],categoria)

    partido = "El próximo partido de nuestro " + alias[categoria] + " será  contra el " + rival + ". " + convierte_estadio(estadio) + " el día " + dia + " de " + mes +  convierte_hora(fecha)
    result["response"] = partido.replace("  "," ")
    result["end_session"] = True
    result["card_title"] = "2"
    return result
    
def lambda_handler(event, context):
    try:
        if event['request']['type'] == "IntentRequest":
            return on_intent(event['request'], event['session'],results,s)
        else:
            card_title = "DEPORTIVO CIUDAD"
            speech_output = "Hola Rojillo"
            reprompt_text = ""
            session_attributes = {}
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    except:
            response = status_intent_response()
            card_title = "DEPORTIVO CIUDAD"
            speech_output = response["response"]
            reprompt_text = ""
            session_attributes = {}
            should_end_session = response["end_session"]
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])



#def lambda_handler(event, context):
print(proximo_partido_response("PREBENJAMIN")["response"])
print (ultimo_resultado_response("ALEVIN")["response"])
print (clasificacion_response("VETERANO")["response"])
print (jugadores_destacados_response()["response"])