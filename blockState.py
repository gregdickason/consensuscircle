import json
from bisect import bisect_left


# Holds the blockState for the current chain we are following that we believe is valid.  We can change this if presented with a better block or chain (Where depth weighted chain distance is lower)
# This class is specific to the environment in which the agent is running.  Same method signatures but differnet implementations per environment
# This is for local agent with all settings and instructions in json files.  Production uses cloud technologies (eg S3)
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
    # get the agent public keys into a binary matrix
    
    self.agents = self.blockState['agents']
    self.agentPublicKeys = {}
    
    # define the levels we accept and the number per level:
    self.agentLevels = {'founder':1,'defender':1,'protector':1,'contributor':2}
    
    # Looks for levels.  This is not efficient but will not be used in production (where these will be DB lookups)
    # storing in lists so we can sort and find nearest matches.  Will slow down if we need to remove some numbers (eg if nearest not available)
    self.level = {}
    self.level['founder'] = [] 
    self.level['defender'] = [] 
    self.level['protector'] = [] 
    self.level['contributor'] = [] 
    
    for e in self.agents:
      self.agentPublicKeys[e['agentID']] = e['agentPubKey']
      self.level[e['level']].append(e['agentID'])
    
    # sort the level lists to make it more efficient and use takeClosest (note sorting is highly optimised in Python)
    for e in self.level:
      self.level[e].sort()
      
  def getPubKey(self, pubKey):
    return self.agentPublicKeys[pubKey]
  
  
  # Distance calculations for finding the nearest agent to a number for a level.  This is not optimised as will be in a data structure in Lambda
  # currently it is order of log(n) 
  def nextCircle(self,lastBlockMatrix, excludedAgents):
    nextcircle, bIndex = [],0
    self.templevel = self.level.copy()
    
    # remove all th excludedAgents per level:
    for level in excludedAgents:
      levelName = level['level']
      for i in level[levelName]:
        self.templevel[levelName].remove(i)
    
    # find next agent and delete from level so cant be chosen twice:    
    for i in self.agentLevels.keys():
      j = 0
      while j < self.agentLevels[i]:
        # note deletes the templevel agent in the takeClosest method
        nextAgent = self.takeClosest(self.templevel[i],lastBlockMatrix[bIndex])
        nextcircle.append(nextAgent)
        self.templevel[i].remove(nextAgent)
        bIndex += 1
        j += 1
    return nextcircle   
        
  
  # Utility functions we dont need when using a database / dynamoDB etc:
  # from https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value/12141511#12141511
  def takeClosest(self,myList, myNumber):
      """
      Assumes myList is sorted. Returns closest value to myNumber.
      If two numbers are equally close, return the smallest number.
      Ignore anything in the excludedList
      """
      
        
      # for efficiency could remove before returning (rather than search through twice on the return call)      
      pos = bisect_left(myList, myNumber)
      if pos == 0:
          return myList[0]
      if pos == len(myList):
          return myList[-1]
      before = myList[pos - 1]
      after = myList[pos]
      if int(after,16) - int(myNumber,16) < int(myNumber,16) - int(before,16):
         return after
      else:
         return before

