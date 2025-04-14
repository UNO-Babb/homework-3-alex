from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Game config
BOARD_SIZE = 10
TREASURE_COUNT = 30

# Initialize game state
def init_game(player_count):
    board = [[{'player': None, 'treasure': False} for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    players = []
    
    # Place players at the start (0, 0)
    for i in range(player_count):
        players.append({
            'id': i,
            'pos': [0, 0],
            'treasure': 0,
            'color': ['red', 'blue', 'green', 'yellow'][i % 4]
        })
        board[0][0]['player'] = i

    # Place treasures randomly
    placed = 0
    while placed < TREASURE_COUNT:
        x = random.randint(0, BOARD_SIZE - 1)
        y = random.randint(0, BOARD_SIZE - 1)
        if not board[y][x]['treasure'] and (x, y) != (0, 0):
            board[y][x]['treasure'] = True
            placed += 1

    return board, players

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player_count = int(request.form.get('players', 2))
        board, players = init_game(player_count)
        session['board'] = board
        session['players'] = players
        session['current_turn'] = 0
        session['game_over'] = False
        session['last_roll'] = None
        return redirect(url_for('game'))
    return render_template('index.html')

@app.route('/game')
def game():
    board = session.get('board')
    players = session.get('players')
    current_turn = session.get('current_turn')
    game_over = session.get('game_over')
    last_roll = session.get('last_roll')
    return render_template('game.html', board=board, players=players, current_turn=current_turn, game_over=game_over, last_roll=last_roll)

@app.route('/roll')
def roll():
    if session.get('game_over'):
        return redirect(url_for('game'))

    board = session['board']
    players = session['players']
    turn = session['current_turn']

    player = players[turn]
    roll = random.randint(1, 6)
    session['last_roll'] = roll

    # Convert position to linear index for 1D movement
    x, y = player['pos']
    index = y * BOARD_SIZE + x
    index += roll
    max_index = BOARD_SIZE * BOARD_SIZE - 1
    if index > max_index:
        index = max_index

    # Convert linear index back to position
    new_y = index // BOARD_SIZE
    new_x = index % BOARD_SIZE

    # Update board
    old_x, old_y = player['pos']
    if board[old_y][old_x]['player'] == player['id']:
        board[old_y][old_x]['player'] = None

    if board[new_y][new_x]['treasure']:
        player['treasure'] += 1
        board[new_y][new_x]['treasure'] = False

    board[new_y][new_x]['player'] = player['id']
    player['pos'] = [new_x, new_y]

    # Check if all players have reached the end
    all_done = all(p['pos'] == [BOARD_SIZE - 1, BOARD_SIZE - 1] for p in players)
    session['game_over'] = all_done

    # Move to next player
    session['current_turn'] = (turn + 1) % len(players)
    session['board'] = board
    session['players'] = players

    return redirect(url_for('game'))

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
