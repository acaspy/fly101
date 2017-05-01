from flask import Flask, render_template, request, jsonify

from Utils import GeoUtils

from FlightProviders import WizzairData, RyanairData


g = GeoUtils.GeoUtils()

app = Flask(__name__)
application = app
@app.route('/<provider>/<departure>/<arrival>/<month>/<year>')
def provider(provider, departure, arrival, month, year):
    flights = []
    if provider == "wizzair":
        wizz = WizzairData.WizzairData()
        flights = wizz.read_flight_time_table(departure, arrival, str(month), str(year))
    if provider == "ryanair":
        ryanair = RyanairData.RyanairData()
        flights = ryanair.get_month_data(departure, arrival, str(month), str(year))
    return jsonify(flights)


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q').lower()
    g.get_all_destinations()
    results = [','.join(dest) for dest in g.get_all_destinations() if search in ' '.join(dest).lower()]
    print results
    return jsonify(matching_results=results)

if __name__ == '__main__':
    app.run(debug=True)
