# Uchat——基于python的安全即时通讯系统

## 目的

设计完成简易的安全即时通讯系统，实现类似于QQ的聊天软件；

## 需求分析

### 功能需求

1. 聊天客户端

   1. 注册：用户与集中服务器通信完成注册，包括用户名、密码、邮箱、性别、年龄、数字证书等信息传输，其中数字证书包含公钥、用户名、邮箱等信息。私钥单独保存在客户端一个文件夹下不进行传输；能显示用户名、邮箱不符合格式规范或者重复，空输入等错误信息。
   2. 认证登录：客户端与集中服务器通信完成用户名、口令认证登录；能显示用户名、密码错误导致的登录错误信息。还有已登录账号再次登录时的多重登录检验，并将之前登陆的账号顶下去。
   3. 好友管理：用户可通过服务器进行搜索、添加、删除好友。
   4. 即时通信：用户通过客户端实现与好友的聊天，包括文字、图片传输。文字可实现字体颜色和大小的改变。
   5. 聊天记录：客户端能够保存聊天记录并且可以查看聊天记录。
   6. 消息加解密：采用D-H体制协商加密秘钥，用对称密码AES算法进行加解密。
   7. 消息摘要：使用MD5算法实现消息摘要认证功能，确保发送消息的完整性。
   8. 用户未读消息提醒：红点标注未读消息数目，并按最后发送消息时间排列好友列表。
   9. 用户离线后消息处理：用户上线后及时接收到离线时好友发送的消息。

   功能结构图

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714124535.png)

2. 集中服务器

   1. 用户注册：与用户通信完成注册，对用户名和邮箱格式、是否重复，输入不规范等做必要的检验，接收客户端的数字证书，发送服务端数字证书。
   2. 登录验证：用户登录时，验证用户名和密码是否正确，并向客户端返回登录结果。如信息正确，就将在线好友用户发给该用户，将该用户的状态发给各在线好友用户，同时在服务器端显示出来。
   3. 用户公钥，证书提供：用户向好友发送消息时，与服务器建立安全连接获取好友的证书信息，服务器控制client.socket像好友用户发送信息，实现用户之间的通信。
   4. 用户在线状态维护：当用户在线时，记录保存用户的在线状态、IP地址、端口号。
   5. 用户消息列表实时发放：由监听函数将操作实时加入到执行函数列表中递归执行。向用户发送其好友列表的在线离线情况，包括好友用户名、IP地址、端口号。并按照最后发消息的时间对好友消息列表进行排序。

   功能结构图

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714124653.png)

3. 高级功能
   1. 离线用户消息通知：暂时存储离线用户的消息，用户上线后，显示未读的消息并用红点标注；
   2. 好友在线离线功能实时更新；
   3. 限制账号只能一处登录：一个账号只能在一处登录，在别处登录时会把原先的登录踢下线；
   4. 支持群聊功能：可以创建群聊，并根据群号加入群聊；
   5. 聊天时字体大小颜色可更改；
   6. 支持聊天各类图像文件的缓存。

### 数据需求

1. 客户端

   客户端登录后加过的好友和加入的群聊需要从数据库中调出信息并在前端反馈呈现出来。客户端的聊天记录可以存储在数据库中，用到时直接读取返回消息历史。

2. 集中服务器

   1. users表：用户信息表，存储用户基本信息，包括用户ID(id)、用户名(username)、密码(password)、电子邮箱(email)、用户登录IP地址(ip)、用户登录端口(port)、性别(sex)、年龄(age)、公钥(pk)。

      | 名称     | 数据类型 | 主键 | 是否唯一 | 是否为空 | 备注     |
      | -------- | -------- | ---- | -------- | -------- | -------- |
      | id       | INTEGER  | Y    | Y        | N        | 用户id   |
      | username | TEXT     | N    | Y        | N        | 用户名   |
      | password | TEXT     | N    | Y        | N        | 密码     |
      | email    | TEXT     | N    | Y        | N        | 邮箱     |
      | ip       | TEXT     | N    | Y        | N        | 登录IP   |
      | port     | TEXT     | N    | Y        | N        | 登录端口 |
      | sex      | TEXT     | N    | Y        | N        | 性别     |
      | age      | TEXT     | N    | Y        | N        | 姓名     |
      | pk       | TEXT     | N    | Y        | N        | 公钥     |

   2. friends表：存储用户的好友信息，包括用户id(from_user_id)、好友id(to_user_id)、加好友请求是否接受(accepted)。

      | 名称         | 数据类型 | 主键 | 是否唯一 | 是否为空 | 备注     |
      | ------------ | -------- | ---- | -------- | -------- | -------- |
      | from_user_id | INTEGER  | Y    | Y        | N        | 本人ID   |
      | to_user_id   | INTEGER  | Y    | Y        | N        | 好友ID   |
      | accept       | BOOLEAN  | N    | N        | N        | 接受状态 |

   3. chat_history表：存储好友的聊天记录，包括发送方ID(user_id)、接收方(target_id)ID(target_type)、聊天数据(data)(BLOB类型存储二进制大对象，可以实现文件数据的直接存储)，sent(用于标识消息是否已发送，若未发送，先存储这个操作，在某一次事件再次触发时检查标志位，操作服务端再次控制client.socket发送消息)。

      | 名称        | 数据类型 | 主键 | 是否唯一 | 是否为空 | 备注              |
      | ----------- | -------- | ---- | -------- | -------- | ----------------- |
      | id          | INTEGER  | Y    | Y        | N        | 消息ID            |
      | user_id     | INTEGER  | N    | N        | N        | 用户ID            |
      | target_id   | INTEGER  | N    | N        | N        | 消息目标ID        |
      | target_type | TEXT     | N    | N        | N        | 目标类型：群/用户 |
      | data        | BLOB     | N    | N        | N        | 消息体            |
      | sent        | BOOLEAN  | N    | N        | N        | 发送是否成功      |

   4. rooms表：群组表，包括该群组的主键ID(id)、群组的名称(room_name)。

      | 名称      | 数据类型 | 主键 | 是否唯一 | 是否为空 | 备注   |
      | --------- | -------- | ---- | -------- | -------- | ------ |
      | id        | INTEGER  | Y    | Y        | N        | 群聊ID |
      | room_name | TEXT     | N    | Y        | N        | 群聊名 |

   5. room_user表：群组用户表，包括群组的ID，群聊房间号(room_id)、加入该群组的用户(user_id)。

      | 名称    | 数据类型 | 主键 | 是否唯一 | 是否为空 | 备注   |
      | ------- | -------- | ---- | -------- | -------- | ------ |
      | id      | INTEGER  | Y    | Y        | N        | ID     |
      | room_id | INTEGER  | N    | N        | N        | 群聊ID |
      | user_id | INTEGER  | N    | N        | N        | 用户ID |

