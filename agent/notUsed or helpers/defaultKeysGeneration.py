from agentUtilities import signMessage, verifyMessage, signMessageFromPassPhrase, verifyMessageFromPassPhrase, getPublicKeyFromPassPhrase, getPrivateKeyFromPassPhrase, getHashofInput
import re

passphraseList = ['I am agent 5000', 'I am agent 5001', 'I am agent 5002', 'I am agent 5003', 'I am agent 5004', 'I am agent 5005', 'I am agent 5006',
                  'I am agent 5007', 'I am agent 5008', 'I am agent 5009', 'I am agent 5010', 'I own agent 5000', 'I own agent 5001', 'I own agent 5002',
                  'I own agent 5003', 'I own agent 5004', 'I own agent 5005', 'I own agent 5006', 'I own agent 5007', 'I own agent 5008', 'I own agent 5009',
                  'I own agent 5010']
keys = {}
keys['passphrase'] = ''
keys['private key'] = ''
keys['public key'] = ''
keys['agentID'] = ''
count = 0
for k in passphraseList:
    keys['passphrase'] = k
    keys['private key'] = getPrivateKeyFromPassPhrase(k)
    keys['public key'] = getPublicKeyFromPassPhrase(k)
    keys['agentID'] = getHashofInput(keys['public key'])
    if count < 11: # eventually change this if we keep using this script to flag whenever I am
        owner = re.sub('^I am', 'I own', k)
        keys['ownerID'] = getHashofInput(getPublicKeyFromPassPhrase(owner))
        keys['signedID'] = signMessageFromPassPhrase(keys['agentID'], owner)
    if count == 11:
        del keys['ownerID']
        del keys['signedID']
    count = count + 1
    print(keys)
