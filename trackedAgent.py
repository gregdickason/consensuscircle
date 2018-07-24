
# Class used to track each agent in the circle (even if we are not directly connected to them).  
# It tracks to ensure that both direct and indirect messages about an agent report the same thing (and if not if we trust them or lose trust in the sending party)
class trackedAgent:
    def __init__(self, signedHash):
        self.agentSign = signedHash  # This is the signature of the previous block.  
        self.agentId = ''
        self.randomVectorHashes = []
        self.seed = 0
        self.instructionMerkleRoot = ''
        self.instructionHandlerMerkleRoot = ''
        self.signedInstructionMerkleRoot = ''
        self.signedInstructionHandlerMerkleRoot = ''
        
        self.trusted = True  # is this trackedAgent trusted?
        # add in gossip metrics: what does this agent think of other agents?
        self.untrustedList = {}
        self.trustedList = {}  
        
        # TODO: add in evidence for why agent is untrusted so can propagate this (in event they send us something untrusted that is provable)

        