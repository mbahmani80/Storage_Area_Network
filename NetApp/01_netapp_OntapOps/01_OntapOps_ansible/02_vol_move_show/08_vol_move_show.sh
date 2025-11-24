#!/bin/bash
# Define variables
user_home=$HOME
PYTHON="$HOME/ansible-env/bin/python"
WORKING_DIR="$(pwd)"
LOG_DIR="${WORKING_DIR}/log"

# Ensure the log directory exists
mkdir -p $LOG_DIR

# Help function
function show_help() {
    echo "Usage: $0 -a PLAYBOOK_NAME -v PLAYBOOK_VAR_NAME -p PYTHON_PROG_NAME"
    echo "Example: $0 -a 08_vol_move_show_main.yml -v vars_pndh-sodbackup01_02.yml -p 08_vol_move_show.py"
    echo "Options:"
    echo "  -a PLAYBOOK_NAME      Name of the Ansible playbook to run"
    echo "  -v PLAYBOOK_VAR_NAME  Name of the variables file to use"
    echo "  -p PYTHON_PROG_NAME   Name of the python program"
    echo "  -h                    Show this help message"
}

# Parse input arguments
while getopts ":a:v:p:h" opt; do
    case ${opt} in
        a )
            PLAYBOOK_NAME=$OPTARG
            ;;
        v )
            PLAYBOOK_VAR_NAME=$OPTARG
            ;;
        p )
            PY_PROGRAM_NAME=$OPTARG
            ;;
        h )
            show_help
            exit 0
            ;;
        \? )
            echo "Invalid option: -$OPTARG" 1>&2
            show_help
            exit 1
            ;;
        : )
            echo "Invalid option: -$OPTARG requires an argument" 1>&2
            show_help
            exit 1
            ;;
    esac
done

# Check if required arguments are provided
if [ -z "$PLAYBOOK_NAME" ] || [ -z "$PLAYBOOK_VAR_NAME" ] || [ -z "$PY_PROGRAM_NAME" ]; then
    echo "Error: PLAYBOOK_NAME, PLAYBOOK_VAR_NAME, and PYTHON_PROG_NAME are required."
    show_help
    exit 1
fi

PLAYBOOK_PATH="${WORKING_DIR}/${PLAYBOOK_NAME}"
PLAYBOOK_VAR_PATH="${WORKING_DIR}/${PLAYBOOK_VAR_NAME}"
LOG_FILE_YML="$LOG_DIR/${PLAYBOOK_NAME}_$(date +'%Y%m%d').log"
PY_PROGRAM_PATH="${WORKING_DIR}/${PY_PROGRAM_NAME}"
LOG_FILE_PY="$LOG_DIR/${PY_PROGRAM_NAME}_$(date +'%Y%m%d').log"

# Run the Ansible playbook and append the output to the log file
{
    echo "===== $(date +'%Y-%m-%d %H:%M:%S') ====="
    cd $WORKING_DIR
    ansible-playbook $PLAYBOOK_PATH -e "vars_file=${WORKING_DIR}/${PLAYBOOK_VAR_NAME}"
    echo "========================================"
} >> $LOG_FILE_YML 2>&1
echo "playbook log: $LOG_FILE_YML"

# Run the python program and append the output to the log file
{
    echo "===== $(date +'%Y-%m-%d %H:%M:%S') ====="
    cd $WORKING_DIR && $PYTHON $PY_PROGRAM_PATH
    echo "========================================"
} >> $LOG_FILE_PY 2>&1
echo "python log: $LOG_FILE_PY"