### 性能需求

1. 可靠性需求

   保证一个用户只能同时使用一个IP地址登录，客户端不会出现闪退、加密无效的情况。

2. 安全性需求

   客户端做好完整的封装；传输信息采用经过公钥加密机制协商的AES对称加密秘钥；服务器及时更新客户端IP地址等信息。

3. 可维护性与可扩展性需求

   对于软件功能方面，采用高内聚低耦合的模块化设计，包括登录模块、注册模块、好友列表模块、聊天模块等，确保每个模块的具有较高的独立性，使软件源码便于维护，同时便于后期添加聊天群等更多扩展内容，保证软件可以进行更新换代。

4. 运行环境需求

   1. 客户端：python3

   2. 服务端：

      python3

      PC硬盘容量：50G
      
      运行内存：2G

### UI需求

1. 页面内容：聊天字体大小和颜色可更改，主题突出，语言简单明了易懂，菜单设置合理、页面布局规范，文字准确，语言流畅。
2. 技术环境：页面大小合适，无错误链接和空链接。
3. 艺术风格：界面版面形象清晰，布局合理，字号大小适宜，字体选择合理，前后一致，动静搭配恰当，色彩和谐自然，与主题内容协调。

### 操作需求

1. 所有弹出的窗口不超过一层，无层层堆叠的现象，不能无故为操作增加复杂度。
2. 用户注册、用户登录、添加好友、删除好友聊天窗口的开启等所有操作务必要简单、快捷，限制在两次点击以内。
3. 考虑到操作人员工作的实际环境状况，就要保证设计的按键足够的清晰足够大。

## 详细设计

### 系统结构说明

本系统的核心控制逻辑在于C-S-C之间发送的数据中包含了操作码，接收方通过对接收码的识别作出规定的操作。例如服务端接收添加好友的操作码会执行add_friend.py。客户端接收操作码并不断把对应函数放入递归函数的队列中，由递归函数逐一执行队列中的函数。

系统主要分为三个部分：

- 聊天客户端(client)
- 集中服务器(server)
- 相互通信时的共同部分(common)

```c
Uchat
│	config.json
│	run_client.py
│	run_server.py
│
├─client
││		__init__.py
││
│├─components
││		contact_item.py//联系人列表UI
││		vertical_scrolled_frame.py//Tkinter可滚动框架
││		__init__.py
││
│├─forms
│││		chat_form.py//聊天界面及处理与聊天相关的事件
│││		contacts_form.py//联系人列表
│││		login_form.py//登录界面
│││		register_form.py//注册界面
│││		__init__.py
│││
││└───images//背景图片
││		contacts_bg.gif
││		contacts_bg.png
││		login_bg.gif
││		register_bg.gif
││		VerticalScrolled.png
││
│├─memory
││		__init__.py//缓存数据
││
│└─util
│	│	__init__.py
│	└─	socket_listener
│			__init__.py//监听socket的线程
│
├─common
││		config.py//获取配置信息
││		global_vars.py//全局变量
││		__init__.py
││
│├─cryptography
││		crypt.py//密钥协商相关函数
││		prime.py//随机生成一个大素数
││		__init__.py
││
│├─message
││		__init__.py//消息处理(消息类型定义，序列化过程等)
││
│├─transmission
││		secure_channel.py//安全信道的建立和传输
││		__init__.py
││
│└─util
│	│	__init__.py
│	│
│	└─	socket_listener
│			__init__.py//客户端socket监听
│
└─server
	│	database.db
	│	main.sql
	│	__init__.py
	│
	├─broadcast
	│	__init__.py//广播消息
	│
	├─event_handler
	│	add_friend.py//加好友
	│	bad.py//出现错误操作使程序走向可处理除0操作
	│	client_echo.py//测试CS通信
	│	create_room.py//创建群聊
	│	del_friend.py//删除好友
	│	join_room.py//加入群聊
	│	login.py//登录
	│	query_room_users.py//执行群聊中发消息的操作
	│	register.py//注册
	│	resolve_friend_request.py//处理加好友请求
	│	send_message.py//发消息
	│	__init__.py
	│
	├─memory
	│	__init__.py//缓存数据
	│
	└─util
		│__init__.py//添加对象类型
		│
		└─database
			__init__.py//数据库操作
```

