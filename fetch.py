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
#  Copyright (C) 2022, 2024 Andrew McConachie, <andrew.mcconachie@icann.org>

import argparse
import ham_group
import html_group
import multiprocessing.pool
from urllib import parse as Url_parse

# Processes a single group
def process_group(gr):
  local_files = gr.local_files()
  for ll in gr.get_links():
    remote_file = gr.remote_file(ll)
    if remote_file not in local_files and Url_parse.unquote(remote_file) not in local_files \
      and gr.clean_filename(remote_file) not in local_files:
      if ARGS.debug:
        print(ll)
      else:
        gr.download(ll)
    else:
      if ARGS.debug:
        print('Skipping ' + ll)


###################
# BEGIN EXECUTION #
###################
ap = argparse.ArgumentParser(description='Fetch stuff from icann.org. By default fetches all groups in set.')
ap.add_argument(dest='group_set', choices=['ham', 'html'], help='Set of groups to use')
ap.add_argument('-d', '--debug', action='store_true', help='Fetch nothing. Instead print what URLs would be fetched')
ap.add_argument('-e', '--exclude', type=str, action='store', default=None,
                help='Fetch all groups except excluded group')
ap.add_argument('-g', '--group', type=str, action='store', default='all',
                help='Fetch single group then exit')
ap.add_argument('-l', '--list', dest='group_list', action='store_true', help='List groups in set then exit')
ap.add_argument('-u', '--url', type=str, action='store', help='Use passed start URL for group. Requires --group.')
ARGS = ap.parse_args()

if ARGS.group_set == 'ham':
  group_set = ham_group
elif ARGS.group_set == 'html':
  group_set = html_group
else:
  print('Invalid group set')
  exit(1)

if ARGS.group_list:
  for gr in group_set.groups.keys():
    if len(gr) > 7: # tab_len
      print(gr + '\t || ' + group_set.groups[gr].help_text)
    else:
      print(gr + '\t\t || ' + group_set.groups[gr].help_text)
  exit(0)

if ARGS.exclude != None:
  if ARGS.exclude not in group_set.groups:
    print('Invalid group')
    exit(1)
  del group_set.groups[ARGS.exclude]

if ARGS.group != 'all':
  if ARGS.group not in group_set.groups:
    print('Invalid group')
    exit(1)

if ARGS.url:
  if ARGS.group == 'all':
    print("--url requires --group")
    exit(1)
  if ARGS.group not in group_set.groups:
    print("group not found")
    exit(1)
  group_set.groups[ARGS.group].uri = ARGS.url

async_groups = []
for key,gr in group_set.groups.items():
  if ARGS.group != 'all' and ARGS.group != key:
    continue

  if ARGS.group == 'all' and not gr.enabled: # Skip disabled groups unless --group is passed
    continue

  if gr.async_safe:
    async_groups.append(gr)
    continue

  process_group(gr)

mpool = multiprocessing.pool.ThreadPool(processes=int(len(async_groups)/3))
mpool.map(process_group, async_groups)
