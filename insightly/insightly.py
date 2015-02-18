from base64 import b64encode
import re
import datetime
class Insightly(object):
    BASE_URL = 'https://api.insight.ly/v2.1/'
    OPERATORS = ('gt', 'eq', 'lt', 'gte', 'lte')

    def __init__(self, api_key):
        self.api_key = api_key

    def _get_headers(self):
        return {'Authorization': b'Basic ' + b64encode(api_key.encode()),
                'Content-Type': 'application/json'}

    def _construct_url(self, obj_type, parents=None, order_by=None,
                       obj_id=None, **filters):

        # Base URL - account for parents
        url = self.BASE_URL
        parents = parents or ()
        for parent in parents:
            url += '%s/%d' % parent
        url += '/%s' % obj_type
        if obj_id:
            url += '/%s' % str(obj_id)

        # Filters
        _filters = filters
        filters = []
        params = []
        for key, val in _filters.items():
            match = re.match(r'^.*__(.*)$', key)
            op = 'eq'
            if match:
                op = match.groups(1)
                if op not in self.OPERATORS:
                    raise ValueError(
                        "%s is not a supported operator for this library."
                        % op)
            if instance(val, datetime.datetime):
                val = val.isoformat().split('.')[0]
                val = "DateTime'%s'" % val
            elif instance(val, datetime.date):
                val = "Date'%s'" % val.isoformat()
            else:
                val = str(val).replace("'", "''")
                val = "'%s'" % val
            filters.append('%s %s %s' % (key, op, val))


        if filters:
            filters = ' and '.join(filters)
            params.append('$filter=%s' % filters)

        # Order by
        _order_bys = order_by or ()
        order_bys = []
        for order_by in _order_bys:
            desc = False
            if order_by.startswith('-'):
                order_by = order_by[1:]
                desc = True
            order_bys.append('%s%s' % (order_by, ' DESC' if desc else ''))
        if order_bys:
            order_bys = ','.join(order_bys)
            params.append('$orderby=%s' % order_bys)

        if params:
            url += '?%s' % '&'.join(params)

    def add(self, object_type, 
    def get(self, obj_type, obj_id):
        url = BASE_URL + obj_type + '/%d' % obj_id
        resp = requests.get(url, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def filter(self, object_type, **kwargs):
        url = '%s%s?%s' % (self.BASE_URL, object_type, filters)
        resp = requests.get(url, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

