# -*- coding: utf-8 -*-
import sys
import eventful
import pprint

reload(sys)
sys.setdefaultencoding('utf-8')

#acasp key:
###79BBkzsdbbqBBr4W



api = eventful.API('79BBkzsdbbqBBr4W')

events = api.call('/events/search', q='music', location='Tel-Aviv', date='2017030100-2017030500', within='25')
for event in events['events']['event']:
    print("{} - performing - {} -  at - {} ".format(event['title'], event['description'], event['city_name']))
#pprint.pprint(events)

