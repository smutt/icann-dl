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
import group
from urllib import parse as Url_parse
from urllib3 import util as Util

###################
# BEGIN EXECUTION #
###################
ap = argparse.ArgumentParser(description='Fetch PDFs from icann.org. By default fetches all groups.')
ap.add_argument('-d', '--debug', action='store_true', help='Fetch nothing. Instead print what URLs would be fetched.')
ap.add_argument('-e', '--exclude', type=str, action='store', default=None,
                choices=group.groups.keys(), help='Fetch all groups except excluded group')
ap.add_argument('-g', '--group', type=str, action='store', default='all',
                choices=group.groups.keys(), help='Fetch single group then exit')
ARGS = ap.parse_args()

if ARGS.exclude != None:
  del group.groups[ARGS.exclude]

for key,gr in group.groups.items():
  if ARGS.group != 'all' and ARGS.group != key:
    continue

  if ARGS.group == 'all' and not gr.enabled: # Skip disabled groups unless --group is passed
    continue

  local_files = gr.local_files()
  for ll in gr.get_links():
    remote_file = Util.parse_url(ll).path.split('/')[-1]
    if remote_file not in local_files and Url_parse.unquote(remote_file) not in local_files:
      if ARGS.debug:
        print(ll)
      else:
        gr.download(ll)
