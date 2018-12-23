#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models.trivia import db, Categoria, Pregunta, Respuesta, Usuario

p_historia_4 = Pregunta(text="Quién fue el Primer Presidente de Uruguay", categoria=1)
r_historia_4 = Respuesta(text="José Fructuoso Rivera", es_correcta=True, pregunta=p_historia_4)
r_historia_4_2 = Respuesta(text="Venancio Flores Barrios", es_correcta=False, pregunta=p_historia_4)
r_historia_4_3 = Respuesta(text="Manuel Oribe", es_correcta=False, pregunta=p_historia_4)
db.session.add(p_historia_4)
db.session.add(r_historia_4)
db.session.add(r_historia_4_2)
db.session.add(r_historia_4_3)

p_historia_3 = Pregunta(text='El Renacimiento marcó el inicio de la Edad...', categoria=1)
r_historia_3 = Respuesta(text="Moderna", es_correcta=True, pregunta=p_historia_3)
r_historia_3_2 = Respuesta(text="Media", es_correcta=False, pregunta=p_historia_3)
r_historia_3_3 = Respuesta(text="Contemporánea", es_correcta=False, pregunta=p_historia_3)
db.session.add(p_historia_3)
db.session.add(r_historia_3)
db.session.add(r_historia_3_2)
db.session.add(r_historia_3_3)

p_historia_2 = Pregunta(text='De qué color es el humo que informa a los creyentes de que se ha elegido un Papa nuevo', categoria=1)
r_historia_2 = Respuesta(text="Blanco", es_correcta=True, pregunta=p_historia_2)
r_historia_2_2 = Respuesta(text="Amarillo", es_correcta=False, pregunta=p_historia_2)
r_historia_2_3 = Respuesta(text="Rojo", es_correcta=False, pregunta=p_historia_2)
db.session.add(p_historia_2)
db.session.add(r_historia_2)
db.session.add(r_historia_2_2)
db.session.add(r_historia_2_3)

p_arte_2 = Pregunta(text='De que estaba fabricado originalmente el maquillaje blanco de las Geishas', categoria=2)
r_arte_2 = Respuesta(text="Arroz molido", es_correcta=False, pregunta=p_arte_2)
r_arte_2_2 = Respuesta(text="Flores de loto", es_correcta=False, pregunta=p_arte_2)
r_arte_2_3 = Respuesta(text="Plomo", es_correcta=True, pregunta=p_arte_2)
db.session.add(p_arte_2)
db.session.add(r_arte_2)
db.session.add(r_arte_2_2)
db.session.add(r_arte_2_3)

p_arte_3 = Pregunta(text='La Mona Lisa fue pintada por...', categoria=2)
r_arte_3 = Respuesta(text="Picasso", es_correcta=False, pregunta=p_arte_3)
r_arte_3_2 = Respuesta(text="Manuel Blanes", es_correcta=False, pregunta=p_arte_3)
r_arte_3_3 = Respuesta(text="Leonardo da Vinci", es_correcta=True, pregunta=p_arte_3)
db.session.add(p_arte_3)
db.session.add(r_arte_3)
db.session.add(r_arte_3_2)
db.session.add(r_arte_3_3)

p_arte_4 = Pregunta(text='Quién fue impulsor del Fovismo', categoria=2)
r_arte_4 = Respuesta(text="Picasso", es_correcta=False, pregunta=p_arte_4)
r_arte_4_2 = Respuesta(text="Torres García", es_correcta=False, pregunta=p_arte_4)
r_arte_4_3 = Respuesta(text="Henri Matisse", es_correcta=True, pregunta=p_arte_4)
db.session.add(p_arte_4)
db.session.add(r_arte_4)
db.session.add(r_arte_4_2)
db.session.add(r_arte_4_3)

p_arte_5 = Pregunta(text='Cuál de estos pintores no es Uruguayo', categoria=2)
r_arte_5 = Respuesta(text="Francisco de Goya", es_correcta=False, pregunta=p_arte_5)
r_arte_5_2 = Respuesta(text="Torres García", es_correcta=False, pregunta=p_arte_5)
r_arte_5_3 = Respuesta(text="Juan Manuel Blanes", es_correcta=True, pregunta=p_arte_5)
db.session.add(p_arte_5)
db.session.add(r_arte_5)
db.session.add(r_arte_5_2)
db.session.add(r_arte_5_3)

# APLICAR CAMBIOS:
db.session.commit()
print("DB OK")
# MOSTRAR TABLAS:
print(Pregunta.query.all())
print(Respuesta.query.all())