
from agentUtilities import getHashofInput, signMessage
import json
import time


# Class that emulates a consensus circle.  Loads the 5 private keys from the circle and
# creates a block from a candidateBlock
# Only used for testing

def consensusEmulator(candidateBlock):


  # get:
  #     # {'gossip': [{'17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920':
    #             {'previousBlock': '695E4A0C4F763FC95DFD6C29F334CC2EAF9C4A2BAFCCE09379B0864EDA001EB4',
    #             'instructionsMerkleRoot': 'c8fcdeb4fe643c368122da53c3ca92fd76634801d416ae68664bc13d16bd8b0b',
    #             'instructionCount': 1,
    #             'blockHeight': 0,
    #             'randomNumberHash': ['24f875bbde99270a3107f2983dc31195f0ef419bf83eeb1306aabf4a8e190ba6', 'a44d06440ac0cd6a1b24e4a4b224348493590d546cbdcad34f44449d51145a2b', '8277f91e9d59187edf78cf6d5c56cbc4118216ac0e6d998ba96f8618e25d051b', 'd650fc1d47c5d9ba80aa3a73d402bf8988da586a8c6d9728bd9ea221d299ad04', 'ad04a4676dd7bac39d5831a10b97870e81093e21dfb45a3b6e32548a327262b6']
    #             },
    #             'sign': 'bTDbEAU1R+Y2riI5QGZnU2QNroNgeLOl8UjrcxkM+8Y5pdovvETem9xuca3kFZ/oENJ97rL8EaqXEAuX1cYjwA==',
    #                'trusted': 1}
    #             ],
    #         'broadcaster': '17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920',
    #         'signedGossip': 'z9Ra2+sZqypR9Ev6iYn1l65Nhb6R/IRfT6h1wWTng4qeV6O6Oxc3XHmBNFLCxs9+JczQ28t9T4wjzk0XU8Oy0A==',
    #         'instructionHashes': ['5908a04a072f0beb2d7521bb9ec77662234c4a8ccb44d4e15541e91952380938'],
    #         'instructions': [{'source': '17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920', 'someRandom': 'e1148ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633', 'slots': [{'wallet': 0, 'escrowAmount': 200000, 'action': 'update', 'somethingelse to work out': '', 'target': 'abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)', 'timeout': 'timeInBlocksToAllow the next closest entity to update'}]}],
    #         'agentSettings': {'randomMatrix': ['731786ba2759286f2068c030a72de5ae5a11d3d8f0dd7d06d4a606eac6b80943', 'c2d36c11040e8f7085bc6dad1d0a53802c89ca0e4fd4aff49a55a773c3b716c3', '49ad5cf2bd108cd686f4f8f5d94c0ca8bc325fef946c5d194385e8e2d2daf7d5', 'ea48b75b62dc0c1ec5a8a8ab2379ccbe1f42d50266e929326a42e796db60efed', 'c9597ef7eae18437004d01288b2f51bb7cb4faa9e8ece755484efdfc16ebef09'],
    #         'seed': '2c917a7c9c79722822c482b809417606f7d73884dfd61828cabb8c33c34af2c1'}}


  print(f'\n\candidateBlock is {candidateBlock}')
  gossip = candidateBlock['gossip']
  print(f'\n\gossip  is {gossip}')

  print(f'\n\gossip values are {gossip[0]}')

  # hardcode the other agents
  agent1 = {}
  agent2 = {}
  agent3 = {}
  agent4 = {}

  agent1['id'] = 'cb4d24f31f25703dd89fee5aa4813f55a16ce8d05d76af819e02b5c9f7ace7b2'
  agent1['randomNumbers'] = ['33054faffa288cf1f3b56c18bf2c34c44a2663f4b8b99282e1e48f85daf1fa53','34054baffa288cf1f3b56c18bf2c34c44a2663f4b8b99282e1e48f85daf1fa52','55054baffa288cf1f3b56c18bf2c34c44a2663f4b8b99282e1e48f85daf1fa52','66054baffa288cf1f3b56c18bf2c34c44a2663f4b8b99282e1e48f85daf1fa55','77054baffa288cf1f3b56c18bf2c34c44a2663f4b8b99282e1e48f85daf1fa59']

  agent2['id'] = '5cbda1c61193fbd4644eeca3d9d5d6572ab8ac3399dcdcfa7241dcab509d2102'
  agent2['randomNumbers'] = ['3307655fa560fc2f2e1a072d877859bc70b801713f71d3d914f265423ed1bf53','4407655fa560fc2f2e1a072d877859bc70b801713f71d3d914f265423ed1bf55','5507655fa560fc2f2e1a072d877859bc70b801713f71d3d914f265423ed1bf54','6607655fa560fc2f2e1a072d877859bc70b801713f71d3d914f265423ed1bf51','7707655fa560fc2f2e1a072d877859bc70b801713f71d3d914f265423ed1bf51']
  agent3['id'] = 'f3d15dbd57deb8320663ebb5afa905ee2458445e6ab512911f39f9eea9a6f89c'
  agent3['randomNumbers'] = ['33b0b02c94f405d2d1112d0bde4b33da8fbc9b7902dd7088b0b76c14afb6e351','54b0b0dc94f405d2d1112d0bde4b33da8fbc9b7902dd7088b0b76c14afb6e359','55b0b0dc94f405d2d1112d0bde4b33da8fbc9b7902dd7088b0b76c14afb6e359','66b0b0dc94f405d2d1112d0bde4b33da8fbc9b7902dd7088b0b76c14afb6e351','77b0b0dc94f405d2d1112d0bde4b33da8fbc9b7902dd7088b0b76c14afb6e353']
  agent4['id'] = '7a160e134c8bbcf888fc75083f18a9cc81722b70e96c20e35628e10b26cbac4e'
  agent4['randomNumbers'] = ['33548ec967f73d6ddaaf19b39c0ad8aab58ef8d7f310d5e36a653f9634f166d4','74548ec967f73d6ddaaf19b39c0ad8aab58ef8d7f310d5e36a653f9634f166d3','55548ec967f73d6ddaaf19b39c0ad8aab58ef8d7f310d5e36a653f9634f166d7','66548ec967f73d6ddaaf19b39c0ad8aab58ef8d7f310d5e36a653f9634f166d2','77548ec967f73d6ddaaf19b39c0ad8aab58ef8d7f310d5e36a653f9634f166d2']

  agent1['privKey'] = 'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSU9VNnRPT0ZLUXZ3NGttQy9VQzdUMkpwaGZkZmJJVGJiNlJ0ZGE2ZHFJYXFvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFckhyMDJiOHAzVklIK084VmhENkYzUjhGQmZUcWxmYjVPVjZwdDhWazhUait4MlNQOTV1Ywo3L28zZ0tyVlhiL29paTdWSjdsazcvRVdwVllaa0FrN1hBPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo='
  agent2['privKey'] = 'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSUxCK0w1SGljQzhaU1RIcm1kaUpFVXNKMzlOZG4yOHYwRTF2MzRMVVRGcDZvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFckpkN1FtSm1WUWIxdUttNlEvTytCWXFZWWhyNElHaFNub3c5eFlGeS8rTTgxZHNVaVVGbAp5MG4rMjJEZkpWQlpRMnZyT3JJRU9tRWtrODBoRGR0UmRnPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo='
  agent3['privKey'] = 'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSUVNTGRvYlUzczZGTG8wbzNkZ21tTHpRMndDN21HdjdweDY1c0NpT0NmUm5vQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFZGtyOVpORSswR2JnOHNnZW9Hb1ZPSjdFTzhVd1Byei9QaUVzTVJEVnVwT3YxdFpVYUNHVgozaSsxa01tWlA4c3dBUm03WVJMMVlKTWZUdUl3Tks5K1d3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo='
  agent4['privKey'] = 'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSURXQzZQSHpQOStyUEpKK2JhNnkrdlFkazRQUWVLOXlEODJUL0VyOWZEZkhvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFMWg3cjFtdDd0elQzendyRVN3Vk9yK2hJRnp4TXhpeEpmTXRXUC90Z24zWE9XTENkSUY0RApUVm9Nc0xkTStzRlpiWnpMbFl0ZWVXSWxHcUtMRGk2dkdRPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo='

  gossipIndex = gossip[0]
  gossipKeys = list(gossipIndex.keys())
  print(f'\n\gossiKeys are {gossipKeys}')

  gossipSender = gossipKeys[0]
  gossipContents = gossipIndex[gossipSender]

  blockOut = {}
  blockOut['blockHeader'] = {}
  blockHeader = blockOut['blockHeader']
  blockHeader['version'] = '0.1'
  blockHeader['staticHeight'] = 10

  blockConvergenceHeader = {}
  blockConvergenceHeader['previousBlock'] = gossipContents['previousBlock']
  blockConvergenceHeader['instructionsMerkleRoot'] = gossipContents['instructionsMerkleRoot']
  blockConvergenceHeader['instructionHandlersMerkleRoot'] = gossipContents['instructionHandlersMerkleRoot']
  blockConvergenceHeader['instructionCount'] = gossipContents['instructionCount']
  blockConvergenceHeader['instructionHandlerCount'] = gossipContents['instructionHandlerCount']
  blockConvergenceHeader['blockHeight'] = gossipContents['blockHeight']
  randomNumbers = []
  # TODO the below is crap code but getting errors if dont setup dicts {} first
  dict0,dict1,dict2,dict3,dict4 = {},{},{},{},{}
  dict0[gossipSender] = candidateBlock['agentSettings']['randomMatrix']
  randomNumbers.append(dict0)
  # put in randomNumbers for other 4 agents
  dict1[agent1['id']] = agent1['randomNumbers']
  randomNumbers.append(dict1)
  dict2[agent2['id']] = agent2['randomNumbers']
  randomNumbers.append(dict2)
  dict3[agent3['id']] = agent3['randomNumbers']
  randomNumbers.append(dict3)
  dict4[agent4['id']] = agent4['randomNumbers']
  randomNumbers.append(dict4)

  #randomNumbers.append({agent1['id'],agent1['randomNumbers']})
  #randomNumbers.append({agent2['id'],agent2['randomNumbers']})
  #randomNumbers.append({agent3['id'],agent3['randomNumbers']})
  #randomNumbers.append({agent4['id'],agent4['randomNumbers']})

  blockConvergenceHeader['randomNumbers'] = randomNumbers

  blockHeader['convergenceHeader'] = blockConvergenceHeader

  consensusCircle = []
  circleMember0 = {}
  circleMember0['level'] = 'founder'
  circleMember0['publicKey'] = gossipSender
  consensusCircle.append(circleMember0)

  circleMember1 = {}
  circleMember1['level'] = 'defender'
  circleMember1['publicKey'] = agent1['id']
  consensusCircle.append(circleMember1)

  circleMember2 = {}
  circleMember2['level'] = 'defender'
  circleMember2['publicKey'] = agent2['id']
  consensusCircle.append(circleMember2)

  circleMember3 = {}
  circleMember3['level'] = 'protector'
  circleMember3['publicKey'] = agent3['id']
  consensusCircle.append(circleMember3)

  circleMember4 = {}
  circleMember4['level'] = 'protector'
  circleMember4['publicKey'] = agent4['id']
  consensusCircle.append(circleMember4)

  blockHeader['consensusCircle'] = consensusCircle

  hashConvergenceHeader = getHashofInput(json.dumps(blockConvergenceHeader))

  blockSignatures = []
  blockSig0 = {}
  blockSig0[gossipSender] = signMessage( hashConvergenceHeader, 'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSVBsOXp4ZTIwT254QmJaR2F6ZHdKS2xWZW5kRnFkZTZmY05acnU2MFV3cWVvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFcmw2ZnVrQnVKU241ZWZ2N21Mei90Y09RaGsrTXRTU0JZYnorNHBheWdueGo4MlQzZ0VZOQpsU1pseUtpUzdDVnd6QmF2WHpDZmpxeGtaa09hazZoR2J3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo=')   # hardcoded agent prikey TODO lookup it
  blockSignatures.append(blockSig0)

  blockSig1 = {}
  blockSig1[agent1['id']] = signMessage( hashConvergenceHeader, agent1['privKey'])
  blockSignatures.append(blockSig1)

  blockSig2 = {}
  blockSig2[agent2['id']] = signMessage( hashConvergenceHeader, agent2['privKey'])
  blockSignatures.append(blockSig2)


  blockSig3 = {}
  blockSig3[agent3['id']] = signMessage( hashConvergenceHeader, agent3['privKey'])
  blockSignatures.append(blockSig3)

  blockSig4 = {}
  blockSig4[agent4['id']] = signMessage( hashConvergenceHeader, agent4['privKey'])
  blockSignatures.append(blockSig4)

  blockHeader['blockSignatures'] = blockSignatures



  blockOut['blockHeader'] = blockHeader
  blockOut['blockHash'] = getHashofInput(json.dumps(blockHeader))
  blockOut['instructions'] = candidateBlock['instructions']
  blockOut['instructionHandlers'] = candidateBlock['instructionHandlers']

  print(f'block is \n {blockOut}')

  # now publish the block.  For emulation purposes we may wait for a period of time
  #time.sleep(10)

  # now write out the block to file, we can emulate the calling later for blockpublished
  with open(blockOut['blockHash'] + '.json', 'w') as outfile:
    json.dump(blockOut, outfile)

  return
