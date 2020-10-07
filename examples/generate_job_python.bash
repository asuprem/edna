#!/bin/bash
# Usage: bash ./generate_job_python.sh appdir/jobdir edna_env
set -o errexit
CYAN='\033[1;36m'
RED='\033[1;31m'
NC='\033[0m' # No Color

# Setup the print
colored_print(){
    printf ${CYAN}"$(date +"%T") -- $1"${NC}"\n"
}
error_print(){
    printf ${RED}"$(date +"%T") -- $1"${NC}"\n"
}
# Setup the print
finished_print(){
    printf ${CYAN}"$1"${NC}"\n"
}

me=`basename "$0"`
if [ ! -e "$me" ]; then
    error_print "Not in repo/examples/ directory. Run from inside the example directory. Exiting"
    exit 0
fi 
# Get the job directory
entrydir=$1
env=$2
# Get the root path
colored_print "Getting repo directory"
cd ..
rootpath=$PWD
cd examples



# Enter the job directory
colored_print "Entering working directory $1"
cd $1

# Get variables
IMAGEADDRESS=$(grep -e registryaddress config.yaml | awk '{print $2}' | tr -d '\r')
APPNAME=$(grep -e applicationname config.yaml | awk '{print $2}' | tr -d '\r')
JOBNAME=$(grep -e jobname config.yaml | awk '{print $2}' | tr -d '\r')
IMAGENAME="${APPNAME}-${JOBNAME}"
IMAGETAG=$(grep -e imagetag config.yaml | awk '{print $2}' | tr -d '\r')


# Generate the Dockerfile
colored_print "Generating the Dockerfile from jinja template"
$rootpath/$2/bin/j2 $rootpath/examples/Dockerfile.jinja2 config.yaml > Dockerfile

# Generate .dockerignore
colored_print "Generating the .dockerignore"
cat <<EOF > .dockerignore
# Ignore .git and .cache
.git
.cache

# Ignore config yaml files and generated docker.sh file
config.yaml
deployment.yaml
docker.sh
EOF

# Copy the source files
colored_print "Copying edna source files"
cp -r $rootpath/python/edna/src .
cp $rootpath/python/edna/setup.py .
cp $rootpath/python/edna/setup.cfg .

# Build the docker image and delete the generated sh file
colored_print "Building the docker image"
$rootpath/$2/bin/j2 $rootpath/examples/docker.sh.j2 config.yaml > docker.sh
./docker.sh
colored_print "Deleting docker.sh and associated detritus"
rm docker.sh
rm .dockerignore


colored_print "Deleting local copy of edna source files (src/, setup.py, and setup.cfg)"
rm -rf -- src
rm setup.py
rm setup.cfg

# Generate the deployment
colored_print "Generating the Kubernetes deployment yaml"
$rootpath/$2/bin/j2 $rootpath/examples/deployment.yaml.jinja2 config.yaml > deployment.yaml

finished_print "\n\nDeployment generated!"
finished_print "\n\nYou can run this after cd'ing into ${entrydir} with:"
finished_print "\n\tkubectl apply -f deployment.yaml"

finished_print "\n\nYou can debug with an interactive pod with:"
finished_print "\n\tkubectl run ${JOBNAME}-debug-pod --rm -i --tty --image ${IMAGEADDRESS}/${IMAGENAME}:${IMAGETAG} -- sh"