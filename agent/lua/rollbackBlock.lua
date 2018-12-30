--[[ Rolls Back the most recent block.  DOES NOT CHECK THAT IT IS THE MOST RECENT BLOCK SO MUST BE CALLED IN ORDER IF MULTIPLE BLOCKS TO BE ROLLED BACK
     ARGV[1] is blockHeight to rollback state (python sends this)
--]]

local name = "rollbackBlock"
  
  -- loop through all keys in a set, order not important.
  -- TODO: check set exists?
  local member = redis.call("SPOP", "BlockState." .. ARGV[1])

  while (member ~= nil)
  
  -- For members that existed before we rollback, for those that did not the state is "None" so we delete them. 
    local hashKeys = redis.call("HKEYS", "PrevBlock." .. ARGV[1] .. "." .. member)   
    for keyCount = 1, #hashKeys do
      local state = redis.call("HGET", "PrevBlock." .. ARGV[1] .. "." .. member, hashKeys[keyCount])
      if state ~= "None"
        redis.call("HSET", member, hashKeys[keyCount], state)
      else
        redis.call("HDEL", member, hashKeys[keyCount])
      end
      
      -- delete the hash now
      redis.call("HDEL", "PrevBlock." .. ARGV[1] .. "." .. member, hashKeys[keyCount])
      
    end  
    
    member = redis.call("SPOP", "BlockState." .. ARGV[1])
    
  end