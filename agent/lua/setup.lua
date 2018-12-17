--[[ set up agents --]]

if redis.call("EXISTS", "agents") == 0 then
  redis.call("SADD", "agents", "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675")
  redis.call("SADD", "agents", "2efb6ec38d1f9ccfa4b1b88bd98ab9b09c4a484496a5713af177b971ccfb922b")
  redis.call("SADD", "agents", "2c24af4bd0889b10e325733c9b468779db7b2a82e9052df3b46a8aa1078262ea")
  redis.call("SADD", "agents", "031a3a259e059ec67971841a267528af2fc42bfcc1271259164b822fedf86102")
  redis.call("SADD", "agents", "5aebce47cab0ff962b7bfde34949f557e5826ccf0a8a572e2f8c8769deb8e58b")
  redis.call("SADD", "agents", "6c2add4237bd9ae4917edbbfc51277816196101affc79b46dc574c7b86df4ef9")
  redis.call("SADD", "agents", "97c4d1d971056016b841dfdfb759aa606d47d6b1d01af5d6b2552505c464f620")
  redis.call("SADD", "agents", "7a319d90121a0113df0333fdf8f4633167f23c398987391a0bbea55b1676ca4f")
  redis.call("SADD", "agents", "359c45d4cb0606f903249bea19da3c178940e2633f34f55c9dca4e425696c1a0")

  redis.call("HSET", "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675", "ownerID", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f")
  redis.call("HSET", "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675", "signedID", "30440220273835a615c5b40afcbd8774684ae3dad27a1c0cdc413789591f12dab0f5d4b0022061cf224c65ae3e4e1d09e34ccd5b861fcba5fd772cd7a00db10d51c632e57c36")
  redis.call("HSET", "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675", "publicKey", "04ae5e9fba406e2529f979fbfb98bcffb5c390864f8cb5248161bcfee296b2827c63f364f780463d952665c8a892ec2570cc16af5f309f8eac6466439a93a8466f")
  redis.call("HSET", "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675", "agentURL", "http, //localhost, 5000")
  redis.call("HSET", "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675", "level", "founder")

  redis.call("HSET", "2efb6ec38d1f9ccfa4b1b88bd98ab9b09c4a484496a5713af177b971ccfb922b", "ownerID", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507")
  redis.call("HSET", "2efb6ec38d1f9ccfa4b1b88bd98ab9b09c4a484496a5713af177b971ccfb922b", "signedID", "304502206a7c377bbf7e693c904ff12cb418b7366cadd888a5ceb6e13ef411fa9a57cd02022100ca3c793a360f88da4b997dbe702743ad6d81f181af7530c19485c5ac1737950c")
  redis.call("HSET", "2efb6ec38d1f9ccfa4b1b88bd98ab9b09c4a484496a5713af177b971ccfb922b", "publicKey", "04ac7af4d9bf29dd5207f8ef15843e85dd1f0505f4ea95f6f9395ea9b7c564f138fec7648ff79b9ceffa3780aad55dbfe88a2ed527b964eff116a5561990093b5c")
  redis.call("HSET", "2efb6ec38d1f9ccfa4b1b88bd98ab9b09c4a484496a5713af177b971ccfb922b", "agentURL", "http, //localhost, 5001")
  redis.call("HSET", "2efb6ec38d1f9ccfa4b1b88bd98ab9b09c4a484496a5713af177b971ccfb922b", "level", "defender")

  redis.call("HSET", "2c24af4bd0889b10e325733c9b468779db7b2a82e9052df3b46a8aa1078262ea", "ownerID", "36cbecda6927749d20bd7fed94d7c4228be1e3f65c7fbca6f1aec776f6037249")
  redis.call("HSET", "2c24af4bd0889b10e325733c9b468779db7b2a82e9052df3b46a8aa1078262ea", "signedID", "304402202e40bf53e140a5da813a351893e134f3e058241c7e90ed018f86c85b4374bca502206f90fedccb105719db22932ab5d341ee2a6f76f18b41d62142bdb7de58fccd23")
  redis.call("HSET", "2c24af4bd0889b10e325733c9b468779db7b2a82e9052df3b46a8aa1078262ea", "publicKey", "04ac977b4262665506f5b8a9ba43f3be058a98621af82068529e8c3dc58172ffe33cd5db14894165cb49fedb60df255059436beb3ab2043a612493cd210ddb5176")
  redis.call("HSET", "2c24af4bd0889b10e325733c9b468779db7b2a82e9052df3b46a8aa1078262ea", "agentURL", "http, //localhost, 5002")
  redis.call("HSET", "2c24af4bd0889b10e325733c9b468779db7b2a82e9052df3b46a8aa1078262ea", "level", "protector")

  redis.call("HSET", "031a3a259e059ec67971841a267528af2fc42bfcc1271259164b822fedf86102", "ownerID", "de92db7c4623db3acb5f8b36ff3e2e6d0bd73dd1490e4e03abf55b7bdaad6657")
  redis.call("HSET", "031a3a259e059ec67971841a267528af2fc42bfcc1271259164b822fedf86102", "signedID", "30460221008d4ed32760ed5fed26d587cbf74b3aee5d5e54d922cadf818ec22e5086622905022100d5298c526de481f25e301899f9453b04c86a829d92551c4248aa33f49e879ebc")
  redis.call("HSET", "031a3a259e059ec67971841a267528af2fc42bfcc1271259164b822fedf86102", "publicKey", "04764afd64d13ed066e0f2c81ea06a15389ec43bc5303ebcff3e212c3110d5ba93afd6d654682195de2fb590c9993fcb300119bb6112f560931f4ee23034af7e5b")
  redis.call("HSET", "031a3a259e059ec67971841a267528af2fc42bfcc1271259164b822fedf86102", "agentURL", "http, //localhost, 5003")
  redis.call("HSET", "031a3a259e059ec67971841a267528af2fc42bfcc1271259164b822fedf86102", "level", "contributor")

  redis.call("HSET", "5aebce47cab0ff962b7bfde34949f557e5826ccf0a8a572e2f8c8769deb8e58b", "ownerID", "73756a58aa5751c33d6b30ec1c429b00a962646d063ab1c31c26e542bd1b3d69")
  redis.call("HSET", "5aebce47cab0ff962b7bfde34949f557e5826ccf0a8a572e2f8c8769deb8e58b", "signedID", "3044022026b534b078b772efd2efce799f01584d3ffc6e4f4076df52e73beecb280a52fe02204da560781079891c1761e4c22c90b8f15df1b33608c79ec446ee057a33a3aaf4")
  redis.call("HSET", "5aebce47cab0ff962b7bfde34949f557e5826ccf0a8a572e2f8c8769deb8e58b", "publicKey", "04d61eebd66b7bb734f7cf0ac44b054eafe848173c4cc62c497ccb563ffb609f75ce58b09d205e034d5a0cb0b74cfac1596d9ccb958b5e7962251aa28b0e2eaf19")
  redis.call("HSET", "5aebce47cab0ff962b7bfde34949f557e5826ccf0a8a572e2f8c8769deb8e58b", "agentURL", "http, //localhost, 5004")
  redis.call("HSET", "5aebce47cab0ff962b7bfde34949f557e5826ccf0a8a572e2f8c8769deb8e58b", "level", "contributor")

  redis.call("HSET", "6c2add4237bd9ae4917edbbfc51277816196101affc79b46dc574c7b86df4ef9", "ownerID", "c1f6bc67f27992a197d429603113a01fc79b3018f98b9fbf5d09aefc2b49c3b1")
  redis.call("HSET", "6c2add4237bd9ae4917edbbfc51277816196101affc79b46dc574c7b86df4ef9", "signedID", "30440220793490d4a18fed4169c9827154ebc3c959c8860397e2c2745b9549b755014c960220491aef4e750d49e367744a84e6a4ee78f44ce791cf5408140340ff3fb0a8414c")
  redis.call("HSET", "6c2add4237bd9ae4917edbbfc51277816196101affc79b46dc574c7b86df4ef9", "publicKey", "048a7319a69459de3c85c7baa6abf1fb7afcc2b5d7b9b71adb77bdd8418e7c8d918b40a52a92700113b7bc00dddb6e7643f2ceb7c3a16d74e323314ed1a035a89a")
  redis.call("HSET", "6c2add4237bd9ae4917edbbfc51277816196101affc79b46dc574c7b86df4ef9", "agentURL", "http, //localhost, 5005")
  redis.call("HSET", "6c2add4237bd9ae4917edbbfc51277816196101affc79b46dc574c7b86df4ef9", "level", "contributor")

  redis.call("HSET", "b5cf01dd19b17a2eb7b7fea1a254f47e286927942fb532388922e4368ea33786", "ownerID", "483da90cba7e9f6e693a1f4b67e925662a08ffc565300842a2c84498c77d12f1")
  redis.call("HSET", "b5cf01dd19b17a2eb7b7fea1a254f47e286927942fb532388922e4368ea33786", "signedID", "304502200c68b0028eb710dd60e441b7c4eded6f8f1362f66ff3abd945a0177ff3caed910221008f076c378d423e7fb0bc48600b1b8e5a368c15dd3e679ecaaaae0c1cf2b79f42")
  redis.call("HSET", "b5cf01dd19b17a2eb7b7fea1a254f47e286927942fb532388922e4368ea33786", "publicKey", "04ca9e079cceaa3c6c64bd1286d7972f8215dd2dcee857064b2e1caf71b1dd594024ac99996806734f498b1234e450ddf013b1045187657ee1abd494ba99fe6e52")
  redis.call("HSET", "b5cf01dd19b17a2eb7b7fea1a254f47e286927942fb532388922e4368ea33786", "agentURL", "http, //localhost, 5006")
  redis.call("HSET", "b5cf01dd19b17a2eb7b7fea1a254f47e286927942fb532388922e4368ea33786", "level", "contributor")

  redis.call("HSET", "7a319d90121a0113df0333fdf8f4633167f23c398987391a0bbea55b1676ca4f", "ownerID", "2f82ada9116bfee825d28168fb356ad257f3d430cceee0851dcb935c39a003fc")
  redis.call("HSET", "7a319d90121a0113df0333fdf8f4633167f23c398987391a0bbea55b1676ca4f", "signedID", "3045022100b69853124f4147e87b66a35c23248f96ffd14fd160ffb9ef1ac764ac3693085a02204c29e7477ff21c2863c6027edf40175329d488e5f1d532fed5351a4e0a24c83d")
  redis.call("HSET", "7a319d90121a0113df0333fdf8f4633167f23c398987391a0bbea55b1676ca4f", "publicKey", "04792e998ec347ecec5d983a794ae6d322dfbf715adf07ed31a0add37ae0e474e03b2200caea1ed6fd1c93c79ed2407257bcf622f6d7467828af7f9bb4fb197186")
  redis.call("HSET", "7a319d90121a0113df0333fdf8f4633167f23c398987391a0bbea55b1676ca4f", "agentURL", "http, //localhost, 5007")
  redis.call("HSET", "7a319d90121a0113df0333fdf8f4633167f23c398987391a0bbea55b1676ca4f", "level", "defender")

  redis.call("HSET", "359c45d4cb0606f903249bea19da3c178940e2633f34f55c9dca4e425696c1a0", "ownerID", "e8f84726a97b390067e47f9087fe7e845131ac463689aeaf5f28f02a731d6b8e")
  redis.call("HSET", "359c45d4cb0606f903249bea19da3c178940e2633f34f55c9dca4e425696c1a0", "signedID", "304502202a31d0634fa0eadd7c328a22095ceb0b7ecc14a633f5b018a66c216027acc9860221009d8e5e067c2aff9b19e26cdde99445d05a300f42c524fe1fe7c842c826677748")
  redis.call("HSET", "359c45d4cb0606f903249bea19da3c178940e2633f34f55c9dca4e425696c1a0", "publicKey", "04767e81d2ed73487b689a6a2da2a5ae8e3b2e908b04601effc9ff70597d4c7ed07131dc4f4377c557feae68210a09fb31a54f74aaf43560d601b4aab793ca0d8e")
  redis.call("HSET", "359c45d4cb0606f903249bea19da3c178940e2633f34f55c9dca4e425696c1a0", "agentURL", "http, //localhost, 5008")
  redis.call("HSET", "359c45d4cb0606f903249bea19da3c178940e2633f34f55c9dca4e425696c1a0", "level", "protector")
end

--[[ set up owners --]]
if redis.call("EXISTS", "owners") == 0 then
  redis.call("SADD", "owners", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f")
  redis.call("SADD", "owners", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507")
  redis.call("SADD", "owners", "36cbecda6927749d20bd7fed94d7c4228be1e3f65c7fbca6f1aec776f6037249")
  redis.call("SADD", "owners", "de92db7c4623db3acb5f8b36ff3e2e6d0bd73dd1490e4e03abf55b7bdaad6657")
  redis.call("SADD", "owners", "73756a58aa5751c33d6b30ec1c429b00a962646d063ab1c31c26e542bd1b3d69")
  redis.call("SADD", "owners", "c1f6bc67f27992a197d429603113a01fc79b3018f98b9fbf5d09aefc2b49c3b1")
  redis.call("SADD", "owners", "483da90cba7e9f6e693a1f4b67e925662a08ffc565300842a2c84498c77d12f1")
  redis.call("SADD", "owners", "2f82ada9116bfee825d28168fb356ad257f3d430cceee0851dcb935c39a003fc")
  redis.call("SADD", "owners", "e8f84726a97b390067e47f9087fe7e845131ac463689aeaf5f28f02a731d6b8e")

  redis.call("HSET", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "publicKey", "0498d11e643f62e4899b400e344c607b60bba3bf7ebe5fbf4942a68859d944673dea3f2cd46ed7ef6429f51e7a4f6e752626cc4f917d627ed98060ef938408f4cd")
  redis.call("HSET", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "publicKey", "04894dbcc86a7b8e5001867298c3a0bc1a002c6aa96c371c40f9a59dfaec48ca6330f521116d15a7b5cbd5adff58e1b4d3973a753778e20d6197d6f39b653ed60e")
  redis.call("HSET", "36cbecda6927749d20bd7fed94d7c4228be1e3f65c7fbca6f1aec776f6037249", "publicKey", "0473fec6e6452828491fe6a526bb960aff24fe92058162ecbf9ac3ff6d41379e41409cf50edf239e4efde2d6da1424907ad9d57fe64b83c6f25c3cf3d7352d86c3")
  redis.call("HSET", "de92db7c4623db3acb5f8b36ff3e2e6d0bd73dd1490e4e03abf55b7bdaad6657", "publicKey", "0486756ee963e421d9a507e93b4197dfb2558a33a8f6cde8ff50eef0767e9701cbc068877fe03869f9d63c4c0a51c7df0496ff9c0d697c6de69e00333129e477e9")
  redis.call("HSET", "73756a58aa5751c33d6b30ec1c429b00a962646d063ab1c31c26e542bd1b3d69", "publicKey", "0452507d43caf4219a7cdf209ce7c9d7e508a741214c3ab895125be6f9cdd51290f5fed421aebdc0025476aa44a5719f120baff1ab008f550070de99a75244e7b2")
  redis.call("HSET", "c1f6bc67f27992a197d429603113a01fc79b3018f98b9fbf5d09aefc2b49c3b1", "publicKey", "041bce58051272f5f244fa6114c723af27e991fa27861d8ef700d739c0bd3c8c57ac2d827db26e1fa3cb95fd6dcd89ac1dcbcc7fbde7eecdae1f073614fa9dd838")
  redis.call("HSET", "483da90cba7e9f6e693a1f4b67e925662a08ffc565300842a2c84498c77d12f1", "publicKey", "0439b01c47eb306be8f43311988446c1aa188aba08ab544d16470f34a9de19986d34a40a58064219f5cd49e408cf229397d21a771616a052bad909b320397e19dc")
  redis.call("HSET", "2f82ada9116bfee825d28168fb356ad257f3d430cceee0851dcb935c39a003fc", "publicKey", "04601db78f0df381bb9f58e2a1e3b2a93d0c586b930b15381da7a84ca10c3a04e539be456da0e715abb1664740dfbda3213ee12d243e0fe09f332c931120bf8de1")
  redis.call("HSET", "e8f84726a97b390067e47f9087fe7e845131ac463689aeaf5f28f02a731d6b8e", "publicKey", "045e288cb901a9bbd11a76cc4d39d48b27509a029c556667653d2bee7a4f9ddbc263eb51e1a79729be884228344a40bd2de3b4cd9ab59cbc1faf2cdb4db4ddc9b6")
end

--[[ set up entities --]]
if redis.call("EXISTS", "entities") == 0 then
  redis.call("SADD", "entities", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f")
  redis.call("SADD", "entities", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507")

  redis.call("HSET", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "wallets.default.balance", "0")
  redis.call("HSET", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "PublicKey", "0498d11e643f62e4899b400e344c607b60bba3bf7ebe5fbf4942a68859d944673dea3f2cd46ed7ef6429f51e7a4f6e752626cc4f917d627ed98060ef938408f4cd")
  redis.call("HSET", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "permissions.all", "[d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f]")
  redis.call("HSET", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "permissions.identity.citizenship.british.status", "[e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507]")
  redis.call("HSET", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "identity.name", "Gregory Dickason")
  redis.call("HSET", "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f", "identity.citizenship.british.status", "claimed")

  redis.call("HSET", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "wallets.default.balance", "1000000")
  redis.call("HSET", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "PublicKey", "04894dbcc86a7b8e5001867298c3a0bc1a002c6aa96c371c40f9a59dfaec48ca6330f521116d15a7b5cbd5adff58e1b4d3973a753778e20d6197d6f39b653ed60e")
  redis.call("HSET", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "permissions.all", "[e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507]")
  redis.call("HSET", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "identity.name", "Cameron McEwan")
  redis.call("HSET", "e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507", "identity.citizenship.australian.status", "verified")
end

--[[ set up genesis block --]]
if redis.call("EXISTS", "state") == 0 then
  redis.call("HSET", "state", "genesisBlock", "695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4")
  redis.call("HSET", "state", "latestBlock", "695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4")
  redis.call("HSET", "695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4", "blockHeight", "0")
  redis.call("HSET", "695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4", "previousBlock", "None")
  redis.call("HSET", "695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4", "nextBlock", "None")
  redis.call("HSET", "695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4", "filePath", "blocks/genesisBlock.json")
  redis.call("HSET", "695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4", "circleDistance", 0)
end

redis.call("SADD", "blocks", "695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4")
