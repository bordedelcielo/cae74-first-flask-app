from flask import render_template, request
import requests
from flask_login import login_required
from .import bp as main



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
    if request.method == 'POST':
        name_of_pokemon = request.form.get('pokemon_name')
        url = f"https://pokeapi.co/api/v2/pokemon/{name_of_pokemon}"
        response = requests.request("GET", url)
        if response.ok:
            if name_of_pokemon == "":
                error_string_poke="Please enter the name of a Pokemon"
                return render_template('pokemon.html.j2', error = error_string_poke)
            name = response.json()["name"]
            hp = response.json()["stats"][0]["base_stat"]
            attack = response.json()["stats"][1]["base_stat"]
            defense = response.json()["stats"][2]["base_stat"]
            ability = response.json()["abilities"][0]["ability"]["name"]
            sprite = response.json()["sprites"]["front_shiny"]
            return render_template('pokemon.html.j2', name=name, hp=hp, attack=attack, defense=defense,ability=ability,sprite=sprite)
        else:
            error_string = f'Could not find Pokemon with name "{name_of_pokemon}". Please confirm your spelling is accurate.'
            return render_template('pokemon.html.j2', error = error_string)
    return render_template('pokemon.html.j2')