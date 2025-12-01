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

import basic
import multiprocessing.pool
import os
import stat
import re
import requests
from bs4 import BeautifulSoup
from urllib3 import util as Util
from datetime import datetime, date

# Grab links in tags matching regex
# URI => the URI to grab and parse
# regex => regex for matching the links
# tags => a list of [html_tag, attribute] to match regex against
# excludes => a list of compiled regex of links to ignore
# Returns deduplicated list of links
def get_links(URI, regex, tags, excludes):
  links = []
  url_t = Util.parse_url(URI)

  try:
    req = requests.get(URI)
  except requests.RequestException:
    basic.logit("err:req_exception:" + URI)
    return []

  if req.status_code == 200:
    soup = BeautifulSoup(req.text, 'html.parser')
    for tag in soup.find_all(tags[0]):
      link = tag.get(tags[1])
      if link is None:
        continue
      if not is_excluded(excludes, link):
        for reg in regex:
          if reg.match(link):
            link = link.split('?')[0] # Strip any trailing garbage
            if Util.parse_url(link).host is None:
              links.append(url_t.scheme + '://' + url_t.host + link)
            elif len(Util.parse_url(link).host) < len('icann.org'): # Relative path missing leading /
              links.append(url_t.scheme + '://' + url_t.host + '/' + link)
            else:
              links.append(link)
  return list(dict.fromkeys(links))

'''
# Grab a file and write to disk
# Takes a remote URI and a local filename
def download(uri, fname):
  if os.path.exists(fname):
    return

  try:
    req = requests.get(uri, stream=True)
    if req.status_code == 200:
      with open(fname, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
          if chunk: # filter out keep-alive new chunks
            f.write(chunk)
      os.chmod(fname, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) # 0644
      basic.logit(uri + ' ' + fname)
    else:
      basic.logit("err:dl_bad_response:" + uri)
  except requests.RequestException:
    basic.logit("err:dl_req_exception:" + uri)
'''

# Return dict of files existing locally on disk under (path)
# Whitespaces in files are escaped with %20
# path => a UNIX path 
def local_files(path):
  rv = {}
  for _, _, files in os.walk(path):
    for ff in files:
      rv[ff.strip()] = True
  return rv

# Determine remote filename to compare to local_files
# Takes a string URL
# Returns a string filename
def remote_file(URL):
  return Util.parse_url(URL).path.split('/')[-1]

# Should we exclude passed link
# excludes => a list of compiled regexps to test
# s => string to match against
def is_excluded(excludes, s):
  for pattern in excludes:
    if pattern.match(s):
      return True
  return False

# Takes a list of URIs
# Returns a new list with the real redirected URIs
# The icann.org webserver hangs forever if you send it an HTTP HEAD request, it's intentionally unimplemented
def real_locations(URIs):
  def get_location(URI):
    try:
      req = requests.get(URI, allow_redirects=True, timeout=2)
    except requests.RequestException:
      basic.logit("err:rf:req_exception:" + URI)
      return

    url_t = Util.parse_url(URI)
    if len(req.history) > 0:
      if 'location' in req.history[-1].headers:
        location = req.history[-1].headers['location']
        if len(location.strip()) > 0:
          if location.startswith('http'):
            return location.strip()
          else:
            return url_t.scheme + '://' + url_t.host + location

  mpool = multiprocessing.pool.ThreadPool(processes=max(1, int(len(URIs)/3)))
  return [URI for URI in mpool.map(get_location, URIs) if URI != None]
