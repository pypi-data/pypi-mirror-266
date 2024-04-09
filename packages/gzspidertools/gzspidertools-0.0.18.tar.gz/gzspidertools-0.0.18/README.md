# 来自
> https://github.com/shengchenyang/AyugeSpiderTools/blob/master/docs//docs/intro/install.md
> 
> 增加个人使用的模板

## 安装

> `python 3.8+` 可以直接输入以下命令：

```shell
pip install gzspidertools
```

> 可选安装1，安装数据库相关的所有依赖：

```shell
pip install gzspidertools[database]
```

> 可选安装2，通过以下命令安装所有依赖：

```shell
pip install gzspidertools[all]
```

*注：详细的安装介绍请查看[安装指南](https://ayugespidertools.readthedocs.io/en/latest/intro/install.html)。*

## 用法
```shell
# 查看库版本
gzcmd version

# 创建项目
gzcmd startproject <project_name>

# 进入项目根目录
cd <project_name>

# 替换(覆盖)为真实的配置 .conf 文件：
# 这里是为了演示方便，正常情况是直接在 VIT 中的 .conf 文件填上你需要的配置即可
cp /root/mytemp/.conf DemoSpider/VIT/.conf

# 生成爬虫脚本
gzcmd genspider <spider_name> <example.com>

# 生成 scrapy-redis 爬虫脚本   pip install scrapy_redis-0.7.3-py2.py3-none-any.whl
gzcmd genspider -t=sr <spider_name> <example.com>

# 运行脚本
scrapy crawl <spider_name>
# 注：也可以使用 gzcmd crawl <spider_name>
```

# RedisDB

RedisDB支持**哨兵模式**、**集群模式**与单节点的**普通模式**，封装了操作redis的常用的方法

## 连接

> 若环境变量中配置了数据库连接方式或者setting中已配置，则可不传参

### 普通模式

```python

db = RedisDB(ip_ports="localhost:6379", db=0, user_pass=None)
```

使用地址连接

```python

db = RedisDB.from_url("redis://[[username]:[password]]@[host]:[port]/[db]")
```

### 哨兵模式

```python

db = RedisDB(ip_ports="172.25.21.4:26379,172.25.21.5:26379,172.25.21.6:26379", db=0, user_pass=None, service_name="my_master")
```

注意：多个地址用逗号分隔，需传递`service_name`

对应setting配置文件，配置方式为：

```python
REDISDB_IP_PORTS = "172.25.21.4:26379,172.25.21.5:26379,172.25.21.6:26379"
REDISDB_USER_PASS = ""
REDISDB_DB = 0
REDISDB_SERVICE_NAME = "my_master"
```

### 集群模式

```python
db = RedisDB(ip_ports="172.25.21.4:26379,172.25.21.5:26379,172.25.21.6:26379", db=0, user_pass=None)
```

注意：多个地址用逗号分隔，不用传递`service_name`

对应setting配置文件，配置方式为：

```python
REDISDB_IP_PORTS = "172.25.21.4:26379,172.25.21.5:26379,172.25.21.6:26379"
REDISDB_USER_PASS = ""
REDISDB_DB = 0
```