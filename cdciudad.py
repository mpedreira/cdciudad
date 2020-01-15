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
        "BENJAMIN" : "BENJAMIN F-8 - TERCERA GALICIA",
        "PREBENJAMIN" : "PREBENJAMIN F-8 - TERCERA GALICIA",
        "VETERANO" : "VETERANOS - PRIMERA GALICIA",
        "CADETE" : "CADETE SEGUNDA AUTONOMICA"
 	}

## CONVERTIR ESTO EN FUNCIONES

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

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    try:
        categoria = intent_request['intent']['slots']['categoria']["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]["name"].upper() 
    except:
        categoria = "ALEVIN"
        
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
        if quita_acentos(i["category"]) == torneos[categoria]:
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
        return " se jugará en un estadio sin confirmar"
    else:
        result = estadio.replace('Nº','Número ').replace("."," ").replace("TORRE","de la torre")
        return  " se jugará en el campo " + result

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
        "2" : "En el equipo benjamin destaca David Pedreira, un defensa con estilo propio que puede marcar una época .",
        "3" : "Oscar Pinchi, exjugador del Deportivo de la Coruña y que actualmente en el Extremadura, jugó en la cantera rojilla durante la decada pasada."
#        "4" : "marzo",
#        "5" : "abril",
#        "6" : "mayo",
#        "7" : "junio",
#        "8" : "julio",
#        "9" : "agosto",
#        "10" : "septiembre",
#        "11" : "octubre",
#        "12" : "noviembre",
#        "13" : "diciembre"
    }   
    
    result["response"] = jugadores [str(randint(1,2))]
    result["end_session"] = True
    return result

def ultimo_resultado_response(categoria):
    resultados_equipo = baseURL + "/getResultsByTeamAndGroup?idGroup="
    equipo = get_group(categoria)
    result = dict()
    obj = s.get(resultados_equipo + str(equipo["idGroup"]))
    get_result = json.loads (normalize( 'NFC',obj.text))
    resultados = get_result["listJornadaData"]
    partidos_jugados = []
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
                    resultado = "goleamos"
                else:
                    resultado = "ganamos"
            else:
                if diferencia == 0:
                    resultado = "empatamos"
                else:
                    resultado = "perdimos"
        else:
            rival = convertir_equipo (ultimo_partido["localName"],categoria)
            condicion = "visitante"
            if  diferencia > 0 :
                resultado = "perdimos"
            else:
                if diferencia == 0:
                    resultado = "empatamos"
                else:
                    if diferencia < -2:
                        resultado = "goleamos"
                    else:
                        resultado = "ganamos"            
        if resultado == "ganamos" or resultado == "goleamos":
            texto = resultado + " como " + condicion + " al " + rival + " " + str(score[0]) + " a " + " " + str(score[2])
        else:
            texto = resultado + " como " + condicion + " contra el " + rival + " " + str(score[0]) + " a " + " " + str(score[2])
        result["response"] = texto
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

        result["response"] = "Nuestro equipo va " + posicion[str(equipo["idPosition"])] + " a " + str(diferencia) + " puntos del primero"
    else:
        diferencia = cdciudad["Puntos"] - segundo["Puntos"] 
        result["response"] = "Nuestro equipo va lider a " + str(diferencia) + " puntos del segundo"
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

    partido = "El próximo partido contra el " + rival + convierte_estadio(estadio) + " el día " + dia + " de " + mes +  convierte_hora(fecha)
    result["response"] = partido
    result["end_session"] = True
    result["card_title"] = "2"
    return result
    
def lambda_handler(event, context):
    
    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'],results,s)
    else:
        card_title = "DEPORTIVO CIUDAD"
        speech_output = "Hola Rojillo"
        reprompt_text = ""
        session_attributes = {}
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])
        
    
#def lambda_handler(event, context):
print(proximo_partido_response("PREBENJAMIN")["response"])
print (ultimo_resultado_response("ALEVIN"))
print (clasificacion_response("VETERANO"))
print (jugadores_destacados_response())