1. 聊天客户端client

   实现安全即时通信系统的客户端，主要功能是通过界面与用户实现交互；通过socket与集中服务器进行通信，获得集中服务器的服务，实现用户的注册登录等功能。与好友即时通信和加入群聊通信。

   1. 登录模块LoginForm
      该模块创建登录界面并可链接到注册界面，若输入为空则报错，否则将获取用户输入的用户名和密码打包成登录请求消息(MessageType.login)发送给服务器，服务器根据消息类型和数据包中的内容以及在数据库查找到的结果进行判断，根据不同情况发送不同的反馈给客户端。客户端收到反馈消息，若data['type']为login_failed，则用户名和密码输入有误；若为data['type']为login_successful则根据memory进入登录后显示好友列表的ContractsForm界面。
   2. 注册模块RegisterForm
      该模块只有在登录界面点击注册按钮时才会显示。通过注册窗口获得用户输出的个人信息：用户名、密码、邮箱、性别、年龄，若其中用户名、邮箱、密码为空或两次密码输入不一致则会提示相应的错误以引导用户进行正确的输入，否则将获取用户输入打包成注册请求消息(MessageType.register)发送给服务器。服务器查找数据库判断是否用户名已经注册过，发送不同反馈给用户，若data['type']为username_taken，则用户名已被注册，若data['type']为MessageType.register_successful则注册成功，并且在客户端生成证书包含用户的用户名，邮箱，公钥。
   3. 主界面ContactsForm
      该模块在用户登录成功以后显示。显示好友列表中好友的用户名、在线状态，ip地址及端口号等。下方的按钮有添加好友、删除好友、添加群聊、创建群聊。可以点击相应的按钮进行相应的操作，发给服务器相应的数据包，服务器接收到数据包后进行解析，根据不同类型进行event_handler。若点击好友列表或群聊即可跳出聊天界面进行聊天。未读的消息会用红点标注，根据最后一条消息的发送时间来对好友列表排序。
   4. .聊天界面ChatForm
      该模块是用户与好友聊天的界面。当用户在好友列表中点击好友列表时，即向好友发出聊天，服务器收到聊天请求后寻找对方的证书，找到对方的公钥，双方使用Diffie-Hellman算法协商算法，然后利用AES加密消息保证消息的机密性，MD5生成消息摘要验证保证消息的完整性。另外还可以更改聊天过程中字体的大小和颜色，支持多行输入，支持发送文件，以图片为例，将保存聊天过程中的接收到的图片，并识别其格式。
   5. 客户端部件(components)模块
      该模块实现tkinter静态部件添加和滚动模块的实现。
   6. 客户端memory管理模块(memory)
      该模块用于初始化tkinter对象tk的属性，如窗口，secure_channel对象等。
   7. 多用(util)中的socket_listener模块
      该模块用于客户端处理消息类型，文本或其他。以及不断循环建立连接socket接收消息，实现数据包的完整接收。定义处理给好友框，消息框更新历史消息的函数，事件操作的监听函数和移除函数，消息的监听函数和移除函数。可以实现接收数据并且拼成块，更新聊天的历史记录，通知客户端更新contacts界面上的最后一条消息的内容，时间，未读消息的数目等。

2. 集中服务器server

   1. event_handler模块
      该模块分为11个部分，分别具体处理客户端发来的各个操作事件。如登录加好友删除好友等操作。
   2. database数据库模块
      该模块主要是根据客户端触发的事件对数据库的各种操作。
   3. broadcast广播模块
      该模块主要是针对群聊，为群组中的每个在线用户广播发送消息。
   4. memory模块
      定义用户与secure_channel对象互相映射的字典列表，所有已经建立的secure_channel对象，以及用户下线后将其从在线secure_channel对象列表中移除的操作。

3. 客户端服务器公用模块common

   1. message模块
      将变量数据等变成可存储或者传输的过程即序列化，同时还将各个事件的类型变为枚举变量保存，将收到的数据包反序列化进行恢复，再提取数据包中Message的类型。
   2. cryptography模块
      用于调用其生成公钥，然后从证书中获取公钥，再使用D-H算法协商生成共享密钥。
   3. prime模块
      该模块主要是判断是否为素数，生成大素数，为证书的生成提供基础。
   4. secure_channel模块
      该模块主要是定义secure_channel类，即包裹了socket和参数秘钥的封装对象。在通信对象之间协商好对称加密秘钥之后封装在这个新的对象中。并且这个对象对数据有新的函数功能：
      - send函数
        用于对发送的序列化之后的数据用对称加密秘钥进行AES加密并用struct结构体将其打包成自设协议格式的数据包。
      - on_data
        函数主要用于接受数据的逆向解析。按照要求配置socket和数据传输的格式进行规则化。数据包的格式为前四个字节为消息体的长度，接着一字节存储AES加密时的消息填充长度，然后16字节AES加密时所需要的初始值，再接着是32字节的消息摘要，最后才是加密后的消息体。

### 重要数据说明

1. 发送接收的数据格式

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714133500.png)

2. 接收数据时的三个字典

   1. bytes_to_receive={}——用于存储对应用户id或者服务器的将要接收的数据；
   2. bytes_received={}——用于标识已经接收的数据；
   3. data_buffer={}——用于将已经接收的数据解密，反序列化生成最初的数据字符串。

3. 全局都在引用的数据

   1. sc_to_user_id={}——表示映射关系为sc->user_id的字典；
   2. user_id_to_sc={}——表示映射关系为user_id->的字典；
   3. socket_to_sc={}——表示socket和已生成sc对象的映射关系字典；
   4. scs=[]——存储所有运行出来的sc(secure_channel)对象；
   5. chat_history=[]——用于暂时存储聊天信息历史。

