import pyodbc
from flask import Flask, render_template, request, redirect, send_from_directory, g, jsonify

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
    return render_template('admin.html')


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
        cursor.execute("""SET IDENTITY_INSERT dbo.MusicianLogin ON INSERT INTO dbo.MusicianLogin (Id, username, password) VALUES (?, ?, ?) SET IDENTITY_INSERT dbo.Candidates OFF""", Id, username, password)
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
        cursor.execute("""SET IDENTITY_INSERT dbo.ExternalLogin ON INSERT INTO dbo.ExternalLogin (Id, username, password) VALUES (?, ?, ?) SET IDENTITY_INSERT dbo.ExternalLogin OFF""", Id, username, password)
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




if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)
