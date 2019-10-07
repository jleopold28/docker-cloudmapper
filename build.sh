set -ex

USERNAME=jamesleopold
IMAGE=cloudmapper

docker build -t $USERNAME/$IMAGE:latest .
