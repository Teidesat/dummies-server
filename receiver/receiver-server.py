#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program to handle the communication between the receiver's GUI and the receiver's
 firmware by using a simple HTTP API server during the optical communications test.
"""

from flask import Flask, request, jsonify


# Set the debug mode to True to print logs in the console
DEBUG_MODE = True

# Initialize the Flask app
app = Flask(__name__)

# Initialize the global variables with default values
experiment_id = "CO_Dd-Aa-Ii-Ff-Ll-Mm"
message = ""
settings = {
    "dummy_distance": 0,
    "transmitter_angle": 0,
    "led_intensity": 0,
    "blinking_frequency": 0,
    "messages_batch": 0,
}

# Buffer with the formed experiments. Each element is a tuple with the experiment ID and array of id and message
EXP_BUFFER = [
    ("CO_D100-A45-I3-F60-L1-Mm", [
        ["1", "hello"],
        ["2", "teidesat"],
        ["3", "cubesat"],
        ["4", "hyperspace"]
    ])
]

@app.route("/")
def hello_world():
    return "<p>Hello world from the receiver server!</p>"


@app.route("/send_data", methods=["POST"])
def receive_data():
    """
    Receives the data from the firmware and processes it to form a message/experiment. Adds it to the buffer for the experiments

    TODO: Implement using the firmware.
    """
    EXP_BUFFER.append(("CO_D100-A45-I3-F60-L1-Mm", [
        ["1", "hello"],
        ["2", "teidesat"],
        ["3", "cubesat"],
        ["4", "hyperspace"]
    ]))

@app.route("/experiment", methods=["GET"])
def get_experiment():
    """
    Returns an experiment, removing it from the experiments' buffer.
    """
    exp = EXP_BUFFER[0]
    #EXP_BUFFER = EXP_BUFFER[1:]
    data = {
        "id": exp[0],
        "messages": exp[1]
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=DEBUG_MODE)
