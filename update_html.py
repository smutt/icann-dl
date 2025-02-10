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
#  Copyright (C) 2022, 2023 Andrew McConachie, <andrew.mcconachie@icann.org>

from datetime import datetime
import math
import os
import ham_group
import html_group

www_base = '/var/www/htdocs/icann-hamster.nl/'

fetch_num = 10 # How many of the last fetches to display on index.html
fetch_num_more = 100 # How many of the last fetches to display on more_recent.html
fetch_log = os.environ['HOME'] + '/log/fetch_ham.log'

index_in =  os.path.dirname(os.path.realpath(__file__)) + '/html/index.html.slug'
index_out = www_base + 'index.html'
collections_in = os.path.dirname(os.path.realpath(__file__)) + '/html/collections.html.slug'
collections_out = www_base + 'collections.html'
more_recent_in = os.path.dirname(os.path.realpath(__file__)) + '/html/more_recent.html.slug'
more_recent_out = www_base + 'more_recent.html'

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

# Read in our slug files
# Return string
def read_in(fname):
  fin = open(fname, 'r')
  rv = fin.read()
  fin.close()
  return rv

# Write output HTML
# Overwrites existing files
def write_out(fname, ss):
  fout = open(fname, 'w')
  fout.write(ss)
  fout.close()


###################
# BEGIN EXECUTION #
###################
index_output = read_in(index_in)
collections_output = read_in(collections_in)
more_recent_output = read_in(more_recent_in)

total_count = total_MB = total_OCR = 0

for group_set in [ham_group, html_group]:
  for name, gr in group_set.groups.items():
    try:
      path = gr.top_path
    except:
      path = gr.path

    count = count_files(lambda x: 1, gr.base_dir + path)
    MB = math.ceil(count_files(lambda x: x.stat().st_blocks, gr.base_dir + path) / 2000)
    OCR = count_files(is_ocr, gr.base_dir + path)
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

# Create list of most recent downloaded docs
fin = open(fetch_log, 'r')
fetches = list(fin)
fin.close()

recent_fetches = []
while len(recent_fetches) < fetch_num_more or len(fetches) == 0:
  line = fetches.pop().strip()
  if not line.split()[1].startswith('https://'):
    continue

  ts = datetime.fromisoformat(line.split()[0]).strftime('%a %b %d')
  linky = line.split(www_base)[1].replace("%", "%25")
  recent_fetches.append([ts, linky])

ss = ''
for ii in range(fetch_num):
  ss += '<tr id="rec"><td id="rec">' + recent_fetches[ii][0] + '</td><td id="rec"><a href=\'' + recent_fetches[ii][1] + '\'>' + \
    recent_fetches[ii][1].split('/')[-1] + '</a></td></tr>\n'
index_output = index_output.replace('@@@recent-fetches@@@', ss.strip('\n'))

ss = ''
for ii in range(fetch_num_more):
  ss += '<tr id="rec"><td id="rec">' + recent_fetches[ii][0] + '</td><td id="rec"><a href=\'' + recent_fetches[ii][1] + '\'>' + \
    recent_fetches[ii][1].split('/')[-1] + '</a></td></tr>\n'
more_recent_output = more_recent_output.replace('@@@more-recent-fetches@@@', ss.strip('\n'))

# Write output HTML
write_out(index_out, index_output)
write_out(collections_out, collections_output)
write_out(more_recent_out, more_recent_output)

