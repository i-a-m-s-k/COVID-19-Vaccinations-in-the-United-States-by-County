#Name: Shivangi Kumar
#Unique ID: iamsk

#Import necessary packages
import requests, json
from bs4 import BeautifulSoup
import pandas as pd
import csv
import sqlite3
import pprint
from flask import Flask, render_template, request, redirect, url_for
import plotly.express as px
import plotly
import plotly.graph_objects as go

app = Flask(__name__)

#Database name has been specified to store the table.
DB_NAME = "Covid_Data.sqlite3"
#CDC website is used as the URL
url = "https://data.cdc.gov/browse?category=Vaccinations"


response1 = requests.get(url)
soup = BeautifulSoup(response1.text, 'html.parser')
#BeautifulSoup library has been used to perform Web scraping and fetch the URL of the page containing the API.
#print(soup)
datasets = []
for link in soup.find_all('a'):
  path = link.get('href')
  try:
    if "http" in path:
      datasets.append(path)
  except:
    pass
#print(datasets)

dataset_url = datasets[-21]
print(dataset_url)

#The API end point has been obtained from the previous webpage.
# print(type(dataset_url))
response2 = requests.get("https://data.cdc.gov/resource/8xkx-amqh.json")

def write_json(filepath, data, encoding='utf-8', ensure_ascii=False, indent=2):
    """
    This function dumps the JSON object in the dictionary `data` into a file on
    `filepath`.
    Parameters:
        filepath (string): The location and filename of the file to store the JSON
        data (dict): The dictionary that contains the JSON representation of the objects.
    Returns:
        None
    """
    with open(filepath, 'w', encoding=encoding) as file_obj:
        json.dump(data, file_obj, ensure_ascii=ensure_ascii, indent=indent)

write_json("response2.json", response2)

def user_input():
    """
    This function displays the dataset after being filtered as per user choice. This function primarily
    serves to showcase different ways to fecth the same dataset.
    Parameters:
        None
    Returns:
        None
    """
    area = input("Select Washington county or Michigan State")
    if area == "Washington County":
        df_Washington = pd.read_json("https://data.cdc.gov/resource/8xkx-amqh.json")
        df_Washington = df_Washington.loc[df_Washington['recip_county']=='Washington County']
        df_Washington.to_csv("WashingtonCounty.csv", index=False)
        print(df_Washington)
    elif area == "Michigan State":
        df_Michigan = pd.read_csv(r"COVID-19.csv")
        df_Michigan = df_Michigan.loc[df_Michigan['Recip_State'] == 'MI']
        df_Michigan.to_csv('MIState.csv', index=False)
        print(df_Michigan)

def create_database():
    """
    This function is to create a database table in SQLite3.
    Parameters:
        None
    Returns:
        None
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_covid_db_sql = "DROP TABLE IF EXISTS 'County_Covid_Data'"

    create_covid_db_sql = '''
        CREATE TABLE IF NOT EXISTS "County_Covid_Data" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Date" DATETIME NOT NULL,
            "Recip_County" TEXT NOT NULL,
            "Recip_State" TEXT NOT NULL,
            "Completeness_pct" FLOAT NOT NULL,
            "Booster_Doses" FLOAT NOT NULL,
            "SVI_CTGY" TEXT NOT NULL,
            "Metro_status" TEXT NOT NULL
        )
    '''
    cur.execute(drop_covid_db_sql)
    cur.execute(create_covid_db_sql)

    conn.commit()
    conn.close()

def populate_database():
    """
    This function is to populate the database table created from the csv file.
    Parameters:
        None
    Returns:
        None
    """

    data_header = []
    data_rows = []

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    with open("COVID-19.csv", 'r') as csvfile:
        data = []
        csv_header = csv.reader(csvfile)
        for h in csv_header:
            data.append(h)
        data_header.extend(data[0])
        data_rows.extend(data[1:])

    insert_covid_db_sql = '''
        INSERT INTO County_Covid_Data
        VALUES (NULL, ?,?,?,?,?,?,?)
    '''

    for dr in data_rows:
        cur.execute(insert_covid_db_sql, [
            dr[0], dr[3], dr[4], dr[5], dr[28], dr[38], dr[-21]
        ])

    conn.commit()
    conn.close()


create_database()
populate_database()

def display_all_data():
    """
    This function is to display the top 20 records in the database table. The records have been limited to allow for easy processing.
    Parameters:
        None
    Returns:
        None
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    calling_command = '''
        SELECT * FROM County_Covid_Data LIMIT 20
        '''
    print(cur.execute(calling_command).fetchall())

