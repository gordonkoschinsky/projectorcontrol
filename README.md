# ProjectorControl

## What is this?

A small wxpython application to control a video projector via ethernet.

I need this to control the shutter of a panasonic video projector during a
theater performance. The projector has a built-in web interface and no other
way of controlling it via ethernet, A web interface is quite clunky for this
purpose, Further, the shutter shall be opened and closed from the video playback
program, which can emit keypresses, midi messages and much more, but is unable
to navigate web interfaces.

Thus, what I need is a program that can be controlled by a system-wide hotkey,
toggles the shutter upon triggering and provides a a small visual feedback
window.

## Requirements

projectorControl is developed under Python 2.7. I don't know if I used something that needs
this version, maybe you'll get lucky with 2.6 or 2.5.

It is tested with Windows 7 only. The application might run on other platforms, however, the hotkey feature will only function with Windows.

The following external dependencies exist:

+ [wxPython](http://www.wxpython.org) - the GUI framework
+ [PyPubSub](http://pypi.python.org/pypi/PyPubSub) - publish-subscribe-API
+ My own ["threadsafe"](https://bitbucket.org/gordonkoschinsky/threadsafepubsub/overview)
version of PyPubSub.pub.sendMessage()
+ [requests](http://python-requests.org) to make HTTP requests to the projector
+ [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) to parse HTM

A .spec-file for PyInstaller 2.0 is included, so you can easily build an .exe
for Windows containing all of the dependencies.

## How to use

Just run

`python projectorControl.py`

inside the `src/projectorControl` directory
or start the built .exe-file

projectorControl will parse a config-file named `projector.ini` that must be in
the same directory
as the .exe or the `projectorControl.py` script.

## I need something like this, but I got a different projector

No problem, the projector "model" is completely decoupled from the GUI and the
control logic. Just have a look at `projector_model.py` as an example of how to
implement your own `Projector` class.

## Testing

I'm using [Turq](https://github.com/vfaronov/turq) as a mock HTTP server. The
file `turq_rules.txt` contains the configuration for Turq to respond like the
actual projector. You have to change the state of the mock projector manually,
by (un)commenting the appropriate line.

## License

Everything is under the GPL. However, the code itself is not marked with a GPL preambel yet.
