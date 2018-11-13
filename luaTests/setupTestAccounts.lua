--[[ sets up some baseline data for testing other LUA functions.  This creates the 2 pubKeys and adds attributes to their hashes
     first we add all the agents to the entities set. Then their owners.  Then add wallets to the owners
--]]
  redis.call("SADD", "entities", "17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920")
  redis.call("SADD", "entities", "17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920")
  redis.call("SADD", "entities", "cb4d24f31f25703dd89fee5aa4813f55a16ce8d05d76af819e02b5c9f7ace7b2")
  redis.call("SADD", "entities", "5cbda1c61193fbd4644eeca3d9d5d6572ab8ac3399dcdcfa7241dcab509d2102")				
  redis.call("SADD", "entities", "f3d15dbd57deb8320663ebb5afa905ee2458445e6ab512911f39f9eea9a6f89c")				
  redis.call("SADD", "entities", "7a160e134c8bbcf888fc75083f18a9cc81722b70e96c20e35628e10b26cbac4e")
  redis.call("SADD", "entities", "66702543e7983626b4e193d4aa8e3ee8c8f1439a1707a91ad45719ad2945c8a6")				
  redis.call("SADD", "entities", "69600aaf355ced9104c1492187f2b7dc9a4946d81dd4e7035fac8dd5b1aebd88")
  redis.call("SADD", "entities", "f01764ff26d590bdfd8e7caa47036eeb897467b77ef1ec42ba4a6f6f77267cac")
  redis.call("SADD", "entities", "cf6f2b6faf657228e27799ab494afe8690b6078d27a435670c3cfa188eb5f5cc")
  redis.call("SADD", "entities", "3878540de6fc5f804a6241f4c2e2a4e68999ccf9d5a9ab9c2638d3790544ea38")
  redis.call("SADD", "entities", "8c00463f8522506def6f41384f168be18d8d3e14b7f205903d6b11122568e53b")	
  
  redis.call("SADD", "entities", "5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c")
  redis.call("SADD", "entities", "a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100")
  redis.call("SADD", "entities", "1874d743da77d67793e424958b06262daa3eefb2ea15fe64b6e646879ad5118d")
  redis.call("SADD", "entities", "dd1139e8c1b85e1488346d07c40a58013e73d2b91b104bcddc0bcff85d0b6ae7")
  redis.call("SADD", "entities", "6b6d614be7e3efc24748cf74d7f1524053f81cd414fd33a31ab141b396f9daf5")
  redis.call("SADD", "entities", "b2544ad676c98dc7c5943abd5137737555e4ee0c028cd5ef1bc7ad85be381a7f")
  redis.call("SADD", "entities", "9794ef206d2e437f7c758df72426a50357a907fc22eaf3549405b41cedbd8b4c")
  redis.call("SADD", "entities", "ba3580be86c485d2d4f617274f9de52d4d3d7534b2c5358b03152cfb50f5ad6a")
  redis.call("SADD", "entities", "e668ea3d173f6ce6bba10dfe24d549f147bd83b704d32d8596413f642258fae4")
  redis.call("SADD", "entities", "217a3b4fc645c761d6f3e462d50637869d1c6a93b1ae78f0652113ab1490742f")
  redis.call("SADD", "entities", "fff2b0decdb5b4d625f4b1fab18bd0316145f81630701ce986aa93bf01a6a7f6")
  
  redis.call("HSET","5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c", "wallets.default.balance", "0")
  redis.call("HSET","5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c", "PublicKey", "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFbU5FZVpEOWk1SW1iUUE0MFRHQjdZTHVqdjM2KwpYNzlKUXFhSVdkbEVaejNxUHl6VWJ0ZnZaQ24xSG5wUGJuVW1Kc3hQa1gxaWZ0bUFZTytUaEFqMHpRPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg==")
  redis.call("HSET","5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c", "permissions.all", "[5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c]")
  redis.call("HSET","5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c", "permissions.identity.citizenship.british.status", "[a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100]")
  redis.call("HSET","5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c", "identity.name", "Gregory Dickason")
  redis.call("HSET","5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c", "identity.citizenship.british.status", "claimed")
  
  redis.call("HSET","a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100", "wallets.default.balance", "1000000")
  redis.call("HSET","a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100", "PublicKey", "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFaVUyOHlHcDdqbEFCaG5LWXc2QzhHZ0FzYXFscwpOeHhBK2FXZCt1eEl5bU13OVNFUmJSV250Y3ZWcmY5WTRiVFRsenAxTjNqaURXR1gxdk9iWlQ3V0RnPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg==")
  redis.call("HSET","a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100", "permissions.all", "[a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100]")
  redis.call("HSET","a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100", "identity.name", "Cameron McEwan")
  redis.call("HSET","a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100", "identity.citizenship.australian.status", "verified")
  
  
  
