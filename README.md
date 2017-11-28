# GEOS
A simple deployable web application for cloud environment

## Why?
This project was created with a single goal: learn about cloud configuration and deployment. GEOS uses some of the main concepts of cloud environments such as Load Balancers, Auto Scaling Instance Groups, Virtual Private Clouds and others, deploying a robust and scalable yet simple Flask + Apache application.

## Supported Cloud Platforms
- AWS (Amazon Web Services)

## Requirements
- Linux (Ubuntu/Debian) operating system
- Python 3
- boto3 (AWS API for Python)
- Configured AWS CLI and credentials

## Install Guide
Download the files inside ```geosapp/``` directory and run ```deploy.sh```. If all requirements are present, GEOS should be automatically deployed to the region configured by AWS command-line tools.

## Usage
GEOS is capable of doing simple REST requests to the server (GET, POST, PUT and DELETE). The ```geos``` client is provided with the install scripts. If the deploy was successful, GEOS is already running. Use ```./geos -h``` for help.
