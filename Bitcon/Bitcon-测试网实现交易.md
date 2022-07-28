**在比特币测试网上模拟比特币交易**

1、首先在网站上生成一个随机测试币地址，要确保此时testnet=true。这样生成的Bitcoin Address 才会是m开头（测试网生成的），如果不设置，便会是1开头，这样生成的是正式比特币网站上的地址。

![](media/f29e79d2720b834cec42e5d44682df8a.png)

2、之后，我们需要获得部分比特币来完成比特币传输发送以及花费这一过程，在（<https://coinfaucet.eu/en/btc-testnet/> ）这个网址中来获得部分比特币（0.01533088），这一部分比特币是付给矿工的费用。

![](media/29db023e457efd11d8b63ec26dbeb688.png)

1.  我们在一个网站Testnet Blockchain中注册一个testnet钱包，进入之后输入我们上面生成的私钥，之后显示出我们的整个过程。

![](media/ff121f9a225cd9b5d1c37db6898a6bb7.png)

该过程便是由33.08254925的比特币，将其中的33.06706889比特币发送给一个用户，另外剩下的0.01533088比特币便是付给矿工的费用

1.  对应的源码为：

{

"address": "n1sH2xFSFAWbU9WL3rTi5xxCAmC1bEihmh",

"total_received": 3306706889,

"total_sent": 3306706889,

"balance": 0,

"unconfirmed_balance": 0,

"final_balance": 0,

"n_tx": 2,

"unconfirmed_n_tx": 0,

"final_n_tx": 2,

"txs": [

{

"block_hash": "000000000000002138539cf9c9fe986877e0575ec7327f3754626b353f7ce702",

"block_height": 2286678,

"block_index": 1,

"hash": "a7acbbcd4f5f9ca9d7eb3d606bf36c93b940333b6579e5d5b058eecffa7d711b",

"addresses": [

"n1sH2xFSFAWbU9WL3rTi5xxCAmC1bEihmh",

"tb1q6mx3fzu5wz0ufc2nducj62dnrrll4g9y98va0g",

"tb1qg3dy2wda2m4pdhzg65sjygns5mderlvvw3se6q"

],

"total": 3306684619,

"fees": 22270,

"size": 219,

"vsize": 219,

"preference": "high",

"relayed_by": "104.197.84.30:39388",

"confirmed": "2022-07-19T01:11:54Z",

"received": "2022-07-19T01:11:46.364Z",

"ver": 2,

"lock_time": 2286677,

"double_spend": false,

"vin_sz": 1,

"vout_sz": 2,

"confirmations": 54,

"confidence": 1,

"inputs": [

{

"prev_hash": "dc99fee2e0841f2a430aa57e7e3734a0bc71e1345387ac2b374fbb4bb49a414c",

"output_index": 0,

"script": "47304402206e31a36616bf1ce198e9795fb94b8ee66ece37b14891165cd9f6bd58124f8a6602206712ae6af763c8f925a15331e1da7541af70a1edf2614c57c30af552d56f7c49012102b2d12be9da4053896745680fd1e2ab2b191f04f4a61eb5869da76bff0336ff9d",

"output_value": 3306706889,

"sequence": 4294967294,

"addresses": [

"n1sH2xFSFAWbU9WL3rTi5xxCAmC1bEihmh"

],

"script_type": "pay-to-pubkey-hash",

"age": 2286677

}

],

"outputs": [

{

"value": 1686029,

"script": "0014d6cd148b94709fc4e1536f312d29b318fffaa0a4",

"addresses": [

"tb1q6mx3fzu5wz0ufc2nducj62dnrrll4g9y98va0g"

],

"script_type": "pay-to-witness-pubkey-hash"

},

{

"value": 3304998590,

"script": "0014445a4539bd56ea16dc48d521222270a6db91fd8c",

"spent_by": "a99168b3a82fad0d756352c117cf44f30446a762247cb3e0c09dd024901d31b2",

"addresses": [

"tb1qg3dy2wda2m4pdhzg65sjygns5mderlvvw3se6q"

],

"script_type": "pay-to-witness-pubkey-hash"

}

]

},

{

"block_hash": "00000000000000383b4c49c835a4aa6ff4aca819d6c4eed1b9f1ce634206b9e9",

"block_height": 2286677,

"block_index": 3,

"hash": "dc99fee2e0841f2a430aa57e7e3734a0bc71e1345387ac2b374fbb4bb49a414c",

"addresses": [

"mwevSP4e7N7NxJ2LoLxhFkQ6i5pwouPbEt",

"n1sH2xFSFAWbU9WL3rTi5xxCAmC1bEihmh",

"tb1qegfaj9nyxtx7t08fnctyd7vftv7wz7jxay0zp7"

],

"total": 3308239977,

"fees": 14948,

"size": 228,

"vsize": 147,

"preference": "high",

"relayed_by": "5.9.121.164:18333",

"confirmed": "2022-07-19T01:09:52Z",

"received": "2022-07-19T01:03:29.482Z",

"ver": 2,

"lock_time": 2286676,

"double_spend": false,

"vin_sz": 1,

"vout_sz": 2,

"confirmations": 55,

"confidence": 1,

"inputs": [

{

"prev_hash": "26160a9d0277d34854642d40a179948c9f7be45863d0a2eea8d66415f924418c",

"output_index": 0,

"output_value": 3308254925,

"sequence": 4294967294,

"addresses": [

"tb1qegfaj9nyxtx7t08fnctyd7vftv7wz7jxay0zp7"

],

"script_type": "pay-to-witness-pubkey-hash",

"age": 2286667,

"witness": [

"304402200681c1f9468c6edf57b3ad881f220175ce1f20ccbc69c3dee5159d0a82d64511022021b8e49cad48f61defe0f815f16e96bac4fd12437d6dbba1ab850f5c90db099901",

"022af95be0685bc34cf465753cbb93e2ffbff1f502cad3efac56861fefb0925a3e"

]

}

],

"outputs": [

{

"value": 3306706889,

"script": "76a914df3a7a5ccce853b7bf71abe35c8aeb188bfcfcdb88ac",

"spent_by": "a7acbbcd4f5f9ca9d7eb3d606bf36c93b940333b6579e5d5b058eecffa7d711b",

"addresses": [

"n1sH2xFSFAWbU9WL3rTi5xxCAmC1bEihmh"

],

"script_type": "pay-to-pubkey-hash"

},

{

"value": 1533088,

"script": "76a914b103ca629737edaaad736ef62f7efecaab62143f88ac",

"addresses": [

"mwevSP4e7N7NxJ2LoLxhFkQ6i5pwouPbEt"

],

"script_type": "pay-to-pubkey-hash"

}

]

}

]

}
