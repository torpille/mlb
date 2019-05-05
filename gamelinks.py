import requests
from bs4 import BeautifulSoup
from multiprocess import Pool
from sortedcontainers import SortedSet

teamlinks = set()
game_links = set()

def find_game_links(teamlink):
	print(teamlink)
	URL = teamlink
	current_page = requests.get(URL)
	soup = BeautifulSoup(current_page.content, 'html.parser')
	past_games = soup.find_all( class_='ml4')
	future_games = soup.find_all( class_="")
	games = past_games + future_games

	for game in games:
		elems = str(game).split('"')
		for elem in elems:
			if elem.find('http://www.espn.com/mlb/game?gameId=') != -1:
				game_links.add(elem)
				print(elem)
	
def find_team_links():
	URL = 'http://www.espn.com/mlb/teams'
	current_page = requests.get(URL)
	soup = BeautifulSoup(current_page.content, 'html.parser')
	teams = soup.find_all( class_='TeamLinks__Link n9 nowrap')

	for team in teams:
		elems = str(team).split('"')
		for elem in elems:
			if elem.find('mlb/team/schedule') != -1:
				teamlinks.add('http://www.espn.com' + elem)
	print(teamlinks)
	# with Pool(30) as p:
	# 	p.map(find_game_links, teamlinks)
	for link in teamlinks:
		find_game_links(link)

find_team_links()
gamelinks = SortedSet(game_links)


