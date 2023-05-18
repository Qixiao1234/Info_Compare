#!/bin/bash
###
### Prototye for converting part of Python, Linux scripts to binary type
### Created by Rex , Date: 2020.5.15
###


#set -x 
SCRIPT=`realpath $0`
SERVER_INFO_DIR=`dirname $SCRIPT`

PCIE_PATH="${SERVER_INFO_DIR}/pcie"
BINARY_DIR="${SERVER_INFO_DIR}/svr_info_ek_bin"


# Get global argument
G_args=("$@")
Binary_mode="DEFAULT"

convert_python(){

    printf "\n\n=== Converting python script... ===\n"
    cd $SERVER_INFO_DIR
    rm -rf dist build __pycache__
    sed -i "s|ACTUAL_PATH|$SERVER_INFO_DIR|g" "server_info.spec"
    pyinstaller server_info.spec
}

convert_shell(){

    file_name=$1 #file name without extension
    printf "\n\n=== Converting shellscript - $1 ===\n"
    
    shc -r -f ${file_name}.sh
    gcc -O2 -D_FORTIFY_SOURCE=2 -static -static-libgcc -static-libstdc++ ${file_name}.sh.x.c -fPIE -fPIC -z noexecstack -z relo -z now -fstack-protector -fstack-protector-strong -o ${file_name}
    
    rm -rf *.[cx] 
}

helper(){
    echo -e "\n"
    echo -e "USAGE:"
    echo -e "The first argument for <build_svt.sh> indicates binary type."
    echo -e "<default> : convert all files to directory"
    echo -e "--all     : convert all files except <server_info_config> to binary"
    echo -e "\n"

}

parse_args(){
    # Parse argument
    for i in "${!G_args[@]}"; do
        
        var=${G_args[$i]}
        if [ $var == "--all" ]; then
            Binary_mode="all"
        elif [ $var == "-h" ] || [ $var == "--help" ]; then
            helper
            exit 0
        fi
    done
}


remove_source(){

    # Move all binary file to one directory
    printf "\n\n=== Remove and clean up .py and .sh files ===\n"
    
    cd $SERVER_INFO_DIR
    mv dist/server_info $SERVER_INFO_DIR

    # Prevent from removing 
    echo "Keep file - server_info_config.py"
    mv  ${SERVER_INFO_DIR}/server_info_config.py ${SERVER_INFO_DIR}/server_info_config.temp
    
    find . -name "*.py"   | xargs rm -rf
    find . -name "*.pyc"  | xargs rm -rf
    find . -name "*.spec" | xargs rm -rf
    find . -name "*.sh"   | xargs rm -rf
    find . -name "*.[cx]" | xargs rm -rf
    find . -name "*.md"   | xargs rm -rf

    rm -rf dist build __pycache__
    # CP Related file for python test
    mv  ${SERVER_INFO_DIR}/server_info_config.temp ${SERVER_INFO_DIR}/server_info_config.py
}

move_to_dir(){

    # Move all binary file to one directory
    printf "\n\n=== Moving binary files to ${BINARY_DIR} ===\n"
    cd $SERVER_INFO_DIR
    mkdir $BINARY_DIR
    mkdir $BINARY_DIR/pcie

    # python
    mv dist/server_info $BINARY_DIR
    rm -rf dist build __pycache__

    mv  ${PCIE_PATH}/run ${BINARY_DIR}/pcie/.
    mv  ${SERVER_INFO_DIR}/svr_info_helper $BINARY_DIR
    mv  ${SERVER_INFO_DIR}/svr_info_helper_extend $BINARY_DIR
    
    # CP Related file for python test
    printf "\n\n=== Copying few python files for testing ===\n"
    cp  ${SERVER_INFO_DIR}/svr_info.yml $BINARY_DIR
    cp  ${SERVER_INFO_DIR}/server_info_config.py $BINARY_DIR
}

convert_files(){

    # Convert
    convert_python
    
    convert_shell "svr_info_helper"
    convert_shell "svr_info_helper_extend"

    cd $PCIE_PATH
    convert_shell "run"
}

main(){

    # Remove old dir
    if [ -e "$BINARY_DIR" ]; then
        rm -rf $BINARY_DIR
    fi

    # Parse Args
    parse_args

    # Check 
    if [ $Binary_mode == "all" ]; then
        echo "=== Convert all files to binary ==="
        convert_files
        remove_source
    else
        echo "=== Run in default mode ==="
        convert_files
        move_to_dir
    fi

}

main $@
