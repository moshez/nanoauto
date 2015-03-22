import json

from zope import interface

from twisted.python import usage, filepath
from twisted.internet import reactor, endpoints
from twisted.cred import portal, checkers
from twisted.web import guard, resource, server
from twisted.application import internet

import klein

class Outline(object):

    app = klein.Klein()

    def __init__(self, store):
        self.store = store

    @app.route('/toc', methods=['GET'])
    def toc(self, request):
        ret = {}
        for child in self.store.children():
            content = child.getContent()
            parsed = json.loads(content)
            logicalName = parsed['logicalName']
            realName = child.basename()
            ret[logicalName] = realName
        return json.dumps(ret)

    @app.route('/children/<child>', methods=['PUT'])
    def add(self, request, child):
        fp = self.store.child(child)
        if fp.exists():
            raise ValueError("cannot modify")
        request.content.seek(0, 0)
        content = json.loads(request.content.read())
        parent = content.get('parent')
        if parent:
            parentFP = self.store.child(parent)
            parentContents = json.loads(parentFP.getContent())
            lastID = parentContents['lastID'] = parentContents.get('lastID', 0)+1
            parentFP.setContent(json.dumps(parentContents))
        child['logicalName'] = parent['logicalName']+'.'+lastID
        fp.setContent(json.dumps(child))
        return 'Done'

class SimpleRealm(object):

    interface.implements(portal.IRealm)

    def __init__(self, guarded):
        self.guarded = guarded

    def requestAvatar(self, avatarId, mind, *interfaces):
        if resource.IResource in interfaces:
            return resource.IResource, self.guarded, lambda:None
        raise NotImplementedError()

def makeWrapper(guarded, username, pwd):
    checkerList = [checkers.InMemoryUsernamePasswordDatabaseDontUse(**{username: pwd})]
    realm = SimpleRealm(guarded)
    myPortal = portal.Portal(realm, checkerList)
    webGuard = guard.BasicCredentialFactory("nanoauto")
    wrapper = guard.HTTPAuthSessionWrapper(myPortal, [webGuard])
    return wrapper

def makeService(opt):
    outline = Outline(filepath.FilePath(opt['store']))
    resource = makeWrapper(outline.app.resource(), opt['username'], opt['password'])
    site = server.Site(resource)
    port = endpoints.TCP4ServerEndpoint(reactor, opt['port'], interface=opt['interface'])
    webService = internet.StreamServerEndpointService(endpoint=port, factory=site)
    return webService

class Options(usage.Options):

    optParameters = [['username', None, 'root', 'Username'],
                     ['password', None, 'root', 'Password'],
                     ['store', None, '.', 'Store'],
                     ['interface', None, '0.0.0.0', 'Interface to serve on'],
                     ['port', None, 8080, 'Port to serve on', int],
                    ]
