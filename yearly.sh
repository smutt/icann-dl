#!/bin/ksh
# To be executed once in the month of December every year
BASE=/var/www/htdocs/icannhaz.org
STAGE=/home/smutt/staging
YEAR=$(($(date +%Y) + 1))

for DIR in ham/soac/alac/pub ham/icann/cor/ html/icann/blog/ html/icann/announcements
do
	mkdir -m 755 $BASE/$DIR/$YEAR
done

for DIR in html/icann/blog html/icann/announcements
do
	mkdir -m 755 $STAGE/$DIR/$YEAR
done
