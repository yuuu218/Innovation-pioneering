#SM3 Rho
## 方法一

从一个初始值a出发，a=f(a),不断计算SM3值，就可能成环（前n bit)

### python运行结果

f=2x+1

8bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/8.png?raw=true)

12bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/12.png?raw=true)

16bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/16.png?raw=true)

20bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/20.png?raw=true)

24bit：

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/24.png?raw=true)

28bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/28.png?raw=true)

## 方法二

从一个初始值出发，a=sm3(a),不断计算SM3值，就可能成环（前n bit)

```c++
    string kaishi = strRand(16);
	vector<string> temp;
	while (1) {
		string hh(sm3(kaishi), 0, bit / 4);
		temp.push_back(hh);
		cout << hh<< endl;
		kaishi = sm3(kaishi);
		string xx(sm3(kaishi), 0, bit / 4);
		vector<string>::iterator result = find(temp.begin(), temp.end(), xx); //查找3
		if (result != temp.end()) //找到
		{
			cout << xx << endl;
			cout << "Yes" << endl;
			return;
		}
```



### C++运行结果

8bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/cpp8.png?raw=true)

12bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/cpp12.png?raw=true)

16bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/cpp16.png?raw=true)

20bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/cpp20.png?raw=true)

24bit:

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/cpp24.png?raw=true)

## 运行指导

直接在C++编译器和python环境下运行

##完成人

李金源
