#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8 ff=unix ft=sh

function show_help() {
cat << EOF
Usage $0 arguments ...

Arguments:
  ${cyan}--help${normal}
    Display the help screen

  ${cyan}--unexpected-username${normal}
    Unexpected username which you want to fix
  
  ${cyan}--unexpected-email${normal}
    Unexpected email which you want to fix
  
  ${cyan}--expected-username${normal}
    Username what you expected
  
  ${cyan}--expected-email${normal}
    Email what you expected

EOF
print_reference
}

function print_reference() {
    echo "Thanks for these helps:"
    echo "修改git全部已提交的用户名和邮箱(https://blog.csdn.net/LOVE____JAVA/article/details/51386218)"
    echo "Check if current directory is a Git repository(https://stackoverflow.com/questions/2180270/check-if-current-directory-is-a-git-repository)"
    echo "Echo text in a certain color in a shell script(https://superuser.com/questions/332223/echo-text-in-a-certain-color-in-a-shell-script)"
    echo "How to determine if a bash variable is empty?(https://serverfault.com/questions/7503/how-to-determine-if-a-bash-variable-is-empty)"
    echo "git log按作者过滤提交(https://blog.csdn.net/ly890700/article/details/73224912)"
}

function init() {
    # check if stdout is a terminal
    if test -t 1; then
        # see if it supports colors...
        ncolors=$(tput colors)
        if test -n "$ncolors" && test $ncolors -ge 8; then
            bold="$(tput bold)"
            underline="$(tput smul)"
            standout="$(tput smso)"
            normal="$(tput sgr0)"
            black="$(tput setaf 0)"
            red="$(tput setaf 1)"
            green="$(tput setaf 2)"
            yellow="$(tput setaf 3)"
            blue="$(tput setaf 4)"
            magenta="$(tput setaf 5)"
            cyan="$(tput setaf 6)"
            white="$(tput setaf 7)"
        fi
    fi
}

function error() {
    echo -n -e "${red}ERROR${normal}:"
    echo $1
}

function info() {
    echo -n -e "${red}INFO ${normal}:"
    echo $1
}

function parse_arguments() {
    unexpected_username=""
    unexpected_email=""
    expected_email=""
    expected_username=""
    
    while [[ "$1" != "" ]];do
        val=`expr "$1" : "--unexpected-username=\(.*\)"`
        if [[ ! -z "${val}" ]];then
            unexpected_username=${val}
        fi

        val=`expr "$1" : "--unexpected-email=\(.*\)"`
        if [[ ! -z "${val}" ]];then
            unexpected_email=${val}
        fi

        val=`expr "$1" : "--expected-username=\(.*\)"`
        if [[ ! -z "${val}" ]];then
            expected_username=${val}
        fi

        val=`expr "$1" : "--expected-email=\(.*\)"`
        if [[ ! -z "${val}" ]];then
            expected_email=${val}
        fi

        if [[ "$1" == "--help" ]];then
            show_help
            exit 0
        fi
    
        shift
    done

    if [[ -z "${unexpected_username}" && -z "${unexpected_email}" ]];then
        error "At least one of --unexpected-username and --unexpected-email cannot be blank"
        exit 1
    fi
    if [[ -z "${expected_username}" && -z "${expected_email}" ]];then
        error "At least one of --expected-username and --expected-email cannot be blank"
        exit 1
    fi
}

function fix() {
    commit_ids=$(git log --pretty=%h)
    for commit_id in ${commit_ids};do
        filename=$(mktemp)
        if [[ ! -z "${unexpected_username}" && ! -z "${unexpected_email}" ]];then
            echo "git filter-branch  -f --commit-filter '" > ${filename}
            echo "if [[ \"\${GIT_AUTHOR_EMAIL}\" == \"${unexpected_email}\" || \"\${GIT_AUTHOR_NAME}\" == \"${unexpected_username}\" ]];then" >> ${filename} 
            if [[ ! -z "${expected_username}" ]];then
                echo "export GIT_AUTHOR_NAME=\"${expected_username}\"" >> ${filename}
            fi
            if [[ ! -z "${expected_email}" ]];then
                echo "export GIT_AUTHOR_EMAIL=\"${expected_email}\"" >> ${filename}
            fi
            echo "git commit-tree \"\$@\"" >> ${filename}
            echo "else" >> ${filename}
            echo "git commit-tree \"\$@\"" >> ${filename}
            echo "fi" >> ${filename}
            echo "' -- ${commit_id} HEAD" >> ${filename}

        elif [[ ! -z "${unexpected_username}" ]];then
            echo "git filter-branch  -f --commit-filter '" > ${filename}
            echo "if [[ \"\${GIT_AUTHOR_NAME}\" == \"${unexpected_username}\" ]];then" >> ${filename} 
            if [[ ! -z "${expected_username}" ]];then
                echo "export GIT_AUTHOR_NAME=\"${expected_username}\"" >> ${filename}
            fi
            if [[ ! -z "${expected_email}" ]];then
                echo "export GIT_AUTHOR_EMAIL=\"${expected_email}\"" >> ${filename}
            fi
            echo "git commit-tree \"\$@\"" >> ${filename}
            echo "else" >> ${filename}
            echo "git commit-tree \"\$@\"" >> ${filename}
            echo "fi" >> ${filename}
            echo "' -- ${commit_id} HEAD" >> ${filename}

        elif [[ ! -z "${unexpected_email}" ]];then
            echo "git filter-branch  -f --commit-filter '" > ${filename}
            echo "if [[ \"\${GIT_AUTHOR_EMAIL}\" == \"${unexpected_email}\" ]];then" >> ${filename} 
            if [[ ! -z "${expected_username}" ]];then
                echo "export GIT_AUTHOR_NAME=\"${expected_username}\"" >> ${filename}
            fi
            if [[ ! -z "${expected_email}" ]];then
                echo "export GIT_AUTHOR_EMAIL=\"${expected_email}\"" >> ${filename}
            fi
            echo "git commit-tree \"\$@\"" >> ${filename}
            echo "else" >> ${filename}
            echo "git commit-tree \"\$@\"" >> ${filename}
            echo "fi" >> ${filename}
            echo "' -- ${commit_id} HEAD" >> ${filename}
        fi

        sh ${filename}
        rm -rf ${filename}
    done

    remote=$(git remote | head -n 1)
    branch_name=$(git rev-parse --abbrev-ref HEAD)
    info "Fix completed, you can run ${cyan} git push ${remote} ${branch_name} --force ${normal} to take effect."
}


function main() {
    init
    if [[ ! $(git rev-parse --is-inside-work-tree 2>/dev/null) ]];then
        error "You should run this command in git repository directory"
        exit 1
    fi

    parse_arguments $@
    fix
}

main $@

