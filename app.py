from flask import Flask, redirect, send_file, render_template, request, session, url_for
import sqlite3
import pandas as pd
import io

# Initialize the Flask app and set the secret key
app = Flask(__name__)
app.secret_key = "your_secret_key"

list_agence = ["akwa", "bonaberi", "new-bell", "bonamoussasi", "ndokoti", "dakar", "mboppi", "nlongkak", "mokolo",
               "biyem-assi", "bamenda", "limbe", "bafoussam", "kumba", "buea", "dschang", "bangangte", "kousseri",
               "melong"]
code_agence = {"AKWA": 1, "BONABERI": 2, "NEWBELL": 3, "BONAMOUSSADI": 4, "NDOKOTI": 5, "DAKAR": 6, "MBOPPI": 7,
               "NLONGKAK": 8, "MOKOLO": 9, "BIYEM ASSI": 10, "BAMDENDA": 11, "LIMBE": 12, "BAFOUSSAM": 13, "KUMBA": 14,
               "BUEA": 15, "DSCHANG": 16, "SANGMELIMA": 17, "BANGANGTE": 18, "MAGBA": 19, "KOUSSERI": 20, "MELONG": 21}


# Decorator function that checks if the user is verified before allowing access to a route
def login_required(f):
    """
    Decorator function that checks if the user is verified before allowing access to a route.

    Args:
        f (function): The route function to be decorated.

    Returns:
        function: The decorated route function.
    """
    def wrapper(*args, **kwargs):
        """
        Wrapper function that checks if the user is verified before executing the original route function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the original route function if the user is verified, otherwise redirects to the verification route.
        """
        if session.get('verified') != True:
            # Redirect to the verification route if the user is not verified
            return redirect(url_for('verification'))
        # Execute the original route function if the user is verified
        return f(*args, **kwargs)

    # Set the name of the wrapper function to match the name of the original function
    wrapper.__name__ = f.__name__
    return wrapper


@app.route("/")  # home page
def home():
    return render_template("home.html")


@app.route("/register")
def register():
    """
    This function is a route handler for the '/register' endpoint.
    It renders the 'formulaire.html' template and passes two variables to it: 'list_agence' and 'code_agence'.

    Returns:
        The rendered 'formulaire.html' template with the passed variables.
    """
    # Render the 'formulaire.html' template and pass the 'list_agence' and 'code_agence' variables to it
    return render_template("formulaire.html", list_agence=list_agence, code_agence=code_agence)


@app.route("/addinfo", methods=['POST', 'GET'])
def addinfo():
    """
    Route for adding information to the database.

    This route handles both POST and GET requests.
    On a POST request, it retrieves form data and inserts it into the 'leasing' table in the database.
    On a GET request, it renders the 'resultats.html' template with a message indicating the success or failure of the insertion.

    Returns:
        If the request method is POST, it renders the 'resultats.html' template with a message indicating the success or failure of the insertion.
    """
    if request.method == 'POST':
        try:
            # Retrieve form data
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
            return render_template('resultats.html', msg=msg)


@app.route("/verification", methods=['GET', 'POST'])
def verification():
    """
    This function handles the verification process for the user.
    It checks if the request method is POST and if the entered code is correct.
    If the code is correct, it marks the user as verified in the session and redirects to the admin page.
    If the code is incorrect, it displays an error message and renders the verification template.
    If the request method is not POST, it renders the verification template.
    """
    if request.method == 'POST':
        # Concatenate the code entered by the user
        code = (
                request.form.get('code1', '') +
                request.form.get('code2', '') +
                request.form.get('code3', '') +
                request.form.get('code4', '') +
                request.form.get('code5', '')
        )

        if code == "19965":
            # Mark the user as verified in the session
            session['verified'] = True
            return redirect("/admin")
        else:
            # Display an error message if the code is incorrect
            error = "Le code est incorrect. Veuillez réessayer."
            return render_template("verification.html", error=error)

    # Render the verification template if the request method is not POST
    return render_template("verification.html")


@app.route("/admin")
@login_required  # Apply access verification
def admin():
    """
    Route for the admin dashboard.

    This route handles the display of the admin dashboard. It retrieves data from
    the SQLite database and paginates the results. It also calculates the total
    number of pages based on the number of records and the number of records per page.

    Returns:
        The rendered admin/dashboard.html template with the paginated data and
        pagination information.

    Raises:
        Exception: If there is an error retrieving the data from the database.
    """
    try:
        # Connect to the SQLite database
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()

            # Number of items per page
            per_page = 10

            # Get the current page number from the request parameters
            page = request.args.get('page', 1, type=int)

            # Calculate the offset (number of records to skip for each page)
            offset = (page - 1) * per_page

            # SQL query to retrieve paginated data
            cur.execute("SELECT * FROM leasing LIMIT ? OFFSET ?", (per_page, offset))
            rows = cur.fetchall()  # Retrieve the current page's rows

            # SQL query to retrieve the total number of records
            cur.execute("SELECT COUNT(*) FROM leasing")
            total_count = cur.fetchone()[0]

            # Calculate the total number of pages
            total_pages = (total_count + per_page - 1) // per_page  # Round up

        # Render the admin/dashboard.html template with the paginated data and pagination information
        return render_template("admin/dashboard.html", rows=rows, page=page, total_pages=total_pages,
                               total_count=total_count)

    except Exception as e:
        # Return an error message if there is an error retrieving the data from the database
        return f"An error occurred while retrieving the data: {e}"


