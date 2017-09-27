class Awardinfo:
        oldawardnames = {'CC':'Competent Communicator',
                          'ACB': 'Advanced Communicator Bronze',
                          'ACS': 'Advanced Communicator Silver',
                          'ACG': 'Advanced Communicator Gold',
                          'CL': 'Competent Leader',
                          'ALB': 'Advanced Leader Bronze',
                          'ALS': 'Advanced Leader Silver',
                          'LDREXC': 'High Performance Leadership Project',
                          'DTM': 'Distinguished Toastmaster'}
                          
        pathnames = {'Dynamic Leadership',
                          'Effective Coaching',
                          'Innovative Planning',
                          'Leadership Development',
                          'Motivational Strategies',
                          'Persuasive Influence',
                          'Presentation Mastery',
                          'Strategic Relationships',
                          'Team Collaboration',
                          'Visionary Communication'}
                         
                         
        # The names of the awards for paths are derived from the path name:
        #  First three letters of the first two words in the path (uppercased)
        #  Followed by "L" and the level number.
        #  Compute them all to reduce typing.
        pathids = {}
        for p in pathnames:
            id = ''.join([s[0:3].upper() for s in p.split()[:2]])
            pathids[id] = p
        
        levels = {}
        paths = {}
        lookup = oldawardnames
        for item in oldawardnames:
            levels[item] = 0
            
        for p in pathids:
            for l in [1, 2, 3, 4, 5]:
                index = '%sL%d' % (p, l)
                lookup[index] = '%s Level %d' % (pathids[p], l)
                levels[index] = l
                paths[index] = pathids[p]