4. 客户端接收到的数据data

   data是一部字典，它包括key:parameters，type.parameters也是一部字典，内部包括key:target_type，time，sender_id(发送者id)，target_id(接收方id)，sender_name(接收者姓名，message字典(内含数据内容，字体，字体大小颜色)。而外层的这个type存储的是交给server的MessageType类型，如果是不同的MessageType会进行不同的数据库操作和客户端操作。具体实例如下：

   ```
   data={
   	'parameters':{
   'target_type':0,
   'time':1562754761321,
   'sender_id':1,
   'target_id':2,
   'sender_name':'1',
   'message'{
   'data':'hello',
   'fontsize':10,
   'type':0,
   'fontcolor':'#000000'
   }
   },
   	'type':<MessageType.on_new_message:109>
   }
   ```

   例子中data\['parameters']['target_type']=0表示文本信息，从id为1的用户发出信息，发给id标号为2的人，发送方昵称为‘1’。给服务器发送的操作码为109。

### 安全传输

1. 数据包结构

   1. 消息加密算法：AES对称加密算法，保证消息机密性

   2. 消息摘要算法：MD5算法，保证消息的完整性

   3. 包结构分析

      1. 第一层(解密前)

         通过函数struct.pack()构造加密的数据包，结构如下

         ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714134257.png)

         相关代码如下

         ```python
         iv1=bytes(os.urandom(16))
         	data_to_encrypt=serialize_message(message_type,parameters)
         length_of_message=len(data_to_encrypt)
         padding_n=math.ceil(length_of_message/16)*16-length_of_message
         	foriinrange(0,padding_n):
         		data_to_encrypt+=b'\0'
         
         ```

         其中iv1是16字节随机数作为初始向量。要加密的数据是序列化的初始数据。获取长度后用\0填充。然后将数据用python库函数aes，cbc模式加密得到加密数据。

      2. 第二层(解密后)

         结构如下

         ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714134437.png)

         - MessageType：event_handler_map()规定的操作码

           ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714134505.png)

         - Parameter：字典参数，包含target_type(标志群聊或者私聊)等

      3. 第三层，序列化数据的安排格式

         ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714134543.png)

      4. 第四层，基础数据部分

         包括int、str、bool、float、binary等

         ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714134625.png)

2. 密钥分发

   1. 协商过程

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714134751.png)

      客户端的证书、公钥、私钥

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714134808.png)

   2. 加密算法

      采用DH协商对称加密的共享密钥，具体过程如下

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714134732.png)

### 程序函数清单

#### 客户端函数

1. socket_listener(self,data)

   - 位置

     - client/forms/register_form.py
     - client/forms/login_form.py
     - client/forms/contacts_form.py
     - client/forms/chat_form.py

   - 参数

     - self：所在的类的自身
     - data：监听数据

   - 功能

     在注册、登录、好友列表、聊天框四个页面建立事件监听，解析监听data，确定数据中MessageType的类型，在register_form.py文件中用于判断用户名是否被占用、返回注册结果；在login_form.py中用于返回登录结果；在contacts_form.py文件中用于判断是否处理添加、删除好友、添加、创建群聊以及执行操作的结果、判断好友是否下线并刷新好友列表。

2. remove_socket_listener_and_close(self)

   - 位置

     - client/forms/register_form.py
     - client/forms/login_form.py
     - client/forms/contacts_form.py
     - client/forms/chat_form.py

   - 参数

     - self：所在的类的自身：RegisterForm、LoginForm、ContactsForm、ChatForm

   - 功能

     通过调用util/socket_listener文件下的remove_listener函数来关闭事件监听，同时调用库函数destroy()关闭窗口、清空客户端缓存信息。

3. \__init__(self,master=None)

   - 位置

     - client/forms/register_form.py

   - 参数

     - self：所在类RegisterForm自身
     - master：注册主窗口用来容纳其他组件,默认一个窗口master=None

   - 功能

     通过库函数super()实现子类__init__()对父类__init__()的继承；对注册窗口进行布局，包括确定注册界面的长宽，确定背景、标签、输入框、按钮等的位置、颜色、类型、链接等；初始化安全信道；通过socket_listener()函数和remove_socket_listener_and_close()函数控制对客户端socket事件监听和关闭。

4. do_register(self)

   - 位置

     - client/forms/register_form.py

   - 参数

     - self：所在类RegisterForm自身

   - 功能

     检查输入的用户名、密码、邮箱是否合法；判断两次输入的密码是否相同；调用get_ip()函数获取客户端的IP地址和端口号；向服务器发送注册请求，并通过调用函数send()将注册输入的用户名、密码、邮箱、性别、年龄以及用户的IP地址和端口号等信息发送给服务器；构造数字证书，命名为IP地址+“——cert.pem”，内容为用户名+邮箱+用户公钥

5. .\__init__(self,master=None)

   - 位置

     - client/forms/login_form.py

   - 参数

     - self：所在类RegisterForm自身
     - master：登录主窗口用来容纳其他组件,默认一个窗口master=None

   - 功能

     通过库函数super()实现子类\_\_init\_\_()对父类\__init__()的继承；对登录窗口进行布局，包括确定注册界面的长宽，确定背景、标签、输入框、按钮等的位置、颜色、类型、链接等；初始化安全信道；通过socket_listener()函数和add_listener()函数将服务器端加入到监听列表中。

6. do_login(self)

   - 位置

     - client/forms/login_form.py

   - 参数

     - 参数self：所在类LoginForm自身

   - 功能

     检查输入的用户名、密码是否合法；通过调用函数send()向服务器发送登录请求，并将输入的用户名、密码等信息发送给服务器。

