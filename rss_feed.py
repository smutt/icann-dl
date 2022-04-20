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

import feedgenerator as fg

base_dir = '/var/www/htdocs/icann-pdf.depht.com/'

feed = fg.Rss201rev2Feed(
  title=u"ICANN Publications",
  link=u"https://icann-pdf.depht.com/pub",
  description=u"New ICANN Publications as they are discovered from icann.org.",
  language=u"en",
)
feed.add_item(title="Hello", link=u"https://icann-pdf.depht.com/pub/ssac/sac-038-en.pdf", description="A stuff")
fp = open(base_dir + 'rss.xml', 'w')
feed.write(fp, 'utf-8')
fp.close()
