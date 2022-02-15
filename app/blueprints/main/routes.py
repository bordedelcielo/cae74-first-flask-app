from flask import render_template, request, session
import requests
from flask_login import login_required
from .import bp as main
from app.models import db, Pokemon, association_table, User
import uuid

from sqlalchemy import select

from app.secrets import con

cursor = con.cursor()

@main.route('/students', methods = ['GET'])
@login_required
def students():
    my_students = ["Pari", "Mike", "Eduardo", "C-tina", "Jesus", "Austin"]
                                            #name inside of HTML = name in python
    return render_template("students.html.j2", students = my_students)


@main.route('/ergast', methods=['GET', 'POST'])
def ergast():
    if request.method == 'POST':
        year = request.form.get('year')
        round = request.form.get('round')
        url = f'http://ergast.com/api/f1/{year}/{round}/driverStandings.json'
        response = requests.get(url)
        if response.ok:
            #request worked
            if not response.json()["MRData"]["StandingsTable"]["StandingsLists"]:
                 error_string="We had an error loading your data likely the year or round is not in the database"
                 return render_template('ergast.html.j2', error = error_string)
            data = response.json()["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
            all_racers=[]
            for racer in data:
                racer_dict={
                    'first_name':racer['Driver']['givenName'],
                    'last_name':racer['Driver']['familyName'],
                    'position':racer['position'],
                    'wins':racer['wins'],
                    'DOB':racer['Driver']['dateOfBirth'],
                    'nationality':racer['Driver']['nationality'],
                    'constructor':racer['Constructors'][0]['name']
                }
                all_racers.append(racer_dict)
            print(all_racers)
            return render_template('ergast.html.j2', racers=all_racers)
        else:
            error_string = "Houston We had a problem"
            return render_template('ergast.html.j2', error = error_string)
            # The request fail
    return render_template('ergast.html.j2')

@main.route('/pokemon', methods=['GET', 'POST'])
def pokemon():
    id = session["_user_id"]
    user = User.query.get(id)
    # print(user.children.all())
    # print([element.sprite for element in user.children.all()])
    # print(user.email)

    if request.method == 'POST':
        name_of_pokemon = request.form.get('pokemon_name').lower()
        print(Pokemon.query.filter_by(name = name_of_pokemon.title()).all())
        the_list = []
        for item in Pokemon.query.filter_by(name = name_of_pokemon.title()).all():
            the_list.append(item.name)
        print(the_list)
        if the_list == []:

        # if name_of_pokemon.title() not in Pokemon.query.filter_by(name = name_of_pokemon.title()).all():
            url = f"https://pokeapi.co/api/v2/pokemon/{name_of_pokemon}"
            response = requests.request("GET", url)
            if response.ok:
                name = response.json()["name"].title()
                hp = response.json()["stats"][0]["base_stat"]
                attack = response.json()["stats"][1]["base_stat"]
                defense = response.json()["stats"][2]["base_stat"]
                ability = response.json()["abilities"][0]["ability"]["name"]
                sprite = response.json()["sprites"]["front_shiny"]

                entry = Pokemon(name, hp, attack, defense, ability, sprite)

                db.session.add(entry)
                db.session.commit()
            else:
                error_string = f'Could not find Pokemon with name "{name_of_pokemon}". Please confirm your spelling is accurate.'
                return render_template('pokemon.html.j2', error = error_string)
        else:
            print(f"The list is not empty and its contents are as follows: {the_list}")
    # else:
            # print(Pokemon.query.filter_by(name = name_of_pokemon.title()).all()[0].name)



    return render_template('pokemon.html.j2', user=user)

    # You may have to stringify the dictionary... Keep an eye out for that.

@main.route('/delete/<id>', methods = ['GET', 'POST'])
def delete(id):
    session_id = session["_user_id"]
    print(type(id))
    db.session.execute(f"DELETE FROM association where pokemon_id = '{id}' and user_id = '{session_id}'")
    db.session.commit()
    cursor.execute(f"SELECT * FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{session_id}';")
    data = cursor.fetchall()

    return render_template('pokemon.html.j2', data=data)
