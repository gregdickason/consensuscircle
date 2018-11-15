--[[ simple payment from the originator to the receiver.  THis is for test only as does not take miner fees
     KEYS[1] is originator (payer) pubKey, KEYS[2] is receiver pubkey
     ARG[1] is the wallet the originator uses, ARG[2] is the receivers wallet
     ARG[3] is the amount to pay in whole numbers
--]]
if redis.call("EXISTS", KEYS[1]) == 1 and redis.call("EXISTS", KEYS[2]) == 1 then
  redis.call("HINCRBY", KEYS[1], ARGV[1], -ARGV[3])
  redis.call("HINCRBY", KEYS[2], ARGV[2], ARGV[3])
  return ARGV[1]
else
  return nil
end
