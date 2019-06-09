--[[ simple payment from the originator to the receiver.  This is for test only as does not take miner fees
     Expected behaviour in production is that this is not included in scripts.txt and therefore is not loaded.
     TESTING ONLY
     Wallet used is presumed to be the default wallet (wallets.default)

     KEYS[1] is originator pubKey (inserted automatically),
     KEYS[2] is receiver pubkey

     ARGV 1,2,3 are all standard for instructions: 1: mining/mined (if testing mining or processing mined block, instruction hash, blockHash if in a block or 'None' if in mining mode

     ARGV[1]: 'mining / mined'
     This is there automatically.  As this is testing it is ignored (so balance can go negative)
       if 'mining' we update the mining state not the actual entity state
       if 'mined' the balance for sender, receiver and mining fees are taken and payments made.  Assuming no sharding

     ARGV[2] is instructionHash to check and remove from pool if instruction passes
     ARGV[3] is blockHash to rollback state (ignored)(this is the state of the chain immediately before applying this block), also used to store the processed instructions in a hash

     ARG[4] is the amount to pay in whole numbers
--]]
if redis.call("EXISTS", KEYS[1]) == 1 and redis.call("EXISTS", KEYS[2]) == 1 then
  redis.call("HINCRBY", KEYS[1], "wallets.default.balance", -ARGV[4])
  redis.call("HINCRBY", KEYS[2], "wallets.default.balance", ARGV[4])
  return {"1", "success"}
else
  return {"0", "does not exist"}
end
