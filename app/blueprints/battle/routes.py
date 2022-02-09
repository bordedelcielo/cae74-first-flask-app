from .import bp as battle
from flask import render_template

@battle.route('/arena', methods = ['GET', 'POST'])
def arena():
    return render_template('arena.html.j2')