display_all_data()


def access_db(state, svi, m):
    """
    This function is to access the database and fetch the percentage of vaccination and recipient county name by filtering state, SVI category and Metro status as per user input.
    Parameters:
        state (str): Recipient State name
        svi(str): SVI category from options A, B, C, or D
        m(str): Metro status of the county - metro or non-metro
    Returns:
        percentage of vaccination and county name
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    fetch_svi = f'''SELECT Completeness_pct, Recip_County FROM County_Covid_Data WHERE Recip_State == '{state}' AND SVI_CTGY == '{svi}' AND Metro_status == '{m}' LIMIT 20 '''
    return cur.execute(fetch_svi).fetchall()
    # return fetch_svi
    conn.commit()
    conn.close()

#Creating list options for generating a tree
states_list = ['MI', 'NY', 'UT', 'OH', 'NC', 'GA', 'IL', 'KY', 'MS', 'MO']
metro_list = ['Metro', 'Non-metro']
SVI_Ctgy = ['A', 'B', 'C', 'D']
tree = {}

def create_tree():
    """
    This function is to create tree structure which is a dictionary of dictionaries.
    Parameters:
        None
    Returns:
        generated tree
    """
    for s in states_list:
        tree[s] = {}
        for m in metro_list:
            tree[s][m] = {}
            for svi in SVI_Ctgy:
                fetch_vaccine = access_db(s, svi, m)
                #print(fetch_vaccine)
                tree[s][m][svi] = fetch_vaccine
                #county_names = county_db_access(s,svi)
    return tree

#Storing the entire tree in a JSON file
obj = create_tree()
write_json("COVID_data_tree.json", obj)


#pprint library has been used to generate the tree in a more efficient manner with increased indent
pprint.pprint(create_tree())

#This dictionary stores user input in the form of key-value pairs
final_dict ={}

@app.route('/', methods=['GET', 'POST'])
def index():
    global final_dict
    # app.logger.info("before")
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/metro', methods = ['POST','GET'])
def metro():
    if request.method == 'GET':
        return "You have accessed the URL directly"
    if request.method == "POST":
        global final_dict
        metro_name = request.form.get("state")
        final_dict['state'] = metro_name
        return render_template('metro.html')

@app.route('/SVI', methods = ['POST','GET'])
def svi():
    if request.method == 'GET':
        return "You have accessed the URL directly"
    if request.method == 'POST':
        global final_dict
        metro_n = request.form.get("metro")
        final_dict['metro'] = metro_n
        return render_template('SVI.html')

@app.route('/final', methods = ['POST','GET'])
def final():
    global final_dict
    if request.method == 'GET':
        # print('This is standard output', file=sys.stdout)
        return "You have accessed the URL directly"

    if request.method == 'POST':
        global final_dict
        metro_n = request.form.get("radgroup")
        final_dict['svi'] = metro_n
        # return final_dict
        # logging.info("I am inside!")
        # logging.config.dictConfig(final_dict)
        obj = create_tree()
        app.logger.info(final_dict)
        empty_list = []
        for key, val in obj.items():
            if key == final_dict['state']:
                for i, j in val.items():
                    # app.logger.info(i)
                    if i == final_dict['metro']:
                        # app.logger.info("I am inside!")
                        for a, b in j.items():
                            if a == final_dict['svi']:
                                empty_list.append(b)
        x_val = []
        y_val = []
        # app.logger.info(empty_list[0])

        for x in empty_list:
            for y in x:
                app.logger.info(y)
                x_val.append(y[0])
                y_val.append(y[1])
            # return(x_val,y_val)
        app.logger.info(x_val)
        app.logger.info(y_val)
        fig = px.bar(empty_list[0],x=y_val, y=x_val)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('final.html', graphJSON=graphJSON)


if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(debug=True)
