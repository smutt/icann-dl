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
import groups

base_dir = '/var/www/htdocs/icann-hamster.nl/ham/'
html_out = '/var/www/htdocs/icann-hamster.nl/index.html'
html_in =  os.path.dirname(os.path.realpath(__file__)) + '/html/index.html.slug'

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


# BEGIN EXECUTION
fin = open(html_in, 'r')
output = fin.read()
fin.close()
total_count = total_MB = total_OCR = 0

for name,gr in groups.groups.items():
  count = count_files(lambda x: 1, base_dir + gr['path'])
  MB = math.ceil(count_files(lambda x: x.stat().st_blocks, base_dir + gr['path']) / 2000)
  OCR = count_files(is_ocr, base_dir + gr['path'])
  total_count += count
  total_MB += MB
  total_OCR += OCR

  output = output.replace('@@@files-' + name + '@@@', "{:,}".format(count))
  output = output.replace('@@@size-' + name + '@@@', "{:,}".format(MB))

output = output.replace('@@@files-total@@@', "{:,}".format(total_count))
output = output.replace('@@@size-total@@@', "{:,}".format(total_MB))
output = output.replace('@@@ocr-total@@@', "{:,}".format(total_OCR))

fout = open(html_out, 'w')
fout.write(output)
fout.close()
