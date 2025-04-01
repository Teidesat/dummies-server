#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program to handle the communication between the receiver's GUI and the receiver's
 firmware by using a simple HTTP API server during the optical communications test.
"""
from threading import Timer

from flask import Flask, request, jsonify
from experiment import Experiment
from utils import addExperimentToBuffer, TimeOutWrapper

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

# Buffer with the formed experiments.
EXP_BUFFER: list[Experiment] = []

# The experiment that is currently forming.
FORMING_EXPERIMENT: Experiment = Experiment(None)

# Timeout to form experiments
TIMEOUT = 3
LAST_EXPERIMENT_TIMER: Timer = Timer(TIMEOUT, lambda x: x)
TIMED_OUT: TimeOutWrapper =  TimeOutWrapper(False)

@app.route("/")
def hello_world():
    return "<p>Hello world from the receiver server!</p>"


@app.route("/send_data", methods=["POST"])
def receive_data():
    """
    Receives the data from the firmware and processes it to form a message/experiment. Adds it to the buffer for the experiments

    TODO: Implement using the firmware.
    """
    data = request.json
    global message
    global FORMING_EXPERIMENT
    global LAST_EXPERIMENT_TIMER
    global TIMED_OUT
    message = data["message"]
    experiment_id = data["experiment_id"]
    stripped_experiment_id = experiment_id[:experiment_id.find("M")]
    print(data)
    if FORMING_EXPERIMENT.id is None: # First run
        print("First run")
        FORMING_EXPERIMENT = Experiment(stripped_experiment_id)
    elif FORMING_EXPERIMENT.hasMessage(experiment_id) or FORMING_EXPERIMENT.id != stripped_experiment_id or TIMED_OUT.timeout:
        # 3 cases on which a experiment has fully formed: 
        # 1. repeated ID (same experiment back to back),
        # 2. different experiment ID (different experiments)
        # 3. or no more messages (last experiment, last message).
        print("Finished experiment " + FORMING_EXPERIMENT.id + ", now adding " + experiment_id)
        print("TIMED_OUT " + str(TIMED_OUT.timeout))
        print("Current and new id are equal? " + str(FORMING_EXPERIMENT.id == stripped_experiment_id))
        print(FORMING_EXPERIMENT.messages)
        if not TIMED_OUT.timeout: # Timeout handler already adds to the buffer
            EXP_BUFFER.append(FORMING_EXPERIMENT)
        TIMED_OUT.timeout = False
        FORMING_EXPERIMENT = Experiment(stripped_experiment_id)
    else:
        print("Same experiment " + experiment_id)

    FORMING_EXPERIMENT.addMessage(experiment_id, message)
    LAST_EXPERIMENT_TIMER.cancel()
    LAST_EXPERIMENT_TIMER = Timer(TIMEOUT, addExperimentToBuffer, (EXP_BUFFER, FORMING_EXPERIMENT, TIMED_OUT))
    LAST_EXPERIMENT_TIMER.start()

    return "OK", 200

@app.route("/experiment", methods=["GET"])
def get_experiment():
    """
    Returns an experiment, removing it from the experiments' buffer.
    """
    global EXP_BUFFER
    if len(EXP_BUFFER) == 0:
        return ""
    exp = EXP_BUFFER[0]
    if len(EXP_BUFFER) > 1:
        EXP_BUFFER = EXP_BUFFER[1:]
    else:
        EXP_BUFFER = []
    data = exp.toDict()
    print(data)
    return jsonify(data)

@app.route("/message", methods=["GET"])
def get_message():
    """
    Returns a single message
    """
    if request.method == "GET":
        return message

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=DEBUG_MODE)
