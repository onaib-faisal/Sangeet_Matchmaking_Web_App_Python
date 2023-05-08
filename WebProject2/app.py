import pyodbc
import smtplib
from email.message import EmailMessage
from hashlib import sha256
from flask import Flask, render_template, request, redirect, send_from_directory, g, jsonify, url_for, session
from flask_session import Session

class candidate:
    def __init__(self, Id, Singer_Name, Preferred_Musical_Genre, Gender, Location_City, Country, Negotiable_Hourly_Rate):
        self.Id = Id
        self.Singer_Name = Singer_Name
        self.Preferred_Musical_Genre = Preferred_Musical_Genre
        self.Gender = Gender
        self.Location_City = Location_City
        self.Country = Country
        self.Negotiable_Hourly_Rate = Negotiable_Hourly_Rate

candidates_list = []

#Populate data from Database
def connection():    
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};'
                                  'Server=(LocalDB)\MSSQLLocalDB;'
                                  'Database=Sangeet;'
                                  'Integrated Security=true'
                                  'AttachDbFileName="D:\Programming Project\Sangeet.mdf"')
    return conn


# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'e4d13d0ea7a8c48c7678e7d0c07c29ef49cc116108fc4e3e' 
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/')
def main():
    return render_template('landingPage.html')

########## Admin Portal Code ########## 

