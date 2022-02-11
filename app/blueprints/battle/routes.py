from .import bp as battle
from flask import render_template, session

from app.secrets import con

cursor = con.cursor()

@battle.route('/arena', methods = ['GET', 'POST'])
def arena():
    id = session["_user_id"]
    cursor.execute(f"SELECT first_name, id FROM public.user WHERE id <> '{id}'")
    data = cursor.fetchall()
    output_dictionary = {}
    for row in data:
        cursor.execute(f"SELECT name, sprite FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{row[1]}';")
        poke_data = cursor.fetchall()
        working_dictionary = {row[1]: poke_data}
        # print(working_dictionary)
        output_dictionary.update(working_dictionary)
    # print(data)
    # print(data[0][1])
    # print(output_dictionary)
    print(output_dictionary[1][0][0])
    # print(working_dictionary)
    return render_template('arena.html.j2', data=data, dictionary = output_dictionary)