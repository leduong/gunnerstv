from bs4 import BeautifulSoup
import requests
from app import db,Fixture,Stream,Channel
from datetime import datetime,timedelta
import json
import pytz
import re


#Scrap fixtures from premierleague.com
def get_world_data():
	countries = ['US', 'SE','NO','AU','IE','IN']
	for country in countries:
		url = "http://www.premierleague.com/content/premierleague-ajax/broadcastschedule.tv.ajax/season:2012-2013/country:%/clubId:1006/rangeType:dateMonth"%country
		r = requests.get(url)
		data = r.json
		for date in data['dateList']:
			for broadcast in date['broadcastList']:
				channel = broadcast['channel']
				date = broadcast['date'] + " " + broadcast['time']
				date = datetime.strptime(date,'%A %d %B %Y %H:%M')
				if Fixture.query.filter_by(date=date).first():
					entry = Fixture.query.filter_by(date=date).first()
					entry.channel.append(Channel(channel,country))
					print entry
					db.session.commit()
				else:
					print "I should add this date for %s viewer"%country

#Scrap US Channel on Arsenal.com blog
def get_us_channel():
	ustz = pytz.timezone('US/Eastern')
	uktz = pytz.timezone('GMT')
	now = datetime.now()
	url ="http://www.arsenal.com/usa/news/features/where-to-watch-arsenal"
	r = requests.get(url)
	soup = BeautifulSoup(r.text,'lxml')
	data = soup.find('h4',class_="full-width").find_next_sibling('p')
	if len(data.find_all('span')) % 3 == 0:
		total_fixtures = len(data.find_all('span')) / 3
	for team in data.find_all('strong'):
		name = team.string.strip()
		date = team.find_previous_sibling('span').string.strip().strip(':') + " " + str(now.year)
		channel_us = team.find_next_sibling('span').string.strip()
		if name.find('@') == 0:
			name = name[name.find('@')+2:]
		elif name.find('vs') == 0:
			name = name[name.find('vs')+3:]
		else:
			print "??? BUG in get_us_channel?"
		date = datetime.strptime(date,'%b. %d - %I:%M%p %Y')
		us_date = ustz.localize(date)
		uk_date = us_date.astimezone(uktz)
		print uk_date,date,us_date
		fix = Fixture.query.all()
		for f in fix:
			if f.date.date() == uk_date.date():
				print "found a match. Adding us channel"
				#convert channel name
				channel_us = Channel(channel_us.replace(' ','-').lower(),"US")
				f.channel.append(channel_us)
				db.session.commit()

#scrap date on gunners
def scrap_fixture_time():
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
				year = str(current_date.year)
				competition = row.find('td',class_="competition").string
				date = day+ " " +month+ " " + year + " " + time
				date = datetime.strptime(date,'%d %B %Y %H:%M')
				date = uktz.localize(date)
				chan = Channel(channel,"GB")
				fixture = Fixture(opponenent, home, date, competition,[chan])
				db.session.add(fixture)
				db.session.add(chan)
				db.session.commit()

scrap_fixture_time()
get_us_channel()





