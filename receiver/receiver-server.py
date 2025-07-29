#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program to handle the communication between the receiver's GUI and the receiver's
 firmware by using a simple HTTP API server during the optical communications test.
"""
from threading import Timer

from flask import Flask, request, jsonify
from experiment import Experiment
from utils import *

import Levenshtein

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

# Temporary buffer for the binary data
BINARY_TEMP = b""
SEARCHING_FOR_HEAD = True

# Buffer with the formed experiments.
EXP_BUFFER: list[Experiment] = []

# The experiment that is currently forming.
FORMING_EXPERIMENT: Experiment = Experiment(None)

# Timeout to form experiments
TIMEOUT = 3
LAST_EXPERIMENT_TIMER: Timer = Timer(TIMEOUT, lambda x: x)
TIMED_OUT: TimeOutWrapper = TimeOutWrapper(False)

# Variables to tell if we found header or tail to decode the oversampling
FOUND_HEADER = False
OVERSAMPLING = -1
LEFTOVER = None


def process_message(data):
    """
    Function to process the message received from the firmware and add it to the buffer.
    """
    global message
    global FORMING_EXPERIMENT
    global LAST_EXPERIMENT_TIMER
    global TIMED_OUT
    message = data["message"]
    experiment_id = data["experiment_id"]
    stripped_experiment_id = experiment_id[: experiment_id.find("M")]
    print(data)
    if FORMING_EXPERIMENT.id is None:  # First run
        print("First run")
        FORMING_EXPERIMENT = Experiment(stripped_experiment_id)
    elif (
        FORMING_EXPERIMENT.hasMessage(experiment_id)
        or FORMING_EXPERIMENT.id != stripped_experiment_id
        or TIMED_OUT.timeout
    ):
        # 3 cases on which a experiment has fully formed:
        # 1. repeated ID (same experiment back to back),
        # 2. different experiment ID (different experiments)
        # 3. or no more messages (last experiment, last message).
        print(
            "Finished experiment "
            + FORMING_EXPERIMENT.id
            + ", now adding "
            + experiment_id
        )
        print("TIMED_OUT " + str(TIMED_OUT.timeout))
        print(
            "Current and new id are equal? "
            + str(FORMING_EXPERIMENT.id == stripped_experiment_id)
        )
        print(FORMING_EXPERIMENT.messages)
        if not TIMED_OUT.timeout:  # Timeout handler already adds to the buffer
            EXP_BUFFER.append(FORMING_EXPERIMENT)
        TIMED_OUT.timeout = False
        FORMING_EXPERIMENT = Experiment(stripped_experiment_id)
    else:
        print("Same experiment " + experiment_id)

    FORMING_EXPERIMENT.addMessage(experiment_id, message)
    LAST_EXPERIMENT_TIMER.cancel()
    LAST_EXPERIMENT_TIMER = Timer(
        TIMEOUT,
        addExperimentToBuffer,
        (EXP_BUFFER, FORMING_EXPERIMENT, TIMED_OUT),
    )
    LAST_EXPERIMENT_TIMER.start()


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
    process_message(data)
    return "OK", 200


@app.route("/receive_binary", methods=["POST"])
def receive_binary():
    """
    Receives the binary data from the firmware and processes it to form a message/experiment. Adds it to the buffer for the experiments
    """
    header = b"TEIDESAT"
    tail = b"TASEDIET"
    tolerance = 5
    global BINARY_TEMP
    global SEARCHING_FOR_HEAD
    global FOUND_HEADER
    global OVERSAMPLING
    global LEFTOVER

    data = request.get_data(as_text=False)
    if LEFTOVER is not None:
        data = LEFTOVER + data
        LEFTOVER = None
    print("Received data length", type(data))
    data, OVERSAMPLING, FOUND_HEADER, LEFTOVER = denoise_message(
        data,
        header,
        tail,
        OVERSAMPLING,
        FOUND_HEADER,
    )
    print("binary", data.hex())
    print("ascii", data.decode("ascii", errors="replace"))
    BINARY_TEMP = BINARY_TEMP + data
    checksum = calculate_checksum(data)
    if checksum != 0:
        print(f"Found error in checksum {checksum} for package ", data)
    HEADER_IND = None
    TAIL_IND = None
    while HEADER_IND != -1 and TAIL_IND != -1:
        if SEARCHING_FOR_HEAD:
            HEADER_IND = find_byte_sequence(BINARY_TEMP, header, tolerance)
            if HEADER_IND != -1:
                # Discard previous bytes
                BINARY_TEMP = BINARY_TEMP[HEADER_IND + 1 :]
                SEARCHING_FOR_HEAD = False
        if not SEARCHING_FOR_HEAD:
            TAIL_IND = find_byte_sequence(BINARY_TEMP, tail, tolerance)
            if TAIL_IND != -1:
                # Process the binary data into json and send it to the receiver
                process_message(
                    process_binary(BINARY_TEMP[0 : TAIL_IND - len(tail) + 1])
                )
                BINARY_TEMP = BINARY_TEMP[TAIL_IND + 1 :]
                SEARCHING_FOR_HEAD = True
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


@app.route("/buffer_size", methods=["GET"])
def get_buffer_size():
    """
    Returns size of the experiment buffer.
    """
    # print(f"Buffer size: {len(EXP_BUFFER)}")

    return str(len(EXP_BUFFER))


@app.route("/message", methods=["GET"])
def get_message():
    """
    Returns a single message
    """
    if request.method == "GET":
        return message


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=DEBUG_MODE)
