import json

from flask import Flask, request, render_template
from wtforms.validators import InputRequired, Email
from flask_wtf import FlaskForm
from wtforms import StringField


DAYS_OF_WEEK = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": "Суббота", "sun": "Воскресенье"}
GOALS_TEXT = {}
with open("data/goals.json") as g:
    GOALS_TEXT = json.load(g)


app = Flask(__name__)
app.secret_key = "randomstring"


@app.route('/')
def render_index():

    output = render_template("index.html", )
    return output


@app.route('/goals/<goal>/')
def render_goal(goal):

    output = render_template("goal.html", goal=goal)
    return output


@app.route('/profiles/<int:teacher_id>/')
def render_profile(teacher_id):
    with open("data/teachers.json", "r") as t_file:
        teachers = json.load(t_file)
    teacher = teachers[teacher_id]
    free_time = {}
    for day, times in teacher["free"].items():
        free_time[day] = [time for time in times.keys() if times[time]]
    output = render_template("profile.html", teacher=teacher, text_goals=GOALS_TEXT, week_days=DAYS_OF_WEEK, free=free_time)
    return output


@app.route('/request/')
def render_request():

    output = render_template("request.html", )
    return output


@app.route('/request_done/')
def render_request_done():

    output = render_template("request_done.html", )
    return output


@app.route('/booking/<teacher_id>/<weekday>/<time>/')
def render_booking(teacher_id, weekday, time):

    output = render_template("booking.html", )
    return output


@app.route('/booking_done/')
def render_booking_done():

    output = render_template("request_done.html", )
    return output


app.run(debug=True)