if __name__ != '__main__':
    raise ImportError("This module is not designed to be imported", __name__)

import os
import sys

from twisted.python import filepath

from ncolony import ctllib

def reset(fp):
    if fp.exists():
        fp.remove()
    fp.makedirs()

binLocation = os.path.join(os.environ['VIRTUAL_ENV'], 'bin')
baseName, username, password = sys.argv[1:]
base = filepath.FilePath(baseName)
tempDir = base.child('_temp')
metadata = base.child('metadata')
store = base.child('store')
logs = base.child('log')
if tempDir.child('twistd.pid').exists():
    sys.exit("Running twistd, aborting")
reset(store)
reset(tempDir)
reset(metadata)
reset(logs)
config = metadata.child('config')
messages = metadata.child('messages')
status = metadata.child('status')
for subd in (config, messages, status):
    subd.createDirectory()

places = ctllib.Places(config=config.path, messages=messages.path)
twistd = os.path.join(binLocation, 'twistd')

def getBaseArgs(name):
    return ['--pidfile', tempDir.child(name+'.pid').path,
            '--logfile', logs.child(name+'.log').path,
            '--nodaemon']

def addService(name, serviceName, args, extras=None):
    baseArgs = getBaseArgs(name)
    args = baseArgs + [serviceName] + args
    ctllib.add(places, name=name, cmd=twistd, args=args, extras=extras)

addService('web', 'nanoauto', 
           args=['--username', username, '--password', password,
                 '--store', store.path,
                 ])
placeConfig = ['--messages='+places.messages, '--config='+places.config]
addService('beatcheck', 'ncolony-beatcheck', args=placeConfig)
args = [twistd] + getBaseArgs('master') + ['ncolony', '--freq', '1'] + placeConfig
os.execv(args[0], args)
