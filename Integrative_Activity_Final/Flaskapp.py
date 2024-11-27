from flask import Flask, jsonify
from Final import CityModel

city_model = CityModel(cars=17)

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"Message": "Hello from the Team 7"})

@app.route("/positions", methods=["GET", "POST"])
def positions():
    city_model.step()

    car_positions = []
    for car in city_model.cars_list:
        car_positions.append({"x": car.pos[0], "y": car.pos[1]})
    
    return jsonify(car_positions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)