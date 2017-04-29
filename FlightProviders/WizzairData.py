# -*- coding: utf-8 -*-
import json
import os
import re
import sys
import urllib2
import requests

from decimal import Decimal
from pprint import pprint
from Utils import GeoUtils
from Utils import CurrencyConvertor

reload(sys)
sys.setdefaultencoding('utf-8')


class WizzairData():

    def __init__(self):
        self._geo_utils = GeoUtils.GeoUtils()

    def read_flight_time_table(self, departure, arrival ,month ,year, target_currency='EUR'):
        """reading json format from wizzair backend services for a whole month"""
        query = "https://cdn.static.wizzair.com/en-GB/TimeTableAjax?departureIATA="\
                +departure+"&arrivalIATA="+arrival+"&year="+year+"&month="+month
        response = urllib2.urlopen(query)
        _orig_currency = self._geo_utils.get_currency_code_for_iata(departure)
        c = CurrencyConvertor.CurrencyConvertor(_orig_currency, target_currency)
        _header = ('#departureCode',
                   'ArrivalCode',
                   'date',
                   'departureTime',
                   'arrivalTime'
                   'targetPrice',
                   'flightNumber',
                   'carrier')
        __flights = [_header]
        print "processing: "+ departure + "->" + arrival + " for " + month + "/" + year + "..."
        j_data = json.loads(response.read())
        for _flights in j_data:
            for _flight_detail in _flights['Flights']:
                if _flights['MinimumPrice']:
                    __flights.append( (_flights['DepartureStationCode'],
                                      _flights['ArrivalStationCode'],
                                      _flights['Date'],
                                      _flight_detail['STD'],
                                      _flight_detail['STA'],
                                       c.convert(Decimal(re.sub(r'[^\d.]', '', _flights['MinimumPrice']))),
                                      _flight_detail['FlightNumber'],
                                      _flight_detail['CarrierCode']) )
        return __flights


    def get_fare_chart(self, departure, arrival, date, day_interval=10, adult_count=1, child_count=0):
        _request = {"wdc": 'false',
                    "flightList": [{"departureStation": departure,
                                    "arrivalStation": arrival,
                                    "date": date}],
                    "dayInterval": day_interval,
                    "adultCount": adult_count,
                    "childCount": child_count}
        try:
            r = requests.post('https://be.wizzair.com/3.8.2/Api/asset/farechart', json=_request).json()
            if 'outboundFlights' in r:
                for _flights in r['outboundFlights']:
                    if _flights['price']:
                        #print departure, arrival,  _flights['date'], _flights['price']['currencyCode'], _flights['price']['amount']
                        return _flights['price']['currencyCode']
            else:
                """comment"""
                #pprint(r)
        except requests.ConnectionError:
            print 'Connection Error'
        return None

    #get_fare_chart('TLV', 'VNO', '2017-03-10', day_interval=10)

    def get_all_destinations(self):
        query = "https://cdn.static.wizzair.com/en-GB/Markets.js"
        response = urllib2.urlopen(query)
        html = response.read()
        _dests = {}
        counter = 0
        for part in html.split('},{'):
            result = re.search(r'IATA\":\"([A-Z][A-Z][A-Z])\"\,[^:]+:\"([^\,]+)\"',part)
            if result is not None:
                _dests[result.group(1)] = result.group(2).encode('ascii','ignore')
        return _dests


    def get_all_lines(self):
        query = "https://cdn.static.wizzair.com/en-GB/Markets.js"
        response = urllib2.urlopen(query)
        html = response.read()
        _lines = []
        for part in html.split(']},{'):
            result = re.search(r'DS\":\"([A-Z][A-Z][A-Z])\"', part)
            if result is not None:
                orig = result.group(1)
                for match in re.finditer(r'\"SC\":\"([A-Z][A-Z][A-Z])\"',part):
                    for group in match.groups():
                            _lines.append((orig,group))
        return _lines

    def scrap_dest_line(self):
        query = "https://cdn.static.wizzair.com/en-GB/Markets.js"
        response = urllib2.urlopen(query)
        html = response.read()
        _lines = {}
        for part in html.split(']},{'):
            result = re.search(r'DS\":\"([A-Z][A-Z][A-Z])\"', part)
            if result is not None:
                orig =  result.group(1)
                for match in  re.finditer(r'\"SC\":\"([A-Z][A-Z][A-Z])\"',part):
                    for group in match.groups():
                        if orig not in _lines:
                            _lines[orig] = group
        return _lines.items()

    def get_detailed_flights(self, departure, arrival, departure_date, return_date, adult_count =1, child_count=0, infant_count=0):

        _request = {
                        "flightList": [
                            {
                                "departureStation": departure,
                                "arrivalStation": arrival,
                                "departureDate": departure_date
                            },
                            {
                                "departureStation": arrival,
                                "arrivalStation": departure,
                                "departureDate": return_date
                            }
                        ],

                        "adultCount": adult_count,
                        "childCount": child_count,
                        "infantCount": infant_count,
                        "wdc": 'true'
                    }
        try:

            r = requests.post('https://be.wizzair.com/3.8.2/Api/search/search/', json=_request)
            pprint(r.json())

        except requests.ConnectionError:
            print 'Could not connect to the Internet'

    def create_flights_csv_file(self, year, month,out_file=None):
        _lines = self.get_all_lines()
        print "lines found..."
        print _lines
        if not out_file:
            out_file = month + "_" + year + "_wizzair.csv"
        try:
            os.remove(out_file)
            print "removed " + out_file
        except os.error:
            "cannot remove file"
        f = open(out_file, 'a')
        for _from, _to in _lines:
            _r = self.read_flight_time_table(_from, _to, str(month), str(year))
            for _l in _r:
                f.write(','.join(str(v) for v in _l) + '\n')
        f.close()
        return True


if __name__ == "__main__":

    month = "5"
    year = "2017"
    values = (year, month)
    _wizz = WizzairData()
    #_wizz.create_flights_csv_file(*values)
    print _wizz.read_flight_time_table("WAW", "TLV", str(month), str(year))