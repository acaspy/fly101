import sys
import os
import csv
from collections import defaultdict

reload(sys)
sys.setdefaultencoding('utf-8')


class GeoUtils:

    def __init__(self):
        self._iata_dict = defaultdict(dict)
        self._city_dict = {}
        self._country_currency_dict = {}
        _path = os.path.dirname(__file__)
        self.read_airports(_path + '/airports.dat')
        self.read_currency(_path + '/currency.dat')


    def read_airports(self, _file):
        """format
            #1 airportName
            #2 city
            #3 country
            #4 IATA
        """
        with open(_file, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row[0].startswith('#'):
                    airportName = row[1]
                    city = row[2]
                    country = row[3]
                    IATA = row[4]
                    self._iata_dict[IATA]['airportName'] = airportName
                    self._iata_dict[IATA]['city'] = city
                    self._iata_dict[IATA]['country'] = country
                    self._city_dict[city] = country
        return True

    def read_currency(self, _file):
        """ format
            #0 country
            #1 UPS Code
            #2 IATA(country) code
            #3 Currency Code
        """
        with open(_file, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row[0].startswith('#'):
                    country = row[0]
                    currency_code = row[3]
                    self._country_currency_dict[country] = currency_code
        return True

    def get_geo_dict(self):
        return self._iata_dict

    def get_city_for_iata(self, iata):
        return self._iata_dict[iata]['city'] if iata in self._iata_dict else "None"

    def get_country_for_iata(self, iata):
        return self._iata_dict[iata]['country'] if iata in self._iata_dict else "None"

    def get_country_for_city(self, city):
        return self._city_dict[city] if city in self._city_dict else "None"

    def get_currency_code_for_country(self, country):
        return self._country_currency_dict[country] if country in self._country_currency_dict else "None"

    def get_currency_code_for_iata(self, iata):
        return self.get_currency_code_for_country(self.get_country_for_iata(iata))


    def get_all_destinations(self):
        return [(iata,
                 self._iata_dict[iata]['city'],
                 self._iata_dict[iata]['country'])
                for iata in self._iata_dict.keys() if iata != ''
                ]


#TODO implement this class
class TimeUtils:

    def __init__(self):
        """should implement this classs"""
        pass

    def getDiffTimeInHours(self, flight_a_time , flight_b_time ):
        #date_format = "%Y%m%d %H:%M"
        date_format = "%Y%m%d %H:%M"
        a = datetime.strptime(flight_a_time,date_format)
        b = datetime.strptime(flight_b_time,date_format)
        return (b-a).total_seconds()/3600

if __name__ == "__main__":
    g = GeoUtils()
    print g.get_city_for_iata('FKB')
    print g.get_country_for_iata('FKB')
    print g.get_currency_code_for_iata('FKB')
    print g.get_all_destinations()
   # print g.get_all_destinations()
