#!/bin/ksh
for IMG in $(pdf_info.py -wi $1)
do
	OCR=$(basename $IMG .pdf)_ocr.pdf
	if [ ! -f "$OCR" ]; then
		echo $IMG
	fi
done
