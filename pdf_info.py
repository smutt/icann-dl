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

'''
Maybe interesting for later
Possible metadata fields, not applicable to all files
Author -> SO/AC
Title -> Title of Doc
Series -> Publication Series
Number -> number in the series
Version -> Version of document
Created -> Created date
OCR Created -> Date of OCR application
Language -> 2-letter language code(en, ar, etc)
'''

import argparse
import os
import stat
from datetime import datetime, date
from PyPDF2 import PdfReader
import pathlib

# Takes a PDF file handle
# Returns true if PDF is a sandwich
def check_sandwich(fh):
  return False

# Takes a PDF file handle
# Returns true if PDF is an image
def check_image(fh):
  for page in fh.pages:
    try:
      text = page.extract_text().strip()
    except:
      continue

    if len(text) == 0:
      continue
    else:
      return False
  return True


###################
# BEGIN EXECUTION #
###################

ap = argparse.ArgumentParser(description='Print names of PDFs that have specific properties')
ap.add_argument('-b', '--broken', action='store_true', help='Find broken PDFs only')
ap.add_argument('-e', '--encrypted', action='store_true', help='Find encrypted PDFs only')
ap.add_argument('-i', '--image', action='store_true', help='Find image only PDFs')
ap.add_argument('-m', '--metadata', nargs='?', help='Print passed metadata field or {all}')
ap.add_argument('-s', '--sandwich', action='store_true',  help='Find sandwich PDFs {NOT IMPLEMENTED}')
ap.add_argument('-r', '--recursive', action='store_true', help='Recursively search directories')
ap.add_argument('path', type=pathlib.Path, help='File or directory')
args = ap.parse_args()

pdfs = []
if args.path.is_file():
  if args.path.suffix == '.pdf':
    if os.access(args.path, os.R_OK):
      pdfs.append(args.path.name)

elif args.path.is_dir():
  sdirs = [args.path]
  while sdirs:
    for line in os.scandir(sdirs.pop(0)):
      if line.is_symlink():
        continue
      if line.is_dir():
        if args.recursive:
          sdirs.append(line)
      elif line.is_file():
        if line.name.endswith('.pdf'):
          if os.access(line, os.R_OK):
            pdfs.append(line.path)

for pdf in pdfs:
  #print(pdf)
  try:
    fh = PdfReader(pdf)
  except:
    print("Broken pdf: " + pdf)
    continue

  if args.broken:
    continue

  # Deal with encryption brokenness
  # https://github.com/py-pdf/PyPDF2/issues/245
  if fh.is_encrypted:
    if args.encrypted:
      print(pdf + ' is encrypted, attempting decryption with NULL password')

    try:
      fh.decrypt('')
      _ = len(fh.pages)
    except:
      try:
        fh._override_encryption=True
        fh._flatten()
        _ = len(fh.pages)
      except:
        print(pdf + ' decryption failed')
        continue
    if args.encrypted:
      continue


  if len(fh.pages) == 0:
    continue
  if args.image:
    if check_image(fh):
      print(pdf)

  if args.sandwich:
    if check_sandwich(fh):
      print(pdf)

  if args.metadata:
    if fh.metadata == None:
      print(pdf)

    elif args.metadata == 'all':
      rv = pdf + ' {'
      for key in fh.metadata:
        rv += "\'" + key + "\': \'" + str(fh.metadata[key]) + "\', "
      print(rv.strip(', ') + '}')

    else:
      if args.metadata in fh.metadata:
        print(pdf + ' {\'' + args.metadata + '\': \'' + str(fh.metadata[args.metadata]) + '\'}')
