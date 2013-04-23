# default: 404
path().status(404).html("404 Not found")

# special URL
path('/cgi-bin/projector_status.cgi').status(200).body_file('canned_data/power_off_status_report.htm')

# standard url
path('/').redirect('/cgi-bin/main.cgi')
path('/cgi-bin/main.cgi').status(200).html("Projector main page", "crappy html galore")
