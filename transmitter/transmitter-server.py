#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program to handle the communication between the transmitter's GUI and the transmitter's
 firmware by using a simple HTTP API server during the optical communications test.
"""


from flask import Flask, request


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


@app.route("/")
def hello_world():
    return "<p>Hello world from the transmitter server!</p>"


@app.route("/start_optical_communications", methods=["POST"])
def send_message():
    """
    Function to receive a message from the transmitter GUI to start the optical
    communications.

    Note: This function produces side effects by changing the global variables
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "POST":
        global experiment_id
        global message
        global settings

        data = request.json

        experiment_id = data["experiment_id"]
        message = data["message"]
        settings = data["settings"]

        print(
            f"Received experiment ID '{experiment_id}' "
            + f"with message '{message}' and settings '{settings}'",
            flush=DEBUG_MODE,
        )

    return {}


@app.route("/get_message_data", methods=["GET"])
def get_message():
    """
    Function to send the message to the transmitter ESP32.

    Note: This function obtains the data from a global variable.
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "GET":
        global message

        print(f"Sending message: {message}", flush=DEBUG_MODE)
        return message

    return ""


@app.route("/get_dummy_distance", methods=["GET"])
def get_dummy_distance():
    """
    Function to send the distance between the dummies to the transmitter ESP32.

    Note: This function obtains the data from a global variable.
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "GET":
        global settings
        distance = settings["dummy_distance"]

        print(f"Sending dummy distance value: {distance}", flush=DEBUG_MODE)
        return str(distance)

    return ""


@app.route("/get_transmitter_angle", methods=["GET"])
def get_transmitter_angle():
    """
    Function to send the angle of the transmitter dummy to the transmitter ESP32.

    Note: This function obtains the data from a global variable.
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "GET":
        global settings
        angle = settings["transmitter_angle"]

        print(f"Sending transmitter angle value: {angle}", flush=DEBUG_MODE)
        return str(angle)

    return ""


@app.route("/get_led_intensity", methods=["GET"])
def get_led_intensity():
    """
    Function to send the LEDs intensity to the transmitter ESP32.

    Note: This function obtains the data from a global variable.
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "GET":
        global settings
        intensity = settings["led_intensity"]

        print(f"Sending LEDs intensity value: {intensity}", flush=DEBUG_MODE)
        return str(intensity)

    return ""


@app.route("/get_blinking_frequency", methods=["GET"])
def get_blinking_frequency():
    """
    Function to send the blinking frequency to the transmitter ESP32.

    Note: This function obtains the data from a global variable.
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "GET":
        global settings
        frequency = settings["blinking_frequency"]

        print(f"Sending blinking frequency value: {frequency}", flush=DEBUG_MODE)
        return str(frequency)

    return ""


@app.route("/get_messages_batch", methods=["GET"])
def get_messages_batch():
    """
    Function to send the number of messages to send in a batch to the transmitter ESP32.

    Note: This function obtains the data from a global variable.
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "GET":
        global settings
        batch = settings["messages_batch"]

        print(f"Sending messages batch value: {batch}", flush=DEBUG_MODE)
        return str(batch)

    return ""


@app.route("/get_experiment_id", methods=["GET"])
def get_experiment_id():
    """
    Function to send the experiment ID to the transmitter ESP32.

    Note: This function obtains the data from a global variable.
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "GET":
        global experiment_id

        print(f"Sending experiment ID value: {experiment_id}", flush=DEBUG_MODE)
        return str(experiment_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=DEBUG_MODE)
