#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import os
from flask import Flask,render_template,redirect,url_for,request,session
from models.trivia import Categoria,Pregunta,Respuesta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, null
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e5ac358cf0bf-11e5-9e39-d3b532c10a28' #or os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///models/trivia.db'
db= SQLAlchemy(app)

@app.route('/')
def trivia_():
    return redirect(url_for('trivia_inicio'))

@app.route('/trivia')
def trivia_inicio():
    return render_template("index.html.jinja2")

@app.route('/trivia/')
def trivia_inicio2():
    return redirect(url_for('trivia_inicio'))

@app.route('/trivia/categorias')
def trivia_categorias():
    if session.get('ti')==None :
        print('EMPIEZA-------')
        session['ti']=time.time()
        session['online']=True
        session['game_status']={}
    else:
        print('SIGUE---------')
    
    #LE PIDO TODAS LAS CATEGORIAS A Categorias
    todas_categorias=Categoria.query.all()
    
    #DECLARO lista_categorias QUE POR CADA CATEGORIA TIENE UN DIC: {'nombre':<NOMBRE>,'url`:<RUTA>}
    lista_categorias=[]
    for categoria in todas_categorias:
        lista_categorias.append({
            "nombre":categoria.nombre,
            #URL_FOR ARMA LA RUTA PARA: trivia_pregunta(id_categoria)
            "url":url_for('trivia_pregunta',id_categoria=categoria.id)
            })
        
    return render_template("categorias.html.jinja2",lista_categorias=lista_categorias)

@app.route('/trivia/<int:id_categoria>/pregunta')
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
        
    return render_template("pregunta.html.jinja2",
                           nombre_categoria=nombre_categoria,
                           pregunta=pregunta.text,
                           respuestas=lista_respuestas
                           )

@app.route('/trivia/<int:id_categoria>/resultado/<int:id_respuesta>')
def trivia_resultado(id_categoria,id_respuesta):
    
    #BUSCO LA Respuesta ELEGIDA CON LA ID 
    respuesta_e=Respuesta.query.filter_by(id=id_respuesta).first()
    
    #CON LA RESPUESTA BUSCO CUAL ES LA PREGUNTA
    pregunta=Pregunta.query.filter_by(id=respuesta_e.id_pregunta).first()
    
    #PIDO LAS 3 RESPUESTAS PARA LA PREGUNTA ELEGIDA POR ORDEN DECRECIENTE/CRECIENTE
    respuestas=Respuesta.query.filter_by(id_pregunta=pregunta.id).order_by("Respuesta.es_correcta desc").all()
    
    #DECLARO lista_respuestas QUE POR CADA RESPUESTA TIENE UN DIC: {'text':<RESPUESTA>,'es_correcta':<True O False>,'url':<RUTA>}
    lista_respuestas=[]
    for respuesta in respuestas:
        lista_respuestas.append({
            "id":respuesta.id,
            "text":respuesta.text,
            "es_correcta":respuesta.es_correcta
            })
        
    url_perdio=url_for('trivia_pregunta',id_categoria=id_categoria)
    url_gano=url_for('trivia_categorias')
        
    return render_template("resultado.html.jinja2",
                           pregunta=pregunta.text,
                           respuestas=lista_respuestas,
                           resultado=respuesta_e.es_correcta,
                           relegida=respuesta_e.text,
                           url_gano=url_gano,
                           url_perdio=url_perdio
                           )

@app.route('/trivia/fin')
def trivia_fin(): 
    tf=time.time()
    duracion=session['ti']-tf
    return render_template("fin.html.jinja2")
