import json

import app

with open("data/goals.json") as g:
    GOALS_TEXT = json.load(g)
for id, text in GOALS_TEXT.items():
    if not app.db.session.query(app.Goal).get(id):
        goal = app.Goal(id=id, text=text)
        app.db.session.add(goal)

with open("data/teachers.json", "r") as t_file:
    teachers = json.load(t_file)

for teacher in teachers:
    if not app.db.session.query(app.Teacher).get(teacher['id']):
        t = app.Teacher(id=int(teacher["id"]), name=teacher["name"], about=teacher["about"],
                        rating=float(teacher["rating"]),
                        picture=teacher["picture"], price=teacher["price"],
                        free=json.dumps(teacher['free']))

        for goal in teacher["goals"]:
            t.goals.append(app.db.session.query(app.Goal).get(goal))
        app.db.session.add(t)
app.db.session.commit()
