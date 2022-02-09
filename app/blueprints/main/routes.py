from flask import render_template, request, session
import requests
from flask_login import login_required
from .import bp as main
from app.models import db, Pokemon, association_table, User

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
    cursor.execute(f"SELECT * FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{id}';")
    data = cursor.fetchall()
    if request.method == 'POST':
        name_of_pokemon = request.form.get('pokemon_name').lower()
        cursor.execute(f"select name from pokemon where name = '{name_of_pokemon.title()}'")
        result = cursor.fetchall()
        if result != []:
            test_name = result[0][0]
            cursor.execute(f"select hp from pokemon where name = '{test_name}'")
            hp = cursor.fetchall()[0][0]
            cursor.execute(f"select attack from pokemon where name = '{test_name}'")
            attack = cursor.fetchall()[0][0]
            cursor.execute(f"select defense from pokemon where name = '{test_name}'")
            defense = cursor.fetchall()[0][0]
            cursor.execute(f"select ability from pokemon where name = '{test_name}'")
            ability = cursor.fetchall()[0][0]
            cursor.execute(f"select sprite from pokemon where name = '{test_name}'")
            sprite = cursor.fetchall()[0][0]
            
            cursor.execute(f"select the_pokemon_id from pokemon where name = '{test_name}'")
            the_pokemon_id = cursor.fetchall()[0][0]
            id = session["_user_id"]
            cursor.execute(f"select pokemon_id from association where pokemon_id = '{the_pokemon_id}' and user_id = '{2}'")
            result = cursor.fetchall()
            cursor.execute(f"SELECT count(*) FROM association WHERE user_id = '{id}';")
            count_result = cursor.fetchall()[0][0]
            cursor.execute(f"SELECT * FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{id}';")
            data = cursor.fetchall()
            if count_result >= 5:
                error_string = f'You have already caught five Pokemon. Please remove a Pokemon from your inventory to make room to catch {test_name}.'
                return render_template('pokemon.html.j2', data=data, error = error_string)
            elif result == [] and count_result < 5:
                id = session["_user_id"]
                statement = association_table.insert().values(user_id = id, pokemon_id = the_pokemon_id)
                db.session.execute(statement)
                db.session.commit()
                cursor.execute(f"SELECT * FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{id}';")
                data = cursor.fetchall()
            else:
                cursor.execute(f"SELECT * FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{id}';")
                data = cursor.fetchall()
                pass

            return render_template('pokemon.html.j2', name=test_name, hp=hp, attack=attack, defense=defense,ability=ability,sprite=sprite, data=data)
        else:
            url = f"https://pokeapi.co/api/v2/pokemon/{name_of_pokemon}"
            response = requests.request("GET", url)
            if response.ok:
                if name_of_pokemon == "":
                    error_string_poke="Please enter the name of a Pokemon"
                    cursor.execute(f"SELECT * FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{id}';")
                    data = cursor.fetchall()
                    return render_template('pokemon.html.j2', data=data, error = error_string_poke)
                name = response.json()["name"].title()
                hp = response.json()["stats"][0]["base_stat"]
                attack = response.json()["stats"][1]["base_stat"]
                defense = response.json()["stats"][2]["base_stat"]
                ability = response.json()["abilities"][0]["ability"]["name"]
                sprite = response.json()["sprites"]["front_shiny"]

                entry = Pokemon(name, hp, attack, defense, ability, sprite)

                db.session.add(entry)
                db.session.commit()

                id = session["_user_id"]
                cursor.execute(f"SELECT count(*) FROM association WHERE user_id = '{id}';")
                count_result = cursor.fetchall()[0][0]
                cursor.execute(f"SELECT * FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{id}';")
                data = cursor.fetchall()

                if count_result >= 5:
                    error_string = f'You have already caught five Pokemon. Please remove a Pokemon from your inventory to make room to catch {name}.'
                    return render_template('pokemon.html.j2', data=data, error = error_string)
                else:
                    id = session["_user_id"]
                    cursor.execute(f"select the_pokemon_id from pokemon where name = '{name}'")
                    the_pokemon_id = cursor.fetchall()[0][0]
                    statement = association_table.insert().values(user_id = id, pokemon_id = the_pokemon_id)
                    db.session.execute(statement)
                    db.session.commit()

                pokemon_dictionary = {"Name":name, "Hp":hp, "Attack":attack,"Defense":defense,"Ability":ability,"Sprite":sprite}
                # print(pokemon_dictionary)
                return render_template('pokemon.html.j2', data=data, name=name, hp=hp, attack=attack, defense=defense,ability=ability,sprite=sprite, pokemon_dictionary = pokemon_dictionary)

            else:
                error_string = f'Could not find Pokemon with name "{name_of_pokemon}". Please confirm your spelling is accurate.'
                return render_template('pokemon.html.j2', error = error_string)
    return render_template('pokemon.html.j2', data=data)

    # You may have to stringify the dictionary... Keep an eye out for that.

@main.route('/delete/<id>', methods = ['GET', 'POST'])
def delete(id):
    session_id = session["_user_id"]
    db.session.execute(f"DELETE FROM association where pokemon_id = '{id}' and user_id = '{session_id}'")
    db.session.commit()
    cursor.execute(f"SELECT * FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{session_id}';")
    data = cursor.fetchall()

    return render_template('pokemon.html.j2', data=data)


@main.route('/addPoke/', methods = ['GET', 'POST'])
def addPoke():
    return render_template('pokemon.html.j2')
# def addPoke(name, hp, attack, defense, ability, sprite):
#     if request.method == 'POST':
#         name = request.form[]
#     pokemon_dictionary = {"Name":name, "Hp":hp, "Attack":attack,"Defense":defense,"Ability":ability,"Sprite":sprite}
#     print(pokemon_dictionary)
#     db.session.commit()