#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from models.trivia import Categoria,Pregunta,Respuesta,logIn,logOff,register,ganar,Usuario
from models.forms import LoginForm, RegisterForm
from flask import Flask,render_template,redirect,url_for,session,send_from_directory,flash,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from sqlalchemy import desc
from datetime import datetime, timedelta
import time
import sqlalchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e5ac358cf0bf-11e5-9e39-d3b532c10a28' #or os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///models/trivia.db'
db= SQLAlchemy(app)

@app.route('/')
def index():
    return redirect(url_for('trivia_inicio'))

@app.route('/trivia', methods=['GET', 'POST'])
def trivia_inicio():
    #LIMPIO LA PARTIDA JUGADA AL ENTRAR EN EL INICIO 
    #PERO EL USUARIO NO
    try:
        if session['ti']:
            session.pop('ti')
            session.pop('cat_jugadas')
            session.pop('tf')
            session.pop('sabelotodo')
    except:
        pass;
    
    user=userControl(session)
    
    ranking=rankear()
    
    debug_printSession()
    return render_template("index.html.jinja2",
                           titulo="",
                           login_form=user['login_form'],
                           register_form=user['register_form'],
                           user_data=user['user_data'],
                           ranking=ranking)

@app.route('/trivia/', methods=['GET', 'POST'])
def trivia_inicio_():
    return redirect(url_for('trivia_inicio'))

@app.route('/trivia/categorias', methods=['GET', 'POST'])
def trivia_categorias():
    #LE PIDO TODAS LAS CATEGORIAS A Categorias
    todas_categorias=Categoria.query.all()
    
    #ACA INICIALIZO LOS DATOS DE LAS CATEGORIAS Y EL TIEMPO EN QUE EMPEZÓ A JUGAR
    #CREO SESSION['ti']=<TIEMPO>
    #CREO SESSION['cat_jugadas'] (ES UNA LISTA DE DICC {<id_categoria>:<True o False>})
    try:
        #PRIMERO COMPRUEBO SI LA SESION YA EXISTE
        if session['ti']:
            pass;
    except:
        #SI NO EXISTE CREO LA SESSION
        session['ti']=time.time()
        #CREO UN DICC CON TODAS LAS CATEGORIAS {'1':False,'2':False,...}
        #LAS GUARDO TODAS EN False PORQUE NO FUERON GANADAS AÚN
        dicc = {}
        for cat in todas_categorias:
            dicc[str(cat.id)] = False
        #GUARDO EN session['cat_jugadas'] EL DIC
        session['cat_jugadas']=dicc
        #SABELOTODO ME INDICA SI CONTESTO BIEN TODAS LAS PREGUNTAS SIN ERRORES
        session['sabelotodo']=True
    
    #ACA SEPARO LAS CATEGORIAS GANAS DE LAS SIN JUGAR/GANAR
    #LE PASO AL TEMPLATE lista_categorias y lista_ganadas
    lista_categorias=[]#  <--- CATEGORIAS SIN JUGAR/GANAR
    lista_ganadas=[]#     <--- CATEGORIAS GANADAS
    #PRIMERO RECORRO TODAS LAS CATEGORIAS
    for categoria in todas_categorias:
        dicc_jugadas=session['cat_jugadas']
        #SI LA CATEGORIA NO FUE GANADA LA GUARDO EN lista_categorias
        if dicc_jugadas.get(str(categoria.id)) == False:
            lista_categorias.append({
                "nombre":categoria.nombre,
                #URL_FOR ARMA LA RUTA HACIA LA PREGUNTA DE LA CATEGORIA
                "url":url_for('trivia_pregunta',id_categoria=categoria.id)
                })
        #SI GANO LA CATEGORIA LA GUARDO EN lista_ganadas
        if dicc_jugadas.get(str(categoria.id)) == True:
            lista_ganadas.append({
                "nombre":categoria.nombre
                #lista_ganadas NO NECESITA URL PORQUE YA FUE GANADA
                })
            
    tiempo=tiempo_formatear(tiempo_jugado(session['ti']))# <-- CALCULA Y CONVIERTE EL TIEMPO A TEXTO
    
    user=userControl(session)
    
    ranking=rankear()
    
    debug_printSession()
    return render_template("categorias.html.jinja2",
                           lista_categorias=lista_categorias,
                           lista_ganadas=lista_ganadas,
                           tiempo=tiempo,
                           titulo=" - Categorías",
                           login_form=user['login_form'],
                           register_form=user['register_form'],
                           user_data=user['user_data'],
                           ranking=ranking)

