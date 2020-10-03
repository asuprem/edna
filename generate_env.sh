#!/bin/bash
set -o errexit
if ! [ -x "$(command -v virtualenv)" ]; then
  echo 'Error: virtualenv not installed'
  pip3 install --user virtualenv
fi
ENVNAME="edna_env"
DIRECTORY="./${ENVNAME}"
if [ -d "$DIRECTORY" ]; then
    # Control will enter here if $DIRECTORY exists.
    echo "$(date +"%T") -- ${ENVNAME} exists."
    # remove the environment and generate it again
    echo "$(date +"%T") -- Removing ${ENVNAME}."
    rm -rf ${ENVNAME} 
    echo "$(date +"%T") -- Generating virtual environment ${ENVNAME}"
    virtualenv -p python3.7 ${ENVNAME}

else
    echo "$(date +"%T") -- ${ENVNAME} does not exist."
    echo "$(date +"%T") -- Generating virtual environment ${ENVNAME}"
    virtualenv -p python3.7 ${ENVNAME}
fi
    
echo "$(date +"%T") -- Activating virtual environment ${ENVNAME}"
source ./${ENVNAME}/bin/activate

if [ $? -eq 0 ]; then
    echo "$(date +"%T") -- Beginning package installs."
    echo "$(date +"%T") -- Installing basic packages"
    
    echo "$(date +"%T") -- Installing edna"
    cd python/edna
    pip3 install --no-cache-dir -e .
    cd ../../

    echo "$(date +"%T") -- Installing interface tools"
    # Interface utilities
    pip3 install --no-cache-dir click==7.1.0 j2cli==0.3.10
else
    echo "FAILED TO ACTIVATE virtual environment $DIRECTORY."
    exit 1
fi


echo "$(date +"%T") -- Finished."