7. show_register(self)

   - 位置

     - client/forms/login_form.py

   - 参数

     - self：所在类LoginForm自身

   - 功能

     与注册按钮关联，通过点击按钮调用库函数Toplevel()跳转到注册页面。

8. .\__init__(self,master=None)

   - 位置

     - client/forms/contacts_form.py

   - 参数

     - self：所在类ContactsForm自身
     - master：登录主窗口用来容纳其他组件,默认一个窗口master=None。

   - 功能

     通过库函数super()实现子类\__init\_\_()对父类\_\_init__()的继承；对好友列表窗口布局，确定好友列表的长宽、按钮的位置、颜色、类型、链接等；调用VerticalScrolledFrame()函数，将列表设置滚动条＋图片背景；初始化安全信道；通过socket_listener()函数和remove_socket_listener_and_close()函数控制对客户端socket事件监听和关闭。

9. refresh_contacts(self)

   - 位置

     - client/forms/contacts_form.py

   - 参数

     - self：所在类ContactsForm自身

   - 功能

     通过比较与好友或群聊最近一次发消息的时间last_message_timestamp和好友的在线情况刷新好友列表，根据好友或群聊发送消息的时间远近对好友列表进行排列，并将在线好友移至列表顶部

10. on_add_friend(self)/on_del_friend(self)/on_add_room(self)on_create_room(self)

    - 位置

      - client/forms/contacts_form.py

    - 参数

      - self：所在类ContactsForm自身

    - 功能

      与添加好友、删除好友、添加群聊、创建群聊四个按钮链接；使用库函数simpledialog.askstring()弹出输入框，并对输入的内容进行检验；使用函数send()向服务器发送操作请求。

11. handle_new_contact(self,data)

    - 位置

      - client/forms/contacts_form.py

    - 参数

      - self：所在类ContactsForm自身
      - data：接收的数据

    - 功能

      被该文件下的另一个函数\_\_init\_\_()调用用来添加或删除列表中的好友。

12. \__init__(self,target,master=None)

    - 位置

      - client/forms/chat_form.py

    - 参数

      - self：所在类ChatFrame自身
      - target：一个用来暂时存储消息的列表
      - master：聊天框主窗口用来容纳其他组件,默认一个窗口master=None

    - 功能

      对聊天框布局，确定聊天框的长宽、输入框、消息框、按钮的位置、颜色、类型、链接等；分辨私人聊天和群聊；利用append_to_chat_box()函数加载、更新历史消息。

13. send_message(self)/send_file(self)

    - 位置

      - client/forms/chat_form.py

    - 参数

      - self：所在类ChatFrame自身

    - 功能

      通过调用input_textbox.get()函数和filedialog.askopenfilename()函数实现发送消息和文件。

14. digest_message(self,data)

    - 位置

      - client/forms/chat_form.py

    - 参数

      - self：所在类ChatFrame自身
      - data：传输的数据

    - 功能

      通过分析传输的数据包，摘取消息的时间戳、发送者、消息类型，为布局做准备。

15. \__init__(self,parent,onclick)

    - 位置

      - client/components/contact_item.py

    - 参数

      - self：所在类ContactItem自身
      - parent：向函数内定义的子类传递的参数
      - onclick：跳转动作

    - 功能

      位于ContactItem类中，对好友列表中的每一行进行布局如

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714140712.png)

16. \__init__(self,parent,*args,**kw)

    - 位置

      - client/components/vertical_scrolled_frame.py

    - 参数

      - self：所在类VerticalScrolledFrame自身
      - parent：向函数内定义的子类传递的参数
      - *args：可变参数
      - **kw：关键字参数

    - 功能

      利用Scrollbar()函数创建一个带有滚动条的画布，并可以通过滚动条对画布及时更新。

#### common函数

1. gen_secret()

   - 位置

     - common\cryptography\crypt.py

   - 功能

     产生用户的公钥私钥

   - 算法描述

     利用prime.generate_big_prime()函数产生一个大的素数作为私钥，然后利用相应算法计算出自己的公钥，将公钥和私钥保存成文件，公钥可写入证书，私钥单独保存不传输

2. \_serialize_xxx(xxx)

   - 位置

     - common\message\__init__.py

   - 参数：要序列化的数据类型

   - 功能

     针对传入的不同数据类型进行序列化算法描述：对不同数据类型进行序列化成二进制然后返回统一格式的数据，方便进行数据的传输和存好友的用户名和在线状态最近一次消息时间好友的IP地址和端口号消息内容未读消息计数储。每个序列化后的数据格式为：|——VAR_TYPE(1Byte)——|——DATA_LEN(4Bytes)——|——DATA——|。即1字节数据类型，4字节数据长度和数据部分。

     主要用_serialize_list(list):_serialize_list(list)数据打包格式如下：|——1ByteTypeofparams——|——4BytesLengthofbody——|——Body(self-evidentlength)——|——Body(selfevidentlength)——|——Body(self-evidentlength)——|..即第一字节为列表类型，然后4字节的数据长度，由每种数据类型占用长度不同分配不同的BODY长度，每一个BODY可以是如list,int,float等数据类型。

3. \_deserialize_xxx(bytes)

   - 位置

     - common\message\__init__.py

   - 参数：二进制数据

   - 功能

     针对传入的不同数据类型数据进行反序列化成原本数据

   - 算法描述

     对二进制进行反序列成指定的数据类型，即是_serialize_xxx的逆过程，可用于解析数据包。

