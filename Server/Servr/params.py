import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from Servr.db import get_db
from Servr.auth import login_required

bp = Blueprint('params', __name__,url_prefix='/params')

@bp.route('/setparams',methods=('GET', 'POST'))
@login_required
def setparams():
    if request.method == 'POST':
        db = get_db()
        temp = request.form['Temperature']
        co2 = request.form['Carbon Dioxide']
        rh = request.form['Humidity']
        
        error = None
        
        if float(co2)>15:
            error = 'CO2 limit exceeded (15%)'
        elif float(temp)>30:
            error = 'Temperature limit exceeded (30C)'
        elif float(rh)>90:
            error = 'Relative Humidity limit exceeded (30C)'
        if error == None:
            try:
                db.execute("DELETE FROM params;")
                db.commit()
                db.execute(
                    "INSERT INTO params (temperature, rh, co2) VALUES (?, ?, ?)",
                    (temp, rh, co2),
                )
                db.commit()
            except db.IntegrityError:
                error = "User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        if error != None:
            flash(error)
        
    return render_template('params/setparams.html')

