#
# RepMan Functions
#

from repman._repmanclass import repman

class funcdefs:
    def __init__(self, version:str):
        self.version = version
        self.repman = repman()
        self.repman.version = self.version
    
    # function to initialize repman
    def init(self, path: str = None):
        self.repman.initialize()
    
    # function to add a repo to the projects directory
    def add(self, val: str):
        self.repman.setvariables()
        self.repman.add(val)
    
    # function to list
    def lister(self, path: bool):
        self.repman.setvariables()
        
        if path:
            self.repman.lister(path=True)
        else:
            self.repman.lister()
    
    # function to add existing path
    def addexisting(self, paths: list[str]):
        self.repman.setvariables()
        self.repman.add_existing(paths)
    
    # function to open a project
    def openthis(self, projects:list[str]):
        self.repman.setvariables()
        self.repman.open(projects)
    
    # function to update a repo
    def update(self, projectname:str):
        self.repman.setvariables()
        self.repman.update(projectname)
    
    def addlocal(self, paths: list[str]):
        self.repman.setvariables()
        self.repman.addlocal(paths)
    
    def setremote(self, project:str, remote:str):
        self.repman.setvariables()
        self.repman.setremote(project, remote)