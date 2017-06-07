#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

function checkGitExists() {
    (which git >> /dev/null) && ec=$? || ec=$?

  if [ ! $ec -eq 0 ] ; then
    >&2 echo "git was not found on your system"
    exit 1
  fi
}

function checkJavaExists() {
    (which java >> /dev/null) && ec=$? || ec=$?

  if [ ! $ec -eq 0 ] ; then
    >&2 echo "Java was not found on your system :)"
    exit 1
  fi
}

function checkMavenExists() {
    (which mvn >> /dev/null) && ec=$? || ec=$?

  if [ ! $ec -eq 0 ] ; then
    >&2 echo "Maven (https://maven.apache.org/) was not found on your system"
    exit 1
  fi
}

function cloneGitIfNotExistsAndRunTests() {
  reponame=${url##*/}
  reponame=${reponame%.git}
  
  if [ ! -d $reponame ] ; then
    git clone $url $reponame
    cd $reponame
    mvn clean install
    cd ..
  else
    >&2 echo "Project already exists"
    exit 1
  fi
}

function checkJavaHomeEnvSet() {
    if [ ! -z ${var+x} ]; then
    >&2 echo "JAVA_HOME environment variable is not set"
    exit 1
    fi
}

checkGitExists
checkJavaExists
checkJavaHomeEnvSet
checkMavenExists

# Perguntando URL do projeto (digitar https://github.com/jfsc/spring-petclinic.git)
read -p "Project URL: " url

# Criando diretórios DEV, TEST, UAT, PRODUCTION
mkdir -p DEV TEST UAT PRODUCTION

cd DEV
cloneGitIfNotExistsAndRunTests