4. send(self,message_type,parameters=None)

   - 位置

     - common\transmission\secure_channel.py

   - 参数

     - self即为SecureChannel类
     - message_type即为消息的类型

   - 功能

     按照自制的协议组织数据包发送数据包

   - 算法描述

     数据包的格式为前四个字节为消息体的长度，接着一字节存储AES加密时的消息填充长度，然后16字节AES加密时所需要的初始值，再接着是32字节的消息摘要，最后才是加密后的消息体。

5. on_data(self,data_array)

   - 位置

     - common\transmission\secure_channel.py

   - 参数

     - self即为SecureChannel类
     - data_array即为字节数组

   - 功能

     解析数据包，并利用mac验证消息的完整性

   - 算法描述

     首先把bytes([padding_n])+iv1+encrypted_message传给本函数，然后得到消息体，和消息摘要，接收方对消息利用相同的算法计算其消息摘要，验证消息是否被篡改最后对消息解密，返回解密后的反序列化后的原始数据。

6. establish_secure_channel_to_server()

   - 位置

     - common\transmission\secure_channel.py

   - 功能

     与集中服务器建立安全信道

   - 算法描述

     客户端首先获取本机的ip地址，生成自己的私钥公钥和证书，首次连接的时候要给服务器发送证书，计算出二者的共同密钥。

7. accept_client_to_secure_channel(socket)

   - 位置

     - common\transmission\secure_channel.py

   - 参数

     - socket：客户端和服务器通信的socket

   - 功能

     服务器接收客户端建立安全信道

   - 算法描述

     首次连接，客户端会发送公钥，把服务器的证书发送给客户端，二者计算出共同密钥。

8. gen_last_message(obj)

   - 位置

     - common\utli\socket_listener\\_\_init__.py

   - 参数

     - obj为传输数据data的obj类型

   - 功能

     获取对象中message的类型，0表示文字信息，1表示图片信息

   - 算法描述

     obj\['message']['type']判断0与1.type0-文字消息1-图片消息。

9. socket_listener_thread(sc,tk_root)

   - 位置

     - common\socket_listener\__init.py

   - 参数

     - sc是已经建立的C-S安全socket，socket_channel,带有对称秘钥
     - tk_root是tkinter界面对象。

   - 功能

     循环接收信息，进入socket监听状态，当接受到信息后完整的接收数据包并从中获取操作码，根据操作码的不同进行不同的处理。

   - 算法描述

     使用select.select函数阻塞运行，当有处理时不会被其他人占用。其中接受数据有三个变量：

     - bytes_to_receive=0
     - bytes_received=0
     - data_buffer=bytes()

     当bytes_to_receive=0、bytes_received=0时表示正准备接受一个新的socket数据。开始接收后会通过数据包前四个字节判断长度。如果长度小于四字节说明是损坏的包或者是空包，没有数据，表示服务器已关闭。通过指针[0]+1+16使指针指向数据部分。+1是aes的填充部分1字节，+16是aes初始向量4字节。直到接收完毕为止。接受完会把数据包解包取出数据部分，并不断拼接形成完整数据字符串。

10. digest_message(data,update_unread_count=True)

    - 位置

      - common\socket_listene\\\_\_init__.py

    - 参数

      - data是要放入的历史数据
      - update_unread_count初始参数设置为True使消息未读数自增

    - 功能

      实现将历史数据放入chat_history列表中，更新最新消息，消息时间，消息未读数量，并更新用户的好友列表，在前端进行刷新，更新聊天窗口。

    - 算法描述

      通过if像chat_history中的数据填入以前的数据。将data更新用于发送。

11. add_listener(func)

    - 位置

      - common\socket_listener\\_\_init__.py

    - 参数

      - func是一个函数

    - 功能

      将某一函数事件放入执行列表中，之后会被逐个调用

    - 算法描述

      将func函数append到callback_funcs待执行函数列表中。

12. remove_listener(func)

    - 位置

      - common\socket_listener\_\_init__.py

    - 参数

      - func是一个函数

    - 功能

      将某一函数事件从执行列表中移除

    - 算法描述

      列表的remove操作

#### 服务器端函数

1. handler_event

   - 位置

     - server\event_handler\__init__.py

   - 参数

     - sc：即为相应的socket；
     - event_type：即为事件的类型；
     - parameters：相应事件中包含的参数。

   - 功能

     将不同类型的event映射到相应的事件处理操作上，比如将MessageType.login映射到执行login的处理操作上。

   - 算法描述

     主要是利用map根据提供的函数对指定事件做映射。

2. run

   - 位置

     - server\event_handler\login.py

   - 参数

     - sc：相应的socket
     - parameters：从客户端传入的相关参数

   - 功能

     客户端点击登录按钮后，集中服务器进行用户登录后的相关操作。

   - 算法描述

     首先从传入的参数中得到用户的username和对应的password，继而得到对数据库的控制操作权限，查询该用户是否存在，用户名和密码是否匹配。若返回值为0，则为客户端发送MessageType.login_failed。下一步查看该用户是否已经登入，若已登入则踢下线，否则登录成功，向客户端发送MessageType.login_successful。登录成功后向客户端发送好友列表，通知他的好友他已上线，最后从数据库中读出他的聊天记录，将其和好友列表一起作为login_bundle的参数发送给客户端。

