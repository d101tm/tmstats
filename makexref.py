#!/usr/bin/env python3

import xlrd
import os,sys

class Path:
    paths = {}
    @classmethod
    def get(self, name):
        if name not in self.paths:
            self.paths[name] = Path(name)
            
        return self.paths[name]
        
    def __init__(self, name):
        self.name = name
        self.projects = []
        self.blurb = ''

class Project:
    def __init__(self, name, order, path, value):
        self.name = name
        self.order = order
        self.value = value
        self.level = int(self.value[0])
        self.required = 'R' in self.value
        self.key = (self.level, not self.required, self.value, self.order)
        Path.get(path).projects.append(self)
        
class Multout:
    def __init__(self):
        self.files = []
    def add(self, handle):
        self.files.append(handle)
    def write(self, str):
        for f in self.files:
            f.write(str)
    def delete(self, handle):
        try:
            del self.files[self.files.index(handle)]
        except Exception:
            print(sys.exc_info())
        
levels = {1: "Mastering Fundamentals",
          2: "Learning Your Style",
          3: "Increasing Knowledge",
          4: "Building Skills",
          5: "Demonstrating Expertise"}
        
styleinfo = """    <style type="text/css">
    .pathname-header {font-size: 175%; font-weight: bold; background: #004165; color: white; padding: 3px; margin-top: 2em; margin-bottom: 0.5em;}
    .level {font-size: 150%; font-weight: bold; background: #f2df7480; margin-top: 1em; padding: 3px; margin-bottom: 0.5em;}
    .projname {font-size: 125%; font-weight: bold; color: #772432}
    .electives {background: #00416520; }
    .electives-header {font-size: 135%; font-weight: bold; background: #00416520; color: black; margin-top: 1em; padding-bottom: 0.5em;}
    .projdesc {margin-bottom: 2em;}
    </style>
"""

def cleanup(s):
    """Remove extraneous newlines (all not before a tag)"""
    return s.replace('\n<', '\x00').replace('\n',' ').replace('\x00','\n<').strip()

book = xlrd.open_workbook('Projects.xlsx')
os.chdir('data')

# Get the projects
sheet = book.sheet_by_name('Projects')
colnames = sheet.row_values(0)

# Create paths
namecol = colnames.index('Name')
ordercol = colnames.index('Order')
pathcols = list(range(namecol+1,sheet.ncols))


# Create projects and assign to paths
for rownum in range(1,sheet.nrows):
    order = sheet.cell_value(rownum, ordercol)
    if not order:
        order = 0
    name = sheet.cell_value(rownum, namecol)
    for p in pathcols:
        val = ('%s' % sheet.cell_value(rownum, p)).strip()
        if val:
            Project(name, order, colnames[p], val)
            
# Now, get the blurbs for each path
sheet = book.sheet_by_name('Paths')
for rownum in range(1, sheet.nrows):
    pathname = sheet.cell_value(rownum, 0)
    path = Path.get(pathname)
    path.blurb = sheet.cell_value(rownum, 1)
            
# OK, now create the output
            
outfiles = Multout()
allout = open("Allpaths.html", "w", encoding="utf-8")
outfiles.add(allout)
allout.write(styleinfo)


for p in pathcols:
    pathname = colnames[p]
    pathid = ''.join([part[0:4] for part in pathname.lower().split()[0:2]])
    path = Path.get(pathname)
    path.projects.sort(key=lambda item:item.key)
    with open('Path ' + pathname + '.html', 'w', encoding='utf-8') as outfile:
        outfiles.add(outfile)
        outfile.write(styleinfo)
        outfiles.write('<div class="pathname-header">\n')
        # Write the expandable header for the all-in-one file
        allout.write('<div class="pathname" onclick="jQuery(\'#%sopen, #%sclosed, #%sdesc\').toggle()">' % (pathid, pathid, pathid))
        allout.write('<span id="%sopen" style="display:none">&#x2296;</span><span id="%sclosed">&#x2295;</span> %s\n' % (pathid, pathid, pathname)) 
        allout.write('</div>\n')
        
        # Write the normal header for the file-per-path version
        outfile.write('<h2 class="pathname">%s</h2>\n' % pathname)
        outfiles.write('</div>')  # Close the pathname header
        outfiles.write('<p class="blurb">%s</p>\n' % path.blurb)
        
        # Write the wrapper for the all-in-one file
        allout.write('<div id="%sdesc" style="display:none">\n' % pathid)
        
        # Write the details
        level = 0
        inelectives = False
        for item in path.projects:
            if item.level != level:
                if inelectives:
                  outfiles.write('</div>\n')
                outfiles.write('<h3 class="level">Level %s: %s</h3>\n' % (item.level, levels[item.level]))
                level = item.level
                inelectives = False
                itemnum = 0
            itemnum += 1
            itemid = '%s%s%s' % (pathid, level, itemnum)
            if not inelectives and not item.required:
                outfiles.write('<div class="electives-header">Electives (Choose %d)</div>\n' % [0, 0, 0, 2, 1, 1][level])   
                outfiles.write('<div class="electives">\n')
                inelectives = True
            outfiles.write('<div class="%s-project">\n' % ('req' if item.required else 'elective'))

            outfiles.write('<div class="projname" onclick="jQuery(\'#%sopen, #%sclosed, #%sdesc\').toggle()">' % (itemid, itemid, itemid))
            outfiles.write('<span id="%sopen" style="display:none">&#x2296;</span><span id="%sclosed">&#x2295;</span> %s\n' % (itemid, itemid, item.name)) 
            outfiles.write('</div>\n')
            outfiles.write('<div id="%sdesc" class="projdesc" style="display:none;">\n' % itemid)
            outfiles.write(cleanup(open(item.name+'.html', 'r', encoding='utf-8').read().encode('ascii','xmlcharrefreplace').decode()))
            outfiles.write('</div>\n')
            outfiles.write('</div>\n')
        if inelectives:
            outfiles.write('</div>\n')
        
        outfiles.delete(outfile)
        
        # Close the wrapper
        allout.write('</div>\n')  

    
            

    
