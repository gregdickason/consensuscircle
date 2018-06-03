import json

# Holds the blockState for the current chain we are following that we believe is valid.  We can change this if presented with a better block or chain (Where depth weighted chain distance is lower)
class blockState:
  def __init__(self):
    with open('currentBlockChainState.json') as json_data:
        self.blockState = json.load(json_data)  # TODO put in exception handling and error checking if file is malformed and also that this block is valid in the context of previous blocks
    print(f'Blockchain State is {self.blockState}')
    self.outputMatrix = self.blockState['blockRandomMatrix']
    self.merkleTreeRoot = self.blockState['blockMerkleRoot']  # Random for simulation 
    self.blockHash = self.blockState['blockHash']   # Hash of the highest block in chain
    self.blockHeight = self.blockState['blockHeight']
    self.depthWeightedChainDistancePreviousBlock = self.blockState['depthWeightedChainDistancePreviousBlock']
    print(f'\nprevious block convergence matrix is {self.outputMatrix}')