from bs4 import BeautifulSoup
import requests
from app import db,Fixture,Stream
from datetime import datetime,timedelta
import json
import pytz
import re

#Scrap fixtures from premierleague.com
def get_us_data():
	url = "http://www.premierleague.com/content/premierleague-ajax/broadcastschedule.tv.ajax/season:2012-2013/country:US/clubId:1006/rangeType:dateMonth"
	r = requests.get(url)
	data = r.json
	uktz = pytz.timezone('GMT')
	ustz = pytz.timezone('US/Eastern')
	for date in data['dateList']:
		for broadcast in date['broadcastList']:
			channel_us = broadcast['channel']
			date = broadcast['date'] + " " + broadcast['time']
			date = datetime.strptime(date,'%A %d %B %Y %H:%M')
			if Fixture.query.filter_by(date=date).first():
				entry = Fixture.query.filter_by(date=date).first()
				entry.channel_us = channel_us
				db.session.commit()
			else:
				print "I should add this date for US viewer"


#scrap date on gunners
def scrap_fixture_time():
	#Reset db for testing
	db.drop_all()
	db.create_all()
	#get date variables
	uktz = pytz.timezone('GMT')
	current_date = datetime.now(uktz)
	current_month = current_date.strftime('%B')
	next_month_date = current_date + timedelta(days=30)
	next_month = next_month_date.strftime('%B')
	#Scrapping arsenal.com
	url = "http://www.arsenal.com/fixtures/fixtures-reports"
	response = requests.get(url)
	html = response.text
	soup = BeautifulSoup(html,'lxml')
	table_month = soup.find('th',class_='first',text=[current_month]).find_parent('table')
	table_next_month = soup.find('th',class_='first',text=[next_month]).find_parent('table')
	tables = [table_month,table_next_month]
	#scrap the data from the tables
	for table in tables:
		month = table.find('th',class_='first').string
		print month
		for row in table.find_all('tr'):
			home = False
			channel = None
			if row.find('td',class_="time") and row.find('td',class_="competition"):
				if row.find('td',class_='home-away').string == 'H':
					home = True
				if row.find('td',class_="tv-channel"):
					channel = row.find('td',class_="tv-channel").string.strip()
				opponenent = row.find('td',class_="opposition").string.strip()
				time = row.find('td',class_="time").string.strip()
				if len(time) == 0:
					time = "15:00"
				day = row.find('td',class_="first").string
				if day.find('/'):
					day = day.split('/')[0]
				if month == 'December':
					year = '2012'
				else:
					year = '2013'
				competition = row.find('td',class_="competition").string
				date = day+ " " +month+ " " + year + " " + time
				date = datetime.strptime(date,'%d %B %Y %H:%M')
				date = uktz.localize(date)
				channel_us = None
				fixture = Fixture(opponenent, home, channel,channel_us, date, competition)
				db.session.add(fixture)
				db.session.commit()

def get_stream():
	url = "http://atdhe.eu/soccer"
	html = requests.get(url).text
	soup = BeautifulSoup(html,'lxml')

	streams = soup.find_all(text=re.compile('Arsenal'))
	for s in streams:
		link = Stream(s.parent['href'])
		db.session.add(link)
		db.session.commit()

scrap_fixture_time()
get_us_data()
get_stream()






