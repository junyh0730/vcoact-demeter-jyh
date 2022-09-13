from actor.actor import Actor

class ActorVM(Actor):
    def __init__(self,env):
        self.cur_t_core = env.max_core
        self.cur_vq_core = env.max_core
        return
    