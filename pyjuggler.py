import os
import uuid
import subprocess
import pip
import importlib
import datetime as dt
import sys

def install_and_import(package):
    try:
        importlib.import_module(package)
    except ImportError:
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)

# check for, install and import the docker package
install_and_import('docker')

def run_tj(projectfile="--help"):
    executeCommand = "tj3 {}".format(projectfile)
    client = docker.from_env()
    client.containers.run('treibholz/tj3:latest',
                          command=executeCommand,
                          remove=True,
                          tty=True,
                          volumes={'pwd':{'bind':'/tj3','mode':'rw'}}
                          )

# Create some functions that can be reused as methods in multiple TJ classes
def setJournalEntry(self,
                    date,
                    headline,
                    alert = None,
                    author = None,
                    details = None,
                    flags = [],
                    summary = None):
    uid = str(uuid.uuid4())
    self.journalentry[uid] = {}
    self.journalentry[uid]['headline'] = headline
    self.journalentry[uid]['alert'] = alert
    self.journalentry[uid]['author'] = author
    self.journalentry[uid]['details'] = details
    self.journalentry[uid]['flags'] = flags
    self.journalentry[uid]['summary'] = summary

def setflag(self, flag):
    self.flags.append(flag)

def setlimit(self, limit):
    self.limits.append(limit)
    
def setprojectid(self, projectid):
    self.projectids.append(projectid)
    
def getTJjournalentries(self):
    outtext = "journalentry".format()
    return outtext

def getTJlimits(self):
    outtext = "limits \{\n\t{}\n\t\}".format("\n\t".join(self.limits)
    return outtext

def getTJflags(self):
    outtext = "flags " + ", ".join(self.flags)
    return outtext

def getTJprojectids(self):
    outtext = "projectsids " + ", ".join(self.projectids)
    return outtext


# TJ3 Project Class
class Project:
    """Definition of a TaskJuggler project class with a reasonable set of default attribute values"""
    
    def __init__(
                 self,
                 id=str(uuid.uuid4()),
                 name="default",
                 version="1.0",
                 interval2="2017-07-01 - 2024-06-30",
                 timingresolution="60min",
                 timezone="America/Denver",
                 dailyworkinghours="8",
                 yearlyworkingdays="260",
                 timeformat="%Y-%m-%d %H:%M",
                 shorttimeformat="%H:%M",
                 currency="USD",
                 currencyformat='(" ")" "," "." 0',
                 startofweek="weekstartsmonday",   # note instance variable name is diff from TJ attribute name
                 workinghours=["mon - fri 8:00 - 12:00, 13:00 - 17:00", "sat, sun off"],
                 auxdir = None,
                 balance = None,
                 copyright = None,
                 rate = None):
        self.id = id
        self.name = name
        self.interval2 = interval2
        self.timingresolution = timingresolution
        self.timezone = timezone
        self.dailyworkinghours = dailyworkinghours
        self.yearlyworkingdays = yearlyworkingdays
        self.timeformat = timeformat
        self.shorttimeformat = shorttimeformat
        self.currency = currency
        self.currencyformat = currencyformat
        self.startofweek = startofweek
        self.workinghours = workinghours
        self.resources = []
        self.tasks = {}
        self.flags = []
        self.reports = {}
        self.journalentry = {}
        self.projectids = []
        self.accounts = {}
        self.outputdir = ""
        self.auxdir = auxdir
        self.balance = balance
        self.copyright = copyright
        self.exports = {}
        self.includes = {}
        self.leaves = []
        self.limits = []
        self.macros = {}
        self.navigators = {}
        self.rate = rate
        self.shifts = {}
        self.statussheets = {}
        self.supplements = {}
        self.timesheets = {}

    # add some shared methods
    setJournalEntry = setJournalEntry
    setflag = setflag
    setlimit = setlimit
    getTJflags = getTJflags

    def generate(self):
        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)
        with open("{}/report.tjp".format(self.outputdir),"w") as f:
            f.write(self.getTJproject()+"\n")
            if len(self.flags) > 0: f.write(self.getTJflags()+"\n")
            if len(self.projectids) > 0: f.write(self.getTJprojectids()+"\n")
            if self.copyright is not None: f.write("copyright {}".format(self.copyright)+"\n")
            if self.rate is not None: f.write("rate {}".format(self.rate)+"\n")
            if len(self.macros) > 0: f.write("#Macros support still needs to be implemented"+"\n")
            if len(self.leaves) > 0: f.write("#Leaves support still needs to be implemented"+"\n")
            if len(self.accounts) > 0: f.write("#Account support still needs to be implemented"+"\n")
            if len(self.shifts) > 0: f.write("#Shifts support still needs to be implemented"+"\n")
            if len(self.resources) > 0: f.write("#Resources support still needs to be implemented"+"\n")
            if len(self.tasks) > 0: f.write("#Tasks support still needs to be implemented"+"\n")
            if self.balance is not None: f.write("#Balance support still needs to be implemented"+"\n")
            if self.auxdir is not None: f.write("#Auxdir support still needs to be implemented"+"\n")
            if len(self.includes) > 0: f.write("#Include support still needs to be implemented"+"\n")
            if len(self.resources) > 0: f.write("#Resources support still needs to be implemented"+"\n")
            if len(self.navigators) > 0: f.write("#Navigators support still needs to be implemented"+"\n")
            if len(self.reports) > 0: f.write("#Report support still needs to be implemented"+"\n")
            if len(self.exports) > 0: f.write("#Export support still needs to be implemented"+"\n")
            if len(self.statussheets) > 0: f.write("#Statussheets support still needs to be implemented"+"\n")
            if len(self.supplements) > 0: f.write("#Supplements support still needs to be implemented"+"\n")
            if len(self.timesheets) > 0: f.write("#Timesheets support still needs to be implemented"+"\n")
        try:
            run_tj("{}/report.tjp".format(self.outputdir))
        except:
            print("Unexpected error when running the TaskJuggler process:", sys.exc_info()[0])

    def getTJproject(self):
        self.outputdir="reports_{}".format(dt.datetime.isoformat(dt.datetime.now()).replace(":","_"))
        
        workinghoursEntries = []
        for hours in self.workinghours:
            workinghoursEntries.append("workinghours {}".format(hours))
        workinghours = "\n\t".join(workinghoursEntries)
        
        outtext = """project {} \"{}\" {} {{
\ttimingresolution {}
\ttimezone \"{}\"
\tdailyworkinghours {}
\tyearlyworkingdays {}
\ttimeformat \"{}\"
\tshorttimeformat \"{}\"
\tcurrencyformat \'{}\'
\t{}
\t{}
\toutputdir \"{}\"
}}\n""".format(self.id,
            self.name,
            self.interval2,
            self.timingresolution,
            self.timezone,
            self.dailyworkinghours,
            self.yearlyworkingdays,
            self.timeformat,
            self.shorttimeformat,
            self.currencyformat,
            self.startofweek,
            workinghours,
            self.outputdir)
        return outtext




