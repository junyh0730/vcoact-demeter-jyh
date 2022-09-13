class Parser():
    def __init__(self):
        #type
        return

    def transPktToData(pkt):
        strings = pkt.split(' ')
        types = strings[0]

        if types == 'act':
            #|Type|Target|core_num|
            target = strings[1]
            core_num = strings[2]
            return [types, target, core_num, ""]
            
        elif types == 'info':
            #|Type|Target|core_num|util|
            target = strings[1]
            core_num = strings[2]
            util = strings[3]
            return [types, target, core_num, util]

    def transInfoToPkt(target, utils):
        l_info = list()
        for core, u in enumerate(utils):
            info = "info " + str(target) + " " + str(core) + " " +str(u)
            info = info.encode('utf-8')
            l_info.append(info)
        
        return l_info
    
    def transActToPkt(target, core_num):
        act = "act " + str(target) + " " + str(core_num)
        act = act.encode('utf-8')
        return act

     
        