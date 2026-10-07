from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "application": "ACEest Fitness & Gym",
        "status": "running"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/calculate-calories", methods=["POST"])
def calculate_calories():
    data = request.get_json()

    weight = float(data.get("weight", 0))
    factor = float(data.get("factor", 0))

    calories = weight * factor

    return jsonify({
        "weight": weight,
        "factor": factor,
        "calories": calories
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
