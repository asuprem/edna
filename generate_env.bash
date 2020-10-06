#!/bin/bash
set -o errexit

# Setup the print
CYAN='\033[1;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color
colored_print(){
    printf ${CYAN}"$(date +"%T") -- $1"${NC}"\n"
}
error_print(){
    printf ${RED}"$(date +"%T") -- $1"${NC}"\n"
}

if ! [ -x "$(command -v virtualenv)" ]; then
  error_print "Virtualenv not installed. Installing for this user."
  pip3 install --user virtualenv
fi
ENVNAME="edna_env"
DIRECTORY="./${ENVNAME}"
if [ -d "$DIRECTORY" ]; then
    # Control will enter here if $DIRECTORY exists.
    error_print "${ENVNAME} exists."
    # remove the environment and generate it again
    error_print "Removing ${ENVNAME}."
    rm -rf ${ENVNAME} 
    colored_print "Generating virtual environment ${ENVNAME}"
    virtualenv -p python3.7 ${ENVNAME}
else
    colored_print "${ENVNAME} does not exist."
    colored_print "Generating virtual environment ${ENVNAME}"
    virtualenv -p python3.7 ${ENVNAME}
fi
    
colored_print "Activating virtual environment ${ENVNAME}"
source ./${ENVNAME}/bin/activate

if [ $? -eq 0 ]; then
    colored_print "Beginning package installs."    
    colored_print "Installing edna"
    cd python/edna
    pip3 install --no-cache-dir -e .[full]
    cd ../../
    colored_print "Installing interface tools"
    # Interface utilities
    pip3 install --no-cache-dir click==7.1.0 j2cli==0.3.10
else
    error_print "FAILED TO ACTIVATE virtual environment $DIRECTORY."
    exit 1
fi

colored_print "Finished."