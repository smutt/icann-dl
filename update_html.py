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

import os

base_dir = '/var/www/htdocs/icann-pdf.depht.com/pub/'
html_out = '/var/www/htdocs/icann-pdf.depht.com/index.html'
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


# BEGIN EXECUTION
fin = open(html_in, 'r')
output = fin.read()
for dd in os.scandir(base_dir):
  if dd.is_dir():
    group = dd.name
    count = count_files(lambda x: 1, base_dir + group)
    MB = count_files(lambda x: x.stat().st_blocks, base_dir + group)

    output = output.replace('@@@files-' + group + '@@@', count)
    output = output.replace('@@@size-' + group + '@@@', MB)

fin.close()
#fout = open(html_out, 'w')
#fout.write(output)
#fout.close()
