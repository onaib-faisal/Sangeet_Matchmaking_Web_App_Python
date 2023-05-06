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

@app.route('/admin')
def admin_portal():
    return render_template('admin.html')

@app.route('/get_musician_logins')
def get_musician_logins():
    musician_logins_list = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dbo.MusicianLogin")
    for row in cursor.fetchall():
        musician_logins_list.append({"Id": row[0], "username": row[1], "password": row[2]})
    conn.close()
    return jsonify(musician_logins_list)



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


@app.route("/addMusicianLogin", methods = ['GET','POST'])
#Function to add Singer Login into database
def addMusicianLogin():
    if request.method == 'GET':
        return render_template("addMusicianLogin.html", singer = {})
    if request.method == 'POST':
        Id = request.form["Id"]
        username = request.form["username"]
        password = request.form["password"]
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("""SET IDENTITY_INSERT dbo.MusicianLogin ON INSERT INTO dbo.MusicianLogin (Id, username, password) VALUES (?, ?, ?) SET IDENTITY_INSERT dbo.Candidates OFF""", Id, username, password)
        conn.commit()
        conn.close()
        return redirect('/admin')

@app.route('/updateSingerLogin/<int:Id>',methods = ['GET','POST'])
#Function to edit singer login details
def updateSingerLogin(Id):
    cr = []
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM dbo.MusicianLogin WHERE Id = ?", Id)
        for row in cursor.fetchall():
            cr.append({"Id": row[0], "username": row[1], "password": row[2]})
        conn.close()
        return render_template("addMusicianLogin.html", singer = cr[0])
    if request.method == 'POST':
        #Id = request.form["Id"]
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("UPDATE dbo.MusicianLogin SET username = ?, password = ? WHERE Id = ?", username, password, Id)
        conn.commit()
        conn.close()
        return redirect('/admin')

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

@app.route("/searchMusicianLogin", methods = ['GET','POST'])
#Function to search Singer login from database
def searchMusicianLogin():
    if request.method == 'GET':
        return render_template("singerLoginSearch.html", singer = {})
   

@app.route('/singerLoginSearchResults', methods = ['GET','POST'])
def singerLoginSearchResults():
    loginFilters = {
        'Id': request.args.get('Id'),
        'username': request.args.get('username'), 
    }
    
    searchResults = search_logins(loginFilters)
    return render_template('loginSearchResults.html', results=searchResults)

def search_logins(filters):
    query = "SELECT * FROM dbo.MusicianLogin"
    conditions = []
    if filters['Id']:
        conditions.append("Id LIKE '%{}%'".format(filters['Id']))
    if filters['username']:
        conditions.append("username LIKE '%{}%'".format(filters['username']))
    if conditions:query += " WHERE " + " AND ".join(conditions)
    #print(query) [for debugging]

    musician_logins_list = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(query)
    for row in cursor.fetchall():
        musician_logins_list.append({"Id": row[0], "username": row[1], "password": row[2], })
    conn.close()
    return musician_logins_list



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


@app.route('/deleteSingerLogin/<int:Id>')
def deleteSingerLogin(Id):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.MusicianLogin WHERE Id = ?", Id)
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)
