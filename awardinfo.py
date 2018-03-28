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

    pathids = {'DL': 'Dynamic Leadership',
               'EC': 'Effective Coaching',
               'IP': 'Innovative Planning',
               'LD': 'Leadership Development',
               'MS': 'Motivational Strategies',
               'PI': 'Persuasive Influence',
               'PM': 'Presentation Mastery',
               'SR': 'Strategic Relationships',
               'TC': 'Team Collaboration',
               'VC': 'Visionary Communication'}

    oldpathids = {'DYNLEA': 'Dynamic Leadership',
                  'EFFCOA': 'Effective Coaching',
                  'INNPLA': 'Innovative Planning',
                  'LEADEV': 'Leadership Development',
                  'MOTSTR': 'Motivational Strategies',
                  'PERINF': 'Persuasive Influence',
                  'PREMAS': 'Presentation Mastery',
                  'STRREL': 'Strategic Relationships',
                  'TEACOL': 'Team Collaboration',
                  'VISCOM': 'Visionary Communication'}

    newtoold = {'DL': 'DYNLEA',
                'EC': 'EFFCOA',
                'IP': 'INNPLA',
                'LD': 'LEADEV',
                'MS': 'MOTSTR',
                'PI': 'PERINF',
                'PM': 'PREMAS',
                'SR': 'STRREL',
                'TC': 'TEACOL',
                'VC': 'VISCOM'}

    oldtonew = {'DYNLEA': 'DL',
                'EFFCOA': 'EC',
                'INNPLA': 'IP',
                'LEADEV': 'LD',
                'MOTSTR': 'MS',
                'PERINF': 'PI',
                'PREMAS': 'PM',
                'STRREL': 'SR',
                'TEACOL': 'TC',
                'VISCOM': 'VC'}

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
