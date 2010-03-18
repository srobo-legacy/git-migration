# Map of repositories that have *already* been exported into git
import os

class Repo:
    def __init__(self, path, svn_path, exists = True):
        self.path = path
        self.svn_path = svn_path
        self.exists = exists

def get_lut( reponame, repopath ):
    f = open( os.path.join( os.path.dirname( os.path.realpath(__file__) ), "externals/gitsvn-revmap" ) , "r")

    lut = {}

    for l in f.readlines():
        lrepo, lpath, lrev, lhash = l.split()
        lrev = int(lrev)

        if lrepo == reponame and lpath == repopath:
            lut[lrev] = lhash

    return lut
    

def find_chash( reponame, repopath, rev ):
    print "find_chash( %s, %s, %i )" % (reponame, repopath, rev)
    lut = get_lut( reponame, repopath )

    if lut.has_key(rev):
        print "Choosing rev %i for external." % rev
        return lut[rev]

    # Otherwise we have to do some more crazy searching

    # Search downwards first
    for r in range(rev, 0,-1):
        if lut.has_key(r):
            print "Choosing rev %i for external." % r
            return lut[r]

    for r in range(rev, max(lut.keys())):
        if lut.has_key(r):
            print "Choosing rev %i for external." % r
            return lut[r]

repos = [ Repo( "srusers.git", "/web/srusers" ),
          Repo( "pyenv-dummy.git", "/boards/slug/pyenv/dummy" ) ]
