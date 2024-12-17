import io
from io import BytesIO

import pandas as pd
from flask import Flask, redirect, url_for, request, session, render_template, jsonify, flash, send_file
import psycopg2

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Utilisez une clé secrète robuste

# Liste des agences et leur code


list_agence = ["Head Office", "akwa", "bonaberi", "new-bell", "bonamoussadi", "ndokoti", "dakar", "mboppi", "nlongkak",
               "mokolo",
               "biyem-assi", "bamenda", "limbe", "bafoussam", "kumba", "buea", "dschang", "bangangte", "kousseri",
               "melong"]
code_agence = {"AKWA": 1, "BONABERI": 2, "NEWBELL": 3, "BONAMOUSSADI": 4, "NDOKOTI": 5, "DAKAR": 6, "MBOPPI": 7,
               "NLONGKAK": 8, "MOKOLO": 9, "BIYEM ASSI": 10, "BAMENDA": 11, "LIMBE": 12, "BAFOUSSAM": 13, "KUMBA": 14,
               "BUEA": 15, "DSCHANG": 16, "SANGMELIMA": 17, "BANGANGTE": 18, "MAGBA": 19, "KOUSSERI": 20, "MELONG": 21}


# Routes


def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('verified'):
            return redirect(url_for('verification'))
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


@app.route("/verification", methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        code = ''.join(request.form.get(f'code{i}', '') for i in range(1, 6))
        if code == "19965":
            session['verified'] = True
            return redirect(url_for('admin'))
        else:
            error = "Le code est incorrect. Veuillez réessayer."
            return render_template("verification.html", error=error)
    return render_template("verification.html")


@app.route("/")
def hello():
    try:
        conn = connect_db()
        conn.close()
        return redirect(url_for('welcome'))

    except psycopg2.Error as e:
        return f"Erreur de connexion à la BD : {e}"


def connect_db():
    return psycopg2.connect(
        database="leasing_db", user='postgres', password='kally@2003', host="127.0.0.1", port="5432"
    )


@app.route("/admin")
@login_required
def admin():
    per_page = 10
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM leasing_db LIMIT %s OFFSET %s", (per_page, offset))
            rows = cur.fetchall()

            cur.execute("SELECT COUNT(*) FROM leasing_db")
            total_count = cur.fetchone()[0]

    total_pages = (total_count + per_page - 1) // per_page
    return render_template("./admin/dashboard.html", rows=rows, page=page, total_pages=total_pages,
                           total_count=total_count, list_agence=list_agence)


@app.route("/welcome")
def welcome():
    return render_template('home.html')


@app.route("/addinfo", methods=['POST'])
def addinfo():
    if request.method == 'POST':
        try:
            # Retrieve form data
            nm = request.form['nm']
            numag = request.form['numag']
            numcompte = request.form['numcompte']
            cle = request.form['cle']
            nom = request.form['nom']
            prenom = request.form['prenom']
            besoin = request.form['besoin']
            montant = request.form['montant']

            # Check if the data already exists in the database
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM leasing_db WHERE num_compte = %s AND num_ag = %s AND cle = %s",
                                (numcompte, numag, cle))
                    if cur.fetchone():
                        msg = "Erreur : Ce numéro de compte a déjà été enregistré !"
                        flash(msg, 'danger')
                        return render_template('error.html', msg=msg)

            # Check for empty fields
            if not all([nm, numag, numcompte, cle, nom, prenom, besoin, montant]):
                msg = "Veuillez remplir tous les champs !"
                flash(msg, 'danger')
                return render_template('error.html', msg=msg)

            # Execute the INSERT
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO leasing_db (agence, num_ag, num_compte, cle, nom, prenom, besoin, montant)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (nm, numag, numcompte, cle, nom, prenom, besoin, montant))
                conn.commit()

            msg = "Votre demande a été enregistrée avec succès"
            flash(msg, 'success')
            return render_template('resultats.html', msg=msg)
        except Exception as e:
            msg = "Erreur de l'enregistrement de la demande. Veuillez reessayer !"
            flash(msg, 'danger')
            return render_template('error.html', msg=msg)

    return render_template('formulaire.html', list_agence=list_agence, code_agence=code_agence)


