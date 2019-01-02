--[[ Clears the mining temporary data used while the agent is working on a candidate block.  This script resets any state for the next time a candidate block
     is needed to be built.  
     Method takes no arguments
--]]

local name = "clearMining"
  
  -- loop through all keys in the mining set and delete the hash, plus corresponding set (done through the POP).
  -- Cant use SPOP as non deterministic (even though we dont care we are removing all elements)
  local members = redis.call("SMEMBERS", "mining")

  for keyCount = 1, #members do
    -- delete all the contents of these hashes.  
    redis.call("DEL", members[keyCount])
    
    -- NOTE we are deleting from table as we iterate.  On testing this seems safe but needs research to confirm
    redis.call("SREM", "mining", members[keyCount])    
  end
    
    