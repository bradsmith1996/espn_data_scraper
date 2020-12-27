#!/usr/local/bin/python3
# Brad Smith
# 12/27/2020
# Run with python 3
from bs4 import BeautifulSoup
import requests
import lxml
import matplotlib.pyplot as plt
import numpy as np

class EspnCollegeFootballTeamStats:
   data = {}
   url = ''
   years = []
   espn_url = "https://www.espn.com"
   fbs_football_teams_url = "https://www.espn.com/college-football/teams"
   #fbs_football_teams_url = "https://www.espn.com/nfl/teams"
   team_name = ""
   team_name_search = ""
   def __init__(self, a_name, a_start_year, a_end_year):
      # Set range of years:
      self.years = list(range(a_start_year, a_end_year+1))
      # Find team statistics url:
      html_content = requests.get(self.fbs_football_teams_url).text
      soup = BeautifulSoup(html_content, "lxml")
      self.team_name_search = a_name
      append_url = ''
      tables = soup.find("div", attrs={"class": "layout is-split"})
      INDEX_CONFERENCE = 0
      INDEX_TEAMS = 1
      for collumns in tables.find_all("div", attrs={"class": "layout__column"}):
         for conferences in collumns.find_all("div",attrs={"class": "mt7"}):
            conference = conferences.find_all("div")
            for team in conference[INDEX_TEAMS].find_all("section", attrs={"class":"TeamLinks flex items-center"}):
               team_name = team.find("h2")
               team_stats_url = team.find("span").find("a", href=True)
               if str(self.team_name_search) in str(team_name.text):
                  append_url = team_stats_url['href']
      self.url = self.espn_url+append_url
   def computePlayerStatistics(self):
      for year in self.years:
         self.data[year] = {}
         temp = self.url +"/season/"+str(year)
         # Make a GET request to fetch the raw HTML content
         html_content = requests.get(temp).text
         # Parse the html content:
         soup = BeautifulSoup(html_content, "lxml")
         page_tables = soup.find_all("div", attrs={"class": "ResponsiveTable ResponsiveTable--fixed-left mt5 remove_capitalize"})
         element = {}
         for table in page_tables: # Change this to general
            table_title = table.find("div", attrs={"class": "Table__Title"})
            element[table_title.text] = {}
            self.data[year][table_title.text] = {}
            left_table = table.find("div", attrs={"class": "flex"}).find("table")
            left_table_header = left_table.find("thead")
            self.data[year][table_title.text][left_table_header.text] = []
            for element in left_table.find("tbody"):
               self.data[year][table_title.text][left_table_header.text].append(element.text)
            right_table = table.find("div", attrs={"class": "flex"}).find("div", attrs = {"class": "Table__Scroller"}).find("table")
            temp = right_table.find("tr")
            for header in right_table.find("tr").find_all("th"):
               self.data[year][table_title.text][header.text] = []
            for line in right_table.find("tbody").find_all("tr"):
               for header, data_point in zip(right_table.find("thead").find("tr").find_all("th"), line.find_all("td")):
                  self.data[year][table_title.text][header.text].append(data_point.text.replace(',', ''))
   def computeTeamStatistics(self):
      print("This method is TBD")


if __name__ == "__main__":
   # Start and end date of ESPN data:
   start_year = 2004
   end_year = 2020
   TOTAL_COLLUMN = -1

   team = EspnCollegeFootballTeamStats("Virginia Tech", start_year, end_year)
   #team = EspnCollegeFootballTeamStats("Oregon Ducks", start_year, end_year)
   team.computePlayerStatistics()

   # Make years list as string:
   years_list = [int(item) for item in team.years]
   bar_width = 0.35

   passing_list = []
   rushing_list = []
   fig = plt.figure()
   for key in team.data:
      passing_list.append(float(team.data[key]['Passing']['YDS'][TOTAL_COLLUMN]))
      rushing_list.append(float(team.data[key]['Rushing']['YDS'][TOTAL_COLLUMN]))
   ax = fig.add_axes([0.1,0.1,0.8,0.8])
   ax.yaxis.grid()
   ax.bar(years_list, passing_list, label="Passing Yards", width=bar_width)
   ax.bar(years_list, rushing_list, label="Rushing Yards", width=bar_width, bottom=passing_list)
   plt.title("ESPN Sourced Total Yards: "+team.team_name_search)
   ax.set_ylabel('Year')
   ax.set_ylabel('Yards')
   ax.set_xticks(years_list)
   ax.set_yticks(np.arange(0, 12000, 1000))
   plt.xticks(rotation=45)
   plt.legend()
   plt.draw()
   plt.savefig(team.team_name_search+".png")