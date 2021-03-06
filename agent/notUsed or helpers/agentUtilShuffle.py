from agentUtilities import signMessage, verifyMessage, signMessageFromPassPhrase, verifyMessageFromPassPhrase, getPublicKeyFromPassPhrase, getPrivateKeyFromPassPhrase

sig = signMessage("aaa", '85d78c74d0f2495c63f04a24eea02f52a41c47539a66289f59a4dc90371dd62e')
print(sig)

msg = "aaa"
pubKey = '046e892457c8c3452595d595ef029cb7e5260ab4da44712a4c09b61971ae75b5a0828b2e9987df12007d7aad579bda3bf7c1b8a6dd963568ec4487a97115a2cd01'
signature = '3044022051e084b33cc8f7f9e0f29760c10e0f4d532eada774a514938c6e5d3ced16abb4022058587e532598837808c20c86997f4f7e19b83a2f418d103185a3d5167d9fe3ce'

print(verifyMessage(msg, signature, pubKey))

sigMsg = signMessageFromPassPhrase('aaa', 'cameron')
print(sigMsg)

print(verifyMessageFromPassPhrase('aaa', sigMsg,  'cameron'))

print(getPublicKeyFromPassPhrase('cameron'))
print(getPrivateKeyFromPassPhrase('cameron'))

# testing signature generated by js
signature = '3046022100ff854b385107c64b24e505a0680e652641ab0b6569552ddf21484ef72b0479af022100f83271f79fdd065e0752d1882b95242d43a8ff70125bd95e2e134bf7397e0b3e'
print(verifyMessageFromPassPhrase('aaa', signature, 'cameron'))