3. run

   - 位置

     - server\event_handler\register.py

   - 参数

     - sc：相应的socket；
     - parameters：从客户端传入的相关参数

   - 功能

     客户端点击注册按钮后，集中服务器进行用户注册后的相关操作

   - 算法描述

     首先从传入的参数中获取用户名，继而得到对数据库的控制操作权限，查询该用户名是否已被注册，若被注册则向客户端发送MessageType.username_taken，否则的话传入的参数中获取用户的ip，重写用户生成的证书，然后再把用户的信息插入到数据库中。

4. run

   - 位置

     - server\event_handler\add_friend.py

   - 参数

     - sc：相应的socket；
     - parameters：从客户端传入的相关参数

   - 功能

     客户端点击添加好友输入好友用户名后，集中服务器进行用户添加好友后的相关操作

   - 算法描述

     首先从传入的参数中得到用户的username，继而得到对数据库的控制操作权限，查询该用户是否存在，若不存在向客户端发送MessageType.add_friend_result，并提示用户“用户名不存在”，否则根据用户名找到用户id，判断其是否为自己的id，则提示用户”不能加自己为好友“。再下一步查询用户自己的id和好友id是否已在friends表中，若存在，则提示用户“已经是好友/已经发送过好友请求”，否则的话将用户自己的id和好友id插入到friends表中，但是accpted的值为0，因为此时还不清楚对方是否同意添加你为好友。然后向用户发送MessageType.add_friend_result，值为true。最后若对方在线，则向其发送MessageType.incoming_friend_request，让对方处理添加好友的请求。

5. run

   - 位置

     - server\event_handler\resolve_friend_request.py

   - 参数

     - sc：相应的socket；
     - parameters：从客户端传入的相关参数

   - 功能

     当有用户向目标用户发送好友添加请求时,服务器处理好友请求操作

   - 算法描述

     首先从传入的参数中得到uid，继而得到对数据库的控制操作权限，查询friends表中好友关系(accepted状态为0)是否在数据库中已存在，若不存在也不进行相关操作。若拒绝添加好友，则将数据库中的该条数据删除，若同意加为好友，则更新friends表accepted为1，并且在数据库中添加双向关系。并给客户端发送MessageType.contact_info，在好友列表中显示添加成功的好友。若对方在线，也发送MessageType.contact_info，在好友列表中显示添加成功的新好友。

6. run

   - 位置

     - server\event_handler\del_friend.py

   - 参数

     - sc：相应的socket；
     - parameters：从客户端传入的相关参数

   - 功能

     客户端点击删除好友，输入好友用户名后，集中服务器进行用户删除好友后的相关操作。

   - 算法描述

     首先从传入的参数中得到用户的username，继而得到对数据库的控制操作权限，查询该用户是否存在，若不存在向客户端发送MessageType.add_friend_result，并提示用户“用户名不存在”，否则根据用户名找到用户id，判断其是否为自己的id，则提示用户”不能删除自己“。再下一步判断对方是否是自己的好友，查询用户自己的id和好友id是否已在friends表中，若不存在，则提示用户“该用户还不是您的好友”，若对方是自己的好友，则在friends表中删除二者的好友关系，并向客户端发送MessageType.del_info，使删除的好友在好友列表中消失。若对方在线，也发送MessageType.del_info，使自己在对方好友列表中也消失，实现双向的删好友功能。

7. run

   - 位置

     - server\event_handler\create_room.py

   - 参数

     - sc：相应的socket；
     - parameters：从客户端传入的相关参数

   - 功能

     客户端点击创建群组聊天，输入群组名后，集中服务器进行创建群组的相关操作。

   - 算法描述

     首先获取user_id，然后将该群聊加入数据库rooms中，并且向客户端发送MessageType.contact_info，使用户在好友列表中显示群聊。最后向客户端发送MessageType.general_msg，提示用户创建群聊成功，并显示群号。

8. run

   - 位置

     - server\event_handler\join_room.py

   - 参数

     - sc：相应的socket；
     - parameters：从客户端传入的相关参数

   - 功能

     客户端点击添加群组聊天，输入群组名后，集中服务器进行添加群聊的相关操作。

   - 算法描述

     首先获取user_id，调用数据库的in_room函数判断用户是否已在群中，若已在则提示用户“已在群里了“，调用数据库的get_room函数判断群聊是否存在，若不存在提示用户”群不存在“，否则调用add_to_room将用户加入到群聊中，并向客户端发送MessageType.contact_info，使用户在好友列表中显示该群聊。

9. get_user(user_id)

   - 位置

     - server\util\database\\_\_init\_\_.py

   - 参数

     - int型，表示该用户的用户id

   - 功能

     获取数据库中users表中id值为user_id的那一行的所有数据。

   - 算法描述

     执行数据库查询语句返回一行结果。若无结果返回空。