@app.route("/admin/delete/<int:id>", methods=['GET', 'POST'])
@login_required  # Apply access check
def delete(id):
    """
    Delete a leasing demand based on the ID.

    Args:
        id (int): The ID of the demand to delete.

    Returns:
        str: A success message if the deletion is successful, or an error message if an exception occurs.
    """
    try:
        # Connect to the database
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()

            # Delete the demand from the database
            cur.execute("DELETE FROM leasing WHERE id=?", (id,))
            con.commit()

            # Return a success message
            return f"La demande a été supprimée avec succès"

    except:
        # Rollback the transaction if an exception occurs
        con.rollback()

        # Return an error message
        return f"Une erreur s'est produite lors de la suppression de la demande"

    finally:
        # Close the database connection
        con.close()

        # Redirect to the administration page
        return redirect("/admin")


@app.route("/admin/edit/<int:id>", methods=['GET', 'POST'])
@login_required  # Apply access check
def edit(id):
    """
    Edit a leasing demand based on the ID.

    Args:
        id (int): The ID of the demand to edit.

    Returns:
        GET: Displays the edit form with current data.
        POST: Updates the demand in the database and redirects to the administration page.
    """
    # Database connection
    try:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()

            if request.method == 'POST':
                # Retrieve form data
                agence = request.form['agence']
                numag = request.form['numag']
                numcompte = request.form['numcompte']
                cle = request.form['cle']
                nom = request.form['nom']
                prenom = request.form['prenom']
                besoin = request.form['besoin']
                montant = request.form['montant']

                # Update the database
                try:
                    cur.execute("""
                        UPDATE leasing 
                        SET agence=?, num_ag=?, num_compte=?, cle=?, nom=?, prenom=?, besoin=?, montant=? 
                        WHERE id=?
                    """, (agence, numag, numcompte, cle, nom, prenom, besoin, montant, id))
                    con.commit()
                    return f"The demand has been successfully modified"
                    return redirect(url_for("admin"))  # Redirect after success

                except Exception as e:
                    con.rollback()
                    return f"Error modifying the demand: {e}"
                    return redirect(url_for('edit', id=id))

            else:
                # Retrieve data of the demand to edit
                cur.execute("SELECT * FROM leasing WHERE id=?", (id,))
                row = cur.fetchone()
                if row is None:
                    return f"No demand found with this ID"
                    return redirect(url_for("admin_dashboard"))

                # Display the edit form with current data
                return render_template("admin/data/edit.html", row=row)

    except sqlite3.Error as e:
        return f"Database connection error: {e}"
        return redirect(url_for("admin_dashboard"))


@app.route("/export_excel")
@login_required  # Apply access check
def export_excel():
    """
    Export leasing data to an Excel file.

    Returns:
        If successful, returns an Excel file with the data.
        If an error occurs, returns an error message.
    """
    try:
        # Connect to the database
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()

            # Retrieve all data from the leasing table
            cur.execute("SELECT * FROM leasing")
            rows = cur.fetchall()

            # Retrieve the column names from the leasing table
            cur.execute("PRAGMA table_info(leasing)")
            columns = [description[1] for description in cur.fetchall()]

            # Create a DataFrame from the data and column names
            df = pd.DataFrame(rows, columns=columns)

            # Create an in-memory BytesIO object to store the Excel file
            output = io.BytesIO()

            # Write the DataFrame to the Excel file
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='LeasingData')

            # Reset the file pointer to the beginning
            output.seek(0)

            # Return the Excel file as a download
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             download_name='leasing_data.xlsx', as_attachment=True)

    except Exception as e:
        # Return an error message if an exception occurs
        return f"Error occurred during data export: {e}"


@app.route("/export_pdf")
@login_required  # Apply access check
def export_pdf():
    """
    Export leasing data to a PDF file.

    Returns:
        If successful, returns a PDF file with the data.
        If an error occurs, returns an error message.
    """
    try:
        # Connect to the database
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()

            # Retrieve all data from the leasing table
            cur.execute("SELECT * FROM leasing")
            rows = cur.fetchall()

            # Retrieve the column names from the leasing table
            cur.execute("PRAGMA table_info(leasing)")
            columns = [description[1] for description in cur.fetchall()]

            # Create a DataFrame from the data and column names
            df = pd.DataFrame(rows, columns=columns)

            # Create an in-memory BytesIO object to store the PDF file
            output = io.BytesIO()

            # Write the DataFrame to the PDF file
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='LeasingData')

            # Reset the file pointer to the beginning
            output.seek(0)

            # Return the PDF file as a download
            return send_file(output, mimetype='application/pdf',
                             download_name='leasing_data.pdf', as_attachment=True)

    except Exception as e:
        # Return an error message if an exception occurs
        return f"Error occurred during data export: {e}"


@app.route("/logout")
def logout():
    """
    Logs out the user by removing the 'verified' session key and redirecting to the home page.

    Returns:
        A redirect response to the home page.
    """
    # Remove the 'verified' session key
    session.pop('verified', None)

    # Redirect to the home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
