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
import stat
import feedgenerator as fg
from datetime import datetime, date

dl_log = '/home/smutt/log/icann-dl.log'
rss_lastrun = '/home/smutt/log/rss_feed.lastrun'
rss_items = '/home/smutt/log/rss_feed.items'
rss_xml = '/var/www/htdocs/icann-pdf.depht.com/rss.xml'

# Basic logging to stdout
def logit(s):
  print(datetime.isoformat(datetime.utcnow()) + ' ' + s.strip())

# Returns dict of file dicts ==> local_name = {ts, remote_name}
def get_files(fname):
  rv = {}
  with open(fname) as fh:
    for line in fh:
      line = line.strip()
      if len(line) == 0:
        continue
      toks = line.split()
      if len(toks) < 3:
        continue
      if os.path.exists(toks[2]):
        rv[toks[2]] = {'ts': toks[0], 'remote': toks[1]}
  return rv

###################
# BEGIN EXECUTION #
###################

last_run = None
with open(rss_lastrun) as fh:
  for line in fh:
   last_run = datetime.fromisoformat(line.strip())

if last_run == None:
  logit('err: Unable to determine lastrun time')
  exit(1)

old_files = get_files(rss_items)
new_files = get_files(dl_log)
for k,v in new_files.items(): # Unionize them
  old_files[k] = v

fh = open(rss_items, 'w')
for k,v in old_files.items():
  fh.write(v['ts'] + ' ' + v['remote'] + ' ' + k + '\n')
fh.close()

feed = fg.Rss201rev2Feed(
  title = u"ICANN Publications",
  link = u"https://icann-pdf.depht.com/pub",
  description = u"New ICANN Publications as they are discovered from icann.org.",
  language = u"en"
)

for k,v in old_files.items():
  fname = os.path.basename(k)
  feed.add_item(
    title = fname,
    link = "https://icann-pdf.depht.com/pub/" + k.split("pub/")[1],
    description = fname
  )

fp = open(rss_xml, 'w')
feed.write(fp, 'utf-8')
fp.close()
