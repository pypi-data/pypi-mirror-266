# Gmtestplugin

    大家软件Python插件定制私有库开发项目

## change logs
v0.0.46
    增加文件上传
v0.0.45
    增加gm_format_parmas工具，支撑批量替换URL中{}参数
v0.0.44
    OperateMysql()类的delete_data()函数支持多条SQL语句

V0.0.42
    OperateMysql()类支撑通过Pytest环境变量调用

V0.0.39
    1：修复登录行采家的登录问题
    2：修复触发二次手机登录时未处理逻辑的问题

V0.0.19
   sql工具类增加达梦数据库ODBC（test1）

V0.0.16
   1、增加登录封装gm_login2_utils.py
   2、优化second_verify.py
   
V0.0.15 
   增加二次验证读取identities的值

V0.0.14
    gm_assert_utils工具增加按列表分别取列表中的值并进行验证gm_assert_list_anyone_in

v0.0.13
  gm_assert_utils工具增加字典类型验证 gm_assert_dict_iseuqal

V0.0.12
  gm_assert_utils工具增加 gm_assert_lists_isinclude和gm_assert_lists_iseuqals验证

V0.0.11
  增加analysis库
v0.0.10
  优化部分内容
v0.0.9
  demo演示

v0.0.8
 修改gm_prase_response的调用名称为gm_extract_json
 增加gm_sucreditcode_utils，用于生成企业社会信用代码

v0.0.6 
 修改gm_request_utils的请求参数verfiy的默认值,由NONE调整成False

v0.0.5

 增加gm_assert_utils：assert验证封装

 增加gm_excel_utils: excel工具类封装

 增加gm_stock_enum: 增加采购数据枚举类

 增加gm_yaml_process_utils: 增加yaml工具类

 增加gm_request_utils：增加requests请求封装类	

v0.0.4
  增加gm_prase_response.py: 解析request请求返回值
  增加gm_timestamp.py： 生成测试的时间戳

v0.0.3 
  优化目录结构
  china_address.py 
  getrandomdata.py -- 生成随机数据
  mysqlconn.py -- 数据库连接池
v0.0.2 
  try something

v0.0.1 
  mydemo-package 实验项目