import json
import pprint
import urllib2



class ProviderNotAvailable(Exception):
    """
    when such provider for currency converting not available
    """
    pass


class CurrencyConvertor:


    def __init__(self, orig_code, target_code, provider='yahoo'):
        self._orig_code, self._target_code = str(orig_code).upper(), str(target_code).upper()
        self._rate = 1
        if self._target_code != self._orig_code:
            if provider == 'yahoo':
                self._rate = self.yahoo_currency()
            elif provider == 'opencurrencyapi':
                self._rate = self.currencyconverterapi_currency()
            else:
                raise ProviderNotAvailable("Provider API not available")

    def yahoo_currency(self):
        _code = self._orig_code+self._target_code
        q = "http://finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s="+_code+"=X"
        response = urllib2.urlopen(q)
        _rate = response.read().split(',')[1]
        if _rate != "N/A":
            return float(_rate)
        else:
            raise RatesNotAvailableError("Currency Rates Source Not Ready")
        return None

    def currencyconverterapi_currency(self):
        code = self._orig_code+"_"+self._target_code
        q = "http://free.currencyconverterapi.com/api/v3/convert?q="+code+"&compact=y"
        response = urllib2.urlopen(q)
        if j_data:
            return float(j_data[code]['val'])
        else:
            raise RatesNotAvailableError("Currency Rates Source Not Ready")
        return None

    def convert(self, price):
        return '{0:.4g}'.format(float(price) * self._rate)

if __name__ == "__main__":
    c = CurrencyConvertor('EUR', 'ILS')
    print c.convert(100)


