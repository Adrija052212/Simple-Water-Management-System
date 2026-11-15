
from flask import Flask, jsonify
from flask_cors import CORS
from routes.household import household_bp
from database.db import initialize_database
from routes.consumption import consumption_bp
from routes.analytics import analytics_bp
from routes.prediction import prediction_bp
from routes.optimization import optimization_bp
from routes.recommendation import recommendation_bp


app = Flask(__name__)
CORS(app)

app.register_blueprint(household_bp)
app.register_blueprint(consumption_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(optimization_bp)
app.register_blueprint(recommendation_bp)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Water Consumption Management System API is running!",
        "status": "success"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "application": "Water Consumption Management System"
    })


if __name__ == "__main__":

    # Initialize database before starting the server
    initialize_database()

    app.run(debug=True, port=5000)
