from .import bp as battle
from flask import render_template, session

from app.secrets import con

cursor = con.cursor()

@battle.route('/arena', methods = ['GET', 'POST'])
def arena():
    id = session["_user_id"]
    cursor.execute(f"SELECT first_name FROM public.user WHERE id <> '{id}'")
    data = cursor.fetchall()
    print(data)
    return render_template('arena.html.j2', data=data)