@app.route('/trivia/<int:id_categoria>/pregunta', methods=['GET', 'POST'])
def trivia_pregunta(id_categoria):
    #LE PIDO nombre A LA CATEGORIA QUE SE ELIGIÓ
    nombre_categoria=Categoria.query.filter_by(id=id_categoria).first().nombre
    #LE PIDO UNA PREGUNTA AL AZAR A LA TABLA Pregunta QUE SEA DE LA CATEGORIA QUE SE ESTA JUGANDO
    pregunta=Pregunta.query.filter_by(id_categoria=id_categoria).order_by(func.random()).first()
    #PIDO LAS RESPUESTAS PARA LA PREGUNTA ELEGIDA EN ORDEN ALEATORIO
    respuestas=Respuesta.query.filter_by(id_pregunta=pregunta.id).order_by(func.random()).all()
    #DECLARO lista_respuestas QUE POR CADA RESPUESTA TIENE UN DIC: {'text':<RESPUESTA>,'es_correcta':<True O False>,'url':<RUTA>}
    lista_respuestas=[]
    for respuesta in respuestas:
        lista_respuestas.append({
            "text":respuesta.text,
            "es_correcta":respuesta.es_correcta,
            #ACÁ LE ENVIO AL TEMPLATE LAS RUTAS PARA QUE CADA RESPUESTA SE DIRIGA A SU RESULTADO
            #URL_FOR ARMA LA RUTA HACIA: trivia_resultado(id_categoria,id_respuesta)
            "url":(url_for('trivia_resultado',id_categoria=id_categoria,id_respuesta=respuesta.id))
            })
        
    tiempo=tiempo_formatear(tiempo_jugado(session['ti']))# CONVIERTE EL TIEMPO A TEXTO
    
    user=userControl(session)
    
    ranking=rankear()
    
    debug_printSession()
    return render_template("pregunta.html.jinja2",
                           nombre_categoria=nombre_categoria,
                           pregunta=pregunta.text,
                           respuestas=lista_respuestas,
                           tiempo=tiempo,
                           titulo=" - Pregunta",
                           login_form=user['login_form'],
                           register_form=user['register_form'],
                           user_data=user['user_data'],
                           ranking=ranking)

