# default: 404
path().status(404).html("404 Not found")

# NO AUTH
path().status(401).html("401 Not authorized")

# GENERAL ERROR
path().status(500).html("Internal server error")

# STATUS URL
#
# OFF
#path('/cgi-bin/projector_status.cgi').status(200).body_file('canned_data/power_off_status_report.htm')

# ON, Shutter OPEN
#path('/cgi-bin/projector_status.cgi').status(200).body_file('canned_data/power_on_shutter_off_status_report.htm')

# ON, Shutter CLOSED
#path('/cgi-bin/projector_status.cgi').status(200).body_file('canned_data/power_on_shutter_on_status_report.htm')

# ON, shutter MANGLED
#path('/cgi-bin/projector_status.cgi').status(200).body_file('canned_data/power_on_shutter_mangled_status_report.htm')

# MANGLED power
#path('/cgi-bin/projector_status.cgi').status(200).body_file('canned_data/power_off_status_report_mangled.htm')


# COMMAND URL
#
#
#path('/cgi-bin/proj_ctl.cgi').status(200).body_file('canned_data/power_off__command_power_off.htm')
#path('/cgi-bin/proj_ctl.cgi').status(200).body_file('canned_data/power_on__command_power_off_cooling.htm')
path('/cgi-bin/proj_ctl.cgi').status(200).body_file('canned_data/power_off__command_power_off_cooling_finished.htm')

# standard url
path('/').redirect('/cgi-bin/main.cgi')
path('/cgi-bin/main.cgi').status(200).html("Projector main page", "crappy html galore")
