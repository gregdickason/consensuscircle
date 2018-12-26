--[[ simple payment from the originator to the receiver.  This is not setup for sharding yet but does take mining fees (as supplied by the originator).
     KEYS[1] is originator pubKey, 
     KEYS[2] is pubkey of payer (pays the actual payment - can be different to the originator if they have permissions on the wallet for this script) 
     KEYS[3] is receiver pubkey
     
     TODO: take payment from originators wallet (and check if same as payer then fees for both have sufficient balance)
     TODO: take in a nonce and a sequence.  Nonce cant be replayed, sequence we check within a few 10's of transactions and reject if too low 
     (so can take out of order but only 'close' to most recent --> range is 20.  height +- 20.
     nonce prevents replay attacks but is short lived (last 20 nonces)
     
     TODO: if successful remove instruction from pool.  
     
     TODO: data associated with payment (eg description) to be stored with instruction but not in redis
     TODO: blockchain long term storage reduced to headers only for scalability (instructions kept off chain), then further to instructionMerkle root chain (can have a global merkel roo for instructions with current block plus previous hashed: gives single checkpoint?)
       
     ARGV[1]: 'test'  - looks local state and sees if will work
     if 'mining' it is a balance check to confirm that the payment does not exhaust the balance.  This is 
       done to a separate 'mining' state where the balance is decremented for the sender and NOT incremented for receiver.
       The sender needs enough confirmed funds from the most recent blockchain state to process all instructions.  Once balance reaches 0 
       further instructions are rejected.  
       TODO: clean up from mining once a round completed.  DELETE mining hashes ('mining'. ... --> may have to use a set to track these?)
       
       if 'mined' the balance for sender, receiver and mining fees are taken and payments made.  Assuming no sharding
       TODO: put in sharding.  
       TODO: we store last 6 blocks state in memory and merge states as bocks become permanent?  So have pool, block 0 (top), 1 (2 below)... 5 (6 below), with 5 'permament'.   updates to pool, as
     blocks written we delete 5 and make 4 permanent and cycle.  If a fork occurs we go back to that version and replay all instructions into pool?
     ARGV[2] is instructionHash to check 
     ARGV[3] is the wallet the payer uses, ARGV[4] is the receivers wallet
     ARGV[5] is the amount to pay in whole numbers
     ARGV[6] is blockHeight to rollback state (python sends this)
     ARGV[7] is instructionFee 
     TODO: update entity with a progressive entity hash (updates hashed with existing entity hash?)
     TODO: add a warning code for if not processed as balance too low for example (eg out of funds). 
     -1 failure and removed from pool, 0 is warning (not processed but in pool), 1 is success and removed
     comments for each response.  
--]]

-- name of instructionType
local name = "simplePayment"

-- Check if originator, payer and payee on this chain:
if redis.call("SISMEMBER", "entities", KEYS[1]) == 1 and redis.call("SISMEMBER", "entities", KEYS[2]) == 1 and redis.call("SISMEMBER", "entities", KEYS[3]) == 1 then
  
  redis.call('ECHO', 'in the lua script' .. KEYS[1])
  -- Check permissions for originator to use payers wallet and the amount to pay
  
  if redis.call("HEXISTS", KEYS[2], "permissions." .. KEYS[1] .. ".all") ~= 1 then
    -- no permissions, TODO: return reason code too for logging?
    return {"0", "not permitted to execute"}
  end

  -- Check wallet exists: cant transfer funds if wallet does not exist.
  if redis.call("HEXISTS", KEYS[1], "wallets.default.balance") ~= 1 or redis.call("HEXISTS", KEYS[2], ARGV[3]) ~= 1 or redis.call("HEXISTS", KEYS[3], ARGV[4]) ~= 1 then
    return {"0", "wallet does not exist"}
  end
  
    -- checking permissions for payment.  If not allowed then abort.  Limit payment will determine if there is a limit on what the payer can pay
    -- This checks if payer has all permissions, or wallet specific permissions.  This script does not have standalone permissions to access 
    -- a wallet but some scripts can have (i.e. combined permissions of script and user --> instruction handler type which removes permissions once done)
  if redis.call("HEXISTS", KEYS[2], "permissions." .. KEYS[1] .. ".all") ~= 1 and redis.call("HEXISTS", KEYS[2], "permissions." .. KEYS[1] .. "." .. ARGV[3]) ~= 1 then
    -- dont have permissions to do this payment
    return {"0", "not permitted to execute"}
  end
 
  
  -- check if we are testing the block and decrementing or if this is a new block (mining or mined)
  if ARGV[1] == "mining" then
    -- we are mining so: copy the balance if not in the mining pool.  Check if can decrement, decrement if possible, return 0 / 1
    -- TODO: check that the originator has the funds to pay the fees (they are not necessarily the same as the payer so have to treat ARG[5] and ARG[7] separately)
    if redis.call("HEXISTS", "mining." .. KEYS[2], ARGV[3]) == 0 then
      -- not yet copied into mining pool, copy
      balance = redis.call("HGET", KEYS[2], ARGV[3])  
      redis.call("HSET", "mining." .. KEYS[2], ARGV[3], balance )
    end

    if redis.call("HGET", "mining." .. KEYS[2], ARGV[3]) >= (ARGV[5] + ARGV[7]) then
      -- sufficient balance: decrement for this mining round
      redis.call("HINCRBY", "mining." .. KEYS[2], ARGV[3], -ARGV[5] - ARGV[7])
      return {"1", "success"}
    else
      -- insufficient balance.  deny payment for this mining round
      return {"0", "insufficient balance"}
    end 
  else 
    -- we are processing mined block so add to balances / decrement etc. Include transaction fees.
    --  Fail if insufficient funds (which will fail the whole block and require a rollback)
    if tonumber(redis.call("HGET", KEYS[2], ARGV[3])) < tonumber((ARGV[5] + ARGV[7])) then
      return {"0", "insufficient balance"}
    end
  end
  
    -- All checks passed, into write mode:
    -- update previous block state if not already stored (TODO: delete state from block n - 5 in python, setup block n-1 in python, setup miner fees to rollback in python, etc) 
  if redis.call("HEXISTS", ARGV[6] .. "." .. KEYS[2], ARGV[3]) == 0 then     
    local payerState = redis.call("HGET", KEYS[2], ARGV[3])
    redis.call("HSET", ARGV[6] .. "." .. KEYS[2], ARGV[3], payerState)
  end

  if redis.call("HEXISTS", ARGV[6] .. "." .. KEYS[3], ARGV[4]) == 0 then     
    local payeeState = redis.call("HGET", KEYS[3], ARGV[4])
    redis.call("HSET", ARGV[6] .. "." .. KEYS[3], ARGV[4],payeeState)
  end

    
   -- change balances 
  redis.call("HINCRBY", KEYS[2], ARGV[3], -ARGV[5])
  redis.call("HINCRBY", KEYS[3], ARGV[4], ARGV[5])
  -- pay miner fees
  redis.call("HINCRBY", KEYS[2], ARGV[3], -ARGV[7])
  redis.call("HINCRBY", "circleFees", ARGV[6], ARGV[7])    
  return {"1", "success"}
  
  -- TODO: remove from pool the instruction, also need to check nonce and counter
  
else
  return {"0", "entity or entities unknown"}
end
