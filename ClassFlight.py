class Flight:
    def __init__(self, basedata):
        self.base_data = [basedata['airline'], basedata['number'], basedata['depAirport'], basedata['arrAirport']]
        self.dep_time = self.date_to_dict(basedata['scheduledDepDateTime'])
        self.upd_time = self.date_to_dict(basedata['lastUpdate'])


    '2018-01-27  18:00:00.000-04:00'
    def date_to_dict(self, s):
        for c in ('T', '+', '.', ':'):
            s = s.replace(c,'-')
        s = s.split('-')
        utc = s[7] if len(s) > 7 else 0
        return {'year': s[0], 'month': s[1], 'day': s[2], 'hour': s[3], 'minute': s[4], 'utc': utc}

    def dict_to_date(self, d, timezone='utc'):
        if timezone == 'local':
            d['hour'] = d['hour'] + d['utc']
        return '{year}-{month}-{day} {hour}:{minute} + {utc}:00'.format(**d)

    def add_full_info(self, fl):
        if fl['success'] == False:
            self.error = fl['errorMessage']
        else:
            self.error = None
            self.upd_time = self.date_to_dict(fl['lastUpdate'])
            self.notes = fl['flightNotes']
            self.forms = fl['forms']
            self.crew_list = fl['crewList']
            self.passengers = fl['passengers']

    def show_base_info(self):
        departure = self.dict_to_date(self.dep_time)
        update = self.dict_to_date(self.upd_time)
        return '{0:>8}{1:>11}{2:>13}{3:>13}{4:>34}{5:>25}'.format(*self.base_data, departure, update)

    def to_csv_str(self):
        departure = self.dict_to_date(self.dep_time)
        update = self.dict_to_date(self.upd_time)
        return '{0}{1}{2}{3}{4}{5}'.format(*self.base_data, departure, update)