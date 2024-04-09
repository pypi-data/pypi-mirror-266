#!/bin/bash

#DBHOST=$1
DBNAME=$1
MPASS=$2
BPASS=$3

#while read p; do
#  echo $p
#done < privileges.sql

mysql -u root -e "create database $DBNAME;"
mysql -u root -e "grant all privileges on $DBNAME.* to 'manager'@'localhost' identified by '$MPASS';"
mysql -u root -e "grant all privileges on $DBNAME.* to 'manager'@'%' identified by '$MPASS';"
mysql -u root -e "grant all privileges on $DBNAME.* to 'browser'@'%' identified by '$BPASS';"
mysql -u root -e "grant all privileges on $DBNAME.* to 'browser'@'localhost' identified by '$BPASS';"

