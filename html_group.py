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
#  Copyright (C) 2024 Andrew McConachie, <andrew.mcconachie@icann.org>

import funk
import re
import os
import stat
import argparse
import subprocess
from urllib import parse as Url_parse
from urllib3 import util as Util
from bs4 import BeautifulSoup

# Generic exception class for anything monolith related
class MonolithException(Exception):
  pass

class Html_group():
  base_dir = '/var/www/htdocs/icann-hamster.nl/html/' # Where the local fun starts
  staging_dir = '/home/smutt/staging/html/' # Temporary storage after download
  mono_bin = '/home/smutt/bin/monolith' # monolith binary
  html_suffix = '_archive.html' # Local ending for downloaded HTML

  def __init__(self):
    self.enabled = True
    self.regex = [] # Compiled regex to match to download
    self.exclude = [] # Compiled regex to exclude for all groups
    return

  # Wrapper for funk.get_links()
  def get_links(self):
    return funk.get_links(self.uri, self.regex, ['a', 'href'], self.exclude)

  # Wrapper for funk.local_files()
  def local_files(self):
    return [ff.rstrip(self.html_suffix) for ff in funk.local_files(self.base_dir + self.path)]

  # Converts remote filename to local equivalant
  def convert_filename(self, url):
    if url.endswith(".html") or url.endswith(".htm"):
      return url.split('/')[-1].rsplit('.', maxsplit=1)[0] + self.html_suffix
    else:
      return url.split('/')[-1] + self.html_suffix

  # Season the soup
  def stamp_file(self, url):
    f_in = self.staging_dir + self.path + '/' + self.convert_filename(url) 
    f_out = self.base_dir + self.path + '/' + self.convert_filename(url)
    with open(f_in, 'r') as pot:
      with open(f_out, 'w') as bowl:
        soup = BeautifulSoup(pot, 'html.parser')
        soup.body.insert(0, "<a href=\"" + url + "\">Original page on icann.org</a>")
        bowl.write(soup.prettify(formatter=None))
    os.chmod(f_out, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) # 0644 
    os.remove(f_in)

  # Wrapper for _html_download()
  def download(self, url):
    try:
      self._html_download(url, self.staging_dir + self.path + '/')
    except MonolithException:
      funk.logit("download failed: " + url)
      return
    self.stamp_file(url)

  # Call external program to download and save remote HTML to dest_dir
  def _html_download(self, url, dest_dir):
    out_path = dest_dir + self.convert_filename(url)
    cmd = self.mono_bin + " --no-video --no-images --no-audio --no-js --no-fonts -o " + out_path + " " + url
    try:
      proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
      proc.wait(timeout=120) # Give up after 2 minutes

    except subprocess.TimeoutExpired as e:
      funk.logit("_html_download: subprocess TimeoutExpired" + str(e))
      raise MonolithException
    except subprocess.CalledProcessError as e:
      funk.logit("_html_download: subprocess CallProcessError" + str(e))
      raise MonolithException
    except OSError as e:
      funk.logit("_html_download: subprocess OSError" + str(e))
      raise MonolithException
    except subprocess.SubprocessError:
      funk.logit("_html_download: general subprocess error")
      raise MonolithException

class Board(Html_group):
  # 6 March 2004 is the first available resolutions page
  # https://www.icann.org/en/board-activities-and-meetings?board-meeting-type=regular&board-meeting-type=special&board-meeting-type=organizational&board-meeting-type=workshops&start-date=01-01-2004&end-date=01-01-2005&document-types=approved-resolutions&expand-all=true

  def __init__(self):
    super().__init__()
    self.uri = 'https://www.icann.org/en/board-activities-and-meetings?board-meeting-type=regular&board-meeting-type=special&board-meeting-type=organizational&board-meeting-type=workshops&start-date=01-01-2004&end-date=01-01-2005&document-types=approved-resolutions&expand-all=true'
    self.path = 'icann/board/resolutions'
    self.regex.append(re.compile('.*/materials/approved-resolutions-.*'))


###################
# BEGIN EXECUTION #
###################
# All our groups
groups = {}
groups['board-resolutions'] = Board()

ap = argparse.ArgumentParser(description='Fetch content from icann.org.')
ap.add_argument('-d', '--debug', action='store_true', help='Fetch nothing. Instead print what URLs would be fetched.')
ap.add_argument('-e', '--exclude', type=str, action='store', default=None,
                choices=groups.keys(), help='Fetch all groups except excluded group.')
ap.add_argument('-g', '--group', type=str, action='store', default='all',
                choices=groups.keys(), help='Fetch single group then exit.')
ap.add_argument('-u', '--url', type=str, action='store', help='Use passed start URL for group. Requires --group.')
ARGS = ap.parse_args()

if ARGS.url:
  if not ARGS.group:
    print("--url requires --group")
    exit(1)

  if ARGS.group not in groups:
    print("group not found")
    exit(1)

  groups[ARGS.group].uri = ARGS.url


if ARGS.exclude != None:
  del groups[ARGS.exclude]

for key,gr in groups.items():
  if ARGS.group != 'all' and ARGS.group != key:
    continue

  if ARGS.group == 'all' and not gr.enabled: # Skip disabled groups unless --group is passed
    continue

  local_files = gr.local_files()
  for ll in gr.get_links():
    remote_file = Util.parse_url(ll).path.split('/')[-1].rsplit('.', maxsplit=1)[0] # Strip remote dir and dot suffix
    if remote_file not in local_files:
      if ARGS.debug:
        print(ll)
      else:
        gr.download(ll)
    else:
      if ARGS.debug:
        print('Skipping ' + ll)
