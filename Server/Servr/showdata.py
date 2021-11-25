import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from Servr.db import get_db
from Servr.auth import login_required

bp = Blueprint('showdata', __name__)
@bp.route('/')
@login_required
def index():
    db = get_db()
    currentparams = db.execute(
        'SELECT temperature, rh, co2 FROM params;').fetchall()
    return render_template('showdata/index.html', currentparams=currentparams)