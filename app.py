from flask import Flask, request, render_template
from wtforms.validators import InputRequired, Email
from flask_wtf import FlaskForm
from wtforms import StringField


app = Flask(__name__)
app.secret_key = "randomstring"


@app.route('/')
def render_index():

    output = render_template("index.html", )
    return output


@app.route('/goals/<goal>/')
def render_goal(goal):

    output = render_template("goal.html", )
    return output


@app.route('/profiles/<teacher_id>/')
def render_profile(teacher_id):

    output = render_template("profile.html", )
    return output


@app.route('/request/')
def render_request():

    output = render_template("request.html", )
    return output


@app.route('/request_done/')
def render_request():

    output = render_template("request_done.html", )
    return output


@app.route('/booking/<teacher_id>/<weekday>/<time>/')
def render_request(teacher_id, weekday, time):

    output = render_template("booking.html", )
    return output


@app.route('/booking_done/')
def render_request_done():

    output = render_template("request_done.html", )
    return output


app.run(debug=True)