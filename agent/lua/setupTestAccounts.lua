--[[ sets up some baseline data for testing other LUA functions.  This creates the 2 pubKeys and adds attributes to their hashes
     first we add all the agents to the entities set. Then their owners.  Then add wallets to the owners
--]]
  redis.call("SADD", "entities", "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675")
  redis.call("SADD", "entities", "2efb6ec38d1f9ccfa4b1b88bd98ab9b09c4a484496a5713af177b971ccfb922b")
  redis.call("SADD", "entities", "2c24af4bd0889b10e325733c9b468779db7b2a82e9052df3b46a8aa1078262ea")
  redis.call("SADD", "entities", "031a3a259e059ec67971841a267528af2fc42bfcc1271259164b822fedf86102")
  redis.call("SADD", "entities", "5aebce47cab0ff962b7bfde34949f557e5826ccf0a8a572e2f8c8769deb8e58b")
  redis.call("SADD", "entities", "6c2add4237bd9ae4917edbbfc51277816196101affc79b46dc574c7b86df4ef9")
  redis.call("SADD", "entities", "97c4d1d971056016b841dfdfb759aa606d47d6b1d01af5d6b2552505c464f620")
  redis.call("SADD", "entities", "7a319d90121a0113df0333fdf8f4633167f23c398987391a0bbea55b1676ca4f")
  redis.call("SADD", "entities", "359c45d4cb0606f903249bea19da3c178940e2633f34f55c9dca4e425696c1a0")
  redis.call("SADD", "entities", "6724d8c191fc3346a7e7c2dea6b58b59111a5ff0cd9af4e69e8c4dfe195192db")
  redis.call("SADD", "entities", "eabdc2e1161a863042749d5fc6604f88a4714d9eda8bb094a7199d76dea24c11")

  redis.call("SADD", "entities", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f")
  redis.call("SADD", "entities", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507")
  redis.call("SADD", "entities", "36cbecda6927749d20bd7fed94d7c4228be1e3f65c7fbca6f1aec776f6037249")
  redis.call("SADD", "entities", "de92db7c4623db3acb5f8b36ff3e2e6d0bd73dd1490e4e03abf55b7bdaad6657")
  redis.call("SADD", "entities", "73756a58aa5751c33d6b30ec1c429b00a962646d063ab1c31c26e542bd1b3d69")
  redis.call("SADD", "entities", "c1f6bc67f27992a197d429603113a01fc79b3018f98b9fbf5d09aefc2b49c3b1")
  redis.call("SADD", "entities", "483da90cba7e9f6e693a1f4b67e925662a08ffc565300842a2c84498c77d12f1")
  redis.call("SADD", "entities", "2f82ada9116bfee825d28168fb356ad257f3d430cceee0851dcb935c39a003fc")
  redis.call("SADD", "entities", "e8f84726a97b390067e47f9087fe7e845131ac463689aeaf5f28f02a731d6b8e")
  redis.call("SADD", "entities", "2f7c0e8406d30fca3a42d58936896e2b2f0409c1ab29606f4d5b4321f0603d85")
  redis.call("SADD", "entities", "eabdc2e1161a863042749d5fc6604f88a4714d9eda8bb094a7199d76dea24c11")

  redis.call("HSET","d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "wallets.default.balance", "0")
  redis.call("HSET","d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "PublicKey", "0498d11e643f62e4899b400e344c607b60bba3bf7ebe5fbf4942a68859d944673dea3f2cd46ed7ef6429f51e7a4f6e752626cc4f917d627ed98060ef938408f4cd")
  redis.call("HSET","d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "permissions.all", "[d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f]")
  redis.call("HSET","d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "permissions.identity.citizenship.british.status", "[e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507]")
  redis.call("HSET","d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "identity.name", "Gregory Dickason")
  redis.call("HSET","d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "identity.citizenship.british.status", "claimed")

  redis.call("HSET","e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "wallets.default.balance", "1000000")
  redis.call("HSET","e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "PublicKey", "04894dbcc86a7b8e5001867298c3a0bc1a002c6aa96c371c40f9a59dfaec48ca6330f521116d15a7b5cbd5adff58e1b4d3973a753778e20d6197d6f39b653ed60e")
  redis.call("HSET","e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "permissions.all", "[e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507]")
  redis.call("HSET","e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "identity.name", "Cameron McEwan")
  redis.call("HSET","e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "identity.citizenship.australian.status", "verified")
