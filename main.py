import datetime
import requests
from math import sin, cos, sqrt, atan2, radians
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
    if IS_DRIVER:
        return redirect(url_for("dHome.html"))
    return render_template("customerViews/cHome.html")


@app.route("/driver")
def driver_home():
    if not USER:
        return redirect(url_for("home"))
    elif IS_DRIVER:
        return render_template("driverViews/dHome.html")
    return redirect(url_for("home"))


@app.route("/account/customer")
def edit_customer():
    if not USER:
        return redirect(url_for("home"))
    return render_template("customerViews/editCustomerAccount.html", customer=USER)


@app.route("/account/driver")
def edit_driver():
    if not USER:
        return redirect(url_for("home"))
    return render_template("driverViews/editDriverAccount.html", driver=USER)


@app.route("/view/favorite_places")
def favorite_places():
    return render_template("customerViews/favoritePlaces.html")


@app.route("/view/transactions")
def view_transactions():
    if not USER:
        return redirect(url_for("home"))

    customers = db.collection("Customer")

    if IS_DRIVER:
        transactions = db.collection("Transaction").where(u'receiver_email', u'==', USER['email']).get()

        for i in range(len(transactions)):
            id = transactions[i].id
            ride = db.collection("Ride").document(id).get().to_dict()

            transaction = transactions[i].to_dict()

            sender_card = "X" + transaction['sender'][11:15]
            receiver_card = "X" + transaction['receiver'][11:15]

            sender_data = customers.document(transaction['sender_email']).get().to_dict()
            sender = {'fname': sender_data['fname'],
                      'lname': sender_data['lname'],
                      'card': sender_card}

            receiver_data = customers.document(transaction['receiver_email']).get().to_dict()
            receiver = {'fname': receiver_data['fname'],
                        'lname': receiver_data['lname'],
                        'card': receiver_card}

            transaction['ride'] = ride
            transaction['sender'] = sender
            transaction['receiver'] = receiver

            transactions[i] = transaction

        return render_template("driverViews/viewTransactions.html", transactions=transactions, is_driver=IS_DRIVER)

    else:
        transactions = db.collection("Transaction").where(u'sender_email', u'==', USER['email']).get()

        for i in range(len(transactions)):
            id = transactions[i].id
            ride = db.collection("Ride").document(id).get().to_dict()

            transaction = transactions[i].to_dict()

            sender_card = "X" + transaction['sender'][11:15]
            receiver_card = "X" + transaction['receiver'][11:15]

            sender_data = customers.document(transaction['sender_email']).get().to_dict()
            sender = {'fname': sender_data['fname'],
                      'lname': sender_data['lname'],
                      'card': sender_card}

            receiver_data = customers.document(transaction['receiver_email']).get().to_dict()
            receiver = {'fname': receiver_data['fname'],
                        'lname': receiver_data['lname'],
                        'card': receiver_card}

            transaction['ride'] = ride
            transaction['sender'] = sender
            transaction['receiver'] = receiver

            transactions[i] = transaction

        return render_template("customerViews/viewTransactions.html", transactions=transactions, is_driver=IS_DRIVER)


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

    driver = {'license_plate': license_plate,
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


@app.route("/ride/book", methods=["POST"])
def book_ride():
    global USER, RIDE

    pickup = request.form.get("pickup")
    destination = request.form.get("destination")
    total_passengers = request.form.get("total_passengers")

    distance = calculate_distance(pickup, destination)

    cost = calculate_cost(int(total_passengers), distance, RATE)

    rides = db.collection("Ride")

    ride = {'customer': USER['email'], 'driver': None, 'status': 1,
            'total_passengers': int(total_passengers), 'pickup': pickup,
            'destination': destination, 'cost': cost, 'distance': distance}

    doc = rides.add(ride)
    ride['id'] = doc[1].id
    RIDE = ride

    return redirect(url_for("searching_driver"))


@app.route("/account/customer/update", methods=["POST"])
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


@app.route("/account/driver/update", methods=["POST"])
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


def calculate_geodistance(start, end):
    lat1, lng1 = start
    lat2, lng2 = end

    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    R = 3958.8

    dlng = lng2 - lng2
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(R * c, 2)


def calculate_distance(start, end):
    base_url = "https://maps.googleapis.com/maps/api/directions/json?origin="
    api_key = "&key=AIzaSyBMoGOvmm_iE2suY-AnGKx8AmVqO6vz7gg"

    response = requests.get(base_url + start + "&destination="
                            + end + api_key)

    if response.status_code == 200:
        data = response.json()

        if data["routes"]:
            distance = data["routes"][0]["legs"][0]["distance"]["text"]
            return round(float(distance.split(" ")[0]), 2)
        else:
            base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="
            response_start = requests.get(base_url + start + api_key)
            response_end = requests.get(base_url + end + api_key)

            if response_start.status_code == 200 and response_end.status_code == 200:
                data1 = response_start.json()
                data2 = response_end.json()

                lat1 = data1['results'][0]['geometry']['location']['lat']
                lng1 = data1['results'][0]['geometry']['location']['lng']
                lat2 = data2['results'][0]['geometry']['location']['lat']
                lng2 = data2['results'][0]['geometry']['location']['lng']

                return round(calculate_geodistance([lat1, lng1], [lat2, lng2]), 2)

    return 999999


def calculate_cost(total_passengers, distance, rate):
    return round(total_passengers * distance * rate, 2)


def get_sorted_rides(origin):
    rides = db.collection("Ride").get()
    customers = db.collection("Customer")

    for i in range(len(rides)):
        id = rides[i].id
        rides[i] = rides[i].to_dict()
        rides[i]['id'] = id

        customer_email = rides[i]['customer']
        customer = customers.document(customer_email).get().to_dict()
        rides[i]['customer'] = {'fname': customer['fname'],
                                'lname': customer['lname']}

        distance = calculate_distance(origin, rides[i]['pickup'].replace(", ", "+").replace(" ", "+"))
        rides[i]['distance_from_customer'] = distance

    rides = sorted(rides, key=lambda ride: ride['distance_from_customer'])

    return rides


@app.route("/api/get_nearby_rides", methods=["POST"])
def nearby_rides():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    origin = lat + "," + lng

    rides = get_sorted_rides(origin)

    available_rides = [ride for ride in rides if ride['status'] == 1]

    return render_template("driverViews/rides.html", rides=available_rides)


def get_ride(id, lat=None, lng=None):
    customers = db.collection("Customer")
    drivers = db.collection("Driver")
    rides = db.collection("Ride")
    ride = rides.document(id).get().to_dict()
    ride['id'] = id

    customer_email = ride['customer']
    customer = customers.document(customer_email).get().to_dict()

    driver_email = ride['driver']
    driver = drivers.document(driver_email).get().to_dict()

    if customer['c_total_rides'] == 0:
        c_rating = 5
    else:
        c_rating = round(customer['c_total_rating'] / customer['c_total_rides'], 1)

    ride['customer_info'] = {'fname': customer['fname'],
                             'lname': customer['lname'],
                             'rating': c_rating}
    if driver:
        driver_info = customers.document(driver_email).get().to_dict()

        if driver['d_total_rides'] == 0:
            d_rating = 5
        else:
            d_rating = round(driver['d_total_rating'] / driver['d_total_rides'], 1)

        ride['driver_info'] = driver
        ride['driver_info']['fname'] = driver_info['fname']
        ride['driver_info']['lname'] = driver_info['lname']
        ride['driver_info']['rating'] = d_rating

    if lat and lng:
        origin = lat + "," + lng
        distance = calculate_distance(origin, ride['pickup'].replace(", ", "+").replace(" ", "+"))
        ride['distance_from_customer'] = distance

    return ride


@app.route("/api/get_ride_info", methods=["GET", "POST"])
def get_ride_info():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    id = request.args.get("id")

    ride = get_ride(id, lat, lng)

    return render_template("driverViews/rideInformation.html", ride=ride)


@app.route("/ride/pickup/view")
def pickup():
    return render_template("driverViews/confirmPickup.html", ride=RIDE)


@app.route("/ride/accept", methods=["POST"])
def accept_ride():
    global RIDE
    rides = db.collection("Ride")

    lat = request.args.get("lat")
    lng = request.args.get("lng")
    id = request.args.get("id")

    ride = get_ride(id, lat, lng)
    ride['driver'] = USER['email']
    ride['status'] = 2

    rides.document(id).update({'driver': USER['email'], 'status': 2})

    RIDE = ride

    return url_for("pickup")


@app.route("/ride/cancel", methods=["POST"])
def cancel_ride():
    global RIDE
    rides = db.collection("Ride")

    id = request.args.get("id")

    rides.document(id).update({'status': 5})
    RIDE = None

    return url_for("driver_home")


@app.route("/ride/dropoff/view")
def dropoff():
    return render_template("driverViews/confirmDropoff.html", ride=RIDE)


@app.route("/ride/pickup/confirm", methods=["POST"])
def confirm_pickup():
    global RIDE
    rides = db.collection("Ride")

    lat = request.args.get("lat")
    lng = request.args.get("lng")
    id = request.args.get("id")

    ride = get_ride(id, lat, lng)
    ride['driver'] = USER['email']
    ride['status'] = 3

    rides.document(id).update({'status': 3})

    RIDE = ride

    return url_for("dropoff")


@app.route("/ride/dropoff/confirm", methods=["POST"])
def confirm_dropoff():
    global RIDE
    rides = db.collection("Ride")

    lat = request.args.get("lat")
    lng = request.args.get("lng")
    id = request.args.get("id")

    ride = get_ride(id, lat, lng)
    ride['driver'] = USER['email']
    ride['status'] = 3

    rides.document(id).update({'status': 4})

    RIDE = ride

    return url_for("customer_review")


@app.route("/ride/review/customer")
def customer_review():
    return render_template("driverViews/reviewCustomer.html", ride=RIDE)


@app.route("/ride/review/customer/submit", methods=["POST"])
def submit_customer_review():
    global RIDE

    rate = request.form.get("rate")
    feedback = request.form.get("feedback")

    if rate:
        customers = db.collection("Customer")

        customer = customers.document(RIDE['customer']).get()
        total_rate = customer.to_dict()['c_total_rating'] + int(rate)
        total_rides = customer.to_dict()['c_total_rides'] + 1

        customers.document(RIDE['customer']).update({'c_total_rating': total_rate,
                                                     'c_total_rides': total_rides})

    if feedback:
        feedbacks = db.collection("Feedback")
        d_feedback = feedbacks.document(RIDE['id']).get().to_dict()

        if d_feedback:
            feedbacks.document(RIDE['id']).update({'d_feedback': feedback})
        else:
            feedbacks.document(RIDE['id']).set({'d_feedback': feedback})

    RIDE = None

    return redirect(url_for("driver_home"))


@app.route("/ride/waiting")
def waiting_driver():
    print(RIDE)
    return render_template("customerViews/waitingForDriver.html", ride=RIDE)


@app.route("/ride/searching")
def searching_driver():
    if not USER:
        return redirect(url_for("home"))
    return render_template("/customerViews/searchingForDriver.html", ride=RIDE)


@app.route("/ride/in_transit")
def in_transit():
    return render_template("customerViews/inTransit.html", ride=RIDE)


@app.route("/ride/make_payment")
def make_payment():
    transactions = db.collection("Transaction")
    customers = db.collection("Customer")

    id = RIDE['id']
    cost = RIDE['cost']
    current_date = datetime.datetime.now()
    sender_data = customers.document(RIDE['customer']).get().to_dict()
    receiver_data = customers.document(RIDE['driver']).get().to_dict()

    transaction = {'date': current_date, 'cost': cost,
                   'sender': sender_data['credit_card_number'],
                   'sender_email': RIDE['customer'],
                   'receiver': receiver_data['credit_card_number'],
                   'receiver_email': RIDE['driver']}

    transactions.document(id).set(transaction)

    return redirect(url_for("driver_review"))


@app.route("/ride/refresh")
def refresh_ride():
    global RIDE

    ride = get_ride(RIDE['id'])
    RIDE = ride

    if ride['status'] == 1:
        return redirect(url_for("searching_driver"))
    elif ride['status'] == 2:
        return redirect(url_for("waiting_driver"))
    elif ride['status'] == 3:
        return redirect(url_for("in_transit"))
    elif ride['status'] == 4:
        return redirect(url_for("make_payment"))
    else:
        return redirect(url_for("home"))


@app.route("/ride/review/driver")
def driver_review():
    return render_template("customerViews/reviewDriver.html", ride=RIDE)


@app.route("/ride/review/driver/submit", methods=["POST"])
def submit_driver_review():
    global RIDE

    rate = request.form.get("rate")
    feedback = request.form.get("feedback")

    if rate:
        drivers = db.collection("Driver")

        driver = drivers.document(RIDE['driver']).get()
        total_rate = driver.to_dict()['d_total_rating'] + int(rate)
        total_rides = driver.to_dict()['d_total_rides'] + 1

        drivers.document(RIDE['driver']).update({'d_total_rating': total_rate,
                                                 'd_total_rides': total_rides})

    if feedback:
        feedbacks = db.collection("Feedback")
        c_feedback = feedbacks.document(RIDE['id']).get().to_dict()

        if c_feedback:
            feedbacks.document(RIDE['id']).update({'c_feedback': feedback})
        else:
            feedbacks.document(RIDE['id']).set({'c_feedback': feedback})

    RIDE = None

    return redirect(url_for("customer_home"))


@app.route("/test")
def test():
    return render_template("customerViews/reviewDriver.html")


if __name__ == "__main__":
    app.run(debug=True)