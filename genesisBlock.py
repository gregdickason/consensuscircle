import json

# For simulation purposes we dont care about instructions or validity just the output of the random vector that will be the root for the next block (determine participants)
# TODO complete this section next
class genesisBlock:
    def __init__(self):
        # The GenesisBlock is hardcoded with the seeds for the chain.  It is not parsed but provides framework for future blocks to be parsed
        self.outputMatrix = ['9c9345cf13413cd0ff0e6af4f33cce4f0555fb3a50364b64265b05ce134af28d','aa054baffa288cf1f3b56c18bf2c34c44a2663f4b8b99282e1e48f85daf1fa57','8b07655fa560fc2f2e1a072d877859bc70b801713f71d3d914f265423ed1bf54','dba0b0dc94f405d2d1112d0bde4b33da8fbc9b7902dd7088b0b76c14afb6e359', 'e2548ec967f73c6ddaaf19b39c0ad8aab58ef8d7f310d5e36a653f9634f166d8']
        self.merkleTreeRoot = '47a07ff7971b0f342e0a832be6776310922f19987873e3bec955d3fc54162d86'
        
        # To give all people everywhere the security of an independent witness for what they own, who they are, and what they can do.
        self.blockHash = '695E4A0C4F763FC95DFD6C29F334CC2EAF9C4A2BAFCCE09379B0864EDA001EB4'   
        self.previousBlock = ''
        self.blockHeight = 0
        self.circleDistance = 0
        # add in the single instruction - where do we put this?
        self.instructionOpensCount = 1
        self.blockEntityCreateCount = 5   # Create the first 5 agents: 1 level 0, 2 level 1 and 2 level 2
        
