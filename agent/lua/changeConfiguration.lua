--[[ changes an attribute of an entity.  Simple not requiring verification.  This is not setup for sharding yet but does take mining fees (as supplied by the originator).
     KEYS[1] is originator pubKey (inserted automatically).  Pays mining fees
     KEYS[2] is entity to update
     
     TODO: take in counter to make unique and prevent replay attacks, counter used in ordering in the block.  Nonce cant be replayed, sequence we check within a few 10's of transactions and reject if too low 
     (so can take out of order but only 'close' to most recent --> range is 20.  height +- 20.
     
     TODO: data associated with update (eg description) to be stored with instruction but not in redis
     TODO: check data types on inbound
     NOTE: update does not apply to permissions (this is a separate instruction type)
       
     ARGV 1,2,3 are all standard for instructions: 1: mining/mined (if testing mining or processing mined block, instruction hash, blockHash if in a block or 'None' if in mining mode
     
     ARGV[1]: 'mining / mined'  
     if 'mining' it is a balance check to confirm that the fees do not exhaust the balance.  
       if 'mined' the attribute is updated
     ARGV[2] is instructionHash to check and remove from unprocessedpool if instruction passes
     ARGV[3] is blockHash to rollback state (this is the state of the chain immediately before applying this block), also used to store the processed instructions in a hash
 
     ARGV[4] is the attribute to update (can be created if not there)
     ARGV[5] is the updated value
     ARGV[6] is the previous value (for optimistic check that change is correct, can be null)
     ARGV[7] is incrementing counter to update state (will be rejected if state counter is greater than or equal to instruction counter) TODO - update NONCE value in the state
     ARGV[8] is evidence hash if evidence is provided
     ARGV[9] is link to evidence 
     ARGV[10] is flag if the attribute is encrypted
     ARGV[11] is flag if the evidence is encrypted 
     ARGV[12] is mining fee being paid (can be rejected if too low - up to agents)
--]]

-- name of instructionType
local name = "changeConfiguration"

-- Check if originator, entity on this chain:
if redis.call("SISMEMBER", "entities", KEYS[1]) == 1 and redis.call("SISMEMBER", "entities", KEYS[2]) == 1 then
  
  -- Check permissions for originator to update entity 
  if redis.call("HEXISTS", KEYS[2], "permissions." .. KEYS[1] .. ".all") ~= 1 and redis.call("HEXISTS", KEYS[2], "permissions." .. KEYS[1] .. ARGV[4]) ~= 1 then
    -- no permissions
    return {"0", "no permissions to update entity " .. KEYS[2] .. " for originator " .. KEYS[1]}
  end

  -- Check wallet exists: cant pay fees if wallet does not exist.
  if redis.call("HEXISTS", KEYS[1], "wallets.default.balance") ~= 1 then
    return {"0", "wallet does not exist to pay fees for originator " .. KEYS[1]}
  end
  
  -- Check if previous value is the same value we currently have (can be nil).  Fail if not 
  if redis.call("HEXISTS", KEYS[1], ARGV[4]
  GREG: here
  
  -- Check is counter is incremented above current state. Fail if not
  GREG: here
  
  
  -- check if we are mining the block or already mined
  if ARGV[1] == "mining" then
    -- we are mining so: copy the old attribute if not in the mining pool.  Check if can decrement wallet by mining fees, decrement if possible, return 0 / 1 as failure / success to stop mining 
    if redis.call("SMEMBER", "mining", KEYS[1]) == 0 then
        -- not yet copied into mining pool, copy
        balance = redis.call("HGET", KEYS[1], "wallets.default.balance")
        redis.call("SADD", "mining",KEYS[1])
        redis.call("HSET", "mining." .. KEYS[1], "wallets.default.balance", balance)
    end

    if redis.call("HGET", "mining." .. KEYS[1], "wallets.default.balance") >= ARGV[10] then
      -- sufficient balance: decrement for this mining round
      redis.call("HINCRBY", "mining." .. KEYS[1], "wallets.default.balance", -ARGV[10])
      return {"1", "in mining successfully processed " .. ARGV[2]}
    else
      -- insufficient balance.  deny payment for this mining round
      return {"0", "insufficient balance to pay mining fees for instruction " .. ARGV[2]}
    end 
  else 

   -- TODO: check why using tonumber here but not higher and in payment_adv??


    -- we are processing mined block so update and include transaction fees.
    --  Fail if insufficient funds (which will fail the whole block and require a rollback)

    if tonumber(redis.call("HGET", KEYS[1], "wallets.default.balance")) < tonumber(ARGV[10]) then
      return {"0", "insufficient balance for instruction " .. ARGV[2]}
    end
  end
  
   -- All checks passed, into write mode:
   -- update previous block state if not already stored (TODO: delete state from block n - 5 in python? or in more advanced LUA script, setup block n-1 in python, setup miner fees to rollback in python, etc) 
   -- we have a hash for this and a set to reduce costs of the rollback
 
  if redis.call("SMEMBER", "BlockState." .. ARGV[3], KEYS[1]) == 0 then
    local payerState = redis.call("HGET", KEYS[1], "wallets.default.balance")
    redis.call("SADD", "BlockState." .. ARGV[3],KEYS[1])
    redis.call("HSET", "PrevBlock." .. ARGV[3] .. "." .. KEYS[1], "wallets.default.balance", payerState)
  end

-- TODO.  GREG here: NOW CHECK JUST THIS ATTRIBUTE.  regardless of if other payments done.  COntinue here 

  if redis.call("SMEMBER", "BlockState." .. ARGV[3], KEYS[3]) == 0 then
    local payeeState = redis.call("HGET", KEYS[3], ARGV[5])
    redis.call("SADD", "BlockState." .. ARGV[3],KEYS[3])
    redis.call("HSET", "PrevBlock." .. ARGV[3] .. "." .. KEYS[3], ARGV[5], payeeState)
  end

    
   -- change balances 
  redis.call("HINCRBY", KEYS[2], ARGV[4], -ARGV[6])
  redis.call("HINCRBY", KEYS[3], ARGV[5], ARGV[6])
  -- pay miner fees
  redis.call("HINCRBY", KEYS[2], ARGV[4], -ARGV[7])
  redis.call("HINCRBY", "circleFees", ARGV[3], ARGV[7])    
  -- delete the instruction from the pool
  
  -- Flag deleted from instruction processed set (we dont delete as may rollback block and want to restore the instruction to the pool, full delete only happens when blockheight above when instruction was issued gets to order 'n')
  redis.call("SADD", "instructionProcessedPool." .. ARGV[3], ARGV[2])
  redis.call("SREM", "instructionUnprocessedPool", ARGV[2])
  return {"1", "success"}
  
  
else
  return {"0", "entity or entities unknown"}
end

