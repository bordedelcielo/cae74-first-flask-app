from .import bp as battle
from flask import render_template, session
import random
from app.models import User

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
    # print(output_dictionary[1][0][0])
    # print(working_dictionary)
    return render_template('arena.html.j2', data=data, dictionary = output_dictionary)

@battle.route('/challenge/<id_for_use>', methods = ['GET', 'POST'])
def challenge(id_for_use):
    session_id = session["_user_id"]
    playerOne = session_id
    playerTwo = id_for_use
    dice = (1,2,3,4,5,6)
    playerOneDice = random.choice(dice)
    print(playerOneDice)
    playerTwoDice = random.choice(dice)
    print(playerTwoDice)
    cursor.execute(f"SELECT attack FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{playerOne}';")
    playerOneData = cursor.fetchall()
    total_attack = 0
    for i in playerOneData:
        print(f'Here is i: {i[0]}')
        total_attack = total_attack + i[0] ** 2
    total_attack = total_attack * playerOneDice
    print(f'Here is the total attack: {total_attack}')
    cursor.execute(f"SELECT hp, defense FROM pokemon INNER JOIN association ON association.pokemon_id = pokemon.the_pokemon_id WHERE user_id = '{playerTwo}';")
    playerTwoData = cursor.fetchall()
    total_defense = 0
    for j in playerTwoData:
        print(f'Here is j: {j[0]} and {j[1]}')
        total_defense = total_defense + j[0] * j[1]
    total_defense = total_defense * playerTwoDice
    if total_defense >= total_attack:
        winner = playerTwo
        print(f"Player Two is the winner.")
    else:
        winner = playerOne
        print(f"Player One is the winner.")
    print(f"Here is the total defense: {total_defense}")
    print(User.query.get(winner))
    print(User.query.get(winner).last_name)
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
    return render_template('arena.html.j2', data=data, dictionary = output_dictionary)