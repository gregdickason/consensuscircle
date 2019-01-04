--[[ Rolls Back the most recent block.  DOES NOT CHECK THAT IT IS THE MOST RECENT BLOCK SO MUST BE CALLED IN ORDER IF MULTIPLE BLOCKS TO BE ROLLED BACK
     ARGV[1] is blockHash to rollback state to the state BEFORE the block was published.  
--]]

local name = "rollbackBlock"
  
  -- loop through all keys in a set, order not important.
  -- TODO: check set exists?
  -- We are storing the state against a blockhash as the state BEFORE that block was applied
  local members = redis.call("SPOP", "BlockState." .. ARGV[1])

  for keyCount = 1, #members do
  
  -- For members that existed before we rollback, for those that did not the state is "None" so we delete them. 
    local hashKeys = redis.call("HKEYS", "PrevBlock." .. ARGV[1] .. "." .. members[keyCount])   
    for hashKeyCount = 1, #hashKeys do
      local state = redis.call("HGET", "PrevBlock." .. ARGV[1] .. "." .. members[keyCount], hashKeys[hashKeyCount])
      if state ~= "None" then
        redis.call("HSET", members[keyCount], hashKeys[hashKeyCount], state)
      else
        redis.call("HDEL", members[keyCount], hashKeys[hashKeyCount])
      end
      
      -- delete the hash now
      redis.call("HDEL", "PrevBlock." .. ARGV[1] .. "." .. members[keyCount], hashKeys[hashKeyCount])
      
    end  
    
    -- NOTE we are deleting from table as we iterate.  On testing this seems safe but needs research to confirm         
    redis.call("SREM", "BlockState." .. ARGV[1], members[keyCount])
    
  end
  
  -- now move the processed instructions back to unprocessed pool and delete the processed pool
    redis.call("SUNIONSTORE", "instructionUnprocessedPool", "instructionUnprocessedPool", "instructionProcessedPool." .. ARGV[1])
    redis.call("DEL", "instructionProcessedPool." .. ARGV[1])
