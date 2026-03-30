#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program to handle the communication between the transmitter's GUI and the transmitter's
 firmware by using a simple HTTP API server during the optical communications test.
"""
import json
import os

from flask import Flask, request
from requests import post as post_request
from server_data import ServerData

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
SERVER_HOST = os.getenv("TRANSMITTER_SERVER_HOST")
SERVER_PORT = int(os.getenv("TRANSMITTER_SERVER_PORT", "5000"))

if SERVER_HOST is None:
    raise ValueError("TRANSMITTER_SERVER_HOST is not set")

# Initialize the Flask app
app = Flask(__name__)

# Variable to control the state of the communication
SERVER_DATA = ServerData()

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

MESSAGES = []
FREQUENCIES = []


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
        # post_request("http://receiver-server:5001/send_data",
        #   headers={"Content-Type": "application/json"},
        #  json=data)
        SERVER_DATA.buffer.insert(data)
        SERVER_DATA.start()
        # post_request("http://receiver-server:5001/receive_binary",
        #             data=b"TEIDESAT" + byte_json.encode() + b"TASEDIET", headers={"Content-Type": "application/octet-stream"})
    return {}


@app.route("/get_message_data", methods=["GET"])
def get_message():
    """
    Function to send the message to the transmitter ESP32.

    Note: This function obtains the data from a global variable.
    # ToDo: Analyze if there is a better way to handle the received data.
    """

    if request.method == "GET":
        if SERVER_DATA.buffer.end_of_experiment:
            SERVER_DATA.change_to_next_experiment()
            return ""
        message = SERVER_DATA.buffer.get_message()
        if message:
            return message
        else:
            SERVER_DATA.stop_communication()

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
        frequency = SERVER_DATA.buffer.get_frequency()
        if frequency:
            print("Frequency: ", frequency)
            return str(frequency)
        else:
            SERVER_DATA.stop_communication()

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


@app.route("/current_status", methods=["GET"])
def get_current_progress():
    """
    Function to retrieve the current progress sending the experiments
    """
    # Get information about the current elements in the buffer:
    # - ID
    # - Remaining Messages in this experiment
    # - Remaining Experiments
    return SERVER_DATA.get_status()

@app.route("/next_experiment", methods=["GET"])
def change_to_next_experiment():
    """
    Changes to the next experiment of the server
    """
    # Modify Buffer to the next experiment
    # Change State of the server to "Change"
    return SERVER_DATA.change_to_next_experiment()

@app.route("/stop_communication", methods=["GET"])
def stop_communication():
    """
    Stops the communication with the server
    """
    # Clear Buffer
    # Change State of the server to "Idle"
    return SERVER_DATA.stop_communication()

@app.route("/firmware_state")
def retrieve_firmware_state():
    """
    Retrieve the firmware state of the server. Either "Idle" or "Sending"
    """
    # This action should change the state of the server
    return SERVER_DATA.return_firmware_state()

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE)
