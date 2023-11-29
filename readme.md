# Water level monitoring in the UK

This project aims for the development of a backend that serves a water level monitoring application in near real-time.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)

## Installation

To run this project, you need to have Docker installed on your machine. If you don't have Docker installed, you can download it from the official website: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

## Usage

1. Clone the repository:

   ```shell
   git clone https://github.com/lenawe/water-level-monitoring-UK.git
   ```

2. Run the project in detached mode:

   ```shell
   docker compose up -d
   ```

3. Access the Kafka UI for monitoring at [http://localhost:8888](http://localhost:8888).