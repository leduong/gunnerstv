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
				channel_us = channel_us.replace(' ','-').lower()
				f.channel_us = channel_us
				db.session.commit()

#scrap date on gunners
def scrap_fixture_time():
	#Reset db for testing
	# db.drop_all()
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
	deleted = 0
	added = 0
	for stream in Stream.query.all():
		db.session.delete(stream)
		db.session.commit()
		print "deleting..."
		deleted += 1

	streams = soup.find_all(text=re.compile('Arsenal'))
	for s in streams:
		link = Stream(s.parent['href'])
		db.session.add(link)
		db.session.commit()
		print "adding..."
		added += 1
	print "Finished getting new stream. Deleted %s and added %s streams"%(deleted,added)

#scrap_fixture_time()
get_us_channel()
# get_stream()






