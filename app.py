from flask import Flask, jsonify, render_template
import os
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://qjfzfnhyhuugtm:2CHyGsZ9ONlw7oShE9bLS5ZY_3@ec2-54-243-182-70.compute-1.amazonaws.com:5432/d7trb2ktuglkdb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gunnerstv.db'

db = SQLAlchemy(app)


fixture_channels = db.Table('fixture_channels',
db.Column('channel_id', db.Integer, db.ForeignKey('channel.id')),
db.Column('fixture_id', db.Integer, db.ForeignKey('fixture.id'))
)


class Fixture(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    opponenent = db.Column(db.String(80))
    home = db.Column(db.Boolean(),default=True)
    date = db.Column(db.DateTime)
    competition = db.Column(db.String(140))
    channel = db.relationship('Channel',secondary=fixture_channels, backref=db.backref('fixtures', lazy='dynamic'))

    def __init__(self, opponenent, home, date, competition,channel):
        self.opponenent = opponenent
        self.home = home
        self.date = date
        self.competition = competition
        self.channel = channel

    def __repr__(self):
        return '<fixure against %r in %r on %r>' % (self.opponenent,self.competition, self.channel)


class Channel(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	channelname = db.Column(db.String(140))
	country	= db.Column(db.String(100))

	def __init__(self,channelname,country):
		self.channelname = channelname
		self.country =country

	def __repr__(self):
		return '<Channel %r in %r>'%(self.channelname,self.country)


class Stream(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	source = db.Column(db.String(300))
	width = db.Column(db.Integer)
	height = db.Column(db.Integer)

	def __init__(self,source,width,height):
		self.source = source
		self.width = width
		self.height = height

	def __repr___(self):
		return '<source is %r>'%self.source


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

	#create Country channel json
	channels = {}
	for channel in fixture.channel:
		channels[channel.channelname] = channel.country


	#create stream json
	if Stream.query.all():
		s = Stream.query.all()
		streams = {}
		for t in s:
			streams[t.id] = {'source':t.source,'width':t.width,'height':t.height}
	else:
		streams = None

	return render_template('index.html',streams=streams,channels=channels,fixture=fixture,today=today,remaining_day=remaining_day)



if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)