class Task:
    def __init__(self,
                 id,
                 name,
                 adopt = None,
                 allocate = {},
                 booking = None,        # treat as text string for now
                 charge = None,         # treat as text string for now
                 chargset = None,       # treat as text string for now
                 complete = None,
                 depends = {},
                 duration = None,
                 effort = None,
                 effortdone = None,
                 effortleft = None,
                 end = None,
                 fail = None,           # treat as text string for now
                 flags = [],
                 length = None,
                 limits = [],
                 maxend = None,
                 maxstart = None,
                 milestone = False,
                 minend = None,
                 minstart = None,
                 note = None,
                 period = None,
                 precedes = {},
                 priority = 500,
                 projectid = None,
                 purge = None,
                 responsible = None,
                 scheduled = None,
                 scheduling = None,
                 schedulingmode = None,
                 shifts = None,
                 start = None,
                 supplement = None,
                 warn = None
                 ):
        self.uid = str(uuid.uuid4())
        self.id = id
        self.name = name
        self.tasks = {}
        self.adopt = adopt
        self.allocate = allocate
        self.booking = booking
        self.charge = charge
        self.chargset = chargset
        self.complete = complete
        self.depends = depends
        self.duration = duration
        self.effort = effort
        self.effortdone = effortdone
        self.effortleft = effortleft
        self.end = end
        self.fail = fail
        self.flags = flags
        self.journalentry = {}
        self.length = length
        self.limits = []
        self.maxend = maxend
        self.maxstart = maxstart
        self.milestone = milestone
        self.minend = minend
        self.minstart = minstart
        self.note = note
        self.period = period
        self.precedes = precedes
        self.priority = priority
        self.projectid = projectid
        self.purge = purge
        self.responsible = responsible
        self.scheduled = scheduled
        self.scheduling = scheduling
        self.schedulingmode = schedulingmode
        self.shifts = shifts
        self.start = start
        self.supplement = supplement
        self.warn = warn
    # add some shared methods
    setJournalEntry = setJournalEntry
    setflag = setflag
    setlimit = setlimit
    getTJflags = getTJflags
    

    def setAllocate(self,
                 resource,
                 alternative = None,
                 mandatory = None,
                 persistent = None,
                 select = None,
                 shifts = None):
        self.allocate[resource] = {}
        self.allocate[resource]['resource'] = resource
        self.allocate[resource]['alternative'] = alternative
        self.allocate[resource]['mandatory'] = mandatory
        self.allocate[resource]['persistent'] = persistent
        self.allocate[resource]['select'] = select
        self.allocate[resource]['shifts'] = shifts

    def setDepends(self,
                         taskId,
                         gapduration = None,
                         gaplength = None,
                         onend = False,
                         onstart = False):
        self.depends[taskId] = {}
        self.depends[taskId]['gapduration'] = gapduration
        self.depends[taskId]['gaplength'] = gaplength
        self.depends[taskId]['onend'] = onend
        self.depends[taskId]['onstart'] = onstart

    def setPrecedes(self,
                         taskId,
                         gapduration = None,
                         gaplength = None,
                         onend = False,
                         onstart = False):
        self.precedes[taskId] = {}
        self.precedes[taskId]['gapduration'] = gapduration
        self.precedes[taskId]['gaplength'] = gaplength
        self.precedes[taskId]['onend'] = onend
        self.precedes[taskId]['onstart'] = onstart


class Resource:
    def __init__(
                 self,
                 name,
                 booking = None,
                 chargeset = None,
                 efficiency = None,
                 email = None,
                 fail = None,
                 flags = [],
                 journalentry = {}
                 leaveallowance = [],
                 leaves = [],
                 limits = [],
                 managers = [],
                 purge = None,
                 rate = None,
                 shifts = {},
                 vacation = {},
                 workinghours = None
                 ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.resources = []
        self.journalentry = journalentry
        self.booking = booking
        self.chargeset = chargeset
        self.efficiency = efficiency
        self.email = email
        self.fail = fail
        self.flags = flags
        self.journalentry = journalentry
        self.leavallowance = leaveallowance
        self.leaves = leaves
        self.limits = limits
        self.managers = managers
        self.purge = purge
        self.rate = rate
        self.shifts = shifts
        self.vacation = vacation
        self.workinghours = workinghours
        


# check to see if Docker is installed, and if so, build (if needed) and test the TaskJuggler container
#if is_tool("docker"):
#run_tj("test")

