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
import subprocess
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
    self.help_text = '' # Help text displayed with the group. Intended to be overridden.
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
      funk.logit(url + ' ' + out_path)

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

# ICANN Board Resolutions
class Board(Html_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ICANN Board Resolutions'
    self.uri = 'https://www.icann.org/en/board-activities-and-meetings?start-date=01-01-2024&end-date=31-12-2024&document-types=approved-resolutions&expand-all=true'
    self.path = 'icann/board/resolutions'
    self.regex.append(re.compile('.*/materials/approved-resolutions-.*'))

# All our groups
groups = {}
groups['board_res'] = Board()
