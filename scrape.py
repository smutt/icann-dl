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
#  Copyright (C) 2025 Andrew McConachie, <andrew.mcconachie@icann.org>

import argparse
import funk
import ham_group
import os
import re

###################
# BEGIN EXECUTION #
###################
ap = argparse.ArgumentParser(description='Scrape URL for PDFs and download to local working directory.')
ap.add_argument(dest='url', help='URL to scrape')
ap.add_argument('-d', '--debug', action='store_true', help='fetch nothing. Instead print what documents would be fetched')
ap.add_argument('-e', '--exclude', type=str, action='store', default=None,
                help='match links to regex for exclusion. Overrides inclusion.')
ap.add_argument('-i', '--include', type=str, action='store', default=r'.*\.pdf$',
                help=r'match links to regex for inclusion. Default: .*\.pdf$')
ARGS = ap.parse_args()
hammy = ham_group.Ham_group()

include_regex = exclude_regex = []
include_regex.append(re.compile(ARGS.include))
if ARGS.exclude:
  exclude_regex = list(re.compile(ARGS.exclude))
else:
  exclude_regex = hammy.exclude

links = funk.get_links(ARGS.url, include_regex, ['a', 'href'], exclude_regex)
actions = []
for ll in links:
  action = {}
  action['remote'] = ll
  action['fname'] = hammy.clean_filename(ll.split('/')[-1])
  actions.append(action)

local_files = os.listdir()
if ARGS.debug:
  for aa in actions:
    if aa['fname'] in local_files:
      print('Skipping '+ aa['fname'])
      continue
    print(aa['remote'] + ' ==> ' + aa['fname'])

else:
  for aa in actions:
    if aa['fname'] in local_files:
      print('Skipping ' + aa['fname'])
      continue
    hammy._download(aa['remote'], aa['fname'])
