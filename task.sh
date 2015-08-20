#!/usr/bin/env sh

CURRDIR=$(cd $(dirname $0);pwd)
source ${CURRDIR}/.env
python ${CURRDIR}/run.py
