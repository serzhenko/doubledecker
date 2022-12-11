from flask import Flask
from flask import render_template
from markupsafe import escape

from data_models import *

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/view/<int:id>/')
def show_deck(id):
    return embed_deck(id)


@app.route('/embed/<int:id>/')
def embed_deck(id):
    deck = Deck.get_by_id(id)
    print(deck)
    if deck:
        return render_template('embed.html', id=escape(id), num_pages=deck.slides_count)
    else:
        return page_not_found()


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