10. get_pending_friend_request(user_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - user_Id,int类型，表示某一个用户的id值。

    - 功能

      返回一个列表，列表中的内容为加user_id的用户的好友们的个人信息。

    - 算法描述

      从数据库中查询friends表，to_user_id为user_id的行中且为accepted=1的获取from_user，用get_user函数查询他们的信息并append到列表中。

11. get_friends(user_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - user_Id,int类型，表示某一个用户的id值。

    - 功能

      类似get_pending_friend_request(user_id)函数，只是会返回‘我’加谁为好友且accept的用户信息。

    - 算法描述

      从数据库中查询friends表，from_user_id为user_id的行中且为accepted=1的获取to_user，用get_user函数查询他们的信息并append到列表中。

12. get_room(room_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - room_id，int类型，表示一个room的id值

    - 功能

      返回群聊id为room_id的群聊房间在rooms表中的所有信息的字典，包括id,名字

    - 算法描述

      从数据库中查询room表，返回对应room_id的room的全部信息，压缩为字典并返回。

13. get_user_rooms(user_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - user_Id,int类型，表示某一个用户的id值。

    - 功能

      返回一个字典，列表中内容为user_id用户加入的群聊的room的全部信息。

    - 算法描述

      从数据库中查询room_user表，返回对应user_id的room的全部信息值，变成字典中并返回。

14. get_user_rooms_id(user_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - user_Id,int类型，表示某一个用户的id值。

    - 功能

      返回一个列表，列表中内容为user_id用户加入的群聊的room_id。

    - 算法描述

      从数据库中查询room_user表，返回对应user_id的room_id的全部信息值，append入列表中并返回。

15. is_friend_with(from_user_id,to_user_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - from_user_id为好友发起请求方
      - to_user_id为接收好友请求方

    - 功能

      返回一个判断值1或者0.判断两者是否为朋友。

    - 算法描述

      从friends表中查询有无两者建立关系的一行，若没有，则返回0表示不是好友。

16. in_room(user_id,room_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - user_id为待检查用户
      - room_id为待检查群聊号

    - 功能

      判断user_id用户是否在room_id的群聊中。

    - 算法描述

      从room_user表中查询有无两者建立关系的一行，若没有，则返回0表示不是不在群聊中。

17. add_to_room(user_id,room_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - user_id为待检查用户
      - room_id为待检查群聊号

    - 功能

      将用户id为user_id的用户加入到room_id的群聊中。

    - 算法描述

      数据库insert将user_id插入到room_id的room_user表中。

18. get_room_members_id(room_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - room_id为待检查群聊号

    - 功能

      获取群聊中的所有用户id。

    - 算法描述

      select逐一查询，将结果返回入列表。

19. add_to_chat_history(user_id,target_id,target_type,data,sent)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - user_Id是发送者id
      - target_id是目标用户id
      - target_type是数据类型，0表示文本信息，1表示图像文件信息
      - data是传输存储的数据
      - sent标志位记录是否发送成功。若为0，下一次还会再发送。

    - 功能

      将聊天信息加入到正确用户的数据库中。

    - 算法描述

      将相关信息insert入表chat_history中。

20. get_chat_history(user_id)

    - 位置

      - server\util\database\\_\_init__.py

    - 参数

      - user_id为待检查用户

    - 功能

      获取user_id用户的聊天记录。

    - 算法描述

      select查询并更新sent标志位。

## 实现效果

1. 注册页面

   对输入的用户名、密码、邮箱、确认密码等进行检查，用户名和密码限制输入非法字符，邮箱限制输入为 xxx@xxx.xxx 形式，同时限制输入的用户名长度不大于 8 个，允许中文输入。

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714145452.png)

2. 登录页面

   对输入的用户名和密码进行检查，限制输入非法字符，同 时限制输入的用户名长度不大于 8 个，允许中文输入。

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714145528.png)

3. 好友列表

   好友列表会显示所有好友的在线状态、IP 地址、端口号、最新消息和未读消息， 好友列表根据用户离线、在线情况对列表进行刷新,将在线和最近聊天用户置顶。

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714145654.png)

4. 添加好友

   1. 添加好友时需要输入用户名，同时会对输入的信息进行合法性检查，不能添加自 己为好友。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714145755.png)

   2. 要添加的好友用户名必须为已经注册的用户，否则会显示用户名不存在。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714145832.png)

   3. 输入正确用户名并点击 OK 后，会显示好友请求已发送。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714145916.png)

   4. 如果在线，会显示好友请求，点击 YSE 后，会在双方的好友列表中添加；点击 NO 后两个用户无法成为好友；点击 cancle 后，下次登陆时会再次弹出好友请求框。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150022.png)

5. 删除好友

   1. 与添加好友相同，需要输入用户名，同时会对输入的信息进行合法性检查，不能删 除自己。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150145.png)

   2. 不能删除好友列表中不存在的用户。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150237.png)

   3. 输入正确用户名并点击 OK 后，会显示成功删除好友，并且好友列表进行刷新删除 刚刚删除的好友信息，删除用户也会对好友列表进行刷新,即双方向删除。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150347.png)

6. 添加群聊

   需要输入要添加的群聊的群号，同时会对输入的信息进行合法性检查，如果群号 不存在则无法添加，同样如果已经在群聊中，会显示已经在群聊中。

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150443.png)

7. 创建群聊

   需要输入创建的群聊的群名称，同时会对输入的信息进行合法性检查，如果群名 称已存在，则无法创建，创建成功后会分配一个群号。

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150547.png)

8. 群聊界面

   1. 在群聊界面中，用户可以直接发送消息，也可以点击发送文件按钮发送文件，聊天 框会显示用户名、发送时间和消息内容，不同用户名颜色不同，历史消息会进行缓 存，用户再次打开聊天框时会直接显示。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150653.png)

   2. 用户可以根据自己的习惯更改字体大小。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150733.png)

   3. 用户可以根据自己的习惯更改字体颜色。

      ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150811.png)

9. 用户聊天界面

   和群聊界面基本相同，用户聊天内容会缓存到客户端文件夹中，发送的文件会存 储到专用文件夹中，如下图。

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714150901.png)

   ![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714151012.png)

## 待优化

正常信息交互流程，server 端会返回加密数据，此时 client 会一直等待接收 （while true）。如果发的太大，server 端加密不出来，client 一直监听，导致 client 无法再次发起操作。

![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714151144.png)

以正常的发送图片数据抓包为例子，server 会不断接收，然后做加密。

![](https://leeyuxun-1258157351.cos.ap-beijing.myqcloud.com/img/20200714151209.png)
