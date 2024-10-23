from flask import Flask, redirect
from flask import render_template
from flask import request
import sqlite3
import pandas as pd
import io

list_agence = ["akwa", "bonaberi", "new-bell", "bonamoussasi", "ndokoti", "dakar", "mboppi", "nlongkak", "mokolo",
               "biyem-assi", "bamenda", "limbe", "bafoussam", "kumba", "buea", "dschang", "bangangte", "kousseri",
               "melong"]
code_agence = {"AKWA": 1, "BONABERI": 2, "NEWBELL": 3, "BONAMOUSSADI": 4, "NDOKOTI": 5, "DAKAR": 6, "MBOPPI": 7,
               "NLONGKAK": 8, "MOKOLO": 9, "BIYEM ASSI": 10, "BAMDENDA": 11, "LIMBE": 12, "BAFOUSSAM": 13, "KUMBA": 14,
               "BUEA": 15, "DSCHANG": 16, "SANGMELIMA": 17, "BANGANGTE": 18, "MAGBA": 19, "KOUSSERI": 20, "MELONG": 21}
app = Flask(__name__)


@app.route("/")  # home page
def home():
    return render_template("home.html")


@app.route("/register")
def register():
    return render_template("formulaire.html", list_agence=list_agence, code_agence=code_agence)


@app.route("/addinfo", methods=['POST', 'GET'])
def addinfo():
    if request.method == 'POST':
        try:
            nm = request.form['nm']  # Agence
            numag = request.form['numag']  # Numero Agence
            numcompte = request.form['numcompte']  # Numero Compte
            cle = request.form['cle']  # Clé
            nom = request.form['nom']  # Nom Prénom
            prenom = request.form['prenom']  # Prénom
            besoin = request.form['besoin']  # Besoin
            montant = request.form['montant']  # Montant

            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO leasing (agence, num_ag, num_compte, cle, nom, prenom, besoin, montant) VALUES (?,?,?,?,?,?,?,?)",
                    (nm, numag, numcompte, cle, nom, prenom, besoin, montant))

                con.commit()
                msg = "Votre demande a été enregistrée avec succès"
        except:
            con.rollback()
            msg = "Erreur de l'enregistrement de la demande"


        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('resultats.html', msg=msg)


@app.route("/verification", methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        code = (
                request.form.get('code1', '') +
                request.form.get('code2', '') +
                request.form.get('code3', '') +
                request.form.get('code4', '') +
                request.form.get('code5', '')
        )

        if code == "19965":
            # Redirection vers le dashboard admin si le code est correct
            return redirect("/admin")
        else:
            error = "Le code est incorrect. Veuillez réessayer."
            return render_template("verification.html", error=error)

    return render_template("verification.html")


@app.route("/admin")
def admin():
    try:
        # Connexion à la base de données SQLite
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()

            # Nombre d'éléments par page
            per_page = 10

            # Récupérer le numéro de la page actuelle à partir des paramètres de requête
            page = request.args.get('page', 1, type=int)

            # Calculer l'offset (combien d'enregistrements sauter pour chaque page)
            offset = (page - 1) * per_page

            # Requête SQL pour récupérer les données paginées
            cur.execute("SELECT * FROM leasing LIMIT ? OFFSET ?", (per_page, offset))
            rows = cur.fetchall()  # Récupération des lignes de la page actuelle

            # Requête pour récupérer le nombre total d'enregistrements
            cur.execute("SELECT COUNT(*) FROM leasing")
            total_count = cur.fetchone()[0]

            # Calculer le nombre total de pages
            total_pages = (total_count + per_page - 1) // per_page  # Arrondi vers le haut

        # Passer les données paginées et les informations de pagination au template
        return render_template("admin/dashboard.html",
                               rows=rows,
                               page=page,
                               total_pages=total_pages,
                               total_count=total_count)

    except Exception as e:
        return f"Une erreur s'est produite lors de la récupération des données : {e}"


@app.route("/admin/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    try:
        # Connexion à la base de données SQLite
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("DELETE FROM leasing WHERE id=?", (id,))
            con.commit()
            return f"La demande a été supprimée avec succès"
    except:
        con.rollback()
        return f"Une erreur s'est produite lors de la suppression de la demande"

    finally:
        con.close()
        # Redirection vers le dashboard admin avec le message de suppression
        return redirect("/admin")


@app.route("/admin/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        agence = request.form['agence']
        numag = request.form['numag']
        numcompte = request.form['numcompte']
        cle = request.form['cle']
        nom = request.form['nom']
        prenom = request.form['prenom']
        besoin = request.form['besoin']
        montant = request.form['montant']

        try:
            # Connexion à la base de données SQLite
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE leasing SET agence=?, num_ag=?, num_compte=?, cle=?, nom=?, prenom=?, besoin=?, montant=? WHERE id=?",
                    (agence, numag, numcompte, cle, nom, prenom, besoin, montant, id))
                con.commit()
                msg = "La demande a été modifiée avec succès"
        except:
            con.rollback()
            msg = "Erreur de modification de la demande"

        finally:
            con.close()
            # Redirection vers le dashboard admin avec le message de modification
            return redirect("/admin", msg=msg)

    else:
        # Connexion à la base de données SQLite
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM leasing WHERE id=?", (id,))
            row = cur.fetchone()

        return render_template("admin/edit.html", row=row)

@app.route("/export_excel")
def export_excel():
    try:
        # Connexion à la base de données SQLite
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            # Requête SQL pour récupérer toutes les données
            cur.execute("SELECT * FROM leasing")
            rows = cur.fetchall()

            # Récupérer les colonnes de la table pour le DataFrame
            cur.execute("PRAGMA table_info(leasing)")
            columns = [description[1] for description in cur.fetchall()]

            # Convertir les résultats en DataFrame pandas
            df = pd.DataFrame(rows, columns=columns)

            # Créer un fichier Excel en mémoire
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='LeasingData')

            # Repositionner le curseur du fichier à 0
            output.seek(0)

            # Envoyer le fichier Excel en tant que réponse
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             download_name='leasing_data.xlsx', as_attachment=True)

    except Exception as e:
        return f"Erreur lors de l'exportation des données : {e}"


if __name__ == "__main__":
    app.run(debug=True)
