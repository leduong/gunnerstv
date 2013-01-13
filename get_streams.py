import re
from bs4 import BeautifulSoup
import requests
from app import db,Stream


blacklisted =['hqfooty.tv','hdsportz.net']

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
	url = "http://atdhe.eu/soccer"
	html = requests.get(url).text
	soup = BeautifulSoup(html,'lxml')
	streams = soup.find(id='table_linky').find_all(text=re.compile('Arsenal'))
	for s in streams:
		link = s.parent['href']
		if link.find('atdhe') != -1:
			stream = requests.get(link)
			if stream.status_code == 200:
				bs = BeautifulSoup(stream.text,'lxml')
				try:
					if int(bs.find('iframe')['height']) >= 400:
						print "stream not an ad"
						stream_url = bs.find('iframe')['src']
						stream_width = bs.find('iframe')['width']
						stream_height = bs.find('iframe')['height']
						if stream_url.split('/')[2] not in blacklisted:
							source = Stream(stream_url,stream_width,stream_height)
							db.session.add(source)
							db.session.commit()
							print "added",stream_url
						else:
							print "stream is blacklisted"
				except:
					print "probably an AD", bs.find('iframe')['src']
	print deleted



	# if requests.get(link) == 200:
	# 	db.session.add(link)
	# 	db.session.commit()
	# 	print "adding..."
	# 	added += 1
	# print "Finished getting new stream. Deleted %s and added %s streams"%(deleted,added)



get_stream()