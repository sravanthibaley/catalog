# !/usr/bin/env python3
# Import Modules
from flask import Flask, render_template, request,\
               redirect, url_for, flash, jsonify
from flask import session as login_session
from flask import make_response

# Importing sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
# Importing database _setup from database_setup.py file
from database_setup import Base, Admin, Category, Product_Details
import os
import random
import string
import httplib2
import json
import requests
# Import login_decorator from login_decorator.py file
from login_decorator import login_required

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
# Database
engine = create_engine("sqlite:///Handbags.db",
                       connect_args={'check_same_thread': False},
                       echo=True)
Base.metadata.bind = engine
#  DBCreate Sessions
DBSession = sessionmaker(bind=engine)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
session = DBSession()

category = session.query(Category).order_by(Category.name)
# Flask Instance
app = Flask(__name__)
app.secret_key = 'itsasecret'


# google client secret
secret_file = json.loads(open('client_secret.json', 'r').read())
CLIENT_ID = secret_file['web']['client_id']
APPLICATION_NAME = 'ItemCatlog'

# create Sessions
DBSession = sessionmaker(bind=engine)
session = DBSession()


# login routing
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# it helps the user to loggedin and display flash profile


# GoogleConnect
@app.route('/gconnect', methods=['POST', 'GET'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')

    # Obtain authorization code

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("""Failed to upgrade
                                            the authorisation code"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
             % access_token)
    header = httplib2.Http()
    result = json.loads(header.request(url, 'GET')[1].decode('utf-8'))

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is'
                                            'already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # ADD PROVIDER TO LOGIN SESSION

    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    admin_id = getUserID(login_session['email'])
    if not admin_id:
        admin_id = createUser(login_session)
    login_session['admin_id'] = admin_id

    output = ''
    output += '<center><h2><font color="red">Welcome '
    output += login_session['name']
    output += '!</font></h1></center>'
    output += '<center><img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['name'])
    print('done..!')
    return output


# Create User in database
def createUser(login_session):
    name = login_session['name']
    email = login_session['email']
    url = login_session['picture']
    newUser = Admin(admin_name=name, admin_email=email, admin_picture=url)
    session.add(newUser)
    session.commit()
    admin = session.query(Admin).filter_by(admin_email=email).first()
    return admin.id


# Getting UserInfornation
def getUserInfo(admin_id):
    admin = session.query(Admin).filter_by(id=admin_id).one()
    return admin


# Getting UserId
def getUserID(admin_email):
    try:
        admin = session.query(Admin).filter_by(admin_email=email).one()
        return admin.id
    except Exception as e:
        print(e)
        return None


# Googledisconnect
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user'
                                            'not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's session.

        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['name']
        del login_session['email']
        del login_session['picture']
        response = redirect(url_for('showcategory'))
        response.headers['Content-Type'] = 'application/json'
        flash("successfully Logout", "success")
        return response
    else:

        # if given token is invalid, unable to revoke token
        response = make_response(json.dumps('Failed to revoke token for user'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


# Display the Categories
@app.route('/')
@app.route('/category/')
def showcategory():
    category = session.query(Category).all()
    productDetails = session.query(Product_Details).all()
    return render_template('category.html',
                           categories=category,
                           products=productDetails)


@app.route('/products/<int:product_id>', methods=["POST", "GET"])
def product_details(product_id):
    """
    this method displays details about the projectors which related to the id
    """
    category = session.query(Category).all()
    product = session.query(Product_Details).get(product_id)
    return render_template('productview.html',
                           product=product,
                           categories=category)


#  Show Category Products
@app.route('/category/<int:category_id>/products/')
def showcategories(category_id):
    categoryOne = session.query(Category).filter_by(id=category_id).one()
    category = session.query(Category).all()
    products = session.query(Product_Details).filter_by(
            category_id=category_id).all()
    if len(products) == 0:
        datas = "NoData"
    else:
        datas = "Data"
    print(products)
    owner = getUserInfo(categoryOne.admin_id)
    return render_template('publicproducts.html',
                           category_id=category_id,
                           categories=category,
                           products=products,
                           datas=datas)


# Create New Category
@app.route('/category/addCategory', methods=['GET', 'POST'])
@login_required
def addCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               admin_id=login_session['admin_id'])
        session.add(newCategory)
        session.commit()
        flash('new Category is Successfully Created..!')
        return redirect(url_for('showcategory'))
    else:
        return render_template('addcategory.html', categories=category)


# Edit the Category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    editCategory = session.query(Category).filter_by(id=category_id).one()
    category = session.query(Category).filter_by(name=category_id).all()
    # See if the logged in user is the owner of item
    owner = getUserInfo(editCategory.admin_id)
    admin = getUserInfo(login_session['admin_id'])
    # If logged in user != item owner redirect them
    if owner.id != login_session['admin_id']:
        flash("You can't edit this Category."
              "This Category belongs to %s" % owner.id)
        return redirect(url_for('showcategory'))
    # POST Methods
    if request.method == 'POST':
        if request.form['name']:
            editCategory.name = request.form['name']
            session.add(editCategory)
            session.commit()
            flash("Category Is Successfully Edited..!")
            return redirect(mineurl_for('showcategory'))
    else:
        return render_template('editcategory.html',
                               category=editCategory,
                               categories=category)


# Delete the Category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    # See if the logged in user is the owner of item
    owner = getUserInfo(categoryToDelete.admin_id)
    admin = getUserInfo(login_session['admin_id'])
    # If logged in user != item owner redirect them
    if owner.id != login_session['admin_id']:
        flash("You can't delete this Category."
              "This Category belongs to %s" % owner.id)
        return redirect(url_for('showcategory'))
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('Category Is Successfully Deleted.!')
        return redirect(url_for('showcategory'))
    else:
        return render_template('deletecategory.html',
                               category=categoryToDelete,
                               categories=category)


# Add the Items
@app.route('/category/addProduct/', methods=['GET', 'POST'])
@login_required
def addProduct():
    category = session.query(Category).all()
    if request.method == 'POST':
        addProduct = Product_Details(
            brandname=request.form['brandname'],
            material=request.form['material'],
            picture=request.form['picture'],
            color=request.form['color'],
            price=request.form['price'],
            description=request.form['description'],
            adminid=login_session['admin_id'],
            category=session.query(
                Category).filter_by(name=request.form['category']).one()
        )
        session.add(addProduct)
        session.commit()
        flash("Add new %s Item  is Successfully Created" % (addProduct.brandname))
        return redirect(url_for('showcategory'))
    else:
        return render_template('addproduct.html', categories=category)


# Edit the Item
@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def editProduct(product_id):
    editProduct = session.query(Product_Details).filter_by(id=product_id).one()
    category = session.query(Category).all()
    # See if the logged in user is the owner of the item
    owner = getUserInfo(editProduct.adminid)
    admin = getUserInfo(login_session['admin_id'])
    # If logged in owner != item owner redirect them
    if owner.id != login_session['admin_id']:
        flash("You can't edit this item. "
              "This item belongs to %s" % owner.id)
        return redirect(url_for('showcategory'))
    # POST Methods
    if request.method == 'POST':
        if request.form['brandname']:
            editProduct.brandname = request.form['brandname']
        if request.form['material']:
            editProduct.material = request.form['material']
        if request.form['picture']:
            editProduct.picture = request.form['picture']
        if request.form['price']:
            editProduct.price = request.form['price']
        if request.form['description']:
            editProduct.description = request.form['description']
            category = session.query(Category).filter_by(
                name=request.form['category']).one()
            editProduct.category = category
        session.commit()
        flash("Item has been edited")
        return redirect(url_for('showcategory',
                                category_id=editProduct.category.id))
    else:
        return render_template('editproduct.html',
                               categories=category,
                               product=editProduct)


# Delete  the product
@app.route('/category/<int:category_id>/<int:product_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteProduct(category_id, product_id):
    productToDelete = session.query(Product_Details).filter_by(id=product_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    category = session.query(Category).all()
    # See if the logged in user is the owner of the item
    owner = getUserInfo(productToDelete.adminid)
    admin = getUserInfo(login_session['admin_id'])
    # If logged in user != item owner redirect them
    if owner.id != login_session['admin_id']:
        flash("You can't delete this item. "
              "This item belongs to %s" % owner.id)
        return redirect(url_for('showcategory'))
    if request.method == 'POST':
        session.delete(productToDelete)
        session.commit()
        flash("Products has been deleted")
        return redirect(url_for('showcategories',
                                category_id=category_id))
    else:
        return render_template('deleteproduct.html',
                               product=productToDelete,
                               categories=category)

# JSON Endpoints


@app.route('/category/JSON')
def allProductsJSON():
    category = session.query(Category).all()
    category_dict = [a.serialize for a in category]
    for a in range(len(category_dict)):
        products= [j.serialize for j in session.query(
           Product_Details).filter_by(category_id=category_dict[a]["id"]).all()]
        if products:
            category_dict[a]["Product"] = products
    return jsonify(Category=category_dict)


@app.route('/category/category/JSON')
def categoryJSON():
    category = session.query(Category).all()
    return jsonify(category=[a.serialize for a in category])


@app.route('/category/products/JSON')
def productsJSON():
    products = session.query(Product_Details).all()
    return jsonify(products=[j.serialize for j in products])


@app.route('/category/<int:category_id>/products/JSON')
def categoryProductsJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    products = session.query(Product_Details).filter_by(category=category).all()
    return jsonify(products=[j.serialize for j in products])


@app.route('/category/<int:category_id>/<int:product_id>/JSON')
def ProductJSON(category_id, product_id):
    category = session.query(Category).filter_by(id=category_id).one()
    product = session.query(Product_Details).filter_by(
           id=product_id, category=category).one()
    return jsonify(product=[product.serialize])


# !Important! Always block should be last ! Important!
if __name__ == '__main__':
    app.secret_key = 'APP_SECRET_KEY'
    app.debug = True
    app.run(host='', port=5000)
