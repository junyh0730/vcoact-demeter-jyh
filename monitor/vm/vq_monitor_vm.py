from bcc import BPF
class VQMonitorVM():
    def __init__(self, env): 
        self.env = env
        f = open("/home/vm/vcoact/monitor/vm/vqm_ebpf.c")
        bpf_text = f.read()
        #text replace
        bpf_text = bpf_text.replace(
            'DEF_MAX_CORE', "#define MAX_CORE " + str(env.max_core))
        
        self.b = BPF(text=bpf_text)
        self.dist_irq = self.b.get_table("dist_irq")
        self.start_softirq_usage = []
        self.end_softirq_usage = []
        return

    def start(self):
        #start record
        #self.clear_softirq_usage()
        self.start_softirq_usage = self.read_softirq_usage()
        return
    
    def end(self):
        #end record
        #self.rst = self.read_softirq_usage()
        self.end_softirq_usage = self.read_softirq_usage()
        return
    
    def get(self,diff_time):
        rst = []
        for start,end in zip(self.start_softirq_usage,self.end_softirq_usage):
            r = round((end - start) * 100 / diff_time, 3)
            rst.append(r)

        return rst
    
    def read_softirq_usage(self):
        l_softirq_usage = [0.0] * self.env.max_core
        dist = self.dist_irq
        for k, v in sorted(sorted(dist.items(), key=lambda dist: dist[0].cpu), key=lambda dist: dist[0].vec):
            if "net_rx" or "net_tx" in self.vec_to_name(k.vec):
                if k.cpu < self.env.max_core:
                    l_softirq_usage[k.cpu] += v.value
        #self.dist_irq.clear()
        print("softirq: ", l_softirq_usage)
        return l_softirq_usage

    def clear_softirq_usage(self):
        self.dist_irq.clear()

    def vec_to_name(self, vec):
        return ["hi", "timer", "net_tx", "net_rx", "block", "irq_poll",
                "tasklet", "sched", "hrtimer", "rcu"][vec]
