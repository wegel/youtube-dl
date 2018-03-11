from __future__ import unicode_literals

import itertools
import re
import urlparse

from .common import SearchInfoExtractor


class GoogleSearchIE(SearchInfoExtractor):
    IE_DESC = 'Google Video search'
    _MAX_RESULTS = 1000
    IE_NAME = 'video.google:search'
    _SEARCH_KEY = 'gvsearch'
    _TEST = {
        'url': 'gvsearch15:python language',
        'info_dict': {
            'id': 'python language',
            'title': 'python language',
        },
        'playlist_count': 15,
    }

    def get_query_dict(self, query, pagenum):
        if query.startswith("q="):
            q = dict(urlparse.parse_qsl(query))
            q['start'] =  pagenum * 10
        else:
            q = {
                    'tbm': 'vid',
                    'q': query,
                    'start': pagenum * 10,
                    'hl': 'en',
                }
        return q

    def _get_n_results(self, query, n):
        """Get a specified number of results for a query"""

        entries = []
        res = {
            '_type': 'playlist',
            'id': query,
            'title': query,
        }

        for pagenum in itertools.count():
            webpage = self._download_webpage(
                'http://www.google.com/search',
                'gvsearch:' + query,
                note='Downloading result page %s' % (pagenum + 1),
                query=self.get_query_dict(query, pagenum))

            for hit_idx, mobj in enumerate(re.finditer(
                    r'<h3 class="r"><a href="([^"]+)"', webpage)):

                # Skip playlists
                if not re.search(r'id="vidthumb%d"' % (hit_idx + 1), webpage):
                    continue

                entries.append({
                    '_type': 'url',
                    'url': mobj.group(1)
                })

            if (len(entries) >= n) or not re.search(r'id="pnnext"', webpage):
                res['entries'] = entries[:n]
                return res
