class Awardinfo:
    oldawardnames = {'CC': 'Competent Communicator',
                     'ACB': 'Advanced Communicator Bronze',
                     'ACS': 'Advanced Communicator Silver',
                     'ACG': 'Advanced Communicator Gold',
                     'CL': 'Competent Leader',
                     'ALB': 'Advanced Leader Bronze',
                     'ALS': 'Advanced Leader Silver',
                     'LDREXC': 'High Performance Leadership Project',
                     'DTM': 'Distinguished Toastmaster'}


    pathids = {'DL': 'Dynamic Leadership',
               'EC': 'Effective Coaching',
               'EH': 'Engaging Humor',
               'IP': 'Innovative Planning',
               'LD': 'Leadership Development',
               'MS': 'Motivational Strategies',
               'PI': 'Persuasive Influence',
               'PM': 'Presentation Mastery',
               'SR': 'Strategic Relationships',
               'TC': 'Team Collaboration',
               'VC': 'Visionary Communication'}


    levels = {}
    paths = {}
    lookup = oldawardnames
    for item in oldawardnames:
        levels[item] = 0

    for p in pathids:
        for l in [1, 2, 3, 4, 5]:
            index = '%s%d' % (p, l)
            lookup[index] = '%s Level %d' % (pathids[p], l)
            levels[index] = l
            paths[index] = pathids[p]