@app.route('/admin')
# Rendering the admin HTML page
def admin_portal():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('adminlogin'))

    return render_template('admin.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = connection()
    cursor = conn.cursor()
    query = "SELECT * FROM dbo.AdminLogin WHERE username = ?"
    cursor.execute(query, (username,))

    admin = cursor.fetchone()
    conn.close()
    print(admin)

    if admin and admin[2] == password:
        session['logged_in'] = True
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 401


@app.route('/adminlogin')
def adminlogin():
    return render_template('adminLoginScreen.html')

@app.route('/adminLogout')
def adminlogout():
    session.clear()
    return redirect(url_for('adminlogin'))






# Dropdown option one - Musician Table
@app.route('/fetchSingers')
def get_singers():
    candidates_list = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dbo.Candidates")
    for row in cursor.fetchall():
        candidates_list.append({"Id": row[0], "Singer_Name": row[1], "Preferred_Musical_Genre": row[2], "Gender": row[3], "Location_City": row[4], "Country": row[5], "Negotiable_Hourly_Rate": row[6]})
    conn.close()
    return jsonify(candidates_list)


# Dropdown option 2 - Musician Login Details Table
# Route to retrieve all musician logins
@app.route('/get_musician_logins')
def get_musician_logins():
    # Initialize an empty list to store musician login records
    musician_logins_list = []
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute a query to fetch all records from the MusicianLogin table
    cursor.execute("SELECT * FROM dbo.MusicianLogin")
    # Iterate through the fetched records and append them to the musician_logins_list
    for row in cursor.fetchall():
        musician_logins_list.append({"Id": row[0], "username": row[1], "password": row[2]})
    # Close the database connection
    conn.close()
    # Return the list of musician logins as a JSON object
    return jsonify(musician_logins_list)

# Route to add a musician login record
@app.route("/addMusicianLogin", methods=['GET', 'POST'])
def addMusicianLogin():
    # Handle the GET request to display the addMusicianLogin form
    if request.method == 'GET':
        return render_template("addMusicianLogin.html", singer={})
    # Handle the POST request to submit the form and add the musician login record to the database
    if request.method == 'POST':
        Id = request.form["Id"]
        username = request.form["username"]
        password = request.form["password"]
        # Establish a connection to the database
        conn = connection()
        cursor = conn.cursor()
        # Execute a query to insert the new musician login record into the MusicianLogin table
        cursor.execute("""SET IDENTITY_INSERT dbo.MusicianLogin ON INSERT INTO dbo.MusicianLogin (Id, username, password) VALUES (?, ?, ?) SET IDENTITY_INSERT dbo.MusicianLogin OFF""", Id, username, password)
        # Commit the transaction
        conn.commit()
        # Close the database connection
        conn.close()
        # Redirect to the /admin page
        return redirect('/admin')

# Route to update a musician login record
@app.route('/updateSingerLogin/<int:Id>', methods=['GET', 'POST'])
def updateSingerLogin(Id):
    # Initialize an empty list to store the singer login record
    cr = []
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Handle the GET request to display the updateSingerLogin form with the existing record data
    if request.method == 'GET':
        # Execute a query to fetch the existing record from the MusicianLogin table
        cursor.execute("SELECT * FROM dbo.MusicianLogin WHERE Id = ?", Id)
        # Iterate through the fetched records and append them to the cr list
        for row in cursor.fetchall():
            cr.append({"Id": row[0], "username": row[1], "password": row[2]})
        # Close the database connection
        conn.close()
        # Render the updateSingerLogin form with the existing record data
        return render_template("addMusicianLogin.html", singer=cr[0])
    # Handle the POST request to submit the form and update the musician login record in the database
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        # Execute a query to update the existing musician login record in the MusicianLogin table
        cursor.execute("UPDATE dbo.MusicianLogin SET username = ?, password = ? WHERE Id = ?", username, password, Id)
        # Commit the transaction
        conn.commit()
        # Close the database connection
        conn.close()
        # Redirect to the /admin page
        return redirect('/admin')

# Route to search for musician login records
@app.route("/searchMusicianLogin", methods=['GET', 'POST'])
def searchMusicianLogin():
    # Handle the GET request to display the searchMusicianLogin form
    if request.method == 'GET':
        return render_template("singerLoginSearch.html", singer={})

# Route to display the search results for musician login records
@app.route('/singerLoginSearchResults', methods=['GET', 'POST'])
def singerLoginSearchResults():
    # Get the search filters from the request arguments
    loginFilters = {
        'Id': request.args.get('Id'),
        'username': request.args.get('username'),
    }
    # Call the search_logins function with the provided filters and store the results
    searchResults = search_logins(loginFilters)
    # Render the loginSearchResults template with the search results
    return render_template('loginSearchResults.html', results=searchResults)

# Function to search for musician login records based on the provided filters
def search_logins(filters):
    # Construct the base query
    query = "SELECT * FROM dbo.MusicianLogin"
    conditions = []
    # Add conditions to the query based on the provided filters
    if filters['Id']:
        conditions.append("Id LIKE '%{}%'".format(filters['Id']))
    if filters['username']:
        conditions.append("username LIKE '%{}%'".format(filters['username']))
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute the constructed query
    cursor.execute(query)
    # Initialize an empty list to store the search results
    musician_logins_list = []
    # Iterate through the fetched records and append them to the musician_logins_list
    for row in cursor.fetchall():
        musician_logins_list.append({"Id": row[0], "username": row[1], "password": row[2]})
    # Close the database connection
    conn.close()
    # Return the search results list
    return musician_logins_list

# Route to delete a musician login record
@app.route('/deleteSingerLogin/<int:Id>')
def deleteSingerLogin(Id):
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute a query to delete the specified musician login record from the MusicianLogin table
    cursor.execute("DELETE FROM dbo.MusicianLogin WHERE Id = ?", Id)
    # Commit the transaction
    conn.commit()
    # Close the database connection
    conn.close()
    # Redirect to the /admin page
    return redirect('/admin')


# Dropdown option 3 - External login details
# Route to retrieve all external logins
@app.route('/get_external_logins')
def get_external_logins():
    # Initialize an empty list to store external login records
    external_logins_list = []
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute a query to fetch all records from the ExternalLogin table
    cursor.execute("SELECT * FROM dbo.ExternalLogin")
    # Iterate through the fetched records and append them to the external_logins_list
    for row in cursor.fetchall():
        external_logins_list.append({"Id": row[0], "username": row[1], "password": row[2]})
    conn.close()
    # Return the list of external logins as a JSON object
    #print(external_logins_list) ##for debugging##
    return jsonify(external_logins_list)

# Route to add an external login record
@app.route("/addExternalLogin", methods=['GET', 'POST'])
def addExternalLogin():
    # Handle the GET request to display the addExternalLogin form
    if request.method == 'GET':
        return render_template("addExternalLogin.html", external={})
    # Handle the POST request to submit the form and add the external login record to the database
    if request.method == 'POST':
        Id = request.form["Id"]
        username = request.form["username"]
        password = request.form["password"]
        # Establish a connection to the database
        conn = connection()
        cursor = conn.cursor()
        # Execute a query to insert the new external login record into the ExternalLogin table
        cursor.execute("""INSERT INTO dbo.ExternalLogin (Id, username, password) VALUES (?, ?, ?)""", Id, username, password)
        # Commit the transaction
        conn.commit()
        # Close the database connection
        conn.close()
        # Redirect to the /admin page
        return redirect('/admin')

# Route to update a external login record
@app.route('/updateExternalLogin/<int:Id>', methods=['GET', 'POST'])
def updateExternalLogin(Id):
    # Initialize an empty list to store the external login record
    cr = []
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Handle the GET request to display the updateExternalLogin form with the existing record data
    if request.method == 'GET':
        # Execute a query to fetch the existing record from the ExternalLogin table
        cursor.execute("SELECT * FROM dbo.ExternalLogin WHERE Id = ?", Id)
        # Iterate through the fetched records and append them to the cr list
        for row in cursor.fetchall():
            cr.append({"Id": row[0], "username": row[1], "password": row[2]})
        # Close the database connection
        conn.close()
        # Render the updateExternalLogin form with the existing record data
        return render_template("addExternalLogin.html", external=cr[0])
    # Handle the POST request to submit the form and update the external login record in the database
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        # Execute a query to update the existing external login record in the ExternalLogin table
        cursor.execute("UPDATE dbo.ExternalLogin SET username = ?, password = ? WHERE Id = ?", username, password, Id)
        # Commit the transaction
        conn.commit()
        # Close the database connection
        conn.close()
        # Redirect to the /admin page
        return redirect('/admin')

# Route to search for external login records
@app.route("/searchExternalLogin", methods=['GET', 'POST'])
def searchExternalLogin():
    # Handle the GET request to display the searchExternalLogin form
    if request.method == 'GET':
        return render_template("externalLoginSearch.html", external={})

# Route to display the search results for external login records
@app.route('/externalLoginSearchResults', methods=['GET', 'POST'])
def externalLoginSearchResults():
    # Get the search filters from the request arguments
    loginFilters = {
        'Id': request.args.get('Id'),
        'username': request.args.get('username'),
    }
    # Call the search_logins function with the provided filters and store the results
    searchResults = external_search_logins(loginFilters)
    # Render the externalLoginSearchResults template with the search results
    return render_template('loginSearchResults.html', results=searchResults)

# Function to search for External login records based on the provided filters
def external_search_logins(filters):
    # Construct the base query
    query = "SELECT * FROM dbo.ExternalLogin"
    conditions = []
    # Add conditions to the query based on the provided filters
    if filters['Id']:
        conditions.append("Id LIKE '%{}%'".format(filters['Id']))
    if filters['username']:
        conditions.append("username LIKE '%{}%'".format(filters['username']))
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute the constructed query
    cursor.execute(query)
    # Initialize an empty list to store the search results
    external_logins_list = []
    # Iterate through the fetched records and append them to the external_logins_list
    for row in cursor.fetchall():
        external_logins_list.append({"Id": row[0], "username": row[1], "password": row[2]})
    # Close the database connection
    conn.close()
    # Return the search results list
    return external_logins_list

# Route to delete a External login record
@app.route('/deleteExternalLogin/<int:Id>')
def deleteExternalLogin(Id):
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute a query to delete the specified External login record from the ExternalLogin table
    cursor.execute("DELETE FROM dbo.ExternalLogin WHERE Id = ?", Id)
    # Commit the transaction
    conn.commit()
    # Close the database connection
    conn.close()
    # Redirect to the /admin page
    return redirect('/admin')
 

# Dropdown option 4 - Admin login details
# Route to retrieve all admin logins
@app.route('/get_admin_logins')
def get_admin_logins():
    # Initialize an empty list to store admin login records
    admin_logins_list = []
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute a query to fetch all records from the AdminLogin table
    cursor.execute("SELECT * FROM dbo.AdminLogin")
    # Iterate through the fetched records and append them to the admin_logins_list
    for row in cursor.fetchall():
        admin_logins_list.append({"Id": row[0], "username": row[1], "password": row[2]})
    conn.close()
    # Return the list of admin logins as a JSON object
    #print(admin_logins_list) ##for debugging##
    return jsonify(admin_logins_list)

# Route to add an admin login record
@app.route("/addAdminLogin", methods=['GET', 'POST'])
def addAdminLogin():
    # Handle the GET request to display the addAdminLogin form
    if request.method == 'GET':
        return render_template("addAdminLogin.html", admin={})
    # Handle the POST request to submit the form and add the admin login record to the database
    if request.method == 'POST':
        Id = request.form["Id"]
        username = request.form["username"]
        password = request.form["password"]
        # Establish a connection to the database
        conn = connection()
        cursor = conn.cursor()
        # Execute a query to insert the new admin login record into the AdminLogin table
        cursor.execute("""SET IDENTITY_INSERT dbo.AdminLogin ON INSERT INTO dbo.AdminLogin (Id, username, password) VALUES (?, ?, ?) SET IDENTITY_INSERT dbo.AdminLogin OFF""", Id, username, password)
        # Commit the transaction
        conn.commit()
        # Close the database connection
        conn.close()
        # Redirect to the /admin page
        return redirect('/admin')

# Route to update a Admin login record
@app.route('/updateAdminLogin/<int:Id>', methods=['GET', 'POST'])
def updateAdminLogin(Id):
    # Initialize an empty list to store the Admin login record
    cr = []
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Handle the GET request to display the updateAdminLogin form with the existing record data
    if request.method == 'GET':
        # Execute a query to fetch the existing record from the AdminLogin table
        cursor.execute("SELECT * FROM dbo.AdminLogin WHERE Id = ?", Id)
        # Iterate through the fetched records and append them to the cr list
        for row in cursor.fetchall():
            cr.append({"Id": row[0], "username": row[1], "password": row[2]})
        # Close the database connection
        conn.close()
        # Render the updateAdminLogin form with the existing record data
        return render_template("addAdminLogin.html", admin=cr[0])
    # Handle the POST request to submit the form and update the Admin login record in the database
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        # Execute a query to update the existing Admin login record in the AdminLogin table
        cursor.execute("UPDATE dbo.AdminLogin SET username = ?, password = ? WHERE Id = ?", username, password, Id)
        # Commit the transaction
        conn.commit()
        # Close the database connection
        conn.close()
        # Redirect to the /admin page
        return redirect('/admin')


# Route to delete a Admin login record
@app.route('/deleteAdminLogin/<int:Id>')
def deleteAdminLogin(Id):
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute a query to delete the specified admin login record from the Login table
    cursor.execute("DELETE FROM dbo.AdminLogin WHERE Id = ?", Id)
    # Commit the transaction
    conn.commit()
    # Close the database connection
    conn.close()
    # Redirect to the /admin page
    return redirect('/admin')

# DROPDOWN OPTION 5 - SIGN UP REQUESTS
# Route to fetch sign-up requests
@app.route('/get_sign_up_requests')
def get_sign_up_requests():
    # Create an empty list to store sign-up requests
    sign_up_requests_list = []

    # Establish database connection
    conn = connection()

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Execute SQL query to fetch all rows from dbo.SignUpRequests table
    cursor.execute("SELECT * FROM dbo.SignUpRequests")

    # Iterate through fetched rows and append them to the sign_up_requests_list
    for row in cursor.fetchall():
        sign_up_requests_list.append({"Id": row[0], "additional_info": row[1]})

    # Close the database connection
    conn.close()

    # Return the sign_up_requests_list as a JSON object
    return jsonify(sign_up_requests_list)

def deleteSignUpRequest(Id):
    # Establish a connection to the database
    conn = connection()
    cursor = conn.cursor()
    # Execute a query to delete the specified sign up requesr record from the Login table
    cursor.execute("DELETE FROM dbo.SignUpRequests WHERE Id = ?", Id)
    # Commit the transaction
    conn.commit()
    # Close the database connection
    conn.close()
    # Redirect to the /admin page
    return redirect('/admin')


# DROPDOWN OPTION 7 - ADMIN USERS TABLE
# Route to fetch admin users
@app.route('/get_admins')
def get_admins():
    # Create an empty list to store admin users
    admins_list = []

    # Establish database connection
    conn = connection()

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Execute SQL query to fetch all rows from dbo.Admins table
    cursor.execute("SELECT * FROM dbo.Admins")

    # Iterate through fetched rows and append them to the admins_list
    for row in cursor.fetchall():
        admins_list.append({
            "Id": row[0],
            "StaffName": row[1],
            "StaffRole": row[2]
        })

    # Close the database connection
    conn.close()

    # Return the admins_list as a JSON object
    return jsonify(admins_list)

# Route to add an Admin login record
@app.route("/addAdmin", methods=['GET', 'POST'])
def addAdmin():
    # If the request is a GET request, render the 'addAdmin.html' template
    if request.method == 'GET':
        return render_template("addAdmin.html", admin={})

    # If the request is a POST request, add the Admin login record to the database
    if request.method == 'POST':
        # Get the form input values
        StaffName = request.form["StaffName"]
        StaffRole = request.form["StaffRole"]

        # Establish database connection
        conn = connection()
        cursor = conn.cursor()

        # Execute SQL query to insert the Admin login record into the dbo.Admins table
        cursor.execute("""INSERT INTO dbo.Admins (StaffName, StaffRole) VALUES (?, ?)""", StaffName, StaffRole)

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Redirect the user to the '/admin' route
        return redirect('/admin')


# Route to update an Admin login record
@app.route('/updateAdmin/<int:Id>', methods=['GET', 'POST'])
def updateAdmin(Id):
    cr = []
    conn = connection()
    cursor = conn.cursor()

    # If the request is a GET request, fetch the Admin login record and render the 'addAdmin.html' template
    if request.method == 'GET':
        cursor.execute("SELECT * FROM dbo.Admins WHERE Id = ?", Id)
        for row in cursor.fetchall():
            cr.append({"Id": row[0], "StaffName": row[1], "StaffRole": row[2]})
        conn.close()
        return render_template("addAdmin.html", admin=cr[0])

    # If the request is a POST request, update the Admin login record in the database
    if request.method == 'POST':
        # Get the form input values
        StaffName = request.form["StaffName"]
        StaffRole = request.form["StaffRole"]

        # Execute SQL query to update the Admin login record in the dbo.Admin table
        cursor.execute("UPDATE dbo.Admins SET StaffName = ?, StaffRole = ? WHERE Id = ?", StaffName, StaffRole, Id)

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Redirect the user to the '/admin' route
        return redirect('/admin')


# Route to delete an Admin login record
@app.route('/deleteAdmin/<int:Id>')
def deleteAdmin(Id):
    # Establish database connection
    conn = connection()
    cursor = conn.cursor()

    # Execute SQL query to delete the Admin login record from the dbo.Admins table
    cursor.execute("DELETE FROM dbo.Admins WHERE Id = ?", Id)

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    # Redirect the user to the '/admin' route
    return redirect('/admin')


# DROPDOWN OPTION 6 - EXTERNAL USERS TABLE
# Route to fetch external users
@app.route('/get_externals')
def get_externals():
    # Create an empty list to store external users
    externals_list = []

    # Establish database connection
    conn = connection()

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Execute SQL query to fetch all rows from dbo.ExternalUsers table
    cursor.execute("SELECT * FROM dbo.Externals")

    # Iterate through fetched rows and append them to the externals_list
    for row in cursor.fetchall():
        externals_list.append({
            "Id": row[0],
            "PersonName": row[1],
            "OrgName": row[2],
            "OrgPostcode": row[3],
            "OrgCity": row[4],
            "OrgCountry": row[5],
            "OrgSocial": row[6]
        })

    # Close the database connection
    conn.close()

    # Return the externals_list as a JSON object
    return jsonify(externals_list)

# Route to add an external login record
@app.route("/addExternal", methods=['GET', 'POST'])
def addExternal():
    # If the request is a GET request, render the 'addExternal.html' template
    if request.method == 'GET':
        return render_template("addExternal.html", external={})

    # If the request is a POST request, add the external login record to the database
    if request.method == 'POST':
        # Get the form input values
        PersonName = request.form["PersonName"]
        OrgName = request.form["OrgName"]
        OrgPostcode = request.form["OrgPostcode"]
        OrgCity = request.form["OrgCity"]
        OrgCountry = request.form["OrgCountry"]
        OrgSocial = request.form["OrgSocial"]

        # Establish database connection
        conn = connection()
        cursor = conn.cursor()

        # Execute SQL query to insert the external login record into the dbo.Externals table
        cursor.execute("""INSERT INTO dbo.Externals (PersonName, OrgName, OrgPostcode, OrgCity, OrgCountry, OrgSocial) VALUES (?, ?, ?, ?, ?, ?)""", PersonName, OrgName, OrgPostcode, OrgCity, OrgCountry, OrgSocial)

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Redirect the user to the '/admin' route
        return redirect('/admin')


# Route to update an external login record
@app.route('/updateExternal/<int:Id>', methods=['GET', 'POST'])
def updateExternal(Id):
    cr = []
    conn = connection()
    cursor = conn.cursor()

    # If the request is a GET request, fetch the external login record and render the 'addExternal.html' template
    if request.method == 'GET':
        cursor.execute("SELECT * FROM dbo.Externals WHERE Id = ?", Id)
        for row in cursor.fetchall():
            cr.append({"Id": row[0], "PersonName": row[1], "OrgName": row[2], "OrgPostcode": row[3], "OrgCity": row[4], "OrgCountry": row[5], "OrgSocial": row[6]})
        conn.close()
        return render_template("addExternal.html", external=cr[0])

    # If the request is a POST request, update the external login record in the database
    if request.method == 'POST':
        # Get the form input values
        PersonName = request.form["PersonName"]
        OrgName = request.form["OrgName"]
        OrgPostcode = request.form["OrgPostcode"]
        OrgCity = request.form["OrgCity"]
        OrgCountry = request.form["OrgCountry"]
        OrgSocial = request.form["OrgSocial"]

        # Execute SQL query to update the external login record in the dbo.Externals table
        cursor.execute("UPDATE dbo.Externals SET PersonName = ?, OrgName = ?, OrgPostcode = ?, OrgCity = ?, OrgCountry = ?, OrgSocial = ? WHERE Id = ?", PersonName, OrgName, OrgPostcode, OrgCity, OrgCountry, OrgSocial, Id)

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Redirect the user to the '/admin' route
        return redirect('/admin')


# Route to search for external login records
@app.route("/searchExternal", methods=['GET', 'POST'])
def searchExternal():
    # If the request is a GET request, render the 'externalSearch.html' template
        if request.method == 'GET':
            return render_template("externalSearch.html", external={})

# Route to display search results for external login records
@app.route('/externalSearchResults', methods=['GET', 'POST'])
def externalSearchResults():
    # Get the search filter values from the request arguments
    searchFilters = {
        'Id': request.args.get('Id'),
        'PersonName': request.args.get('PersonName'),
        'OrgName': request.args.get('OrgName'),
        'OrgPostcode': request.args.get('OrgPostcode'),
        'OrgCity': request.args.get('OrgCity'),
        'OrgCountry': request.args.get('OrgCountry'),
        'OrgSocial': request.args.get('OrgSocial'),
    }

    # Call the 'external_search' function with the search filters and store the results
    searchResults = external_search(searchFilters)

    # Render the 'externalSearchResults.html' template with the search results
    return render_template('externalSearchResults.html', results=searchResults)

# Function to search for external login records based on the provided filters
def external_search(filters):
    query = "SELECT * FROM dbo.Externals"
    conditions = []

    # Add conditions to the SQL query based on the provided filters
    if filters['Id']:
        conditions.append("Id LIKE '%{}%'".format(filters['Id']))
    if filters['PersonName']:
        conditions.append("PersonName LIKE '%{}%'".format(filters['PersonName']))
    if filters['OrgName']:
        conditions.append("OrgName LIKE '%{}%'".format(filters['OrgName']))
    if filters['OrgPostcode']:
        conditions.append("OrgPostcode LIKE '%{}%'".format(filters['OrgPostcode']))
    if filters['OrgCity']:
        conditions.append("OrgCity LIKE '%{}%'".format(filters['OrgCity']))
    if filters['OrgCountry']:
        conditions.append("OrgCountry LIKE '%{}%'".format(filters['OrgCountry']))
    if filters['OrgSocial']:
        conditions.append("OrgSocial LIKE '%{}%'".format(filters['OrgSocial']))

    # If there are any conditions, add them to the query
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Establish database connection
    conn = connection()
    cursor = conn.cursor()

    # Execute the SQL query and fetch the results
    cursor.execute(query)
    external_list = []
    for row in cursor.fetchall():
        external_list.append({"Id": row[0], "PersonName": row[1], "OrgName": row[2], "OrgPostcode": row[3], "OrgCity": row[4], "OrgCountry": row[5], "OrgSocial": row[6]})

    # Close the database connection
    conn.close()

    # Return the list of external login records
    return external_list

# Route to delete an external login record
@app.route('/deleteExternal/<int:Id>')
def deleteExternal(Id):
    # Establish database connection
    conn = connection()
    cursor = conn.cursor()

    # Execute SQL query to delete the external login record from the dbo.Externals table
    cursor.execute("DELETE FROM dbo.Externals WHERE Id = ?", Id)

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    # Redirect the user to the '/admin' route
    return redirect('/admin')

@app.route('/singerslist')
def singerslist():
    candidates_list = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dbo.Candidates")
    for row in cursor.fetchall():
        candidates_list.append({"Id": row[0], "Singer_Name": row[1], "Preferred_Musical_Genre": row[2], "Gender": row[3], "Location_City": row[4], "Country": row[5], "Negotiable_Hourly_Rate": row[6]})
    conn.close()
    return render_template("singerslist.html", candidates_list = candidates_list)



@app.route("/addSinger", methods = ['GET','POST'])
#Function to add Singer into database
def addSinger():
    if request.method == 'GET':
        return render_template("addSinger.html", singer = {})
    if request.method == 'POST':
        #Id = request.form["Id"]
        Singer_Name = request.form["Singer_Name"]
        Gender = request.form["Gender"]
        Preferred_Musical_Genre = request.form["Preferred_Musical_Genre"]
        Location_City = request.form["Location_City"]
        Country = request.form["Country"]
        Negotiable_Hourly_Rate = float(request.form["Negotiable_Hourly_Rate"])
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("""SET IDENTITY_INSERT dbo.Candidates OFF INSERT INTO dbo.Candidates (Singer_Name, Gender, Preferred_Musical_Genre, Location_City, Country, Negotiable_Hourly_Rate) VALUES (?, ?, ?, ?, ?, ?) SET IDENTITY_INSERT dbo.Candidates OFF""", Singer_Name, Gender, Preferred_Musical_Genre, Location_City, Country, Negotiable_Hourly_Rate)
        conn.commit()
        conn.close()
        return redirect('/admin')

@app.route("/searchSinger", methods = ['GET','POST'])
#Function to search Singer from database
def searchSinger():
    if request.method == 'GET':
        return render_template("singerSearch.html", singer = {})





@app.route('/searchResults', methods = ['GET','POST'])
def searchResults():
    singerFilters = {
        'Singer_Name': request.args.get('Singer_Name'),
        'Gender': request.args.get('Gender'),
        'Preferred_Musical_Genre': request.args.get('Preferred_Musical_Genre'),
        'Location_City': request.args.get('Location_City'),
        'Country': request.args.get('Country'),
        'Negotiable_Hourly_Rate': request.args.get('Negotiable_Hourly_Rate') 
    }
    
    searchResults = search_songs(singerFilters)
    return render_template('searchResults.html', results=searchResults)

def search_songs(filters):
    query = "SELECT * FROM dbo.Candidates"
    conditions = []
    if filters['Singer_Name']:
        conditions.append("Singer_Name LIKE '%{}%'".format(filters['Singer_Name']))
    if filters['Gender']:
        conditions.append("Gender LIKE '%{}%'".format(filters['Gender']))
    if filters['Preferred_Musical_Genre']:
        conditions.append("Preferred_Musical_Genre LIKE '%{}%'".format(filters['Preferred_Musical_Genre']))
    if filters['Location_City']:
        conditions.append("genre LIKE '%{}%'".format(filters['Location_City']))
    if filters['Country']:
        conditions.append("Country = '{}'".format(filters['Country']))
    if filters['Negotiable_Hourly_Rate']:
        conditions.append("Negotiable_Hourly_Rate = '{}'".format(filters['Negotiable_Hourly_Rate']))
    if conditions:query += " WHERE " + " AND ".join(conditions)
    print(query)

    candidates_list = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(query)
    for row in cursor.fetchall():
        candidates_list.append({"Id": row[0], "Singer_Name": row[1], "Preferred_Musical_Genre": row[2], "Gender": row[3], "Location_City": row[4], "Country": row[5], "Negotiable_Hourly_Rate": row[6]})
    conn.close()
    return candidates_list

@app.route('/updateSinger/<int:Id>',methods = ['GET','POST'])
#Function to edit singer details
def updateSinger(Id):
    cr = []
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM dbo.Candidates WHERE Id = ?", Id)
        for row in cursor.fetchall():
            cr.append({"Id": row[0], "Singer_Name": row[1], "Preferred_Musical_Genre": row[2], "Gender": row[3], "Location_City": row[4], "Country": row[5], "Negotiable_Hourly_Rate": row[6]})
        conn.close()
        return render_template("addSinger.html", singer = cr[0])
    if request.method == 'POST':
        Singer_Name = request.form["Singer_Name"]
        Gender = request.form["Gender"]
        Preferred_Musical_Genre = request.form["Preferred_Musical_Genre"]
        Location_City = request.form["Location_City"]
        Country = request.form["Country"]
        Negotiable_Hourly_Rate = float(request.form["Negotiable_Hourly_Rate"])
        cursor.execute("UPDATE dbo.Candidates SET Singer_Name = ?, Gender = ?, Preferred_Musical_Genre = ?, Location_City = ?, Country = ?, Negotiable_Hourly_Rate = ? WHERE Id = ?", Singer_Name, Gender, Preferred_Musical_Genre, Location_City, Country, Negotiable_Hourly_Rate, Id)
        conn.commit()
        conn.close()
        return redirect('/admin')

@app.route('/deleteSinger/<int:Id>')
def deleteSinger(Id):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.Candidates WHERE Id = ?", Id)
    conn.commit()
    conn.close()
    return redirect('/admin')



############# Musician Portal Code ##############

@app.route('/musicians')
def musicians():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('musician_login'))
    return render_template("musicians.html", username=session['username'])


