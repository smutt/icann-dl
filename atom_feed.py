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
import xml.etree.ElementTree as ET
from datetime import datetime, date
import uuid

dl_log = '/home/smutt/log/fetch.log'
atom_lastrun = '/home/smutt/log/atom_feed.lastrun'
atom_xml = '/home/smutt/www/icann-hamster.nl/feed.xml'
atom_ns = 'http://www.w3.org/2005/Atom'
link_base = 'https://icann-hamster.nl/ham'

# Basic logging to stdout
def logit(s):
  print(datetime.isoformat(datetime.utcnow()) + ' ' + s.strip())

# Takes a log filename to read and a minimum timestamp
# Returns dict of file dicts ==> local_name = {ts, remote_name}
def get_files(fname, min_ts):
  rv = {}
  with open(fname) as fh:
    for line in fh:
      line = line.strip()
      if len(line) == 0:
        continue

      toks = line.split()
      if len(toks) < 3:
        continue
      try:
        f_ts = datetime.fromisoformat(toks[0])
      except:
        continue
      if os.path.exists(toks[2]):
        if min_ts <= f_ts:
          rv[toks[2]] = {'ts': toks[0], 'remote': toks[1]}
  return rv

###################
# BEGIN EXECUTION #
###################

last_run = None
with open(atom_lastrun) as fh:
  for line in fh:
   last_run = datetime.fromisoformat(line.strip())

if last_run == None:
  logit('err: Unable to determine lastrun time')
  exit(1)

fp = open(atom_lastrun, 'w')
fp.write(datetime.utcnow().isoformat(timespec='seconds'))
fp.close()

new_files = get_files(dl_log, last_run)
if len(new_files) == 0:
  exit(0)

tree = ET.parse(atom_xml)
ET.register_namespace('', atom_ns)
tree.find('./{' + atom_ns + '}updated').text = datetime.utcnow().isoformat(timespec='seconds') + 'Z'

for k,v in new_files.items():
  fname = os.path.basename(k)
  UID = str(uuid.uuid5(uuid.NAMESPACE_URL, fname)) # uuid.RFC_4122 is broken

  new_entry = "<entry>\n<title>" + fname + "</title> \
    <link href=\"" + link_base + k.split("pub/")[1] + "\"/> \
    <id>urn:uuid:" + UID + "</id> \
    <updated>" + datetime.utcnow().isoformat(timespec='seconds') + 'Z' + "</updated> \
    <summary/></entry>"
    #<updated>" + datetime.fromisoformat(v['ts']).isoformat(timespec='seconds') + "Z</updated> \
    #<summary>" + "<a href=\"" + v['remote'] + "\">" + fname + "</a></summary></entry>"

  tree.find('.').append(ET.fromstring(new_entry))

ET.indent(tree)
tree.write(atom_xml, xml_declaration=True, encoding='UTF-8')
