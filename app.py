from flask import Flask, render_template

app = Flask(__name__)

@app.route('/trivia')
def trivia():
    return render_template("trivia.html")

@app.route('/trivia/categorias')
def trivia_categorias():
    return render_template("categorias.html")

@app.route('/trivia/<id_categoria>/pregunta')
def trivia_pregunta(id_categoria):
    return render_template("pregunta.html",id_categoria)

@app.route('/trivia/{id_categoria}/resultado/{id_respuesta}')
def trivia_resultado():
    return render_template("resutlaado.html",id_categoria,id_respuesta)

@app.route('/trivia/fin')
def trivia_fin():
    return render_template("fin.html")

