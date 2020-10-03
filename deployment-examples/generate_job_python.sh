#!/bin/bash
# Usage: sudo ./generate_job_python.sh KafkaIngestEmitJob ../edna_env
set -o errexit

# Get the job directory
entrydir=$1
env=$2
CYAN='\033[1;36m'
NC='\033[0m' # No Color

# Setup the print
colored_print(){
    printf ${CYAN}"$(date +"%T") -- $1"${NC}"\n"
}
# Setup the print
finished_print(){
    printf ${CYAN}"$1"${NC}"\n"
}


cd $1
# Generate the Dockerfile
colored_print "Generating the Dockerfile from jinja template"
../$2/bin/j2 ../Dockerfile.jinja2 config.yaml > Dockerfile

# Generate .dockerignore
colored_print "Generating the .dockerignore"
cat <<EOF > .dockerignore
# Ignore .git and .cache
.git
.cache

# Ignore config yaml files
config.yaml
deployment.yaml
EOF

# Copy the source files
colored_print "Copying edna source files"
cp -r ../../python/edna/src .
cp ../../python/edna/setup.py .
cp ../../python/edna/setup.cfg .

# Build the docker image and delete the generates sh file
colored_print "Building the docker image"
../$2/bin/j2 ../docker.sh.j2 config.yaml > docker.sh
./docker.sh
rm docker.sh
colored_print "Deleting local copy of edna source files"
rm -rf -- src
rm setup.py
rm setup.cfg

# Generate the deployment
colored_print "Generating the Kubernetes deployment"
../$2/bin/j2 ../deployment.yaml.jinja2 config.yaml > deployment.yaml

finished_print "\n\nDeployment generated!"
finished_print "\n\nYou can run this after cd'ing into ${entrydir} with:"
finished_print "\n\tkubectl apply -f deployment.yaml"

IMAGEADDRESS=$(grep -e registryaddress config.yaml | awk '{print $2}' | tr -d '\r')
IMAGENAME=$(grep -e imagename config.yaml | awk '{print $2}' | tr -d '\r')
IMAGETAG=$(grep -e imagetag config.yaml | awk '{print $2}' | tr -d '\r')
JOBNAME=$(grep -e jobname config.yaml | awk '{print $2}' | tr -d '\r')

finished_print "\n\nYou can debug with an interactive pod with:"
finished_print "\n\tkubectl run ${JOBNAME}-debug-pod --rm -i --tty --image ${IMAGEADDRESS}/${IMAGENAME}:${IMAGETAG} -- sh"