@app.route('/trivia/<int:id_categoria>/resultado/<int:id_respuesta>', methods=['GET', 'POST'])
def trivia_resultado(id_categoria,id_respuesta):
    #BUSCO LA RESPUESTA ELEGIDA CON LA ID 
    respuesta_e=Respuesta.query.filter_by(id=id_respuesta).first()
    #CON LA RESPUESTA BUSCO CUAL ES LA PREGUNTA
    pregunta=Pregunta.query.filter_by(id=respuesta_e.id_pregunta).first()
    #PIDO LAS 3 RESPUESTAS PARA LA PREGUNTA ELEGIDA POR ORDEN DECRECIENTE
    respuestas=Respuesta.query.filter_by(id_pregunta=pregunta.id).order_by(desc(Respuesta.es_correcta)).all()
    
    #SI LA RESPUESTA ES CORRECTA GUARDO EN LA SESSION SU CATEGORIA COMO True
    #PRIMERO RECORRO TODAS LAS RESPUESTAS
    if respuesta_e.es_correcta:
        #EN EL DIC 'cat_jugadas' ACTUALIZO LA CATEGORIA A True
        dic=session['cat_jugadas']
        dic.update({str(id_categoria):True})
        session['cat_jugadas']=dic
    else:
        #SI SE EQUIVOCA EN ALGUNA RESPUESTA:
        session['sabelotodo']=False
    
    #SI EL JUGADOR GANÓ TODAS LAS CATEGORIAS REDIRIGO EL FLUJO AL FINAL DEL JUEGO
    todas_categorias=Categoria.query.all()
    ganador = True
    #PRIMERO RECORRO TODAS LAS CATEGORIAS
    for cat in todas_categorias:
        #SI QUEDA ALGUNA CATEGORIA SIN GANAR ganador = False
        if session['cat_jugadas'].get(str(cat.id)) == False:
            ganador = False
    #SI GANADOR ES True OSEA QUE GANO TODAS LAS CATEGORIAS, REDIRIGO AL TEMPLATE FINAL
    if ganador==True:
        #ganar() INCREMENTA EN UNO LA DB Y RETONRNA DIC {'ganadas':<int>,'mejor_tf':<float>,'sabelotodo':<bool>}
        #DE PASO ACTUALIZO 'ganadas', 'mejor_tf' y 'sabelotodo' EN LA SESION
        try:
            session['tf']=(time.time())-(session['ti'])
            ganador_id=session['user'].get("id")
            dic_ganador=ganar(ganador_id,session['tf'],session['sabelotodo'])
            session['user'].update({'ganadas':dic_ganador.get('ganadas')})
            session['user'].update({'mejor_tf':round(dic_ganador.get('mejor_tf'),2)})
            session['user'].update({'sabelotodo':dic_ganador.get('sabelotodo')})
        except:
            pass;
        return redirect(url_for('trivia_fin'))
    
    url_perdio=url_for('trivia_pregunta',id_categoria=id_categoria)
    url_gano=url_for('trivia_categorias')
    
    #DECLARO lista_respuestas QUE POR CADA RESPUESTA TIENE UN DIC: {'text':<RESPUESTA>,'es_correcta':<True O False>,'url':<RUTA>}
    #LE PASO TODAS LAS RESPUESTAS AL TEMPLATE
    lista_respuestas=[]
    for respuesta in respuestas:
        lista_respuestas.append({
            "id":respuesta.id,
            "text":respuesta.text,
            "es_correcta":respuesta.es_correcta
            })
        
    #LA FUNCION TIEMPO JUGADO DEVUELVE LA RESTA DE TI-TF FORMATEADA EN TEXTO
    tiempo=tiempo_formatear(tiempo_jugado(session['ti']))# CONVIERTE EL TIEMPO A TEXTO
    
    user=userControl(session)
    
    ranking=rankear()
    
    debug_printSession()
    return render_template("resultado.html.jinja2",
                           pregunta=pregunta.text,
                           respuestas=lista_respuestas,
                           resultado=respuesta_e.es_correcta,
                           relegida=respuesta_e.text,
                           url_gano=url_gano,
                           url_perdio=url_perdio,
                           tiempo=tiempo,
                           titulo=" - Respuesta",
                           login_form=user['login_form'],
                           register_form=user['register_form'],
                           user_data=user['user_data'],
                           ranking=ranking)
    
@app.route('/trivia/fin', methods=['GET', 'POST'])
def trivia_fin():
    tiempo=tiempo_formatear(tiempo_jugado(session['ti']))# CONVIERTE EL TIEMPO A TEXTO
    
    #SI SE REGISTRA O INICIA SESION EN ESTA RUTA SE LE AGREGA LA TRIVIA GANADA
    try:
        #CHEQUEO QUE SI YA HA INICIADO SESION
        if session['user']:
            #SI YA HABIA UNA SESION CARGO LOS DATOS NORMALMENTE
            user=userControl(session)
    except:
        #SI NO HABIA SESION CARGO LOS DATOS DE REGISTRO O LOGIN Y LE AGREGO LA TRIVIA GANADA
        user=userControl(session)
        if request.method == 'POST' and user['user_data']:
            session['user'].update({'ganadas':user['user_data'].get('ganadas')})
            session['user'].update({'mejor_tf':round(user['user_data'].get('mejor_tf'),2)})
            session['user'].update({'sabelotodo':user['user_data'].get('sabelotodo')})
    try:
        if session['sabelotodo']==True:
            flash("Ganaste sin equivocarte, has obtenido un premio de Sabelotodo!", 'success')
        else:
            flash("Se te ha añadido una Trivia exitosamente!", 'success')
    except:
        pass;
    
    ranking=rankear()
    
    debug_printSession()
    return render_template("fin.html.jinja2",
                           tiempo=tiempo,
                           titulo=" - Fin",
                           login_form=user['login_form'],
                           register_form=user['register_form'],
                           user_data=user['user_data'],
                           ranking=ranking)
    
