#!/usr/bin/env python3
"""
Direct photodiode receiver for Raspberry Pi.
Replaces ESP32 firmware by reading photodiode directly on GPIO.
"""

from __future__ import annotations

import argparse
import struct
import sys
import time
from typing import Optional
from collections import deque
from threading import Thread, Lock

import requests

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO not installed. Install with: pip install RPi.GPIO", file=sys.stderr)
    sys.exit(1)


# Configuration constants
BUFFER_SIZE = 1024
CIRCULAR_BUFFER_SIZE = 4096
PACKAGE_SLOTS = CIRCULAR_BUFFER_SIZE // BUFFER_SIZE

# Default bit period used by the transmitter. Tune with --bit-duration-us if needed.
DEFAULT_BIT_DURATION_US = 1000.0


class PhotodiodeReader:
    """Reads photodiode via GPIO and sends raw binary payloads to the receiver server."""

    def __init__(self, gpio_pin: int, server_url: str, bit_duration_us: float):
        self.gpio_pin = gpio_pin
        self.server_url = server_url
        self.bit_duration_s = max(bit_duration_us, 1.0) / 1_000_000
        
        # Circular buffer for decoded bytes
        self.circular_buffer = deque(maxlen=CIRCULAR_BUFFER_SIZE)
        self.buffer_lock = Lock()
        
        # Ready packages queue
        self.ready_packages = deque(maxlen=PACKAGE_SLOTS)
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        try:
            GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        except Exception as exc:
            if "busy" in str(exc).lower():
                raise RuntimeError(
                    f"GPIO {gpio_pin} is busy. Another process is likely using it. "
                    "Stop previous photodiode_receiver instances and retry."
                ) from exc
            raise
        
        print(f"Photodiode reader initialized on GPIO {gpio_pin}")
        print(f"Server: {server_url}")
        print(f"Bit period: {bit_duration_us} us")

    def read_bit(self) -> int:
        """Read one bit from GPIO."""
        return 1 if GPIO.input(self.gpio_pin) else 0

    def sleep_until(self, target_time: float) -> None:
        """Sleep until a target monotonic timestamp."""
        while True:
            remaining = target_time - time.monotonic()
            if remaining <= 0:
                return
            time.sleep(min(remaining, self.bit_duration_s / 10))

    def read_byte(self, next_bit_time: float) -> tuple[int, float]:
        """Read one byte from the photodiode bitstream and return the next bit time."""
        value = 0
        for i in range(7, -1, -1):
            self.sleep_until(next_bit_time)
            bit = self.read_bit()
            value |= bit << i
            next_bit_time += self.bit_duration_s
        return value, next_bit_time

    def send_package(self, payload: bytes) -> bool:
        """Send raw payload bytes to the receiver server."""
        try:
            response = requests.post(
                self.server_url,
                data=payload,
                headers={"Content-Type": "application/octet-stream"},
                timeout=10,
            )
            response.raise_for_status()
            print(f"Sent {len(payload)} bytes to server")
            return True
        except requests.RequestException as e:
            print(f"Failed to send package: {e}", file=sys.stderr)
            return False

    def reader_thread(self):
        """Thread that reads the photodiode bitstream and fills the byte buffer."""
        byte_count = 0
        next_bit_time = time.monotonic() + (self.bit_duration_s / 2)
        
        try:
            while True:
                value, next_bit_time = self.read_byte(next_bit_time)
                
                with self.buffer_lock:
                    self.circular_buffer.append(value)
                    byte_count += 1
                    
                    # Check if we have a complete package
                    if byte_count % BUFFER_SIZE == 0:
                        # Get the last BUFFER_SIZE bytes as a complete package
                        package_start = max(0, len(self.circular_buffer) - BUFFER_SIZE)
                        package_data = list(self.circular_buffer)[package_start:]
                        
                        if len(package_data) == BUFFER_SIZE:
                            self.ready_packages.append(package_data)
                            print(f"Package ready: {byte_count // BUFFER_SIZE} ({len(self.circular_buffer)} bytes in buffer)")
        except KeyboardInterrupt:
            print("Reader thread interrupted", file=sys.stderr)
        except Exception as e:
            print(f"Error in reader thread: {e}", file=sys.stderr)

    def sender_thread(self):
        """Thread that sends complete packages to server."""
        try:
            while True:
                if self.ready_packages:
                    package_data = None
                    with self.buffer_lock:
                        if self.ready_packages:
                            package_data = self.ready_packages.popleft()

                    if package_data is None:
                        continue
                    
                    payload = bytes(package_data)

                    if not self.send_package(payload):
                        # Put package back to avoid losing data when server is down.
                        with self.buffer_lock:
                            self.ready_packages.appendleft(package_data)
                        time.sleep(1.0)
                else:
                    time.sleep(0.01)  # Avoid busy-waiting
        except KeyboardInterrupt:
            print("Sender thread interrupted", file=sys.stderr)
        except Exception as e:
            print(f"Error in sender thread: {e}", file=sys.stderr)

    def run(self):
        """Start reader and sender threads."""
        reader = Thread(target=self.reader_thread, daemon=True)
        sender = Thread(target=self.sender_thread, daemon=True)
        
        reader.start()
        sender.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            GPIO.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read photodiode directly on Raspberry Pi GPIO and send to receiver server."
    )
    parser.add_argument(
        "--gpio",
        type=int,
        default=17,
        help="GPIO pin number (BCM mode) for photodiode signal",
    )
    parser.add_argument(
        "--bit-duration-us",
        type=float,
        default=DEFAULT_BIT_DURATION_US,
        help="Bit period in microseconds used to sample the photodiode signal",
    )
    parser.add_argument(
        "--server",
        default="http://127.0.0.1:5001/receive_binary",
        help="Receiver server endpoint",
    )
    args = parser.parse_args()

    reader = PhotodiodeReader(args.gpio, args.server, args.bit_duration_us)
    reader.run()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
