#!/bin/ksh
for IMG in $(pdf_info.py -wir $1)
do
	OCR=$(echo $IMG | rev | cut -d. -f2- | rev)_ocr.pdf
	if [ ! -f "$OCR" ]; then
		echo $IMG
	fi
done
