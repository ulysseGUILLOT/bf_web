from app import app
from flask import render_template, redirect, url_for, request, jsonify
from models import User, Game, GamesUsers
from init_db import db_session
import random

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return render_template("user/list.html", users=users)

@app.route("/users/new", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        username = request.form["username"]
        new_user = User(username=username)
        db_session.add(new_user)
        db_session.commit()
        return redirect(url_for('get_all_users'))
    return render_template("user/new.html")

@app.route("/users/delete", methods=["DELETE"])
def delete_user():
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    if user :
        for game_user_assoc in user.games :
            db_session.delete(game_user_assoc)
        db_session.delete(user)
        db_session.commit()
        return 'success'
    else :
        return 'user not found'

@app.route("/games", methods=["GET"])
def get_all_games():
    games = Game.query.all()
    return render_template("game/list.html", games=reversed(games))

@app.route("/games/new", methods=["GET", "POST"])
def new_game():
    if request.method == "POST":
        selected_player_ids = request.form.getlist('selected_players')
        auto_choice_checkbox = 'true' in request.form.getlist('auto-choice')

        game = Game()

        if len(selected_player_ids) < 2 :
            return 'Nombre de joueur sélectionné insuffisant'

        def assign_user_to_team(user_id, team):
            user = User.query.get(user_id)
            if user:
                game_user_assoc = GamesUsers(team=team)
                game_user_assoc.game = game
                game_user_assoc.user = user
                game.users.append(game_user_assoc)
                user.games.append(game_user_assoc)
                user.matches = user.matches + 1
            else:
                return 'erreur : joueur introuvable'

        if auto_choice_checkbox:
            random.shuffle(selected_player_ids)
            team_size = len(selected_player_ids) // 2
            for idx, player_id in enumerate(selected_player_ids):
                assign_user_to_team(player_id, idx < team_size)
        else:
            for player_id in selected_player_ids:
                assign_user_to_team(player_id, 1)

        db_session.add(game)
        db_session.commit()
        return redirect(url_for("play_game", game_id=game.id))
    
    # GET method
    else:
        users = User.query.all()
        return render_template("game/new.html", users=users)


@app.route("/games/<int:game_id>")
def play_game(game_id):
    game = Game.query.get(game_id)
    if game:
        return render_template("game/play.html", game=game)
    else:
        return 'no game'
    
@app.route("/games/<int:game_id>/goal", methods=["POST"])
def goal(game_id):
    if request.method == "POST" :
        score_type = request.form.get('score_type')
        user_id = request.form.get('user_id')
        game = Game.query.get(game_id)
        user = User.query.get(user_id)
        if game and user :
            team = -1
            for assoc in user.games :
                if assoc.game.id == game.id :
                    team = assoc.team
            if team != -1 :
                if game.finished == False :
                    if team == 0 and score_type == 'goal' :
                        game.white_score = game.white_score + 1
                    elif team == 1 and score_type == 'goal' :
                        game.black_score = game.black_score + 1
                    elif team == 0 and score_type == 'bounce_out' :
                        game.black_score = game.black_score - 1
                    elif team == 1 and score_type == 'bounce_out' :
                        game.white_score = game.white_score -1
                    elif team == 0 and score_type == 'own_goal' :
                        game.black_score = game.black_score + 1
                    elif team == 1 and score_type == 'own_goal' :
                        game.white_score = game.white_score + 1
                    elif team == 0 and score_type == 'own_bounce_out' :
                        game.white_score = game.white_score -1
                    elif team == 1 and score_type == 'own_bounce_out' :
                        game.black_score = game.black_score - 1


                    if score_type == 'goal' :
                        user.goals_total = user.goals_total + 1
                    else :
                        user.bounce_out_total = user.bounce_out_total + 1
                
                # detection de fin de partie
                if game.white_score == 10 or game.black_score == 10 or game.white_score == -10 or game.black_score == -10 :
                    game.finished = True
                    db_session.commit()
                    return jsonify({'message': 'end_game'})
                else :
                    db_session.commit()

                return jsonify({'white_score': game.white_score, 'black_score': game.black_score})
            else :
                return "error while retrieving user's team"
        else :
            return 'error while retrieving user or game'    

@app.route("/games/<int:game_id>/end")
def end_game(game_id):
    game = Game.query.get(game_id)
    if game :
        return render_template("game/end.html", game=game)
    else :
        return 'error while retrieving game'