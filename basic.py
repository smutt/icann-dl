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

import datetime as dd

# Return the kind of timestamp we like
# Optionally takes a string in ISO format
def timestamp(ts=None):
  if ts == None:
    return dd.datetime.now(dd.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds')
  return dd.datetime.fromisoformat(ts).replace(tzinfo=None).isoformat(timespec='seconds')
  
# Log string (s) to stdout with timestamp
def logit(s):
  print(timestamp() + ' ' + s.strip())
