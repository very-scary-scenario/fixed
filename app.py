import os
import json
from random import choice, shuffle
from string import ascii_lowercase
from uuid import uuid4

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
)

from game import CATEGORIES, get_categories_shortlist
from version import random_version

LOBBIES_DIR = os.path.join(os.path.dirname(__file__), 'lobbies')
if not os.path.isdir(LOBBIES_DIR):
    os.mkdir(LOBBIES_DIR)

app = Flask(__name__)
app.secret_key = str(os.urandom(32))


def validate_lobby_code(code):
    code = code.lower()
    if (
        isinstance(code, str) and
        code in os.listdir(LOBBIES_DIR)
    ):
        return code


def entry_filename_for_code(lobby_code):
    return os.path.join(LOBBIES_DIR, lobby_code)


def state_filename_for_code(lobby_code):
    return entry_filename_for_code(lobby_code) + '.json'


def load_state(lobby_code):
    with open(state_filename_for_code(lobby_code), 'r') as rsf:
        return json.load(rsf)


def save_state(lobby_code, state):
    with open(state_filename_for_code(lobby_code), 'w') as wsf:
        return json.dump(state, wsf)


def generate_lobby_code():
    code = ''.join((choice(ascii_lowercase) for c in range(4)))
    open(entry_filename_for_code(code), 'a').close()
    return code


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def dispatch():
    code = request.form.get('lobby')
    mode = request.form.get('mode')

    if mode == 'join':
        code = validate_lobby_code(code)
        name = request.form.get('name')

        if not (code and name):
            return redirect('/')
        else:
            session['playing_lobby'] = code
            session['name'] = (
                name.replace('\n', '').replace('\r', '').replace('#', '')
            )
            session['player_uuid'] = str(uuid4())
            state = load_state(code)
            state['players'][session['player_uuid']] = {
                'name': name,
                'score': 0,
                'turns': 0,
            }
            save_state(code, state)
            return redirect('/play')

    elif mode == 'start':
        code = generate_lobby_code()
        session['hosting_lobby'] = code
        save_state(code, {'players': {}})
        return redirect('/host')


@app.route('/host')
def host():
    session_code = session.get('hosting_lobby')
    if session_code:
        return render_template('host.html', session_code=session_code)
    else:
        return redirect('/')


@app.route('/play')
def play():
    return render_template('player.html')


@app.route('/play', methods=['POST'])
def log_entry():
    entry = request.form.get('entry')

    if not entry.strip():
        return redirect('')

    if not validate_lobby_code(session.get('playing_lobby')):
        return redirect('/')

    with open(
        entry_filename_for_code(session.get('playing_lobby')), 'a',
    ) as lf:
        lf.write('{}#{}#{}'.format(
            session.get('name'),
            session.get('player_uuid'),
            entry.replace('\n', '').replace('\r', ''),
        ))
        lf.write('\n')

    return redirect('')


@app.route('/_categories', methods=['POST'])
def _categories():
    state = load_state(session.get('hosting_lobby'))

    if not state['players']:
        return 'Get some people to join the session first.', 400

    winner = request.form.get('winner')
    if winner and winner in state['players']:
        state['players'][winner]['score'] += 1

    judge = request.form.get('judge')
    if judge and judge in state['players']:
        state['players'][judge]['turns'] += 1

    fewest_turns = min((
        pl['turns'] for pl in state['players'].values()
    ))
    player_id = choice([
        uuid for uuid, p in state['players'].items()
        if p['turns'] == fewest_turns
    ])
    save_state(session.get('hosting_lobby'), state)

    turn_set = {p['turns'] for p in state['players'].values()}
    if len(turn_set) == 1:
        turn, = turn_set
        if turn == 0:
            message = None
        else:
            message = (
                'Round complete! The scores are:\n\n{}'
                .format('\n'.join((
                    '{name}: {score}'.format(**p) for p in sorted(
                        state['players'].values(),
                        key=lambda pl: pl['score'], reverse=True
                    )
                )))
            )
    else:
        message = None

    return jsonify({
        'categories': get_categories_shortlist(),
        'player': {
            'uuid': player_id, 'name': state['players'][player_id]['name'],
        },
        'message': message,
    })


@app.route('/_prompt', methods=['POST'])
def _prompt():
    category_name = request.form.get('category')
    category = CATEGORIES.get(category_name)
    if not category:
        return '', 400
    # wipe out the existing submissions
    session_code = validate_lobby_code(session.get('hosting_lobby'))
    if session_code:
        open(entry_filename_for_code(session_code), 'w').close()
    else:
        return '', 400

    product = choice(category['releases'])
    product['version'] = random_version()
    product['category'] = category_name
    if product['comments'] or category['generic_comments']:
        product['comment'] = choice(
            product['comments'] or category['generic_comments']
        )
    return product


@app.route('/_entries', methods=['POST'])
def _entries():
    code = validate_lobby_code(session.get('hosting_lobby'))

    if not code:
        return '', 400

    with open(entry_filename_for_code(code)) as ef:
        entries = [{
            'name': name, 'uuid': uuid, 'entry': entry,
        } for name, uuid, entry in (
            e.strip().split('#', 2)
            for e in ef.readlines() if e.strip()
        )]
        shuffle(entries)
        return jsonify({
            'entries': entries,
        })
