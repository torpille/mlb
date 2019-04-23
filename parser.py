from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from models import Base, Game
from dateutil import parser
from sortedcontainers import SortedSet
import numpy as np
from gamelinks import gamelinks
# gamelinks = ['http://www.espn.com/mlb/game?gameId=401075835']



# db_config_line = 'sqlite:///db.sqlite'
db_config_line = 'mysql+pymysql://admin:admin@127.0.0.1:3306/espn_mlb'
def get_html(url):
    r = requests.get(url, timeout = (100, 100))
    return r.text

def add_games_to_db(url, session):
    def get_team_info(team):
        long_name = team.find(class_="long-name").text
        short_name = team.find(class_="short-name").text
        full_name = long_name + ' ' + short_name
        record = team.find(class_="record").text
        return long_name, short_name, full_name, record


    scheldule_html = get_html(url)
    soup = BeautifulSoup(scheldule_html, 'html5lib')
    
    id = url.split('=')[-1]
    print(id)
    game = session.query(Game).filter_by(id=id).first()
    if not game:
        game = Game(id=id)
        date_time = soup.find(attrs={"data-date":True})
        if date_time:
            date_time = date_time.get("data-date")
            game.date = date_time.split('T')[0]
            game.time = date_time.split('T')[-1].split('Z')[0]
            tbd = soup.find(class_='game-date')
            tbd = (str(tbd).split('data-istbd="')[-1].split('"')[0])
            if tbd == "true":
                game.tbd = True

            teams = soup.find_all(class_="team-info")
            loc = soup.find(class_='icon-font-before icon-location-solid-before')
            city = loc.text.split(',')[0].split('   ')[-1]
            if city:
                game.city = city
            else:
                city = loc.text.strip()
                game.city = city
            state = loc.text.split(',')[-1].split(' ')[0].strip()
            if state:
                game.state = state
            else:
                game.state = 'outside the US'

            stadium = soup.find(class_='caption-wrapper')
            if stadium:
                    game.stadium = stadium.text.strip().split('\n')[0]
            else:
                stadium = soup.find(class_='venue-date')
                if stadium:
                    game.stadium = stadium.text.split('-')[0]
                
                else:
                    stadium = soup.find(class_='location-details')
                    if stadium:
                        game.stadium = stadium.text.strip().split('\n')[0]  

            last_games = soup.find(class_='last-games sub-module__tabs')
            if last_games:
                results = last_games.find_all(class_='game-result')
                visiting_results = results[0:5]
                home_results = results[5:10]
                visiting_last_games = []
                home_last_games =[]
                for result in home_results:
                    current_result = result.next + result.next.next
                    home_last_games.append(current_result)
                for result in visiting_results:
                    current_result = result.next + result.next.next
                    visiting_last_games.append(current_result) 
                visiting_last_games = ', '.join(visiting_last_games)
                home_last_games = ', '.join(home_last_games)
            else:
                visiting_last_games = 'no information'
                home_last_games = 'no information'


            game.visiting_last_games = visiting_last_games
            game.home_last_games = home_last_games


            visiting_pitchers = [[''] * 3 for i in range(1)]
            home_pitchers = [[''] * 3 for i in range(1)]
            pitchers_block = soup.find_all(class_ = 'stats-wrap stats-wrap--post')
            
            if pitchers_block:
                pitchers_block = pitchers_block[1:4:2] 

                teams_links = []
                for pitchers in pitchers_block:
                    current_team_links = []    
                    pitchers_links = pitchers.find_all('a')
                    for pitcher_link in pitchers_links:
                        p_link = str(pitcher_link)
                        a=p_link.find('http://')
                        b=p_link.find('" name')
                        current_team_links.append(p_link[a:b])
                    teams_links.append(current_team_links)
                    
                     
                visiting_pitcher_list = get_pitchers(teams_links[0])
                home_pitcher_list = get_pitchers(teams_links[1])
            else:
                visiting_pitcher_list = visiting_pitchers
                home_pitcher_list = home_pitchers

                

            game.visiting_pitcher_name, game.visiting_pitcher_birthdate, game.visiting_pitcher_birthplace = visiting_pitcher_list
                

            game.home_pitcher_name, game.home_pitcher_birthdate, game.home_pitcher_birthplace = home_pitcher_list



            game.visiting_long_name, game.visiting_short_name, game.visiting_full_name, game.visiting_record = get_team_info(teams[0])
            game.home_long_name, game.home_short_name, game.home_full_name, game.home_record = get_team_info(teams[1])
            

            session.add(game)
            session.commit()
            print('Done')
        else:
            print("Page didn't load")

def get_pitchers(current_team):
                    
                    for t_link in current_team:
                        pitcher_html = get_html(t_link)
                        p_soup = BeautifulSoup(pitcher_html, 'html5lib')
                        p_name = p_soup.find('h1').text
                        if p_name != 'MLB Players':
                            
                            p_data = p_soup.find(class_='player-metadata floatleft')
                            date = str(p_data).split('/span>')[1].split(' (')[0]
                            birth_date = date_format(date).strip()
                            birth_date = birth_date.replace(' ', '-')
                            birth_place = str(p_data).split('/span>')[2].split('<')[0]
                            pitcher = []
                            pitcher.extend((p_name, birth_date, birth_place))
                            
                    return pitcher

def date_format(date):
    d = date.split(',')
    d.reverse()
    word_date =' '.join(d)
    word_month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    num_month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    for i in range(12):
        a =(change_name(word_date, word_month[i], num_month[i]))
        if a != None:
            return a
    
def change_name(str, old, new):
    i = str.find(old)
    if i > 0:
        old_len = len(old)
        str = str[:i] + new + str[i+old_len:]
        return str


def main():
    engine = create_engine(db_config_line)
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for link in gamelinks:
        add_games_to_db(link, session)
        print(link)

if __name__ == '__main__':
    main()
