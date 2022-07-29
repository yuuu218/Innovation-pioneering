一、名称：利用RFC6979实现SM2算法  
二、	简介：  
1、	SM2签名、验签流程  
 ![image](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/sm2_5.png)  
2、多个用户重用k的弊端  
 ![image](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/sm2_6.png)  
因此，如果有多个用户使用了相同的k，那么在他们已知了其他用户的签名时可以通过计算获知其他用户的私钥。  
3、解决方案  
比特币的签名机制是基于椭圆曲线算法。在椭圆曲线里面k值(用于签名)是要严格保密的，暴露k值就相当于暴露私钥。k值要保证两点：  
1、保密  
2、唯一 
RFC6979确定性签名算法就实现了以上两点，它的机制类似于：k = SHA256(d + HASH(m)); 其中，d是私钥，m是消息，我们一般会对消息的HASH进行签名，因此这里是HASH(m)。  
有私钥d，就保证了“保密”，再加上消息m，保证了“唯一”，这也是“确定性”的算法，只要SHA256是安全的，此算法就是安全的。  
当然真正的RFC6979比这个要复杂的多。其实现为：  
首先我们定义:HMAC_K(V)  
1使用密钥(key)K对数据V进行HMAC算法：给定输入消息m，应用以下过程：通过哈希函数H处理m，产生：h1 = H（m）  
2.V = 0x01 0x01 0x01 ... 0x01。V（以比特）的长度等于8 * ceil（hlen / 8）。例如，如果H是SHA-256，则V被设置为值为1的32个八位字节的序列。  
3.K = 0x00 0x00 0x00 ... 0x00。K的长度（以比特）等于8 * ceil（hlen / 8）。  
4.K = HMAC_K（V || 0x00 || int2octets（x）|| bits2octets（h1））。x是私钥。  
5.V = HMAC_K（V）  
6.K = HMAC_K（V || 0x01 || int2octets（x）|| bits2octets（h1））  
7.V = HMAC_K（V）  
执行以下流程，直到找到适当的值k：  
将T设置为空序列。 T的长度（以比特为单位）表示为tlen, 因此tlen = 0。  
当tlen  
V = HMAC_K（V）  
T = T || V  
计算k = bits2int（T），如果k的值在[1，q-1]范围内，那么k的生成就完了。否则，计算：  
K = HMAC_K（V || 0x00）  
V = HMAC_K（V）  
并循环（尝试生成一个新的T，等等）。  
三、完成人：于晓畅、张琴心、王婧涵、李金源  
四、项目代码说明  
本项目的基础是实现SM2签名及验证算法，在此基础上将普通的随机生成k改变为RFC6979生成k，故我们先实现了随机生成k时的SM2签名及验证算法，再定义了一个RFC6979生成k的函数def deterministic_generate_k(m, pk)，将两者进行比较。  
为实现椭圆曲线的运算，需要一些基本的函数，如素数检测、字节和int的转换、求最大公约数、求乘法逆元等，本代码的前面部分实现了这些基础函数。其后定义了椭圆曲线密码类，用以实现一般的ECC运算：加法、乘法、求反等。再然后定义了SM2类继承ECC，实现SM2算法的签名、验签等。最后是与本项目直接相关的RFC6979生成k的函数，利用了项目说明里的过程，代码实现之。  
五、运行指导：利用PyCharm在安装了所需模块的前提下直接run即可  
六、运行截图  
RFC6979生成k下的SM2签名及验签：  
 ![image](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/sm2_7.png)
随机生成k下的SM2签名及验签：  
![image](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/sm2_8.png)   
七、具体贡献说明  
王婧涵：实现椭圆曲线密码类（实现一般的ECC运算）  
张琴心：实现SM2类继承ECC  
于晓畅：实现RFC6979生成k，整合代码  
李金源：实现素数检测、字节和int的转换、求最大公约数、求乘法逆元等基础函数  

