from math import remainder


class Parser():
    def __init__(self):
        #type
        return

    def transPktToData(pkt):
        strings = pkt.decode('utf-8')
        strings = strings.split('\n')
        res_strings = list()
        remainder = bytearray()

        for s in strings:
            a_s = s.split()

            try: 
                types = a_s[0]
                target = a_s[1]
                arg0 = a_s[2]
                arg1 = a_s[3]
            except:
                remainder.extend(s.encode('utf-8'))
                break

            res_strings.append([types, target, arg0, arg1])
                
            
        return res_strings, remainder

    def transInfoToPkt(target, utils):
        s_info = ""
        l_s = list()
        for core, u in enumerate(utils):
            s = ["info ",str(target)," " ,str(core)," ",str(u)," \n"]
            l_s.extend(s)
        s_info = s_info.join(l_s)
        s_info = s_info.encode('utf-8')
        return s_info
    
    def transTrafficToPkt(target, utils):
        s_info = ""
        l_s = list()
        s = ["info_traffic ",str(target)," " ,str(0)," ",str(utils)," \n"]
        l_s.extend(s)
        s_info = s_info.join(l_s)
        s_info = s_info.encode('utf-8')
        return s_info
    
    def transActToPkt(target, core_num):
        act=""
        act = act.join(["act ", str(target), " ", str(core_num), " \n"])
        print(act)
        act = act.encode('utf-8')
        return act

     
        
