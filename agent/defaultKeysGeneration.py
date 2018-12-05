from agentUtilities import signMessage, verifyMessage, signMessageFromPassPhrase, verifyMessageFromPassPhrase, getPublicKeyFromPassPhrase, getPrivateKeyFromPassPhrase, getHashofInput

passphraseList = ['I am agent 5000', 'I am agent 5001', 'I am agent 5002', 'I am agent 5003', 'I am agent 5004', 'I am agent 5005', 'I am agent 5006',
                  'I am agent 5007', 'I am agent 5008', 'I am agent 5009', 'I am agent 5010', 'I own agent 5000', 'I own agent 5001', 'I own agent 5002',
                  'I own agent 5003', 'I own agent 5004', 'I own agent 5005', 'I own agent 5006', 'I own agent 5007', 'I own agent 5008', 'I own agent 5009',
                  'I own agent 5010']
keys = {}
keys['passphrase'] = ''
keys['private key'] = ''
keys['public key'] = ''
keys['agentID'] = ''
for k in passphraseList:
    keys['passphrase'] = k
    keys['private key'] = getPrivateKeyFromPassPhrase(k)
    keys['public key'] = getPublicKeyFromPassPhrase(k)
    keys['agentID'] = getHashofInput(keys['public key'])
    keys['signedID'] = signMessageFromPassPhrase(keys['agentID'], k)
    print(keys)
