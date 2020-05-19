#!/usr/bin/env python3
""" Build District Credit Report based on Google spreadsheet """


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
    parms.add_argument('--outfile', default='${workdir}/districtcredit.html')
    parms.add_argument('--creditfile', default='https://docs.google.com/spreadsheets/d/1p0IEPYW4BWL2BKXSwo6cQBie2hfYjXUsMiVDFC5alSQ/')
    parms.add_argument('--sheetname', default='D101_RecognitionCredits')

    # Do global setup
    myglobals.setup(parms)
    curs = myglobals.curs
    conn = myglobals.conn

    
    # Get the spreadsheet
    gc = gspread.authorize(getGoogleCredentials())
    book = gc.open_by_url(parms.creditfile)
    sheet = book.worksheet(parms.sheetname)

    outfile = open(parms.outfile, 'w')

    ### We are dependent on the format of the spreadsheet
    
    # Last updated value is in 'B1' - let's convert it to English text
    asof = sheet.acell('B1', value_render_option='UNFORMATTED_VALUE').value
    asof = datetime(1899, 12, 30) + timedelta(days=asof)
    asof = asof.strftime("%B %-d, %Y")


    # Bring in the dataTables resources
    outfile.write(
"""
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.3.1.js"></script>
<script src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>
<script type="text/javascript">
    $(document).ready(function() {
        $('#credits').DataTable({"paging":false});
    } );
</script>
<style type="text/css">
    th.rjust, td.rjust {text-align: right;}
</style>
""")

    # Write the prefatory information
    outfile.write(
f"""<p>The following table shows District Credit as of {asof}.  You can sort
any column by clicking on it, or limit the table to lines containing a string.</p>
""")

    # Write the table header
    outfile.write(
"""
    <table id="credits" class="compact stripe row-border">
      <thead>
        <tr>
        <th>Area</th>
        <th>Club Number</th>
        <th>Club Name</th>
        <th>Earned</th>
        <th>Available</th>
        </tr>
      </thead>
      <tbody>
""")    
    # Labels are in row 3
    labels = sheet.row_values(3)
    nlabels = [normalize(c) for c in labels]

    # Find 'ID' (club number), 'TOTAL CREDITS' and 'BALANCE CREDITS'
    #   We'll pick up club name and alignment from the database

    idcol = nlabels.index('id')
    namecol = nlabels.index('name')
    credcol = nlabels.index('totalcredits')
    balancecol = nlabels.index('balancecredits')
    areacol = nlabels.index('area')

    clubs = Club.getActiveClubs(curs)

    # Values begin in row 4
    for row in sheet.get_all_values()[3:]:
        clubnum = row[idcol]
        clubname = row[namecol]
        alignment = row[areacol]
        if not clubnum:
            continue
        try:
            club = clubs[clubnum]
            alignment = club.division + club.area
            clubname = club.clubname
        except KeyError:
            continue
        earned = row[credcol]
        available = row[balancecol]
        outfile.write('<tr>\n')
        outfile.write(f'  <td>{alignment}</td>\n')
        outfile.write(f'  <td class="rjust">{clubnum}</td>\n')
        outfile.write(f'  <td>{clubname}</td>\n')
        outfile.write(f'  <td class="rjust">{earned}</td>\n')
        outfile.write(f'  <td class="rjust">{available}</td>\n')
        outfile.write('</tr>\n')

    outfile.write('  </tbody>\n')
    outfile.write('</table>\n')
