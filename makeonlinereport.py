#!/usr/bin/env python3
""" Build Online Club Report based on Google spreadsheet """


from datetime import datetime, timedelta
import gspread
import tmglobals
from tmutil import cleandate, normalize, getGoogleCredentials, getClubBlock
from simpleclub import Club
from datetime import datetime, timedelta

myglobals = tmglobals.tmglobals()


class Clubinfo:
    def __init__(self, labels, row):
        self.labels = labels
        for (k, v) in zip(labels, row):
            setattr(self, k, v)

    def __repr__(self):
        return ', '.join([f'{l, getattr(self, l)}' for l in labels])

class Winner:
    def __init__(self, clubname):
        self.clubname = clubname


if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('--outfile', default='${workdir}/onlineclubs.html')
    parms.add_argument('--clubfile', default='https://docs.google.com/spreadsheets/d/1JZUk7zKgwEm4rBvlVRo966I93Gali49Gw09sWtaMXJw/')
    parms.add_argument('--sheetname', default='Form Responses')

    # Do global setup
    myglobals.setup(parms)
    curs = myglobals.curs
    conn = myglobals.conn

    
    # Get the spreadsheet
    gc = gspread.authorize(getGoogleCredentials())
    book = gc.open_by_url(parms.clubfile)
    sheet = book.worksheet(parms.sheetname)

    outfile = open(parms.outfile, 'w')

    # Bring in the dataTables resources
    outfile.write(
"""
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.3.1.js"></script>
<script src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>
<script type="text/javascript">
    $(document).ready(function() {
        $('#clubs').DataTable({"paging":false});
    } );
</script>
<style type="text/css">
    th.rjust, td.rjust {text-align: right;}
</style>
""")

    # Write the prefatory information
    outfile.write(
f"""<p>The following table shows clubs which are currently meeting online.<br>You can sort
any column by clicking on it, or limit the table to lines containing a string.</p>
""")

    # Write the table header
    outfile.write(
"""
    <table id="clubs" class="compact stripe row-border">
      <thead>
        <tr>
        <th>Area</th>
        <th>Club Number</th>
        <th>Club Name</th>
        <th>Contact</th>
        <th>Meeting Day/Time</th>
        </tr>
      </thead>
      <tbody>
""")

    ### We are dependent on the format of the spreadsheet

    class Row:

        # Build the converter
        colnames = ('timestamp', 'online', 'transition', 'guests', 'contactinfo', 'contactemail', 'distreach' ,'clubname', 'area', 'clubnum', '')

        def __init__(self, line):
            for (colnum, name) in enumerate(self.colnames):
                if name:
                    self.__setattr__(name, line[colnum])

    clubs = Club.getClubsOn(curs)

    # Values begin in row 2
    for line in sheet.get_all_values()[1:]:
        row = Row(line)
        if not row.clubnum:
            continue
        # Only list clubs currently meeting online
        if not row.online.lower().startswith('yes'):
            continue
        try:
            club = clubs[row.clubnum]
            row.alignment = club.division + club.area
        except KeyError:
            continue
        if row.contactemail:
            club.clubemail = row.contactemail  # Override if requested
        if row.guests.lower().startswith('no'):
            contact = ''
            link = club.clubname
        else:

            contact = f'<a href="{club.clubemail}">{club.clubemail.split("mailto:")[-1]}</a>'
            link = club.getLink()
            link = f'<a href="{link}">{club.clubname}</a>'

        outfile.write('<tr>\n')
        outfile.write(f'  <td>{row.alignment}</td>\n')
        outfile.write(f'  <td class="rjust">{row.clubnum}</td>\n')
        outfile.write(f'  <td>{link}</td>\n')
        outfile.write(f'  <td>{contact}</td>\n')
        outfile.write(f'  <td>{club.meetingday}: {club.meetingtime}</td>\n')
        outfile.write('</tr>\n')

    outfile.write('  </tbody>\n')
    outfile.write('</table>\n')
