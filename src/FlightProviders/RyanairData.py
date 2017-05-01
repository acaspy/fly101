import json
import os
import sys
import urllib2
import pprint
from Utils import GeoUtils
from Utils import CurrencyConvertor

reload(sys)
sys.setdefaultencoding('utf-8')


class RyanairData:

    RYANAIR_API_VER = "3"
    CARRIER = "ryanair"

    def __init__(self):
        self._geo_utils = GeoUtils.GeoUtils()

    def get_month_data(self, departure, arrival, month, year, target_currency='EUR'):
        departure = departure.upper()
        arrival = arrival.upper()
        if len(month) == 1:
            month = "0"+str(month)
        c = None
        _date = str(year)+"-"+str(month)+"-"+"01"
        # _header = ('#departureCode',
        #            'ArrivalCode',
        #            'origPrice',
        #            'currencyCode',
        #            'targetPrice',
        #            'targetCurrencyCode',
        #            'carrier')
        _header = ('#departureCode',
                   'ArrivalCode',
                   'date',
                   'departureTime',
                   'arrivalTime'
                   'targetPrice',
                   'flightNumber',
                   'carrier')
        query = "https://api.ryanair.com/farefinder/"+self.RYANAIR_API_VER+"/oneWayFares/"+departure+"/"+arrival+"/" \
                +"cheapestPerDay?market=en-gb&outboundMonthOfDate="+_date
        response = urllib2.urlopen(query)
        j_data = json.loads(response.read())
        _flights = []
        _flights.append(_header)
        for _flight_detail in j_data['outbound']['fares']:
            if not _flight_detail['unavailable'] and not _flight_detail['soldOut']:
                if not c:
                    orig_currency = _flight_detail['price']['currencyCode']
                    print "Converting "+orig_currency+" "+target_currency
                    c = CurrencyConvertor.CurrencyConvertor(orig_currency, target_currency)
                _flights.append((departure,
                                 arrival,
                                 _flight_detail['day'].replace('-', ''),
                                 '99:99',
                                 '99:99',
                                 c.convert(_flight_detail['price']['value']),
                                 '1234',
                                 "RYANAIR"))
        return _flights

    def get_all_lines(self, uniq=0):
        query = "https://api.ryanair.com/aggregate/"+self.RYANAIR_API_VER+"/common?embedded=airports&market=en-gb"
        response = urllib2.urlopen(query)
        j_data = json.loads(response.read())
        _lines = []
        for _iata_data in j_data['airports']:
            _dests = [x.split(':')[1] for x in _iata_data['routes'] if x.split(':')[0] == "airport"]
            if uniq:
                _lines += [(_iata_data['iataCode'], _dests[0])]
            else:
                _lines += [(_iata_data['iataCode'], _dest) for _dest in _dests]
        return _lines

    def get_all_flights(self, month, year):
        _flights = []
        for _departure, _arrival in self.get_all_lines():
            print "Proccessing "+_departure+" "+_arrival+" for "+month+"-"+year
            _flights.append(self.get_month_data(_departure, _arrival, month, year))
            #print _flights
        return _flights

    def create_flights_csv(self, year, month, out_file=None):
        if not out_file:
            out_file = month+"_"+year +"_"+self.CARRIER+".csv"
        try:
            os.remove(out_file)
            print "removed " + out_file
        except os.error:
            "cannot remove file"
        f = open(out_file, 'a')
        for _line in self.get_all_flights(*values):
            for _l in _line:
                print _l
                f.write(','.join(str(v) for v in _l) + '\n')
        f.close()
        return True


    def create_iatas_csv(self, out_file=None):
        if not out_file:
                out_file = "iatas_"+self.CARRIER+".csv"
        try:
            os.remove(out_file)
            print "removed " + out_file
        except os.error:
            "cannot remove file"
        f = open(out_file, 'a')
        for _line in self.get_destinations():
            f.write(','.join(str(v) for v in _line) + '\n')
        f.close()
        return True

    def get_destinations(self):
        _header = ('#iataCode', 'city', 'country', 'currencyCode')
        query = "https://api.ryanair.com/aggregate/"+self.RYANAIR_API_VER+"/common?embedded=airports,countries&market=en-gb"
        response = urllib2.urlopen(query)
        j_data = json.loads(response.read())
        _code_to_country = {}
        _result = [_header]
        for _country_data in j_data['countries']:
            _code_to_country[_country_data['code']] = _country_data['name']
        for _airport_data in j_data['airports']:
            _result.append((_airport_data['iataCode'],
                                    _airport_data['name'],
                                    _code_to_country[_airport_data['countryCode']],
                                    _airport_data['currencyCode']))
        return _result

#create_flights_csv_file(year, month)
if __name__ == "__main__":

    _ryanair = RyanairData()
    print _ryanair.get_month_data('TLV', 'PFO', '5', '2017', 'EUR')
    values = ("05", "2017")
    #_ryanair.create_flights_csv(*values)


