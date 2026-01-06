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
#  Copyright (C) 2022 2024 2025, Andrew McConachie, <andrew.mcconachie@icann.org>

import argparse
import basic
import datetime as dd
import ham_group
import html_group
import os
import stat
import xml.etree.ElementTree as ET
import uuid

ham = {}
ham['dl_log'] = '/home/smutt/log/fetch_ham.log'
ham['atom_xml'] = '/home/smutt/www/icannhaz.org/feed.xml'
ham['link_base'] = 'https://icannhaz.org/ham'
ham['base_dir'] = ham_group.Ham_group.base_dir
ham['print_pos'] = 3
html = {}
html['dl_log'] = '/home/smutt/log/fetch_html.log'
html['atom_xml'] = '/home/smutt/www/icannhaz.org/feed_html.xml'
html['link_base'] = 'https://'
html['base_dir'] = 'https://'
html['print_pos'] = 2
conf = [ham, html]

atom_lastrun = '/home/smutt/log/atom_feed.lastrun'
atom_ns = 'http://www.w3.org/2005/Atom'

# Takes a log filename to read and a minimum timestamp
# Returns list of new entry lists ==> [timestamp, remote, local]
def get_files(fname, min_ts, base_dir):
  # Returns a 4 tuple (ts, help_text, remote, local) (new)
  def parse_line(line, base_dir):
      toks = line.split('||')
      if len(toks) == 4:
        return (toks[0].strip(), toks[1].strip(), toks[2].strip(), toks[3].strip())
      else:
        return (None, None, None, None)

  rv = []
  with open(fname) as fh:
    for line in fh:
      ts, group, remote, local = parse_line(line.strip(), base_dir)

      if ts == None:
        continue

      try:
        f_ts = dd.datetime.fromisoformat(ts)
      except:
        basic.logit('err: Invalid date encountered in logfile')
        continue

      if os.path.exists(local):
        if min_ts <= f_ts:
          rv.append([ts, group, remote, local.replace("%", "%25")])
  return rv

###################
# BEGIN EXECUTION #
###################
ap = argparse.ArgumentParser(description='Update atom feeds with new documents found.')
ap.add_argument('-l', '--lastrun', action='store', type=str, help='Use passed lastrun. Do not read or write lastrun from file.')
ap.add_argument('-d', '--debug', action='store_true', help='Print links to STDOUT. Do not write feed. Do not write lastrun.')
ARGS = ap.parse_args()

if ARGS.lastrun:
  try:
    last_run = dd.datetime.fromisoformat(ARGS.lastrun)
  except:
    basic.logit('Bad --lastrun')
    exit(1)

else:
  last_run = None
  with open(atom_lastrun) as fh:
    for line in fh:
      last_run = dd.datetime.fromisoformat(line.strip())

  if last_run == None:
    basic.logit('err: Unable to determine lastrun time')
    exit(1)
  else:
    fp = open(atom_lastrun, 'w')
    fp.write(basic.timestamp())
    fp.close()

for cc in conf:
  new_files = get_files(cc['dl_log'], last_run, cc['base_dir'])
  if len(new_files) == 0:
    continue

  tree = ET.parse(cc['atom_xml'])
  ET.register_namespace('', atom_ns)
  tree.find('./{' + atom_ns + '}updated').text = basic.timestamp() + 'Z'

  for nf in new_files:
    title = '[' + nf[1] + '] ' + os.path.basename(nf[cc['print_pos']])
    UID = str(uuid.uuid5(uuid.NAMESPACE_URL, title)) # uuid.RFC_4122 is broken

    new_entry = "<entry> \
      \n  <title>" + title + "</title> \
      \n  <link href=\"" + cc['link_base'] + "/" + nf[cc['print_pos']].split(cc['base_dir'])[1] + "\"/> \
      \n  <id>urn:uuid:" + UID + "</id> \
      \n  <updated>" + basic.timestamp() + 'Z' + "</updated> \
      \n  <summary/> \
      \n</entry>"
    tree.find('.').append(ET.fromstring(new_entry))
    if ARGS.debug:
      print(ET.tostring(ET.fromstring(new_entry), encoding='unicode'))

  if ARGS.debug:
    continue

  ET.indent(tree)
  tree.write(cc['atom_xml'], xml_declaration=True, encoding='UTF-8')
