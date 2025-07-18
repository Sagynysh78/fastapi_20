#!/usr/bin/env bash
#   Use this script to test if a given TCP host/port are available

# The MIT License (MIT)
# Copyright (c) 2016 Giles Hall
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

set -e

TIMEOUT=15
QUIET=0
HOST=""
PORT=""

print_usage() {
    echo "Usage: $0 host:port [-t timeout] [-- command args]"
    echo "-h HOST | --host=HOST       Host or IP under test"
    echo "-p PORT | --port=PORT       TCP port under test"
    echo "-t TIMEOUT | --timeout=TIMEOUT  Timeout in seconds, zero for no timeout"
    echo "-q | --quiet                Don't output any status messages"
    echo "-- COMMAND ARGS             Execute command with args after the test finishes"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        *:* )
        HOST=$(echo $1 | cut -d: -f1)
        PORT=$(echo $1 | cut -d: -f2)
        shift 1
        ;;
        -h)
        HOST="$2"
        shift 2
        ;;
        --host=*)
        HOST="${1#*=}"
        shift 1
        ;;
        -p)
        PORT="$2"
        shift 2
        ;;
        --port=*)
        PORT="${1#*=}"
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        shift 2
        ;;
        --timeout=*)
        TIMEOUT="${1#*=}"
        shift 1
        ;;
        -q|--quiet)
        QUIET=1
        shift 1
        ;;
        --)
        shift
        break
        ;;
        *)
        print_usage
        ;;
    esac
    done

if [[ "$HOST" = "" || "$PORT" = "" ]]; then
    print_usage
fi

wait_for() {
    for i in $(seq $TIMEOUT); do
        if nc -z $HOST $PORT; then
            return 0
        fi
        sleep 1
    done
    return 1
}

if [[ $QUIET -ne 1 ]]; then
    echo "Waiting for $HOST:$PORT..."
fi

if wait_for; then
    if [[ $QUIET -ne 1 ]]; then
        echo "$HOST:$PORT is available!"
    fi
else
    echo "Timeout occurred after waiting $TIMEOUT seconds for $HOST:$PORT"
    exit 1
fi

exec "$@" 