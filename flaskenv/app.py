import os
from flask import Flask, render_template, request, url_for, redirect, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# TODO: figure out how this works 
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import *


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# initialize the app with the extension
app.json.compact = False

CORS(app)


migrate = Migrate(app, db)
db.init_app(app)
migrate.init_app(app, db)

@app.route("/")
def base():
    with app.app_context():
        db.create_all()

    return "<h1>heya world!</h1>"

@app.route("/entry/get/<id>")
# TODO: make this something that falls under user so that it gets all of their entries
def entry_get(id):
    # return all the list contents; right now, there's just one
    # entry = db.first_or_404(Entry, id)
    entry = db.first_or_404(Entry, id)
    return entry

@app.route("/entry/update/<id>", methods=['POST'])
def entry_update(id):
    try:
        json_data = request.get_json()
        entry_id = json_data.get("entry_id")
        entry = db.session.query(Entry).filter_by(entry_id=entry_id).first()
        if not entry:
            return jsonify({"error": "Entry not found, cannot update"}), 404
        
        entry.show_id = json_data.get("show_id", entry.show_id)
        entry.notes = json_data.get("notes", entry.notes)
        entry.is_watched = json_data.get("is_watched", entry.is_watched)
        entry.user_id = json_data.get("user_id", entry.user_id)
        
        db.session.commit()
        
        return jsonify({"message": "Entry updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route("/entry/add/<id>", methods=['POST'])
# TODO: need id?
def entry_add(id):
    try:
        json_data = request.get_json()
        new_entry = Entry(json.dumps(json_data))
        
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({"message": "Entry added successfully"}), 200
    except Exception as ex:
        db.session.rollback()
        return jsonify({"error": str(ex)}), 400

@app.route("/entry/delete/<id>", methods=['POST'])
def entry_delete(id):
    try:        
        to_delete = get_entry(id)
        db.session.delete(to_delete)
        db.session.commit()
        
        return jsonify({"message": "Entry deleted successfully"}), 200
    except Exception as ex:
        db.session.rollback()
        return jsonify({"error": str(ex)}), 400


@app.route("/show/add/<id>", methods=['POST'])
# TODO: id necessary here?
def show_add(id):
    try:
        json_data = request.get_json()

        new_show = Show(json.dumps(json_data))
        
        db.session.add(new_show)
        db.session.commit()
        
        return jsonify({"message": "Show entry deleted successfully"}), 200
    except Exception as ex:
        db.session.rollback()
        return jsonify({"error": str(ex)}), 400


@app.route("/show/delete/<id>", methods=['POST'])
def show_delete(id):
    try:
        to_delete = get_show(id)
        db.session.delete(to_delete)
        db.session.commit()
        
        return jsonify({"message": "Show entry deleted successfully"}), 200
    except Exception as ex:
        db.session.rollback()
        return jsonify({"error": str(ex)}), 400


# TODO: fix this being inconsistent, make it a user method
@app.route("/entry/get/watched")
def entry_get_watched():
    return db.session.query(Entry).filter_by(is_watched=True).all()


# helper functions
def get_show(id):
    return db.session.query(Show).filter_by(show_id=id)

def get_entry(id):
    return db.session.query(Entry).filter_by(entry_id=id)