@app.route("/register")
def register():
    return render_template("formulaire.html", list_agence=list_agence, code_agence=code_agence)


@app.route("/results")
def results():
    return render_template('resultats.html')


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit(id):
    # Connexion à la base de données
    with connect_db() as conn:
        with conn.cursor() as cur:
            if request.method == 'POST':
                try:
                    # Récupération des données du formulaire
                    agence = request.form['agence']
                    numag = request.form['numag']
                    numcompte = request.form['numcompte']
                    cle = request.form['cle']
                    nom = request.form['nom']
                    prenom = request.form['prenom']
                    besoin = request.form['besoin']
                    montant = request.form['montant']

                    # Mise à jour des données dans la base de données
                    cur.execute("""
                        UPDATE leasing_db
                        SET agence = %s, num_ag = %s, num_compte = %s, cle = %s, nom = %s, prenom = %s, besoin = %s, montant = %s
                        WHERE id = %s
                    """, (agence, numag, numcompte, cle, nom, prenom, besoin, montant, id))
                    conn.commit()

                    msg = "Demande mise à jour avec succès"
                    return render_template('admin/data/success.html', msg=msg)

                except KeyError as e:
                    # Gestion d'erreur si un champ du formulaire est manquant
                    app.logger.warning(f"Champ manquant dans le formulaire : {e}")
                    flash(f"Un champ requis est manquant : {e}", 'warning')
                except Exception as e:
                    # Gestion d'autres exceptions générales
                    app.logger.error(f"Erreur lors de la mise à jour : {e}")
                    flash("Une erreur est survenue lors de la mise à jour.", 'danger')

            # Récupération des données actuelles pour les afficher dans le formulaire
            cur.execute("SELECT * FROM leasing_db WHERE id = %s", (id,))
            row = cur.fetchone()
            app.logger.debug(f"Fetched Row: {row}")
            if not row:
                flash("Demande introuvable", 'danger')
                return redirect(url_for('admin'))

    # Chargement du formulaire avec les données actuelles
    return render_template('admin/data/edit.html', row=row, id=id)


@app.route("/success")
def success():
    return render_template('admin/data/success.html')


@app.route("/delete/<int:id>", methods=['GET', 'POST'])
@login_required
def delete(id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM leasing_db WHERE id = %s", (id,))
                conn.commit()
        flash("Demande supprimée avec succès", 'success')
        return redirect(url_for('admin'))
    except Exception as e:
        msg = f"Erreur lors de la suppression de la demande: {e}"
        flash(msg, 'danger')
        return render_template('error.html', msg=msg)


@app.route("/export_excel")
@login_required
def export_excel():
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT agence, num_ag, num_compte, cle, nom, prenom, besoin, montant FROM leasing_db")
                rows = cur.fetchall()

        if not rows:
            flash("Aucune donnée à exporter.", "warning")
            return redirect(url_for("admin"))

        columns = ["Agence", "Numéro d'agence", "Numéro de compte", "Cle", "Nom", "Prenom", "Besoin", "Montant"]
        df = pd.DataFrame(rows, columns=columns)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="LeasingData")
        output.seek(0)

        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            download_name="leasing_data.xlsx",
            as_attachment=True,
        )
    except Exception as e:
        app.logger.error(f"Erreur lors de l'exportation : {e}")
        flash(f"Erreur lors de l'exportation des données : {e}", "danger")
        return redirect(url_for("admin"))


@app.route("/logout")
def logout():
    session.pop('verified', None)
    flash("Déconnexion réussie", 'info')
    return redirect("/")


if __name__ == "__main__":
    app.run()
