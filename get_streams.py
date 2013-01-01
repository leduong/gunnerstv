import re
from bs4 import BeautifulSoup
import requests
from app import Stream,db


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

get_stream()