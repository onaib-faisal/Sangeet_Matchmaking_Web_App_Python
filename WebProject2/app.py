from datetime import date, datetime
from tkinter.tix import Form
from flask import Flask

class candidate:
    def __init__(self, Singer_Name, Preferred_Musical_Genre, Gender, Location_City, Country, Negotiable_Hourly_Rate):
        self.Singer_Name = Singer_Name
        self.Preferred_Musical_Genre = Preferred_Musical_Genre
        self.Gender = Gender
        self.Location_City = Location_City
        self.Country = Country
        self.Negotiable_Hourly_Rate = Negotiable_Hourly_Rate

candidates_list = []

#Populate data from Database


#Populate list with data
candidates_list.append(candidate('Ford', 'Mustang', 1964, 'Manchester', 'England', 15))
candidates_list.append(candidate('Honda', 'Mustang', 1975, 'Manchester', 'England', 15))
candidates_list.append(candidate('Ferrari', 'Mustang', 1979, 'Manchester', 'England', 15))
candidates_list.append(candidate('Ford', 'Mustang', 1980, 'Manchester', 'England', 15))
candidates_list.append(candidate('Ford', 'Mustang', 1999, 'Manchester', 'England', 15))
candidates_list.append(candidate('Ford', 'Mustang', 2005, 'Manchester', 'England', 15))

#Old code, example of a dictionary
#Candidates = {
#  "Singer_Name": "Ford",
#  "Preferred_Musical_Genre": "Mustang",
#  "Gender": 1964,
#  "Location_City": "Manchester",
#  "Country": "England",
#  "Negotiable_Hourly_Rate" : 15
#}

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/')
@app.route('/hello')
@app.route('/form') 



def hello():
    # Render the page
    html_text = """
        <h2>Sangeet Pakistan Musician Database</h2>
        
        <form> 
        <input type = \"text\" id = \"search_inp\" name = \"search_inp\"<br>
        <input type = \"button\" value = \"Search Musician\">
        </form>
        
        <style>
        table, th, td {
        border:1px solid black;
        }
        </style>

        <table>
            <tr>
                <th>Singer Name</th>
                <th>Preffered Musical Genre</th>
                <th>Gender</th>
                <th>Location/City</th>
                <th>Country</th>
                <th>Negotiable Hourly Rate</th>
            </tr>"""

    for c in candidates_list:
       html_text += outputRow(c)

    html_text += "</table>" 
    return html_text
    


def outputRow(c):
    obj1 = c

    tmp = "<tr>"
    tmp += "<td>" + obj1.Singer_Name + "</td>"
    tmp += "<td>" + obj1.Preferred_Musical_Genre + "</td>"
    tmp += "<td>" + str(obj1.Gender) + "</td>"
    tmp += "<td>" + obj1.Location_City + "</td>"
    tmp += "<td>" + obj1.Country + "</td>"
    tmp += "<td>" + str(obj1.Negotiable_Hourly_Rate) + "</td>"
    tmp += "</tr>"

    return tmp

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)
