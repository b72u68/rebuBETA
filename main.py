from flask import Flask, render_template

app = Flask(__name__)


class Driver:
    def __init__(self, username, password, name, rating, car_description):
        self.username = username
        self.password = password
        self.name = name
        self.rating = rating
        self.car_description = car_description


drivers = [
        Driver("driver1", "driver1", "Driver 1", 4.6, "Porsche"),
        Driver("driver2", "driver2", "Driver 2", 5.0, "Ferrari"),
        Driver("driver3", "driver3", "Driver 3", 3.9, "Limousine"),
        Driver("driver4", "driver4", "Driver 4", 4.2, "Toyota")
        ]


@app.route("/customer/home")
def home():
    return render_template("home.html", drivers=drivers)


if __name__ == "__main__":
    app.run(debug=True)

