from . import session
import json

class LVStat(object):
    """ Version 0.1.1 """
    def __init__(self, lang, *args):
        self.ids = list(args)
        self.url = 'https://data.stat.gov.lv/api/v1/{}/OSP_PUB/'.format(lang)
        self.url_out = 'https://data.stat.gov.lv/pxweb/{}/OSP_PUB/START__'.format(lang)
        self.query = {"query": [], 
                      "response": {"format": "json"}
                      }
        self._info = None

    def info(self):
        """ Returns the metadata associated with the current folder. """
        if not self._info:
            response = session.get(self.url + '/'.join(self.ids))
            self._info = response.json()
        return self._info

    def go_down(self, *args):
        """ Goes deeper in the hierarchical metadata structure. """
        self.ids += list(args)
        self._info = None

    def go_up(self, k=1):
        """ Goes k levels up in the hierarchical metadata structure. """
        self.ids = self.ids[:-k]
        self._info = None

    def get_url(self):
        """ Returns the url to the current folder. """
        if len(self.ids[-1]) >= 3:
            try:
                int(self.ids[-1][3])
            except ValueError:
                return self.url_out + '__'.join(self.ids[:-1]) + '/' + self.ids[-1]
        return self.url_out + '__'.join(self.ids)

    def get_variables(self, values=True):
        """ Returns a dictionary of variables and their ranges for the bottom node. 
        
        :param values specifies whether the variables will be returned by code value (default) or by text value."""
        response = self.info()
        val_dict = {}
        try:
            variables = response['variables']
        except TypeError:
            print("Error: You are not in a leaf node.")
            return
        for item in variables:
            val_dict[item['code']] = item['values']\
                if values else item['valueTexts']
        return val_dict

    def clear_query(self):
        """ Clears the query. Mostly an internal function to use in others. """
        self.query = {"query": [], 
                      "response": {"format": "json"}
                      }

    def set_query(self, **kwargs):
        """ Forms a query from input arguments. """
        self.clear_query()
        response = self.info()
        variables = response['variables']
        for kwarg in kwargs:
            for var in variables:
                if var["code"] == kwarg:
                    self.query["query"].append({
                            "code": var['code'],
                            "selection": {
                                    "filter": "item",
                                    "values": [var['values'][j] for j in \
                                                range(len(var['values'])) if \
                                                var['values'][j] in \
                                                kwargs[kwarg]]
                                    }
                                })

    def get_query(self):
        """ Returns the current query. """
        return self.query

    def get_data(self):
        """ Returns the data from the constructed query. """
        response = session.post(self.url + '/'.join(self.ids), json = self.query)
        response_json = json.loads(response.content.decode('utf-8-sig'))
        return response_json
