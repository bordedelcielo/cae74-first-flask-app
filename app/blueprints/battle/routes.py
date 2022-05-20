from .import bp as battle
from flask import render_template, session
import random
from app.models import User, db

@battle.route('/arena', methods = ['GET', 'POST'])
def arena():
    id = session["_user_id"]
    test = User.query.all()
    output_dictionary = {}
    user_list = []
    for item in test:
        if item.id != int(id):
            user_list.append(item)
            user = User.query.get(item.id)
            children_list = [element.sprite for element in user.children.all()]
            working_dictionary = {item.first_name: children_list}
            output_dictionary.update(working_dictionary)

    return render_template('arena.html.j2', data = test, output_dictionary = output_dictionary, user_list = user_list)

@battle.route('/challenge/<id_for_use>', methods = ['GET', 'POST'])
def challenge(id_for_use):

    dice = (1,2,3,4,5,6)
    playerOneDice = random.choice(dice)
    playerTwoDice = random.choice(dice)

    playerOneId = session["_user_id"]
    playerTwoId = id_for_use

    playerOne = User.query.get(playerOneId)
    playerTwo = User.query.get(playerTwoId)

    playerOnePokemon = User.query.get(playerOneId).children.all()
    print(playerOnePokemon)
    print(type(playerOnePokemon))
    total_attack = 0
    for i in playerOnePokemon:
        total_attack = total_attack + i.attack ** 2
    total_attack = total_attack * playerOneDice
    print(total_attack)

    playerTwoPokemon = User.query.get(playerTwoId).children.all()
    total_defense = 0
    for i in playerTwoPokemon:
        total_defense = total_defense + i.defense * i.hp
    total_defense = total_defense * playerTwoDice
    print(total_defense)

    if total_attack > total_defense:
        playerOne.wins += 1
        playerTwo.losses += 1
        print(playerOne)
    else:
        playerTwo.wins += 1
        playerOne.losses += 1
        print(playerTwo)
    db.session.commit()

    return arena()