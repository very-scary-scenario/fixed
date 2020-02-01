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

from game import CATEGORIES, VERSIONS, get_categories_shortlist

app = Flask(__name__)
app.secret_key = 'XXX'  # XXX


def validate_lobby_code(code):
    # XXX normalise it and check it exists
    code = code.lower()
    if (
        isinstance(code, str)
    ):
        return code


def generate_lobby_code():
    return ''.join((choice(ascii_lowercase) for c in range(4)))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def dispatch():
    if request.form.get('lobby'):
        raise NotImplementedError(
            'validate code, add lobby code to session, redirect to player'
        )
    else:
        session['hosting_lobby'] = generate_lobby_code()
        return redirect('/host')


@app.route('/host')
def host():
    session_code = session.get('hosting_lobby')
    if session_code:
        return render_template('host.html', session_code=session_code)
    else:
        return redirect('/')


@app.route('/player')
def player():
    return render_template('player.html')


@app.route('/_categories', methods=['POST'])
def _categories():
    return jsonify(get_categories_shortlist())


@app.route('/_prompt', methods=['POST'])
def _prompt():
    category = CATEGORIES.get(request.form.get('category'))
    if not category:
        return '', 400
    product = choice(category)
    product['version'] = choice(VERSIONS)
    if product['comments']:
        product['comment'] = choice(product['comments'])
    return product
