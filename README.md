# Introduction
This project was implemented as a part of the SI 507 Intermediate Python Programming Course. The dataset has been obained from the Centers for Disease Control and Prevention (CDC) website and includes COVID-19 vaccination data based on counties and states in the United States. The dataset along with the visualization can be used for finding the percentages of vaccinated population in counties based on the State, Metro or Non-metro type counties, and Social Vulnerability Index (SVI).

# Required Packages
1.	Requests
2.	json
3.	bs4 (BeautifulSoup)
4.	pandas
5.	csv
6.	sqlite3
7.	pprint
8.	flask
9.	plotly.express
10.	plotly
11.	plotly.graph_objects

# Environment
This project was implemented in Visual Studio Code and can be run by typing the command "python SI507_Final_Project.py" in the terminal on opening the .py file. 

# User Interaction
On running the .py file, the user will be prompted to choose an option between Washington County and Michigan State. The user can input this through the Visual Studio Code terminal. This serves the purpose to demonstrate various ways (web scraping, .csv, and .json) to access the same dataset. Then, the user can shift over to the localhost server at 127.0.0.0.0/5000 to access the user interface designed through Flask.

# Data Visualization/Data Structure
When the user makes selections as prompted in the user interface on the local host server, the final page depicts a bar plot of the percentage of COVID-19 vaccinations as per county. At the back end, a tree data structure has been first generated based on user-inputted values, stored in a .json format, and then converted to a bar plot using plotly with Flask.