@app.route('/trivia/salir')
def trivia_salir():
    logOff()
    return redirect(url_for('trivia_inicio'))
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'),'favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')

def tiempo_jugado(ti):
    tf=time.time()
    return tf-ti

def tiempo_formatear(duracion):
    formato=datetime(1,1,1)+(timedelta(seconds=int(duracion)))
    if formato.hour>0:
        return "%d horas, %d minutos y %d segundos" % (formato.hour, formato.minute, formato.second)
    else:
        return "%d minutos y %d segundos" % (formato.minute, formato.second)

def userControl(session):
    #DECLARO FORMULARIOS PARA LOGEAR Y REGISTRARSE
    login_form = LoginForm(prefix="login_form")
    register_form = RegisterForm(prefix="register_form")
    #ESTA FUNCIÓN logInRequest() SE ENCARGA DE HACER EL LOGIN CUANDO HAY POST
    #RECIVE LOS DATOS DEL FORMULARIO Y CREA UNA session['user'] CON LOS DATOS DEL USUARIO
    #AL MISMO TIEMPO RETORNA LOS DATOS PARA PODER PASARSELOS AL TEMPLATE
    try:
        if session['user']:
            user_data=session['user']
    except:
        user_data=None
    
    if request.method == 'POST':
        if register_form.submit() and register_form.password_repeat.data:
            user_data=registerRequest(register_form,session)
        if login_form.submit() and (not register_form.password_repeat.data):
            user_data=logInRequest(login_form,session)
    return {'user_data':user_data,'login_form':login_form,'register_form':register_form}

def logInRequest(login_form,session):
    try:
        if session['user']:
            if login_form.submit():
                flash("Ya has iniciado sesión.",'info')
            return session['user']
    except:
        try:
            session['user']=logIn(login_form.username.data, login_form.password.data)
            flash("Has iniciado sesión como {}.".format(login_form.username.data),'success')
            #ESTA LINEA LE DEJA A mejor_tf SOLO DOS FRACCIONES
            try:
                session['user'].update({'mejor_tf':round(session['user'].get('mejor_tf'),2)})
            except:
                session['user'].update({'mejor_tf':"--.--"})
            return session['user']
        except Exception as e:
                flash(e.to_dic().get('message'),'warning')
    return None
    
def registerRequest(register_form,session):
    try:
        if session['user']:
            flash("Ya has iniciado sesión.",'info')
            return session['user']
    except:
        try:
            try:
                if session['tf']:
                    session['user']=register(register_form.username.data,
                                             register_form.password.data,
                                             register_form.password_repeat.data,
                                             register_form.email.data,
                                             session['tf'],
                                             1)
                    session['user'].update({'mejor_tf':round(session['user'].get('mejor_tf'),2)})
                    
            except:
                session['user']=register(register_form.username.data,
                                         register_form.password.data,
                                         register_form.password_repeat.data,
                                         register_form.email.data)
                session['user'].update({'mejor_tf':"--.--"})
            flash("Usuario registrado", 'success')
            return session['user']
        except Exception as e:
            try:
                flash(e.to_dic().get('message'),'warning')
            except:
                print(str(e)+" "+str(type(e)))
            return None
    return None

def rankear():
    dato={'mejor_tf':None,'ganadas':None,'sabelotodo':{}}
    dato.update({'mejor_tf':Usuario.query.filter(sqlalchemy.not_(Usuario.ganadas.contains(0))).order_by(Usuario.mejor_tf).limit(100).all()})
    dato.update({'ganadas':Usuario.query.filter(sqlalchemy.not_(Usuario.ganadas.contains(0))).order_by(desc(Usuario.ganadas)).limit(100).all()})
    dato.update({'sabelotodo':Usuario.query.filter(sqlalchemy.not_(Usuario.sabelotodo.contains(0))).order_by(desc(Usuario.sabelotodo)).limit(100).all()})
    return dato

def debug_printSession():
    print("\n"+"-"*100)
    print("SESSION_ITEMS:\n")
    for key in session.keys():
        try:
            print('{:>12}  {:>1}  {:>12}'.format(key, ":", str(session[key])))
        except:
            pass;
    print("\n"+"-"*100)