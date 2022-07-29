# 项目：长度扩展攻击

长度扩展攻击（length extension attack），是指针对某些允许包含额外信息的加密散列函数的攻击手段。对于满足以下条件的散列函数，都可以作为攻击对象：  

1. 加密前将待加密的明文按一定规则填充到固定长度（例如512或1024比特）的倍数；

2. 按照该固定长度，将明文分块加密，并用前一个块的加密结果，作为下一块加密的初始向量（Initial Vector）。满足上述要求的散列函数称为Merkle–Damgård散列函数（Merkle–Damgård hash function），

   ![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/tu2.png?raw=true)

   

这个结构的好处是，如果压缩函数是抗碰撞的，那经过此结构处理后的散列函数也是抗碰撞的。SM3，HMAC就是基于这种结构，因为Merkle-Damgard结构并不能抵抗扩展攻击，因此HMAC引入了Key。

## 长度扩展攻击实现

1. 选择a，首先对其进行填充，得到 m=a||fillFunction；
2. 计算哈希值即 x1=hash(m,IV)；
3. 自选b，计算 x2=hash(m||b,IV),即x2=hash(a||fillFunction||b,IV)；
4. x3=hash(b,iv)，其中iv=x1；
5. 如果x2与x3相同，攻击成功。

## 运行指导

直接在C++编译器和python环境下运行

## sm3

### C++运行结果

   ![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/tu1.png?raw=true)

### python运行结果

   ![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/tu3.png?raw=true)

## md5

   ![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/tu4.png?raw=true)

## sha1

   ![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/tu5.png?raw=true)

## 完成人

王婧涵

## 参考文献

[抗碰撞性、生日攻击及安全散列函数结构解析](https://blog.csdn.net/Metal1/article/details/79887252?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522165883091116780366534907%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=165883091116780366534907&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~pc_rank_34-7-79887252-null-null.142^v34^pc_rank_34,185^v2^control&utm_term=%E9%95%BF%E5%BA%A6%E6%8B%93%E5%B1%95%E6%94%BB%E5%87%BB%20sm3&spm=1018.2226.3001.4187)
