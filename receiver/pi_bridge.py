#!/usr/bin/env python3
"""Bridge receiver frames from a local serial link to the receiver server."""

from __future__ import annotations

import argparse
import struct
import sys
from typing import Optional

import requests
import serial


FRAME_MAGIC = b"DUMM"
FRAME_HEADER_SIZE = len(FRAME_MAGIC) + 2
FRAME_FOOTER_SIZE = 2


def calculate_checksum(payload: bytes) -> int:
    checksum = 0
    for index in range(0, len(payload), 2):
        checksum ^= int.from_bytes(payload[index : index + 2], "little")
    return checksum & 0xFFFF


def parse_frame(buffer: bytearray) -> Optional[bytes]:
    magic_index = buffer.find(FRAME_MAGIC)
    if magic_index < 0:
        buffer.clear()
        return None

    if magic_index > 0:
        del buffer[:magic_index]

    if len(buffer) < FRAME_HEADER_SIZE:
        return None

    payload_size = struct.unpack_from("<H", buffer, len(FRAME_MAGIC))[0]
    total_size = FRAME_HEADER_SIZE + payload_size + FRAME_FOOTER_SIZE
    if len(buffer) < total_size:
        return None

    payload = bytes(buffer[FRAME_HEADER_SIZE : FRAME_HEADER_SIZE + payload_size])
    expected_checksum = struct.unpack_from(
        "<H", buffer, FRAME_HEADER_SIZE + payload_size
    )[0]
    del buffer[:total_size]

    if calculate_checksum(payload) != expected_checksum:
        print("Checksum mismatch, dropping frame", file=sys.stderr)
        return None

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Forward receiver frames from serial to the local Flask server."
    )
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate")
    parser.add_argument(
        "--server",
        default="http://127.0.0.1:5001/receive_binary",
        help="Receiver server endpoint",
    )
    args = parser.parse_args()

    buffer = bytearray()
    print(f"Opening serial port {args.port} at {args.baud} baud")
    with serial.Serial(args.port, args.baud, timeout=1) as serial_port:
        while True:
            chunk = serial_port.read(4096)
            if not chunk:
                continue

            buffer.extend(chunk)
            while True:
                payload = parse_frame(buffer)
                if payload is None:
                    break

                response = requests.post(
                    args.server,
                    data=payload,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=10,
                )
                response.raise_for_status()
                print(f"Forwarded {len(payload)} bytes to receiver server")


if __name__ == "__main__":
    raise SystemExit(main())