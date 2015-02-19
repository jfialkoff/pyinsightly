import datetime
import logging
import re
from base64 import b64encode
from urllib.parse import urlencode

import requests

try:
    import pytz
except ImportError:
    pytz = None

class UTC(datetime.tzinfo):
    """
    UTC implementation taken from Python's docs.

    Used only when pytz isn't available.
    """

    def __repr__(self):
        return "<UTC>"

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = pytz.utc if pytz else UTC()

class Insightly(object):
    BASE_URL = 'https://api.insight.ly/v2.1'
    OPERATORS = ('gt', 'eq', 'lt', 'gte', 'lte')

    def __init__(self, api_key, debug=False):
        self.api_key = api_key

        if debug:
            # These two lines enable debugging at httplib level
            # (requests->urllib3->http.client).
            # You will see the REQUEST, including HEADERS and DATA, and
            # RESPONSE with HEADERS but without DATA.
            # The only thing missing will be the response.body which is not
            # logged.
            try:
                import http.client as http_client
            except ImportError:
                # Python 2
                import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1

            # You must initialize logging, otherwise you'll not see debug output.
            logging.basicConfig() 
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    def _get_headers(self):
        return {'Authorization': b'Basic ' + b64encode(self.api_key.encode()),
                'Content-Type': 'application/json'}

    def _construct_url(self, obj_type, obj_id=None, parents=None):
        # Base URL - account for parents
        url = self.BASE_URL
        parents = parents or ()
        for parent in parents:
            url += '/%s/%d' % parent
        url += '/%s' % obj_type
        if obj_id:
            url += '/%s' % str(obj_id)

        print(url)
        return url

    def add(self, object_type, data, **kwargs):
        url = self._construct_url(object_type, **kwargs)
        resp = requests.post(url, json=data, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def get(self, object_type, obj_id, **kwargs):
        url = self._construct_url(object_type, obj_id, **kwargs)
        resp = requests.get(url, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def delete(self, object_type, obj_id, **kwargs):
        url = self._construct_url(object_type, obj_id, **kwargs)
        resp = requests.delete(url, headers=self._get_headers())
        resp.raise_for_status()
        return

    def list(self, object_type, parents=None, order_by=None, top=None,
             skip=None, **filters):

        # Filters
        _filters = filters
        filters = []
        params = {}
        for key, val in _filters.items():
            match = re.match(r'^(.*)__(.*)$', key)
            op = 'eq'
            if match:
                key = match.group(1)
                op = match.group(2)
                if op not in self.OPERATORS:
                    raise ValueError(
                        "'%s' is not a supported operator for this library."
                        % op)
            if isinstance(val, datetime.datetime):
                val = val.isoformat().split('.')[0]
                val = "DateTime'%s'" % val
            elif isinstance(val, datetime.date):
                val = "Date'%s'" % val.isoformat()
            else:
                val = str(val).replace("'", "''")
                val = "'%s'" % val
            filters.append('%s %s %s' % (key, op, val))


        if filters:
            params['$filter'] = ' and '.join(filters)

        # Order by
        _order_bys = order_by or ()
        if isinstance(_order_bys, str):
            _order_bys = (order_bys,)
        order_bys = []
        for order_by in _order_bys:
            desc = False
            if order_by.startswith('-'):
                order_by = order_by[1:]
                desc = True
            order_bys.append('%s%s' % (order_by, ' desc' if desc else ''))
        if order_bys:
            params['$orderby'] = ','.join(order_bys)

        # Paging
        if top:
            params['$top'] = top
        if skip:
            params['$skip'] = skip
        print(params)

        url = self._construct_url(object_type, parents=parents)
        resp = requests.get(url, params=params, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def update(self, object_type, obj_id, data):
        data['ORGANISATION_ID'] = obj_id
        url = self._construct_url(object_type)
        resp = requests.put(url, json=data, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def test(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        name = 'pyinsightly test'

        # Get an empty list based on name and creation date
        res = self.list('organisations', DATE_CREATED_UTC__gt=now,
                                         ORGANISATION_NAME=name)
        if len(res) != 0:
            raise AssertionError("Expected no results.")

        # Try to create an org
        res = self.add('organisations', {'ORGANISATION_NAME': name})
        org_id = res['ORGANISATION_ID']


        # Find that org using list
        res = self.list('organisations', DATE_CREATED_UTC__gt=now,
                                         ORGANISATION_NAME=name)
        if len(res) != 1:
            raise AssertionError("Expected 1 result")

        # Update the org and confirm its name changed.
        new_name = '%s CHANGED' % name
        res = self.update('organisations', org_id,
                          {'ORGANISATION_NAME': new_name})
        res = self.get('organisations', org_id)
        if res['ORGANISATION_NAME'] != new_name:
            raise AssertionError("Expected organization name to be '%s'." %
                                 new_name)

        # Test order by
        res = self.list('organisations', order_by=('-DATE_CREATED_UTC',), top=5)
        if len(res) > 5 or len(res) < 1:
            raise AssertionError("Expected at least 1 result and fewer than 5. "
                                 "Got %d." % len(res))
        if res[0]['ORGANISATION_ID'] != org_id:
            raise AssertionError(
                "Expected test org as top org in response but got %s instead."
                % res[0]['ORGANISATION_NAME'])

        # Test delete
        self.delete('organisations', org_id)

        print("Tests passed.")
