
# Class used to track each agent in the circle (even if we are not directly connected to them).  This is used to store the origin of instructions, randomVector outputs, and any gossip about other agents 
class trackedAgent:
    def __init__(self):
        self.randomVector = []
        self.randomVectorHashes = []
        self.seed = 0
        self.identifier = ''  # Would be the public key in the real network        
        self.instructions = []
        self.instructionHashes = set()
        self.trusted = True  # is this trackedAgent trusted?
        # add in gossip metrics: what does this agent think of other agents?
