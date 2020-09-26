import json
import os
import random

from flask import Flask, render_template, abort, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TimeField, IntegerField, RadioField
from wtforms.validators import InputRequired, AnyOf, NumberRange, Regexp

app = Flask(__name__)
app.secret_key = "randomstring"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

teachers_goals_association = db.Table('teachers_goals',
                                      db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
                                      db.Column('goal_id', db.String, db.ForeignKey('goals.id'))
                                      )


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.String, primary_key=True)
    text = db.Column(db.String, nullable=False)
    teachers = db.relationship('Teacher', secondary=teachers_goals_association, back_populates='goals')
    requests = db.relationship('LessonRequest', back_populates='goal')


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String)
    rating = db.Column(db.Float)
    picture = db.Column(db.String)
    price = db.Column(db.Integer)
    goals = db.relationship('Goal', secondary=teachers_goals_association, back_populates='teachers')
    free = db.Column(db.String)
    bookings = db.relationship("Booking", back_populates="teacher")

    def get_free(self):
        return json.loads(self.free)


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.relationship('Teacher', uselist=False, back_populates='bookings')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    day = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_phone = db.Column(db.String, nullable=False)
    start_time = db.Column(db.Text, nullable=False)


class LessonRequest(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_phone = db.Column(db.String, nullable=False)
    goal_id = db.Column(db.String, db.ForeignKey("goals.id"))
    goal = db.relationship("Goal", uselist=False, back_populates='requests')
    amount_of_time = db.Column(db.String, nullable=False)


PHONE_RE = r"^((\+\d)|\d)?\-?(\([\d]+\))?\-?[\d\-]+[\d]$"
DAYS_OF_WEEK = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница",
                "sat": "Суббота", "sun": "Воскресенье"}

GOALS_TEXT = {}
for goal in db.session.query(Goal).all():
    GOALS_TEXT[goal.id] = goal.text

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
    goals = RadioField("goals", choices=GOALS_TEXT.items(), default="travel")
    times = RadioField("times", choices=TIMES.items(), default="1-2")
    clientName = StringField('Вас зовут', validators=[InputRequired()])
    clientPhone = StringField('Ваш телефон', validators=[InputRequired(),
                                                         Regexp(PHONE_RE, message="Номер телефона не номер телефона")])
    submit = SubmitField('Найдите мне преподавателя')


@app.route('/')
def render_index():
    teachers = db.session.query(Teacher).all()
    selected_teachers = random.sample(teachers, 6)
    output = render_template("index.html", teachers=selected_teachers)
    return output


@app.route('/goals/<goal>/')
def render_goal(goal):
    selected_teachers = db.session.query(Goal).get(goal).teachers
    output = render_template("goal.html", goal=GOALS_TEXT[goal].lower(), teachers=selected_teachers)
    return output


@app.route('/profiles/<int:teacher_id>/')
def render_profile(teacher_id):
    teacher = db.session.query(Teacher).get_or_404(teacher_id)
    free_time = {}
    for day, times in teacher.get_free().items():
        free_time[day] = [time for time in times.keys() if times[time]]
    output = render_template("profile.html", teacher=teacher, text_goals=GOALS_TEXT, week_days=DAYS_OF_WEEK,
                             free=free_time)
    return output


@app.route('/request/', methods=["POST", "GET"])
def render_request():
    teachers = db.session.query(Teacher).all()
    if request.method == 'GET':
        form = RequestForm()
        output = render_template("request.html", form=form)
    else:
        form = RequestForm()
        if not form.validate_on_submit():
            return render_template("request.html", form=form)
        goal = form.goals.data
        time = form.times.data
        clientName = form.clientName.data
        clientPhone = form.clientPhone.data

        request_record = LessonRequest(user_name=clientName, user_phone=clientPhone, goal_id=goal, amount_of_time=time)

        db.session.add(request_record)
        db.session.commit()

        output = render_template("request_done.html", goal=GOALS_TEXT[goal], time=TIMES[time], clientName=clientName,
                                 clientPhone=clientPhone)
    return output


@app.route('/booking/<int:teacher_id>/<weekday>/<time>/', methods=["GET", "POST"])
def render_booking(teacher_id, weekday, time):
    teachers = db.session.query(Teacher).all()
    if request.method == 'GET':
        if weekday not in DAYS_OF_WEEK.keys() or int(time) not in range(8, 24, 2):
            return abort(404)
        form = BookForm()
        teacher = teachers[teacher_id]
        if not teacher.get_free()[weekday][time + ":00"]:
            return abort(403, f"{teacher['name']} Вас не ждет")

        output = render_template("booking.html", form=form, teacher=teacher, book_time=time,
                                 book_day=(weekday, DAYS_OF_WEEK[weekday]))
    else:
        form = BookForm()

        if not form.validate_on_submit():
            return render_template("booking.html", form=form, teacher=teachers[form.clientTeacher.data],
                                   book_time=form.clientTime.data.strftime("%H"),
                                   book_day=(form.clientWeekday.data, DAYS_OF_WEEK[form.clientWeekday.data]))

        clientWeekday = form.clientWeekday.data
        clientTime = form.clientTime.data
        clientName = form.clientName.data
        clientPhone = form.clientPhone.data

        booking_record = Booking(start_time=clientTime.strftime("%H:%M"), teacher_id=form.clientTeacher.data,
                                 day=clientWeekday,
                                 user_name=clientName, user_phone=clientPhone)
        db.session.add(booking_record)
        db.session.commit()
        output = render_template("booking_done.html", book_day=DAYS_OF_WEEK[clientWeekday], book_time=clientTime,
                                 clientName=clientName, clientPhone=clientPhone)
    return output


if __name__ == '__main__':
    app.run()
