# ACEest Fitness & Gym — DevOps CI/CD Project

## Project Overview

ACEest Fitness & Gym is a Python-based fitness application enhanced with a DevOps workflow for automated testing, containerization, and continuous integration.

This project demonstrates the use of Git, GitHub, GitHub Actions, Docker, Jenkins, Pytest, and GitHub Webhooks.

## Technology Stack

- Python 3.11
- Flask
- Pytest
- Docker
- Jenkins
- GitHub Actions
- Git / GitHub
- Cloudflare Quick Tunnel for webhook connectivity

## Application

The Flask application provides:

- Application status endpoint
- Health check endpoint
- Calorie calculation endpoint

### API Endpoints

#### GET `/`

Returns the application status.

#### GET `/health`

Returns the application health status.

#### POST `/calculate-calories`

Example request:

```json
{
  "weight": 70,
  "factor": 22
}
