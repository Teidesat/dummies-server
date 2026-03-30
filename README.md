# Dummies server

This program provides a simple HTTP API server to connect the dummies GUI with their corresponding firmware during the Optical Communications technical tests.

## Environment configuration

Runtime settings (debug mode, host names, ports, firmware endpoints, etc.) are injected through a local `.env` file. To prepare a new environment:

1. Copy the template: `cp .env.example .env`.
2. Edit `.env` and provide real values for:
	- `DEBUG_MODE`
	- `TRANSMITTER_SERVER_HOST` / `TRANSMITTER_SERVER_PORT`
	- `RECEIVER_SERVER_HOST` / `RECEIVER_SERVER_PORT`
3. Launch the services with `./launch-transmitter.sh --build` or `./launch-receiver.sh --build`. Docker Compose automatically loads `.env` via the `env_file` directive.

Never commit the populated `.env`; it contains deployment-specific data. If a secret leaks into the repository, remove it with `git rm --cached .env`, rotate the credentials, and rebuild the containers.
