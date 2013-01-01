from flask import Flask, request, render_template
import os
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ncgqudzbntrdew:B4byX_aOXb2G7UP40S11KIM7NA@ec2-54-243-249-191.compute-1.amazonaws.com:5432/dcjvicrign3o0r'
db = SQLAlchemy(app)



class Stream(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	link = db.Column(db.String(300))

	def __init__(self,link):
		self.link = link

	def __repr___(self):
		return '<Link is %r>'%self.link


class Fixture(db.Model):
    id = db.Column(db.Integer)
    opponenent = db.Column(db.String(80))
    home = db.Column(db.Boolean(),default=True)
    channel = db.Column(db.String(120))
    channel_us = db.Column(db.String(120))
    date = db.Column(db.DateTime,primary_key=True)
    competition = db.Column(db.String(140))

    def __init__(self, opponenent, home, channel, channel_us, date, competition):
        self.opponenent = opponenent
        self.home = home
        self.channel = channel
        self.channel_us = channel_us
        self.date = date
        self.competition = competition

    def __repr__(self):
        return '<fixure against %r in %r at home? %r on %r channel %r>' % (self.opponenent,self.competition,self.home,self.date,self.channel)



@app.route('/', methods=['GET'])
def index():
	now = datetime.now()
	today = False
	fixtures = Fixture.query.all()
	dates = []
	for f in fixtures:
		if f.date.date() >= now.date():
			dates.append(f.date)
	fixture_date = min(dates,key=lambda date : abs(now-date))
	if fixture_date.date() == now.date():
		today = True
	remaining_day = (fixture_date.date() - now.date()).days
	fixture = Fixture.query.filter_by(date=fixture_date).first()

	if Stream.query.all():
		streams = Stream.query.all()
	else:
		streams = None

	return render_template('index.html',streams=streams,fixture=fixture,today=today,remaining_day=remaining_day)



if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)