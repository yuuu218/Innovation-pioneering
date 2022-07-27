**伪造一个数字签名假设你是中本聪**

一、比特币中的数字签名过程

<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R1.png?raw=true"  height="330" width="400">

首先获得一个公钥P，P的生成采用的是椭圆曲线签名算法，d对应的是私钥，G为椭圆曲线的基点，采用的乘法运算也是椭圆曲线的点乘法。

我们对消息m进行数字签名Sign(m)，过程便是生成r，也就是临时公钥n的X坐标，之后进行最重要的步骤，s=k\^(-1)(e+dr)mod n ,生成对应的信息m的S，这样对应的（r，s）便是消息m的数字签名了。

之后我们可以利用公钥P对消息m的数字签名（r，s）进行验证，验证的便是临时公钥n的x坐标和r是否相等。相等的话便说明签名是有效的。

二、交易举例

<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R2.png?raw=true"  height="500" width="400">

在比特币系统中，其实是先有输出才有的输入。只有在新交易中合法引入UTXO，才可以构建成合法的交易。输入 = 之前的未被花费的输出（UTXO），所以我们通过查找txid找到区块链中之前的UTXO来验证输入合法。

<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R3.png?raw=true"  height="200" width="600">

在上面的示例中可以看出：引入的UTXO中包含0.1BTC以及一个“锁定脚本(scriptPubKey)”。普遍情况下锁定脚本包括其中的PubKHash 。

<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R4.png?raw=true"  height="200" width="600">

所以说，当新的交易使用正确的“解锁脚本”引入该UTXO时，才能算合法引入。如下红线中所示，即为引入该UTXO时提供的“解锁脚本”，也就对应于图中sig字段：

<img src="https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R5.png?raw=true"  height="300" width="600">

三、伪造数字签名

针对数字签名的情况，几年前，Craig Wright通过简单地从区块链中复制一些预先存在的签名，并在验证它们时发布了一些混淆的指令来证明自己就是中本聪。后来这一做法被人揭穿。在之后，诈骗者发布’hash'，r，s元组。

我们需要知道的是，ECDSA的哈希部分是算法不可获取的部分。如果验证者本身没有运行哈希，则ECDSA的安全属性不会成立，则伪造会变得微不足道。同样的漏洞也被带到了BCH中的原始OP_DSV操作码中，它最初没有对输入数据进行哈希处理，而是将其留给了用户。

所以说，如果验证者自己不执行哈希，但仅接受签名者给出的值，则给定公钥P，选择随机非零值a和b。计算R=aG+bP。现在， (R.x, R.x/b)是密钥P对“消息哈希” (R.x\*a/b)的有效签名。但是，这不会危及真实ECDSA的安全性，因为你无法找到哈希至所选（R.x \* a / b）值的消息。

所以我们利用sage平台进行数字签名的伪造，关于为何使用sage平台主要是因为便于实现具体的有限域，具体代码实现如下：
```c

F = FiniteField (0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)

C = EllipticCurve ([F (0), F (7)])

G = C.lift_x(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)

N = FiniteField (C.order())

P = P=-C.lift_x(0x11db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5c)

\# block 9 coinbase payout key

def forge(c, a=-1): \#创造一个伪造的ECDSA签名

\#将a设置为-1以外的值，使其不那么明显

           a = N(a)

           R = c\*G + int(a)\*P

           s = N(int(R.xy()[0]))/a

           m = N(c)\*N(int(R.xy()[0]))/a

           print('hash1 = %d'%m)

           print('r1 = %d'%(int(R.xy()[0])))

           print('s1 = %d'%s)

for c in range(1,10):

           forge(c)
```

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R6.png?raw=true)

实现结果为：

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/R7.png?raw=true)

hash1 = 25292222169426362969760742810503101183086560848420849767135309758511048414376

r1 = 61518691557461623794232686914770715342344584505217074682876722883231084339701

s1 = 54273397679854571629338298093917192510492979773857829699728440258287077154636

参考资料：https://www.528btc.com/college/25125.html
