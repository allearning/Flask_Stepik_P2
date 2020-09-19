import json
import random

from flask import Flask, render_template, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TimeField, IntegerField, RadioField
from wtforms.validators import InputRequired, AnyOf, NumberRange, Regexp

PHONE_RE = r"^((\+\d)|\d)?\-?(\([\d]+\))?\-?[\d\-]+[\d]$"
DAYS_OF_WEEK = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница",
                "sat": "Суббота", "sun": "Воскресенье"}
with open("data/goals.json") as g:
    GOALS_TEXT = json.load(g)
TIMES = {"1-2": "1-2 часа в неделю", "3-5": "3-5 часов в неделю", "5-7": "5-7 часов в неделю",
         "7-10": "7-10 часов в неделю"}


class BookForm(FlaskForm):
    clientWeekday = StringField(validators=[InputRequired(), AnyOf(DAYS_OF_WEEK.keys())])
    clientTime = TimeField(validators=[InputRequired()])
    clientTeacher = IntegerField(validators=[InputRequired(), NumberRange(min=0)])
    clientName = StringField('Вас зовут', validators=[InputRequired()])
    clientPhone = StringField('Ваш телефон', validators=[InputRequired(),
                                                         Regexp(PHONE_RE, message="Номер телефона не номер телефона")])
    submit = SubmitField('Записаться на пробный урок')


class RequestForm(FlaskForm):
    goals = RadioField("goals", choices=list([(goal, GOALS_TEXT[goal]) for goal in GOALS_TEXT.keys()]),
                       default="travel")
    times = RadioField("times", choices=list([(time, TIMES[time]) for time in TIMES.keys()]), default="1-2")
    clientName = StringField('Вас зовут', validators=[InputRequired()])
    clientPhone = StringField('Ваш телефон', validators=[InputRequired(),
                                                         Regexp(PHONE_RE, message="Номер телефона не номер телефона")])
    submit = SubmitField('Найдите мне преподавателя')


app = Flask(__name__)
app.secret_key = "randomstring"


@app.route('/')
def render_index():
    with open("data/teachers.json", "r") as t_file:
        teachers = json.load(t_file)
    selected_teachers = random.sample(teachers, 6)
    output = render_template("index.html", teachers=selected_teachers)
    return output


@app.route('/goals/<goal>/')
def render_goal(goal):
    with open("data/teachers.json", "r") as t_file:
        teachers = json.load(t_file)
    selected_teachers = [t for t in teachers if goal in t["goals"]]
    output = render_template("goal.html", goal=GOALS_TEXT[goal].lower(), teachers=selected_teachers)
    return output


@app.route('/profiles/<int:teacher_id>/')
def render_profile(teacher_id):
    with open("data/teachers.json", "r") as t_file:
        teachers = json.load(t_file)
    teacher = teachers[teacher_id]
    free_time = {}
    for day, times in teacher["free"].items():
        free_time[day] = [time for time in times.keys() if times[time]]
    output = render_template("profile.html", teacher=teacher, text_goals=GOALS_TEXT, week_days=DAYS_OF_WEEK,
                             free=free_time)
    return output


@app.route('/request/')
def render_request():
    form = RequestForm()
    output = render_template("request.html", form=form)
    return output


@app.route('/request_done/', methods=["POST"])
def render_request_done():
    requests = {}
    with open("data/booking.json") as b:
        string_data = b.read()
        if string_data:
            requests = json.loads(string_data)
    form = RequestForm()
    if not form.validate_on_submit():
        return render_template("request.html", form=form)
    goal = form.goals.data
    time = form.times.data
    clientName = form.clientName.data
    clientPhone = form.clientPhone.data

    request_record = {"clientName": form.clientName.data, "clientPhone": form.clientPhone.data, "time": form.times.data,
                      "goal": form.goals.data}
    if requests:
        requests["records"].append(request_record)
    else:
        requests["records"] = [request_record]
    with open("data/request.json", "w") as b:
        json.dump(requests, b)

    output = render_template("request_done.html", goal=GOALS_TEXT[goal], time=TIMES[time], clientName=clientName,
                             clientPhone=clientPhone)
    return output


@app.route('/booking/<int:teacher_id>/<weekday>/<time>/')
def render_booking(teacher_id, weekday, time):
    if weekday not in DAYS_OF_WEEK.keys() or int(time) not in range(8, 24, 2):
        return abort(404)
    form = BookForm()
    with open("data/teachers.json", "r") as t_file:
        teachers = json.load(t_file)
    teacher = teachers[teacher_id]
    if not teacher["free"][weekday][time + ":00"]:
        return abort(403, f"{teacher['name']} Вас не ждет")

    output = render_template("booking.html", form=form, teacher=teacher, book_time=time,
                             book_day=(weekday, DAYS_OF_WEEK[weekday]))
    return output


@app.route('/booking_done/', methods=["POST"])
def render_booking_done():
    with open("data/teachers.json", "r") as t_file:
        teachers = json.load(t_file)
    bookings = {}
    with open("data/booking.json") as b:
        string_data = b.read()
        if string_data:
            bookings = json.loads(string_data)
    form = BookForm()

    if not form.validate_on_submit():
        return render_template("booking.html", form=form, teacher=teachers[form.clientTeacher.data],
                               book_time=form.clientTime.data.strftime("%H"),
                               book_day=(form.clientWeekday.data, DAYS_OF_WEEK[form.clientWeekday.data]))

    clientWeekday = form.clientWeekday.data
    clientTime = form.clientTime.data
    clientName = form.clientName.data
    clientPhone = form.clientPhone.data

    booking_record = {"clientName": form.clientName.data, "clientPhone": form.clientPhone.data,
                      "teacherID": form.clientTeacher.data, "clientWeekday": form.clientWeekday.data,
                      "clientTime": form.clientTime.data.strftime("%H:%M")}
    if bookings:
        bookings["records"].append(booking_record)
    else:
        bookings["records"] = [booking_record]
    with open("data/booking.json", "w") as b:
        json.dump(bookings, b)
    output = render_template("booking_done.html", book_day=DAYS_OF_WEEK[clientWeekday], book_time=clientTime,
                             clientName=clientName, clientPhone=clientPhone)
    return output


if __name__ == '__main__':
    app.run()
