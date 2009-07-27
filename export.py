#!/usr/bin/env python
import subprocess, os

GIT_SVN_PROP_FILTER = "%s/git-svn-props" % os.getcwd()

def complete_url(path):
    return "http://svn.srobo.org%s" % path

class Repo:
    def __init__(self, name, path):
        # Whether it has trunk/tags/branch
        self.stdlayout = True
        self.name = name
        self.path = path
        self.tags = []
        self.layout = { "trunk": "trunk",
                        "branch": "branch",
                        "tags": "tags" }
        self.git_dir = "./git/%s" % name


    def __repr__(self):
        s = """Repo( name = '%s',
      path = '%s',
      stdlayout = %s,
      layout = %s )""" % ( self.name, self.path, 
                           str(self.stdlayout), 
                           str(self.layout) )
        return s

    def process(self):
        #git svn clone $SVN_DIR${1} -T trunk -t tags -b branches $2 
        layout = ""
        if self.stdlayout:
            layout = "-T %s -t %s -b %s" % ( self.layout["trunk"],
                                             self.layout["tags"],
                                             self.layout["branch"] )

        p = subprocess.Popen( args = "git svn clone %s %s %s" % ( layout,
                                                                  complete_url( self.path ),
                                                                  self.name ),
                              shell = True )
        p.communicate()
        p.wait()

        self._sort_tags()
        self._sort_branches()
        self._filter_props()

        # Clone ourself into another place -- get rid of git-svn gunge
        p = subprocess.Popen( args = "git clone --bare %s ../git/%s.git" % ( self.name, self.name ),
                              shell = True )
        p.communicate()
        p.wait()

    def _tag_list(self):
        tags = []
        p = subprocess.Popen( args = "git branch -r | grep tags/", 
                              shell = True, cwd = self.name,
                              stdout = subprocess.PIPE )
        r = p.communicate()
        p.wait()

        for tag in r[0].split():
            name = tag.split('/')[1]
            if '@' not in name:
                tags.append( name )

        return tags

    def _branch_list(self):
        branches = []
        p = subprocess.Popen( args = "git branch -r | grep -v tags/", 
                              shell = True, cwd = self.name,
                              stdout = subprocess.PIPE )
        r = p.communicate()
        p.wait()

        for branch in r[0].split():
            if '@' not in branch and branch != "trunk":
                branches.append( branch )
        return branches

    def _sort_tags(self):
        # git tag $x tags/$x
        for tag in self._tag_list():
            p = subprocess.Popen( args = "git tag %s tags/%s" % ( tag, tag ),
                                  shell = True, cwd = self.name )
            p.communicate()
            p.wait()

    def _sort_branches(self):
        # git branch $x $x
        for branch in self._branch_list():
            p = subprocess.Popen( args = "git branch %s %s" % ( branch, branch ),
                                  shell = True, cwd = self.name )
            p.communicate()
            p.wait()

    def _filter_props(self):
        # We need to filter all commits that are reachable from all tags and branches
        f = ["heads/master"] + self._tag_list() + [ "heads/" + x for x in self._branch_list() ]
        f = " ".join(f)

        p = subprocess.Popen( args = "git filter-branch --tree-filter %s %s" % ( GIT_SVN_PROP_FILTER, f ) ,
                              shell = True,
                              cwd = self.name )
        p.communicate()
        p.wait()

def NSRepo( name, path ):
    r = Repo( name, path )
    r.stdlayout = False
    return r

repos = [
    Repo( "flash430", "/boards/lib-fw/flash430" ),
    Repo( "msp430-types", "/boards/lib-fw/types" ),

    Repo( "pyenv", "/boards/slug/pyenv" ),
    # TODO: pyenv disttools + dummy

    Repo( "i2c-msd", "/boards/slug/i2c-msd" ),
    Repo( "c2py", "/boards/slug/c2py" ),
    Repo( "slug-outline", "/boards/slug/outline" ),

    NSRepo( "robovis", "/boards/slug/vision/robovis" ),
    NSRepo( "slug-br", "/boards/slug/init-br" ),

    Repo( "xbout", "/boards/slug/xbout" ),
    NSRepo( "battmon", "/boards/slug/utils/battmon" ),
    Repo( "flashb", "/boards/slug/utils/flashb" ),
    NSRepo( "xb-pinger", "/boards/slug/utils/pinger" ),

    NSRepo( "drupal", "/web/drupal" ),
    NSRepo( "planet", "/web/planet" ),

    Repo( "srusers", "/web/srusers" ),
    NSRepo( "userman", "/web/userman" ),
    NSRepo( "tools", "/tools" )
]

r = Repo( "Robo-IDE", "/Robo-IDE" )
r.layout["branch"] = "branches"
repos += [r]

# Add the boards
for board in [ "motor", "jointio", "pwm", "power" ]:

    # Test util
    test_util = Repo( "%s-test-util" % board, "/boards/%s/test-util" % board )
    if board == "motor":
        test_util.stdlayout = False

    # Firwmare
    fw = Repo( "%s-fw" % board, "/boards/%s/firmware" % board )

    # PCB
    pcb = Repo( "%s-pcb" % board, "/boards/%s/pcb" % board )

    # Outline
    outline = Repo( "%s-outline" % board, "/boards/%s/outline" % board )
    outline.layout["branch"] = "branches"

    repos += [ fw, pcb, outline, test_util ]

os.mkdir( "git" )
os.mkdir( "tmp" )
os.chdir( "tmp" )

for r in repos:
    r.process()

