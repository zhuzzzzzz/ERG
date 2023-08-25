#!/bin/bash

# execute command

if test $# -gt 0
then 
	${PHOEBUS_PATH}/phoebus.sh -server ${SERVER_PORT} -resource $*

else
	${PHOEBUS_PATH}/phoebus.sh -server ${SERVER_PORT}
fi

