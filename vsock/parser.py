from math import remainder


class Parser():
    def __init__(self):
        #type
        return

    def transPktToData(pkt):
        strings = pkt.decode('UTF-8')
        strings = strings.split('\n')
        res_strings = list()
        remainder = bytearray()

        for s in strings:
            a_s = s.split(' ')

            try: 
                types = a_s[0]
                target = a_s[1]
                core_num = a_s[2]
                util = a_s[3]
            except:
                remainder.extend(s.encode('utf-8'))
                break

            if types == 'act':
                #|Type|Target|core_num|
                res_strings.append([types, target, core_num, -1])
                
            elif types == 'info':
                #|Type|Target|core_num|util|
                res_strings.append([types, target, core_num, util])
        
        print(res_strings)
            
        return res_strings, remainder

    def transInfoToPkt(target, utils):
        s_info = ""
        for core, u in enumerate(utils):
            info = "info " + str(target) + " " + str(core) + " " +str(u) + " \n "
            info = info.encode('utf-8')
            s_info += info
        
        return s_info
    
    def transActToPkt(target, core_num):
        act = "act " + str(target) + " " + str(core_num) + " \n "
        act = act.encode('utf-8')
        return act

     
        