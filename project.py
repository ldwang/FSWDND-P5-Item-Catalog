from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category,Item, User

from flask import session as login_session
import random, string

from oauth2client.client import  flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from functools import wraps

app = Flask(__name__)


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#Google Connect Authenitcation
G_ClIENT_ID = json.loads(
    open('google_client_secret.json','r').read())['web']['client_id']
G_APPLICATION_NAME = "Item Catalog App"

#create a state token to prevent request forgery.
#store it in the session for later validation.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    #render the login template
    return render_template('login.html', STATE = state)

@app.route('/logout')
def logout():
    if 'gplus_id' in login_session:
        print "redirect to gdisconnect"
        return redirect(url_for('gdisconnect'))
    else:
        response = make_response(
            json.dumps('Not logged in as google_plus user before'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/gconnect', methods= ['POST'])
def gconnect():
# Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # obtain authorization code
    code = request.data

    try:
        # upgrade the authorization code into a credentails object
        oauth_flow = flow_from_clientsecrets('google_client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the acess token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if there was an error in the access token info. abort
    if result.get('error') is not None:
        response = make_response(
            json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != G_ClIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


#user helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None

def checkUser():
    if 'user_id' not in login_session:
        return None
    else:
        return getUserInfo(login_session['user_id'])

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

#decroater to check login status
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            print request.url
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# DISCONNECT - REVOKE a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    # access_token = login_session.get('access_token')
    # print 'In gdisconnect credentials is %s' % credentials
    # print 'User name is: '
    # print login_session['username']
    if credentials is None:
        print 'Crediential is None'
        # response = make_response(json.dumps("Current user not connected"), 401)
        # response.headers['Content-Type'] = 'application/json'
        # return response
        flash("Current user not connected")
        return render_template('logout.html')
    access_token = credentials.access_token
    print access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print 'result is '
    # print result

    if result['status'] == '200':
        # del login_session['credentials']
        # del login_session['gplus_id']
        # del login_session['username']
        # del login_session['email']
        # del login_session['picture']
        # del login_session['user_id']
        # response = make_response(json.dumps("Successfully disconnected"), 200)
        # response.headers['Content-Type'] = 'application/json'
        # return response
        login_session.clear()
        flash("Successfully disconnected")
    else:
        login_session.clear()
        flash("Failed to revoke token for given user.")
    return render_template('logout.html')

#show the catelog homepage with latest items
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    latestItems = session.query(Item).order_by(desc(Item.created))
    #latestItems = latestItems[:10]
    print login_session
    print checkUser()
    return render_template('catalog.html', categories = categories, latestItems = latestItems, user = checkUser())

#Show a category item list
@app.route('/catalog/<int:cat_id>')
def showCategory(cat_id):
    categories = session.query(Category).order_by(asc(Category.name))
    selectedCategory = session.query(Category).filter_by(id = cat_id).one()
    items = session.query(Item).filter_by(cat_id = cat_id).all()
    return render_template('category.html', items=items, categories = categories, selectedCategory = selectedCategory, user=checkUser())

#Show a specific item detail
@app.route('/item/<int:item_id>')
def showItem(item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    return render_template('item.html', item = item, user=checkUser())


#Add item
@app.route('/item/new/',methods=['GET','POST'])
@login_required
def newItem():
    if request.method == 'POST':
        print request.form
        newItem = Item(name=request.form['name'],description=request.form['description'],
                            cat_id=request.form['cat_id'], user = checkUser() )
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created' % (newItem.name))
        return redirect(url_for('showItem', item_id=newItem.id))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('newitem.html', user=checkUser(),categories=categories)


#Edit Ttem
@app.route('/item/<int:item_id>/edit/', methods=['GET','POST'])
@login_required
def editItem(item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    #check if user is the creator
    if editedItem.user != checkUser():
        flash("You are not allowed to edit other user's item.")
        return redirect(url_for('showItem', item_id=item_id))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['cat_id']:
            editedItem.cat_id = request.form['cat_id']
        session.add(editedItem)
        session.commit()
        flash("Item successfully Edited.")
        return redirect(url_for('showItem', item_id=item_id))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('edititem.html', item=editedItem, user=checkUser(), categories=categories)

#Delete Item
@app.route('/item/<int:item_id>/delete/', methods=['GET','POST'])
@login_required
def deleteItem(item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    cat_id = itemToDelete.cat_id
    # check if user is the creator
    if itemToDelete.user != checkUser():
        flash("You are not allowed to delete other user's item.")
        return redirect(url_for('showItem', item_id=item_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item %s successfully Deleted." % (itemToDelete.name))
        return redirect(url_for('showCategory', cat_id=cat_id))
    else:
        #categories = session.query(Category).order_by(asc(Category.name))
        return render_template('deleteitem.html', item=itemToDelete, user=checkUser())

#JSON APIs to view Catalog Information
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).order_by(asc(Category.name))
    return jsonify(categories=[c.serialize for c in categories])

@app.route('/catalog/<int:cat_id>/JSON')
def categoryJSON(cat_id):
    category = session.query(Category).filter_by(id=cat_id).one()
    items = session.query(Item).filter_by(cat_id=cat_id).all()
    return jsonify(items=[i.serialize for i in items])

@app.route('/item/<int:item_id>/JSON')
def itemJSON(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item.serialize)

@app.route('/catalog.json')
def catalogAllJSON():
    categories = session.query(Category).order_by(asc(Category.name))
    catalog_list = []
    for c in categories:
        cat_dict = {}
        items = session.query(Item).filter_by(cat_id=c.id).all()
        cat_dict["name"] = c.name
        cat_dict["id"] = c.id
        cat_dict["item"] = [i.serialize for i in items]
        catalog_list.append(cat_dict)
    return jsonify(categories=catalog_list)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port = 8000)
