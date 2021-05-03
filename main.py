import requests
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
RATE = 1
SHARE_RATE = 0.5


@app.route("/")
def home():
    if USER:
        if IS_DRIVER:
            return redirect(url_for("driver_home"))
        return redirect(url_for("customer_home"))

    return render_template("home.html")


@app.route("/signout")
def signout():
    global USER, IS_DRIVER, RIDE
    USER = IS_DRIVER = RIDE = None
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
    return render_template("customerViews/editCustomerAccount.html", customer=USER)


@app.route("/edit/driver")
def edit_driver():
    if not USER:
        return redirect(url_for("home"))
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


@app.route("/searching_ride")
def searching_ride():
    if not USER:
        return redirect(url_for("home"))
    return render_template("/customerViews/searchingForDriver.html")


@app.route("/book_ride", methods=["POST"])
def book_ride():
    global USER, RIDE

    pickup = request.form.get("pickup")
    destination = request.form.get("destination")
    total_passengers = request.form.get("total_passengers")
    share = request.form.get("is_share")

    distance = calculate_distance(pickup, destination)

    if share and share == "yes":
        share = True
    else:
        share = False

    if share:
        cost = calculate_cost(int(total_passengers), distance, SHARE_RATE)
    else:
        cost = calculate_cost(int(total_passengers), distance, RATE)

    rides = db.collection("Ride")

    ride = {'customer': USER['email'], 'driver': None, 'status': 1,
            'total_passengers': total_passengers, 'pickup': pickup,
            'destination': destination, 'share': share, 'cost': cost,
            'distance': distance}

    doc = rides.add(ride)
    RIDE = ride
    RIDE['id'] = doc[1].id

    return redirect(url_for("searching_ride"))


@app.route("/update_account/customer", methods=["POST"])
def update_customer():
    global USER

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

    if not password or not password.strip():
        password = USER['customer']['password']

    if not fname or not fname.strip():
        fname = USER.customer.fname
        password = USER['customer']['password']

    if not lname or not lname.strip():
        lname = USER['customer']['lname']

    if not street or not street.strip():
        street = USER['customer']['street']

    if not city or not city.strip():
        city = USER['customer']['city']

    if not state or not state.strip():
        state = USER['customer']['state']

    if not zip_code or not zip_code.strip():
        zip_code = USER['customer']['zip_code']

    if not credit_card_number or not credit_card_number.strip():
        credit_card_number = USER['customer']['credit_card_number']

    if not expired_month or not expired_month.strip():
        expired_month = USER['customer']['expired_month']

    if not expired_year or not expired_year.strip():
        expired_year = USER['customer']['expired_year']

    if not cvv or not cvv.strip():
        cvv = USER['customer']['cvv']

    customers = db.collection("Customer")

    customer = {'password': password, 'fname': fname, 'lname': lname,
                'street': street, 'city': city, 'state': state,
                'zip_code': zip_code,
                'credit_card_number': credit_card_number,
                'expired_month': int(expired_month),
                'expired_year': int(expired_year), 'cvv': cvv,
                'c_total_rating': USER['customer']['c_total_rating'],
                'c_total_rides': USER['customer']['c_total_rides']}

    customers.document(email).update(customer)

    USER = {'email': email, 'customer': customer}

    return redirect(url_for("edit_customer"))


@app.route("/update_account/driver", methods=["POST"])
def update_driver():
    global USER

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

    license_plate = request.form.get("license_plate")
    car_manufacturer = request.form.get("license_plate")
    total_seats = request.form.get("total_seats")
    car_description = request.form.get("car_description")

    if not password or not password.strip():
        password = USER['customer']['password']

    if not fname or not fname.strip():
        fname = USER.customer.fname
        password = USER['customer']['password']

    if not lname or not lname.strip():
        lname = USER['customer']['lname']

    if not street or not street.strip():
        street = USER['customer']['street']

    if not city or not city.strip():
        city = USER['customer']['city']

    if not state or not state.strip():
        state = USER['customer']['state']

    if not zip_code or not zip_code.strip():
        zip_code = USER['customer']['zip_code']

    if not credit_card_number or not credit_card_number.strip():
        credit_card_number = USER['customer']['credit_card_number']

    if not expired_month or not expired_month.strip():
        expired_month = USER['customer']['expired_month']

    if not expired_year or not expired_year.strip():
        expired_year = USER['customer']['expired_year']

    if not cvv or not cvv.strip():
        cvv = USER['customer']['cvv']

    if not license_plate or not license_plate.strip():
        license_plate = USER['driver']['license_plate']

    if not car_manufacturer or not car_manufacturer.strip():
        car_manufacturer = USER['driver']['car_manufacturer']

    if not total_seats or not total_seats.strip():
        total_seats = USER['driver']['total_seats']

    if not car_description or not car_description.strip():
        car_description = USER['driver']['car_description']

    customers = db.collection("Customer")
    drivers = db.collection("Driver")

    customer = {'password': password, 'fname': fname, 'lname': lname,
                'street': street, 'city': city, 'state': state,
                'zip_code': zip_code,
                'credit_card_number': credit_card_number,
                'expired_month': int(expired_month),
                'expired_year': int(expired_year), 'cvv': cvv,
                'c_total_rating': USER['customer']['c_total_rating'],
                'c_total_rides': USER['customer']['c_total_rides']}

    driver = {'license_plate': license_plate,
              'available': USER['driver']['available'],
              'car_manufacturer': car_manufacturer,
              'total_seats': int(total_seats),
              'car_description': car_description,
              'd_total_rating': USER['driver']['d_total_rating'],
              'd_total_rides': USER['driver']}

    customers.document(email).update(customer)
    drivers.document(email).update(driver)

    USER = {'email': email, 'customer': customer, 'driver': driver}

    return redirect(url_for("edit_driver"))


def calculate_distance(start, end):
    base_url = "https://maps.googleapis.com/maps/api/directions/json?origin="
    api_key = "&key=AIzaSyBMoGOvmm_iE2suY-AnGKx8AmVqO6vz7gg"

    response = requests.get(base_url + start + "&destination="
                            + end + api_key)

    if response.status_code == 200:
        data = response.json()
        text = data["routes"][0]["legs"][0]["distance"]["text"]
        return float(text.split(" ")[0])

    return None


def calculate_cost(total_passengers, distance, rate):
    return total_passengers * distance * rate


if __name__ == "__main__":
    app.run(debug=True)
