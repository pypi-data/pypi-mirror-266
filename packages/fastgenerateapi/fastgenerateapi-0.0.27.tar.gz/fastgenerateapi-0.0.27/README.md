
# FastGenerateApi

[联系作者](https://github.com/ShiLiangAPI)

[Github](https://github.com/ShiLiangAPI)

#### 介绍
稳定版本：v0.0.21
建议python版本：3.9+
推荐fastapi版本：0.97.0

###### FastGenerateApi 使用说明


#### 软件架构说明

```
封装了 快速生成API,包括(增,删,改,查,递归查询,递归删除,关联修改,关联查询)
封装了 新增缓存配置，默认不使用缓存；新增树状查询方案，可配置选择
封装了 Websocket API和分组消息发送
封装了 路由接口路径的灵活配置,返回值字段的灵活配置,分页参数的灵活配置,等其他项
封装了 增,改 对唯一字段的校验,非空字段的校验
封装了 删 对唯一字段追加时间戳格式修改
封装了 查 灵活的筛选,以及swagger文档的自动生成
封装了 通过数据库模型,自动生成schemas,并swagger附带文档
封装了 类方法的实现,增加了相关的钩子函数
封装了 通用性接口,例如excel的导入导出,pdf文件生成,模型数据跨表取值
待封装 RPC的调用
```

#### 使用教程

1.  简单使用
2.  增删改查进一步优化使用
3.  查询筛选文档注意项（本地FastAPI源码修改，上线部署不需要修改）
4.  其他接口书写方式
5.  websocket 使用
6.  配置参数的使用

#### 使用说明

#### 1. 简单使用

数据库模型以 附带的example为例,代码如下
- 启动后自动生成 增,删,改,查 接口
```
app = FastAPI()

class StaffView(APIView):
  model_class = StaffInfo

app.include_router("v1", StaffView())

uvicorn.run(app)
```
注意点：
- 路径自动添加数据库模型转换的字段 "/staff-info"
- 自动添加swagger对应的标签，内容为数据库模型的描述
- 自动通过数据库模型生成对应的所有的schemas

#### 2. 增删改查进一步优化使用
根据增,删,改,查类，对应成员的填写
数据库模型 class PydanticMeta， 对schemas生成空值:
- include, exclude
  - include: 为兼容手写schemas，推荐只限制数据库模型字段
- get_one_include, get_one_exclude
  - 与include同时生效，无include自动包含数据库模型搜友字段
  - 可添加跨表字段，自动生成校验和文档
  - 其他字段: ("test", Optioanl[str], FieldInfo(..., description="文档描述"))
- get_all_include, get_all_exclude
- create_include, create_exclude
- update_include, update_exclude

```
待完成...
```

#### 3. 查询筛选文档注意项
本地FastAPI源码修改，上线部署不需要修改
- (fastapi == 0.97.0、0.87.0)源码修改
    - 文件路径：fastapi/dependencies/utils.py/第302行
    - 可搜索方法：get_dependant
```
...
param_field = get_param_field(
    param=param, default_field_info=params.Query, param_name=param_name
)
############### 添加内容  ####################
try:
	if type(call).__name__ == 'ModelMetaclass' and issubclass(call, BaseModel):
	    param.default.description = call.__fields__.get(param_name).field_info.description  
except:
    ...
##################################
if param_name in path_param_names:
  ...
```

#### 4、其他接口书写方式
方法使用规则
- view 标识符号
- get/post/put/patch/delete 方法
- 后续字段: 路由路径
    - pk 路径参数,可省略
- 多段路径： view_get_test__test
    - url .../test/test
- 其他使用与原FastAPI一致
```
class TestSchema(BaseModel):
  pk: str
  test: str

class TestView(BaseView):

  def view_get_test_pk(self, pk: str, name: str) -> TestSchema:
    return self.success(data=TestSchema(pk=pk, test=name))

# url = .../test/{pk}
```

#### 5、websocket 使用
详情请查看example文件

#### 6、配置参数的使用
第一步：配置参数的查看
- 如果生成.env.example全局Settings中继承SettingsModel
```
from fastgenerateapi import SettingsModel

class Settings(SettingsModel):
    """
        Global settings
    """
    ...
```
第二步：配置参数修改
- 在.env中修改参数值，会自动生效
```
[AppSettings]
# 当前页字段
APP_CURRENT_PAGE_FIELD=page
```





















