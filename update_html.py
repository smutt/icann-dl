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

import math
import os
import group

index_in =  os.path.dirname(os.path.realpath(__file__)) + '/html/index.html.slug'
index_out = '/var/www/htdocs/icann-hamster.nl/index.html'
collections_in =  os.path.dirname(os.path.realpath(__file__)) + '/html/collections.html.slug'
collections_out = '/var/www/htdocs/icann-hamster.nl/collections.html'

# High-order func to recursively count files
# Return f(func(cur_dir)) total
def count_files(func, cur_dir):
  rv = 0
  for dd in os.scandir(cur_dir):
    if dd.is_dir():
      rv += count_files(func, cur_dir + '/' + dd.name)
    elif dd.is_file():
      rv += func(dd)
  return rv

# Takes an os.DirEntry
def is_ocr(de):
  if de.name.endswith('_ocr.pdf'):
    return 1
  else:
    return 0

###################
# BEGIN EXECUTION #
###################
fin = open(index_in, 'r')
index_output = fin.read()
fin.close()

fin = open(collections_in, 'r')
collections_output = fin.read()
fin.close()

total_count = total_MB = total_OCR = 0

for name,gr in group.groups.items():
  count = count_files(lambda x: 1, gr.base_dir + gr.path)
  MB = math.ceil(count_files(lambda x: x.stat().st_blocks, gr.base_dir + gr.path) / 2000)
  OCR = count_files(is_ocr, gr.base_dir + gr.path)
  total_count += count
  total_MB += MB
  total_OCR += OCR

  collections_output = collections_output.replace('@@@files-' + name + '@@@', "{:,}".format(count))
  collections_output = collections_output.replace('@@@size-' + name + '@@@', "{:,}".format(MB))

index_output = index_output.replace('@@@files-total@@@', "{:,}".format(total_count))
index_output = index_output.replace('@@@size-total@@@', "{:,}".format(total_MB))
index_output = index_output.replace('@@@ocr-total@@@', "{:,}".format(total_OCR))

collections_output = collections_output.replace('@@@files-total@@@', "{:,}".format(total_count))
collections_output = collections_output.replace('@@@size-total@@@', "{:,}".format(total_MB))

fout = open(index_out, 'w')
fout.write(index_output)
fout.close()

fout = open(collections_out, 'w')
fout.write(collections_output)
fout.close()
