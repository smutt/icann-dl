#!/usr/bin/env python3

#  The file is part of the icann-dl Project.
#
#  The icann-dl Project is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  The icann-dl Project is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#  Copyright (C) 2022, Andrew McConachie, <andrew.mcconachie@icann.org>

import argparse
import os
import stat
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
import pathlib

ap = argparse.ArgumentParser(description='Process PDFs')
ap.add_argument('infile', type=pathlib.Path, help='Input PDF file')
args = ap.parse_args()

if not args.infile.exists() or not args.infile.is_file():
  print("Invalid input file")

group = args.infile.parts[-2]

fh = PdfFileReader(str(args.infile))

print(fh.numPages)

print(fh.getDocumentInfo())

# Possible metadata fields, not applicable to all files
# Author -> SO/AC
# Title -> Title of Doc
# Series -> Publication Series
# Number -> number in the series
# Version -> Version of document
# Created -> Created date
# OCR Created -> Date of OCR application
# Language -> 2-letter language code(en, ar, etc)
