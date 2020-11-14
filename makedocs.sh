#!/bin/sh
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


ENVNAME="edna_env"
DIRECTORY="./${ENVNAME}"
if [ -d "$DIRECTORY" ]; then
    # Control will enter here if $DIRECTORY exists.
    colored_print "Found edna virtual environment ${ENVNAME}."
else
    error_print "edna virtual environment ${ENVNAME} does not exist! Create it with"
    colored_print "\t$ ./generate_env.bash"
fi

DOCS="docs"
DOCSDIRECTORY="./${DOCS}"
if [ -d "$DOCSDIRECTORY" ]; then
    colored_print "$DOCS directory exists."
    colored_print "Deleting $DOCS"
    rm -rf -- $DOCS
else
    error_print "$DOCS does not exist. Creating..."
    mkdir -p $DOCS
fi

rootpath=$PWD
cd $DOCS
$rootpath/$ENVNAME/bin/pdoc --html edna --force

