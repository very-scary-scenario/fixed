import os
from random import choice
from string import ascii_lowercase

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


def filename_for_code(lobby_code):
    return os.path.join(LOBBIES_DIR, lobby_code)


def generate_lobby_code():
    code = ''.join((choice(ascii_lowercase) for c in range(4)))
    open(filename_for_code(code), 'a').close()
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
        if not code:
            return redirect('/')
        else:
            session['playing_lobby'] = code
            return redirect('/play')

    elif mode == 'start':
        session['hosting_lobby'] = generate_lobby_code()
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
    if not validate_lobby_code(session.get('playing_lobby')):
        return redirect('/')
    with open(filename_for_code(session.get('playing_lobby')), 'a') as lf:
        lf.write(entry)
        lf.write('\n')
    return redirect('')


@app.route('/_categories', methods=['POST'])
def _categories():
    return jsonify(get_categories_shortlist())


@app.route('/_prompt', methods=['POST'])
def _prompt():
    category_name = request.form.get('category')
    category = CATEGORIES.get(category_name)
    if not category:
        return '', 400
    # wipe out the existing submissions
    session_code = validate_lobby_code(session.get('hosting_lobby'))
    if session_code:
        open(filename_for_code(session_code), 'w').close()
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
    with open(filename_for_code(
        validate_lobby_code(session.get('hosting_lobby'))
    )) as ef:
        return jsonify([
            e.strip() for e in ef.readlines() if e.strip()
        ])
