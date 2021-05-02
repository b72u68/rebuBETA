from flask import Flask, render_template, request, url_for, redirect
from firebase_admin import credentials, firestore, initialize_app

# Initialize Flask app
app = Flask(__name__)

# Initialize Firesotre DB
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()

USER = None
IS_DRIVER = None
RIDE = None


@app.route("/")
def home():
    if USER:
        if IS_DRIVER:
            return redirect(url_for("driver_home"))
        return redirect(url_for("customer_home"))

    return render_template("home.html")


@app.route("/signout")
def signout():
    global USER, IS_DRIVER
    USER = IS_DRIVER = None
    return redirect(url_for("home"))


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/driver_signup")
def driver_signup():
    if not USER:
        return redirect(url_for("home"))
    return render_template("driverSignup.html")


@app.route("/customer")
def customer_home():
    if not USER:
        return redirect(url_for("home"))
    elif IS_DRIVER:
        return redirect(url_for("dHome.html"))
    return render_template("customerViews/cHome.html")


@app.route("/driver")
def driver_home():
    if not USER:
        return redirect(url_for("home"))
    elif IS_DRIVER:
        return render_template("driverViews/dHome.html")
    return redirect(url_for("home"))


@app.route("/edit/customer")
def edit_customer():
    if not USER:
        return redirect(url_for("home"))
    print(USER['customer']['street'])
    return render_template("customerViews/editCustomerAccount.html", customer=USER)


@app.route("/edit/driver")
def edit_driver():
    print(USER)
    if not USER:
        return redirect(url_for("home"))
    print(USER['customer']['street'])
    return render_template("driverViews/editDriverAccount.html", driver=USER)


@app.route("/authorize_login", methods=["POST"])
def authorize_login():
    global USER, IS_DRIVER

    email = request.form.get('email')
    password = request.form.get('password')
    IS_DRIVER = 'is_driver' in request.form

    print(email, password, IS_DRIVER)

    if not email or not password:
        return redirect(url_for("home"))

    customers = db.collection('Customer')
    customer = customers.document(email).get().to_dict()

    if customer and customer['password'] == password:
        if IS_DRIVER:
            drivers = db.collection('Driver')
            driver = drivers.document(email).get().to_dict()

            if driver:
                USER = {'email': email, 'customer': customer, 'driver': driver}
                return redirect(url_for("driver_home"))

        else:
            USER = {'email': email, 'customer': customer}
            return redirect(url_for("customer_home"))

    return redirect(url_for("home"))


@app.route("/authorize_signup", methods=["POST"])
def authorize_signup():
    global USER, IS_DRIVER

    email = request.form.get("email")
    password = request.form.get("password")
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    street = request.form.get("street")
    city = request.form.get("city")
    state = request.form.get("state")
    zip_code = request.form.get("zip_code")
    credit_card_number = request.form.get("credit_card_number")
    expired_month = request.form.get("expired_month")
    expired_year = request.form.get("expired_year")
    cvv = request.form.get("cvv")

    if not (email and password and fname and lname and street and city and
            state and zip_code and credit_card_number and expired_month and
            expired_year and cvv):
        return redirect(url_for("signup"))
    else:
        customers = db.collection("Customer")

        customer = {'password': password, 'fname': fname, 'lname': lname,
                    'street': street, 'city': city, 'state': state,
                    'zip_code': zip_code,
                    'credit_card_number': credit_card_number,
                    'expired_month': int(expired_month),
                    'expired_year': int(expired_year), 'cvv': cvv,
                    'c_total_rating': 0, 'c_total_rides': 0}

        if customers.document(email).get().to_dict():
            return redirect(url_for("signup"))

        customers.document(email).set(customer)
        USER = {'email': email, 'customer': customer}
        IS_DRIVER = False

        if request.form.get("is_driver") and request.form.get("is_driver") == "yes":
            return redirect(url_for("driver_signup"))

        return redirect(url_for("home"))


@app.route("/authorize_driver", methods=["POST"])
def authorize_driver():
    global USER, IS_DRIVER
    license_plate = request.form.get("license_plate")
    car_manufacturer = request.form.get("license_plate")
    total_seats = request.form.get("total_seats")
    car_description = request.form.get("car_description")

    if not (license_plate and car_manufacturer and
            total_seats and car_description):
        return redirect(url_for("driver_signup"))

    drivers = db.collection("Driver")

    driver = {'license_plate': license_plate, 'available': True,
              'car_manufacturer': car_manufacturer,
              'total_seats': int(total_seats),
              'car_description': car_description, 'd_total_rating': 0,
              'd_total_rides': 0}

    drivers.document(USER['email']).set(driver)

    USER['driver'] = driver
    IS_DRIVER = True

    return redirect(url_for("home"))


@app.route("/switch_to_customer")
def switch_to_customer():
    global USER, IS_DRIVER

    if USER:
        IS_DRIVER = False
        USER = {'email': USER['email'], 'customer': USER['customer']}

    return redirect(url_for("home"))


@app.route("/switch_to_driver")
def switch_to_driver():
    global USER, IS_DRIVER

    if USER:
        drivers = db.collection('Driver')
        driver = drivers.document(USER['email']).get().to_dict()

        if driver:
            USER = {'email': USER['email'], 'customer': USER['customer'],
                    'driver': driver}
            IS_DRIVER = True

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
