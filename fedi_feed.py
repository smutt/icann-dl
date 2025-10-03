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
#  Copyright (C) 2025, Andrew McConachie, <andrew.mcconachie@icann.org>

import argparse
import basic
import datetime as dd
import ham_group
import html_group
import os
import stat

ham = {}
ham['dl_log'] = '/home/smutt/log/fetch_ham.log'
ham['base_dir'] = ham_group.Ham_group.base_dir
ham['desc'] = 'file'
html = {}
html['dl_log'] = '/home/smutt/log/fetch_html.log'
html['base_dir'] = html_group.Html_group.base_dir
html['desc'] = 'html'
conf = [ham, html]

fedi_lastrun = '/home/smutt/log/fedi_feed.lastrun'

# Takes a log filename to read and a minimum timestamp
# Returns dict of file dicts ==> local_name = {ts, remote_name}
def get_files(fname, min_ts, base_dir):
  def parse_line(line, base_dir): # Returns a 3 tuple (ts, remote, local)
    toks = line.split()
    if len(toks) == 3:
      return (toks[0], toks[1], toks[2])
    elif len(toks) < 3:
      return (None, None, None)
    else:
      start = len(toks[0])
      end = line.find(base_dir)
      return (toks[0], line[start:end].strip(), line[end:].strip())

  rv = {}
  with open(fname) as fh:
    for line in fh:
      ts, remote, local = parse_line(line.strip(), base_dir)
      if ts == None:
        continue

      try:
        f_ts = dd.datetime.fromisoformat(ts)
      except:
        continue

      if os.path.exists(local):
        if min_ts <= f_ts:
          rv[local.replace("%", "%25")] = {'ts': ts, 'remote': remote}
  return rv

###################
# BEGIN EXECUTION #
###################
ap = argparse.ArgumentParser(description='Update the fediverse feed with new documents found.')
ap.add_argument('-l', '--lastrun', action='store', type=str, help='Use passed lastrun. Do not read or write lastrun from file.')
ap.add_argument('-d', '--debug', action='store_true', help='Print links to STDOUT. Do not write feed. Do not write lastrun.')
ARGS = ap.parse_args()

if ARGS.lastrun:
  try:
    last_run = dd.datetime.fromisoformat(ARGS.lastrun)
  except:
    print('Bad --lastrun')
    exit(1)

else:
  last_run = None
  with open(fedi_lastrun) as fh:
    for line in fh:
      last_run = dd.datetime.fromisoformat(line.strip())

  if last_run == None:
    basic.logit('err: Unable to determine lastrun time')
    exit(1)
  else:
    pass
    #fp = open(fedi_lastrun, 'w')
    #fp.write(basic.timestamp())
    #fp.close()

for cc in conf:
  new_files = get_files(cc['dl_log'], last_run, cc['base_dir'])
  if len(new_files) == 0:
    continue

  if ARGS.debug:
    for key,val in new_files.items():
      print(basic.timestamp(val['ts']) + ' :: ' + key + ' :: ' + val['remote'])
    continue

  for key,val in new_files.items():
    print(val['remote'] + " [" + cc['desc'] + "][" + basic.timestamp(val['ts']).split('T')[0] + "]")

