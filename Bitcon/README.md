项目三
=
## 一、名称：

1、发送一个tx在比特币测试网，并解析tx数据到每一位。

2、伪造一个签名，来假装你是中本聪。
## 二、简介：
### 1、比特币交易
完成比特币交易我们需要借助UTXO，，每个UTXO都被一个公钥(钱包地址)锁定，只有持有该公钥对应私钥的人，可以通过私钥签名(解锁)并使用该UTXO。
对应的比特币里面的公钥通过两次哈希算法(SHA256)运算得到一个散列值(也叫做哈希)，再经过Base58Check编码生成了我们常见到的比特币的钱包地址。

<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R11.png?raw=true"  height="200" width="400">

当脚本被执行时，结果是OP_TRUE，从而使得交易有效。不仅该笔交易的输出锁定脚本有效，同时UTXO也能被任何知晓这个运算技巧的人所使用。
而在比特币交易的过程中，有部分费用交付给完成实现该交易的矿工所得到，便称为交易手续费。
所以我们在比特币测试网进行模拟交易的时候首先需要获取部分比特币以及得知他对应的公私钥对。在获取公私钥对时要确保获得的是对应于比特币测试网的，他跟比特币正式官网的公私钥不一样，注意区分。所以要在地址上添加一句：testnet=true。
### 2、数字签名
<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R1.png?raw=true"  height="330" width="400">
进行数字签名伪造便是根据数字签名的过程来进行。ECDSA的哈希部分是算法不可获取的部分。如果验证者本身没有运行哈希，则ECDSA的安全属性不会成立。
所以说，如果验证者自己不执行哈希，但仅接受签名者给出的值，则给定公钥P，选择随机非零值a和b。计算R=aG+bP。 (R.x, R.x/b)是密钥P对“消息哈希” (R.x*a/b)的有效签名。
##三、完成人：
王婧涵、李金源、张琴心
## 四、项目代码说明
1、第一问中的比特币交易的代码便是根据我们得到的比特币进行相关的交易实现，代码也是有输入和输出以及对应的给予矿工的手续费。
2、第二问中模拟数字签名便是根据数字签名的生成过程，生成对应的哈希值hash。代码选择在sage平台下运行便是为了方便表达有限域以及对应的hash的生成。
## 五、运行指导：第一问找到对应的测试网，第二问在Sage平台下输入代码直接运行即可
## 六、运行截图
在实现测试网比特币交易中首先生成的公私钥对：
<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R8.png?raw=true"  height="300" width="500">
之后对应的交易为：
<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R10.png?raw=true"  height="200" width="600">
第二问伪造数字签名中：
代码截图：
<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R6.png?raw=true"  height="350" width="600">
运行结果截图：
<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R7.png?raw=true"  height="350" width="600">
## 七、具体贡献说明

王婧涵：实现伪造数字签名来假装是中本聪

李金源：实现比特网交易流程原理的说明

张琴心：实现比特币测试网处比特币的交易
