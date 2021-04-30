import random
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

USER = None
IS_DRIVER = None
RIDE_ID = None


class Driver:
    def __init__(self,
                 email,
                 password,
                 fname,
                 lname,
                 car_description,
                 active=False,
                 rating=None):

        self.email = email
        self.password = password
        self.fname = fname
        self.lname = lname
        self.car_description = car_description
        self.active = active
        self.rating = rating


class Customer:
    def __init__(self,
                 email,
                 password,
                 fname,
                 lname,
                 rating=None):

        self.email = email
        self.password = password
        self.fname = fname
        self.lname = lname
        self.rating = rating


class Ride:
    def __init__(self,
                 customer,
                 driver,
                 pickup,
                 destination,
                 number_of_passengers,
                 status):

        self.id = random.randint(0, 1000000)
        self.customer = customer
        self.driver = driver
        self.pickup = pickup
        self.destination = destination
        self.number_of_passengers = number_of_passengers
        self.status = status


drivers = [
        Driver("driver1", "pwd1", "Driver", "1", "Porsche", False, 4.6),
        Driver("driver2", "pwd2", "Driver", "2", "Lambogini", True, 3),
        Driver("driver3", "pwd3", "Driver", "3", "Toyota", True, 5.0),
        Driver("driver4", "pwd4", "Driver", "4", "Ferrari", True, 4.2),
        ]

customers = [
        Customer("customer1", "pwd1", "Customer", "1", 4.6),
        Customer("customer2", "pwd2", "Customer", "2", 3.6),
        Customer("customer3", "pwd3", "Customer", "3", 5.0),
        Customer("customer4", "pwd4", "Customer", "4", 4.7),
        Customer("driver1", "pwd1", "Driver", "1", 5.0)
        ]

rides = []


@app.route("/")
def home():
    if USER:
        if IS_DRIVER:
            return render_template("dHome.html")
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


@app.route("/customer")
def customer_home():
    if not USER:
        return redirect(url_for("home"))
    elif IS_DRIVER:
        return redirect(url_for("dHome.html"))
    return render_template("cHome.html")


@app.route("/driver")
def driver_home():
    if not USER:
        return redirect(url_for("home"))
    elif IS_DRIVER:
        return render_template("dHome.html")
    return redirect(url_for("home"))


@app.route("/edit/customer")
def edit_customer():
    if not USER:
        return redirect(url_for("home"))
    return render_template("editCustomerAccount.html", customer=USER)


@app.route("/edit/driver")
def edit_driver():
    if not USER:
        return redirect(url_for("home"))
    return render_template("editDriverAccount.html", driver=USER)


@app.route("/api/authorize_login", methods=["POST"])
def authorize_login():
    global USER, IS_DRIVER

    print(request.form)
    email = request.form.get('email')
    password = request.form.get('password')
    IS_DRIVER = 'is-driver' in request.form

    print(email, password, IS_DRIVER)

    if not email or not password:
        return redirect(url_for("home"))

    if IS_DRIVER:
        for driver in drivers:
            if driver.email == email and driver.password == password:
                USER = driver
                break
        return redirect(url_for("driver_home"))

    else:
        for customer in customers:
            if customer.email == email and customer.password == password:
                USER = customer
                break
        return redirect(url_for("customer_home"))


@app.route("/api/switch_to_customer")
def swith_to_customer():
    global USER, IS_DRIVER

    IS_DRIVER = False

    for customer in customers:
        if customer.email == USER.email:
            USER = customer
            break

    return redirect(url_for("home"))


@app.route("/api/switch_to_driver")
def swith_to_driver():
    global USER, IS_DRIVER

    for driver in drivers:
        if driver.email == USER.email:
            USER = driver
            IS_DRIVER = True
            break

    return redirect(url_for("home"))


@app.route("/api/search_location")
def search_location():
    result = ""
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/xml?query="
    api_key = "&key=AIzaSyBMoGOvmm_iE2suY-AnGKx8AmVqO6vz7gg"
    location = request.args.get("loc")

    if not location:
        return "No location found"

    response = requests.get(base_url + location.replace(" ", "+") + api_key)

    if response:
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, "lxml")
            result = soup.formatted_address.text
    else:
        return "No location found"

    return result


if __name__ == "__main__":
    app.run(debug=True)
