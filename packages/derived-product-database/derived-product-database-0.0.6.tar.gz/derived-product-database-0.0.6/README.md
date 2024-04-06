# Sample GitLab Project

This sample project shows how a project in GitLab looks for demonstration purposes. It contains issues, merge requests and Markdown files in many branches,
named and filled with lorem ipsum.

You can look around to get an idea how to structure your project and, when done, you can safely delete this project.

[Learn more about creating GitLab projects.](https://docs.gitlab.com/ee/gitlab-basics/create-project.html)

ENVIRONMENT VARIABLES:
export INFLUX_BUCKET="dpd"
export INFLUX_URL="http://localhost:8086"
export INFLUX_TOKEN="[INFLUX TOKEN]"
export INFLUX_ORG="USGS"

SETUP

Create DPD conda environment
conda create -n dpd
conda install python=3.10.0

conda activate dpd

Install Influx
https://docs.influxdata.com/influxdb/v2/install/?t=Linux

Red hat install: 
cat <<EOF | sudo tee /etc/yum.repos.d/influxdata.repo
[influxdata]
name = InfluxData Repository - Stable
baseurl = https://repos.influxdata.com/stable/\$basearch/main
enabled = 1
gpgcheck = 1
gpgkey = https://repos.influxdata.com/influxdata-archive_compat.key
EOF

sudo yum install influxdb2

Start service influxdb: 
sudo service influxdb start

Verify linux influxdb: 
sudo service influxdb status

Mac install: 
brew update
brew install influxdb

Start mac influcdb: 
influxd


Clone repository to /data/

Install dependencies with pip install -r requirements.txt
Install FastAPI 

Install local dependecies
Run pip install . from topmost directory 

Build
pip install build
build . (from topmost directory)

Setup initial environment variables:
export INFLUX_BUCKET="dpd-infrasound"
export INFLUX_URL="http://localhost:8086"
export INFLUX_ORG="USGS"

Influxdb setup (must be done after environment variables):
Navigate to localhost:8086 and create account
Username, password
Intitial Organiztation name: USGS
Initial bucket name: dpd-infrasound

Copy api token to clipboard. It will be stored via environment variables later. 
Set token to environment variable
export INFLUX_TOKEN="[INFLUX TOKEN]"

Start Api, navigate to /src/service
uvicorn service.main:app --reload

Navigate to localhost:8000/docs

Run cont_processing:
Open new terminal window
Reset all environment variables

run python cont_processing.py