@app.route('/musician/create_account', methods = ['GET', 'POST'])
def create_account():
    if request.method == 'GET':
        return render_template('createMusicianAccount.html')
    if request.method == 'POST':
        username = request.json["username"]
        password = request.json["password"]
        hashed_password = sha256(password.encode('utf-8')).hexdigest()
        confirm_password = request.json["confirm_password"]
        Singer_Name = request.json["Singer_Name"]
        dob = request.json["dob"]
        Gender = request.json["Gender"]
        Preferred_Musical_Genre = request.json["Preferred_Musical_Genre"]
        Location_City = request.json["Location_City"]
        Country = request.json["Country"]
        Negotiable_Hourly_Rate = float(request.json["Negotiable_Hourly_Rate"])
        Social_Media = request.json["Social_Media"]
        Email = request.json["Email"]


        additional_info = {
            "username": username,
            "password (hash)": hashed_password,
            "dob": dob,
            "Singer_Name": Singer_Name,
            "Gender": Gender,
            "Preferred_Musical_Genre": Preferred_Musical_Genre,
            "Location_City": Location_City,
            "Country": Country,
            "Negotiable_Hourly_Rate": Negotiable_Hourly_Rate,
            "Social_Media": Social_Media,
            "Email": Email
        }

        conn = connection()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO dbo.SignUpRequests (additional_info) VALUES (?)""", str(additional_info))
        conn.commit()
        conn.close()

        return jsonify({"message": "Request submitted. Please check your email for a reply in 7-14 days."})
    return jsonify({"error": "Invalid request method."})



###### RUN WHEN EMAIL PURCHASED ############
#@app.route('/musician/forgot_password')
#def forgot_password():
#    return render_template('forgotPassword.html')



#def send_email(subject, body, to):
#    EMAIL_ADDRESS = #Enter email here 
#    EMAIL_PASSWORD = #Enter password here

#    msg = EmailMessage()
#    msg.set_content(body)
#    msg['Subject'] = subject
#    msg['From'] = EMAIL_ADDRESS
#    msg['To'] = to

#    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#        smtp.send_message(msg)

#@app.route('/api/request_password_reset', methods=['POST'])
#def request_password_reset():
#    data = request.get_json()
#    Singer_Name = data['Singer_Name']
#    username = data['username']
#    typeUser = data['typeUser']

#    # Email the admin with password reset request details
#    subject = 'Forgot Password Request'
#    body = f"Dear Admin,\n\nA user has requested to reset their password.\n\nUsername: {username}\nFull Name: {Singer_Name}\nUser Type: {typeUser}\n\nPlease verify the user's identity and assist them in resetting their password.\n\nBest regards,\nThe Sangeet.pk Team"
#    admin_email = 'sangeet.pk@hotmail.com'
#    print(subject, body, admin_email)
#    send_email(subject, body, admin_email)

#    return jsonify({"success": True})



@app.route('/api/musician_login', methods=['POST'])
def api_musician_login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    hashpassword = sha256(password.encode('utf-8')).hexdigest()

    conn = connection()
    cursor = conn.cursor()
    query = "SELECT * FROM dbo.MusicianLogin WHERE username = ?"
    cursor.execute(query, (username,))

    musician = cursor.fetchone()
    conn.close()

    if musician and musician[2] == hashpassword:
        session['logged_in'] = True
        session['username'] = username
        return jsonify({"success": True})
    else:
        session['logged_in'] = False
        return jsonify({"success": False}), 401

@app.route('/musician_login')
def musician_login():
    return render_template('musicianLoginScreen.html')

@app.route('/musician_logout')
def musician_logout():
    session.clear()
    return redirect(url_for('musician_login'))


@app.route('/get_musician_by_username', methods=['POST'])
def get_musician_by_username():
    username = request.form.get("username")
    conn = connection()
    cursor = conn.cursor()

    # Fetch musician from dbo.MusicanLogin by username
    cursor.execute("SELECT * FROM dbo.MusicianLogin WHERE username = ?", (username,))
    musician_login = cursor.fetchone()

    if musician_login:
        musician_id = musician_login[0]

        # Fetch the matching candidate from dbo.Candidates
        cursor.execute("SELECT * FROM dbo.Candidates WHERE Id = ?", (musician_id,))
        candidate = cursor.fetchone()

        if candidate:
            candidate_dict = {
            "Id": candidate[0],
            "Singer_Name": candidate[1],
            "Preferred_Musical_Genre": candidate[2],
            "Gender": candidate[3],
            "Location_City": candidate[4],
            "Country": candidate[5],
            "Negotiable_Hourly_Rate": candidate[6]
            }


            conn.close()
            return jsonify(candidate_dict)

    conn.close()
    return jsonify({}), 404

@app.route('/updateCandidate/<int:Id>',methods = ['GET','POST'])
#Function to edit singer details
def updateCandidate(Id):
    cr = []
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM dbo.Candidates WHERE Id = ?", Id)
        for row in cursor.fetchall():
            cr.append({"Id": row[0], "Singer_Name": row[1], "Preferred_Musical_Genre": row[2], "Gender": row[3], "Location_City": row[4], "Country": row[5], "Negotiable_Hourly_Rate": row[6]})
        conn.close()
        return render_template("addSinger.html", singer = cr[0])
    if request.method == 'POST':
        Singer_Name = request.form["Singer_Name"]
        Gender = request.form["Gender"]
        Preferred_Musical_Genre = request.form["Preferred_Musical_Genre"]
        Location_City = request.form["Location_City"]
        Country = request.form["Country"]
        Negotiable_Hourly_Rate = float(request.form["Negotiable_Hourly_Rate"])
        cursor.execute("UPDATE dbo.Candidates SET Singer_Name = ?, Gender = ?, Preferred_Musical_Genre = ?, Location_City = ?, Country = ?, Negotiable_Hourly_Rate = ? WHERE Id = ?", Singer_Name, Gender, Preferred_Musical_Genre, Location_City, Country, Negotiable_Hourly_Rate, Id)
        conn.commit()
        conn.close()
        return redirect('/musicians')

    @app.route('/deleteCandidate/<int:Id>')
    def deleteCandidate(Id):
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dbo.Candidates WHERE Id = ?", Id)
        conn.commit()
        conn.close()
        return redirect('/musicians')


############### Externals Portal ###################

@app.route('/externals')
def externals():
    candidates_list = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dbo.Candidates")
    for row in cursor.fetchall():
        candidates_list.append({"Id": row[0], "Singer_Name": row[1], "Preferred_Musical_Genre": row[2], "Gender": row[3], "Location_City": row[4], "Country": row[5], "Negotiable_Hourly_Rate": row[6], "Email": row[7]})
    conn.close()
    return render_template("externals.html", candidates_list = candidates_list)


if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)
