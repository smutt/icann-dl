#!/bin/ksh
# To be executed once in the month of December every year
BASE=/var/www/htdocs/icannhaz.org/
YEAR=$(($(date +%Y) + 1))

for DIR in ham/soac/alac/pub ham/icann/cor/ html/icann/blog/
do
	mkdir -m 755 $BASE/$DIR/$YEAR
done
