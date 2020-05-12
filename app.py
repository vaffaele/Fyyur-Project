#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import string
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description=db.Column(db.String(120))
    website=db.Column(db.String(120))



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue =db.Column(db.Boolean)
    seeking_description=db.Column(db.String(120))
    website=db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
    __tablename__ = 'Shows'
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_tima = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():

    return render_template('pages/home.html',results=populate_homepage_venue(),result=populate_homepage_artist())


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_venue = Venue.query.distinct(Venue.city,Venue.state).all()

    data=[]
    city=[]
    state=[]

    for v in all_venue:
        a=v.city
        b=v.state

        city.append(a)
        state.append(b)

    for i in range(len(city)):
        c=city[i]
        d=state[i]


        all_venue2 = Venue.query.order_by('city').filter_by(city = c).filter_by(state=d).all()
        temp1=[]
        for venue in all_venue2:
                show_upcoming = Shows.query.filter(Shows.start_tima > datetime.today()).filter_by(venue_id=venue.id).count()
                temp2={ "id": venue.id,
                    "name":venue.name.title(),
                    "num_upcoming_shows": show_upcoming}
                temp1.append(temp2)


        temp_data ={
                "city": c,
                "state": d,
                "venues": temp1}
        data.append(temp_data)


    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_form = request.form.get('search_term', '')
  list = Venue.query.filter(Venue.name.ilike('%'+search_form+'%')).all()
  count = len(list)

  response = []
  partial_response =[]
  city_response = []
  city_partial_response =[]




  for v in list:

          show_for_venue = Shows.query.filter(Shows.start_tima > datetime.today()).filter_by(venue_id=v.id).count()

          temp_resp={ "id": v.id,
                  "name": v.name,
                  "num_upcoming_shows": show_for_venue,}

          partial_response.append(temp_resp)


  city_list=Venue.query.filter(Venue.city.ilike('%'+search_form+'%')).all()
  city_count = Venue.query.filter(Venue.city.ilike('%'+search_form+'%')).count()

  for c in city_list :
      show_for_venue = Shows.query.filter(Shows.start_tima > datetime.today()).filter_by(venue_id=c.id).count()

      resp={ "id": c.id,
              "name": c.name,
              "num_upcoming_shows": show_for_venue,}
      city_partial_response.append(resp)


  response = {"count": count,"data":partial_response}
  city_response = {"count": city_count,"data":city_partial_response}

  return render_template('pages/search_venues.html', results=response, result =city_response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  venue_genres= venue.genres[1:-1].split(",")
  show_for_venue = Shows.query.filter_by(venue_id=venue_id).all()
  upcoming_count=0
  past_shows=0
  data_upcoming=[]
  data_past=[]
  for s in show_for_venue:
      if s.start_tima >= datetime.today():
          #artist = Artist.query.get(s.artist_id)

          artist = Artist.query.join(Shows).filter_by(artist_id=s.artist_id).first()
          temp={
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(s.start_tima)
          }
          upcoming_count+=1
          data_upcoming.append(temp)
      else:
          artist = Artist.query.join(Shows).filter_by(artist_id=s.artist_id).first()
          temp={
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(s.start_tima)
          }

          data_past.append(temp)
          past_shows+=1



  current_data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue_genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": data_past,
      "upcoming_shows": data_upcoming,
      "past_shows_count": past_shows,
      "upcoming_shows_count": upcoming_count,

      }


  return render_template('pages/show_venue.html', venue=current_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

    if request.form['seeking_talent']=='True':
        seeking=True
    else:
        seeking=False

    error = False
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    address = request.form['address']
    facebook_link = request.form['facebook_link']
    genres= request.form.getlist('genres')
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_talent = seeking
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, city=city, state= state,
                    phone = phone,address= address,facebook_link= facebook_link,
                    genres = genres,image_link=image_link,website=website,
                    seeking_talent=seeking_talent,seeking_description=seeking_description)

    try:
        db.session.add(venue)
        db.session.commit()

        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    finally:
        db.session.close()



    if not error:
        return render_template('pages/home.html',results=populate_homepage_venue(),result=populate_homepage_artist())
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):

    error = False
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        deleting_venue = Venue.query.get(venue_id)

        db.session.delete(deleting_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html',results=populate_homepage_venue(),result=populate_homepage_artist())

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  list_artist = Artist.query.all()
  for artist in list_artist:
      temp_data={
        "id": artist.id,
        "name": artist.name.title(),
      }
      data.append(temp_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_form = request.form.get('search_term', '')
  artist_list = Artist.query.filter(Artist.name.ilike('%'+search_form+'%')).all()
  count = Artist.query.filter(Artist.name.ilike('%'+search_form+'%')).count()

  response = []
  partial_response =[]
  city_response = []
  city_partial_response =[]

  for artist in artist_list:
          show_upcoming = Shows.query.filter(Shows.start_tima > datetime.today()).filter_by(artist_id=artist.id).count()
          temp_resp={ "id": artist.id,
                  "name": artist.name,
                  "num_upcoming_shows": show_upcoming,}

          partial_response.append(temp_resp)

  city_list=Artist.query.filter(Artist.city.ilike('%'+search_form+'%')).all()
  city_count = Artist.query.filter(Artist.city.ilike('%'+search_form+'%')).count()

  for c in city_list :
      show_upcoming = Shows.query.filter(Shows.start_tima > datetime.today()).filter_by(artist_id=c.id).count()
      temp_resp={ "id": c.id,
              "name": c.name,
              "num_upcoming_shows": show_upcoming,}
      city_partial_response.append(temp_resp)

  response = {"count": count,"data":partial_response}

  city_response = {"count": city_count,"data":city_partial_response}

  return render_template('pages/search_artists.html', results=response,result=city_response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  artist_genres= artist.genres[1:-1].split(",")
  show_for_venue = Shows.query.filter_by(artist_id=artist_id).all()
  upcoming_count=0
  past_shows=0
  data_upcoming=[]
  data_past=[]
  for s in show_for_venue:
      if s.start_tima >= datetime.today():
          venue = Venue.query.join(Shows).filter_by(venue_id=s.venue_id).first()
          temp={
          "artist_id": venue.id,
          "artist_name": venue.name,
          "artist_image_link": venue.image_link,
          "start_time": str(s.start_tima)
          }
          upcoming_count+=1
          data_upcoming.append(temp)
      else:
          venue = Venue.query.join(Shows).filter_by(venue_id=s.venue_id).first()
          temp={
          "artist_id": venue.id,
          "artist_name": venue.name,
          "artist_image_link": venue.image_link,
          "start_time": str(s.start_tima)
          }

          data_past.append(temp)
          past_shows+=1


  current_data={
      "id": artist.id,
      "name": artist.name,
      "genres":artist_genres ,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": data_past,
      "upcoming_shows": data_upcoming,
      "past_shows_count": past_shows,
      "upcoming_shows_count": upcoming_count,

       }

  return render_template('pages/show_artist.html', artist=current_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist_edit = Artist.query.get(artist_id)
  form = ArtistForm(name = artist_edit.name, city =  artist_edit.city,
                        state=  artist_edit.state, phone= artist_edit.phone)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_edit)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()


  try:
      a=Artist.query.get(artist_id)
      a.name = request.form['name']
      a.city = request.form['city']
      a.state = request.form['state']
      a.phone = request.form['phone']
      a.facebook_link = request.form['facebook_link']


      db.session.commit()


      flash('Artist' + request.form['name'] + ' was successfully updated!')
  except:
      db.session.rollback()
      error = True
      flash('An error occurred. Venue ' + a.name + ' could not be listed.')
  finally:
      db.session.close()

  return render_template('pages/home.html',results=populate_homepage_venue(),result=populate_homepage_artist(), form=form, artist = a)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_edit = Venue.query.get(venue_id)
  form = VenueForm(name = venue_edit.name, city =  venue_edit.city,
                        state=  venue_edit.state,address = venue_edit.address, phone= venue_edit.phone)
  return render_template('forms/edit_venue.html', venue = venue_edit, form = form)

@app.route('/venues/<int:venue_id>/edit/', methods=['POST'])
def fname(venue_id):


  form = VenueForm()


  try:
      v=Venue.query.get(venue_id)
      v.name = request.form['name']
      v.city = request.form['city']
      v.state = request.form['state']
      v.phone = request.form['phone']
      v.address = request.form['address']
      v.facebook_link = request.form['facebook_link']


      db.session.commit()


      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
      db.session.rollback()
      error = True
      flash('An error occurred. Venue ' + v.name + ' could not be listed.')
  finally:
      db.session.close()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('pages/home.html', results=populate_homepage_venue(),result=populate_homepage_artist(),form=form, venue=v)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if request.form['seeking_venue']=='True':
      seeking=True
  else:
      seeking=False

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  image_link = request.form['image_link']
  seeking_venue = seeking
  seeking_description = request.form['seeking_description']

  artist_new = Artist(name=name, city=city, state= state, phone = phone,facebook_link= facebook_link,
                        genres=genres,website=website,image_link=image_link,
                        seeking_venue=seeking_venue,seeking_description=seeking_description)
  try:
      db.session.add(artist_new)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully created!')
  except:
      db.session.rollback()
      error = True
      flash('An error occurred. Artist ' + artist_new.name + ' could not be listed.')
  finally:
      db.session.close()

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html',results=populate_homepage_venue(),result=populate_homepage_artist())

@app.route('/artists/<int:artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):

    deleting_artist = Artist.query.get(artist_id)
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        deleting_artist = Artist.query.get(artist_id)

        db.session.delete(deleting_artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()


    return render_template('pages/home.html',results=populate_homepage_venue(),result=populate_homepage_artist())


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  all_shows = Shows.query.all()
  for show in all_shows:
      venue =Venue.query.get(show.venue_id)
      artist = Artist.query.get(show.artist_id)
      data_temp={
        "venue_id":show.venue_id,
        "venue_name":venue.name,
        "artist_id":show.artist_id,
        "artist_name":artist.name,
        "artist_image_link":artist.image_link,
        "start_time": str(show.start_tima)
      }
      data.append(data_temp)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  curr_venue = Venue.query.get(request.form['venue_id'])
  curr_artist= Artist.query.get(request.form['artist_id'])

  date = request.form['start_time']


  if curr_venue==None or curr_artist==None:
      flash('Show not listed!...Invalid ArtistID or Invalid VenueID')
  else:
      try:
          insert_show = Shows(venue_id=curr_venue.id, artist_id = curr_artist.id, start_tima=date )
          db.session.add(insert_show)
          db.session.commit()
          flash('Show was successfully listed!')

      except:
         db.session.rollback()
         flash('Show not listed!')
      finally:
          db.session.close()
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html',results=populate_homepage_venue(),result=populate_homepage_artist())

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')



def populate_homepage_venue():

        list = Venue.query.order_by(Venue.id.desc()).limit(10).all()
        response = []
        partial_response =[]

        for v in list:
                show_for_venue = Shows.query.filter_by(venue_id=v.id).count()
                resp={ "id": v.id,
                        "name": v.name,
                        "num_upcoming_shows": show_for_venue,}

                partial_response.append(resp)
        response = {"data":partial_response}
        return response
def populate_homepage_artist():

        list = Artist.query.order_by(Artist.id.desc()).limit(10).all()
        response = []
        partial_response =[]
        count=0
        for a in list:
                show_for_venue = Shows.query.filter_by(artist_id=a.id).count()
                resp={ "id": a.id,
                        "name": a.name,
                        "num_upcoming_shows": show_for_venue,}

                partial_response.append(resp)


        response = {"data":partial_response}
        return response
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
