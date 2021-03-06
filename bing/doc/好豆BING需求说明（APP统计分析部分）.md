APP统计分析部分

2014/05/27

# 概述


## 常用术语
本文中，“用户”在大多数情况下，与“设备”同义，按设备ID 统计。在谈到“登录用户”时，则理解为网站/应用注册用户，按用户ID 统计。

| 术语       | 术语含义                                     |
| -------- | ---------------------------------------- |
| 新增用户     | 首次启动应用的用户（以设备为判断标准）                      |
| 活跃用户     | 在统计周期内启动过应用的用户（去重），启动过一次的设备即视为活跃用户，包括新用户与老用户 |
| 累计用户     | 截止统计周期结束时间，启动过应用的所有独立用户（去重，以设备为判断标准）。    |
| 留存用户     | 某段时间内的新增用户，经过一段时间后，仍继续使用应用的被认作是留存用户，这部分用户占当时新增用户的比例既是留存率。 |
| 启动次数     | 在收到用户发起的一次请求时，如果之前5分钟（超时时长）没有发生请求，则该请求被视为开始一个会话（启动）。*注：友盟口径分为安卓设备与iOS 设备。安卓设备启动是通过再所有Activity 中调用MobclickAgent.onResme() 和MobclickAgent.onPause() 方法来监测的。若用户使用过程中进入home 或其他程序，经过一段时间间隔后才返回之前的应用，如果间隔超过x（x可以由开发者自由设定，默认30）秒，则被认为是两次启动。iOS 设备在iOS4.x之后的系统，由于iOS 开始支持后台运行，进入后台即算是当前统计会话结束，当再次进入前台时，算作一次新的启动行为，并开始新的统计会话。* |
| 单次使用时长   | 用户首次发起请求后，被视为开始一个会话。如果在每次请求接下来的5分钟内有下一个请求发生，则该会话持续，直到5分钟内没有请求发生，此时被视为该会话结束。该会话第1个请求发生时间到最后一次请求发生时间之差，即为本次会话时长（单次使用时长） |
| 平均单次使用时长 | 单次使用时长的均值，即应用的总使用时长/总启动次数。               |
| 数据变化率    | (本次数据-上次数据)/上次数据                         |
| 过去N天活跃用户 | 过去N天内启动过应用的用户（去重），启动过一次的用户即视为活跃用户，包括新用户与老用户。 |
| 过去N天活跃占比 | 过去N天活跃用户占累计用户的比例                         |
| IDFA     | 苹果设备的 Identifier for Advertiser 的缩写。     |
| IDFV     | 苹果设备的 Identifier for Vendor 的缩写。         |
|          |                                          |

# 数据说明

## 原始数据部分（ODS）

**应用请求日志（APPLOG）**

在原BI系统中，该数据被命名为CDA39907，对应的表名为： dw.t_dw_applog
在大数据平台上，该数据HDFS存放路径为： /user/yarn/logs/source-log.php.CDA39907

从原始表logs.log_php_app_log 导入

表名： bing.ods_app_requestlog_dm

字段信息

| 字段名            | 字段说明                                     |
| -------------- | ---------------------------------------- |
| request_time   | 请求时间。该请求时间格式为Unix 时间戳。                   |
| device_id      | 设备ID。iOS 设备ID 格式：设备MAC 地址的MD5+IDFA+IDFV。安卓设备ID 格式：haodou+设备IMEI。 |
| channel_id     | 渠道ID。格式：渠道编码+版本。                         |
| userip         | 用户访问IP                                   |
| app_id         | 应用ID。取值，1:去哪吃iphone/2:菜谱安卓/3:去哪吃安卓/4:菜谱iphone/5:华为机顶盒/6:菜谱ipad |
| version_id     | 版本。                                      |
| userid         | 用户ID。未登录用户为0。                            |
| function_id    | 请求调用的函数                                  |
| parameter_desc | 请求传递的参数                                  |
| uuid           | 设备UUID                                   |
| statis_date    | 日志日期（分区字段）。格式：yyyy-mm-dd。                |
|                |                                          |

**应用行为日志**

该日志为菜谱4.0新增日志，存放客户端的操作行为信息。
格式参考：手机APP数据统计技术文档 <http://wiki.haodou.com/index.php?title=手机APP数据统计技术文档>

表名： bing.ods_app_actionlog_raw_dm

字段信息

| 字段名         | 字段说明                    |
| ----------- | ----------------------- |
| statis_date | 统计日期 分区字段。格式：yyyy-mm-dd |
| json_msg    | 消息正文 数据格式为json 格式。      |
|             |                         |


## 数据仓库部分（DW）

**活跃设备日表**

表名：bing.dw_app_device_dm

字段信息

| 字段名           | 字段说明                                     |
| ------------- | ---------------------------------------- |
| statis_date   | 统计日期（分区字段）。格式：yyyy-mm-dd                 |
| app_id        | 好豆应用ID                                   |
| device_id     | 好豆设备ID                                   |
| channel_id    | 渠道ID。格式：渠道编码+版本。                         |
| first_time    | 首次活跃时间。格式：yyyy-mm-dd hh24:mi:ss。         |
| first_version | 当天首次版本ID                                 |
| first_userip  | 当天首次访问IP                                 |
| first_userid  | 当天首次登录用户ID。                              |
| dev_imei      | 安卓设备IMEI                                 |
| dev_uuid      | 设备UUID                                   |
| mac_md5       | 苹果设备MAC 的MD5 值                           |
| idfa          | 苹果设备IDFA                                 |
| idfv          | 苹果设备IDFV                                 |
| req_cnt       | 访问请求次数                                   |
| eff_reqcnt    | 有效访问次数                                   |
| isvirtual     | 虚拟机标识。取值：0 否（缺省）/1 是                     |
| isfake        | 虚假标识。取值：0 否（缺省）/1 单IP设备过多/2 特定IP（福建莆田IP） |
|               |                                          |


**渠道虚假活跃IP表**

表名：bing.dw_app_fake_ip

字段信息

| 字段名         | 字段说明                     |
| ----------- | ------------------------ |
| statis_date | 统计日期（分区字段）。格式：yyyy-mm-dd |
| app_id      | 好豆应用ID                   |
| channel_id  | 渠道ID。格式：渠道编码+版本。         |
| userip      | 虚假活跃IP地址                 |
| dev_num     | 该IP 下的活跃设备数              |
| req_cnt     | 该IP 下的访问请求次数             |
|             |                          |

**设备总表**

字段信息

| 字段名           | 字段说明                             |
| ------------- | -------------------------------- |
| app_id        | 好豆应用ID                           |
| device_id     | 好豆设备ID                           |
| first_day     | 首次活跃日期。格式：yyyy-mm-dd hh24:mi:ss。 |
| first_channel | 首次活跃渠道ID。格式：渠道编码+版本。             |
| first_version | 首次活跃版本ID                         |
| first_userip  | 首次活跃访问IP                         |
| first_userid  | 首次登录用户ID                         |
| last_day      | 最近活跃日期。格式：yyyy-mm-dd hh24:mi:ss。 |
| last_channel  | 最近活跃渠道ID。格式：渠道编码+版本。             |
| last_version  | 最近活跃版本ID                         |
| last_userip   | 最近活跃访问IP                         |
| last_userid   | 最近登录用户ID                         |
| dev_imei      | 安卓设备IMEI                         |
| dev_uuid      | 安卓设备UUID                         |
| mac_md5       | 苹果设备MAC 的MD5 值                   |
| idfa          | 苹果设备IDFA                         |
| idfv          | 苹果设备IDFV                         |
| virtual       | 虚拟机判断信息                          |
| issilent      | 沉默用户标识。取值：0，否（缺省）／1，是            |
| isvirtual     | 虚拟机用户标识。取值：0，否（缺省）／1，是           |
| isfake        | 虚假标识。取值：0，否（缺省）／1，是              |
| uninst_date   | 卸载日期。格式：yyyy-mm-dd。              |
|               |                                  |

**设备留存表**

字段信息

| 字段名           | 字段说明                                    |
| ------------- | --------------------------------------- |
| app_id        | 好豆应用ID                                  |
| device_id     | 好豆设备ID                                  |
| first_day     | 首次活跃日期。格式：yyyy-mm-dd hh24:mi:ss。        |
| first_channel | 首次活跃渠道ID。格式：渠道编码+版本。                    |
| first_version | 首次活跃版本ID                                |
| remainlog     | 留存日志串。缺省：000~000（60个0）。对应天数活跃，相应天位置改为1。 |

注：目前保留两个月内的留存情况。

**活跃时长日表**

字段信息

| 字段名          | 字段说明                               |
| ------------ | ---------------------------------- |
| statis_date  | 统计日期（分区字段）。格式：yyyy-mm-dd           |
| app_id       | 好豆应用ID                             |
| device_id    | 好豆设备ID                             |
| channel_id   | 活跃渠道ID。格式：渠道编码+版本。                 |
| version_id   | 活跃版本ID                             |
| session_id   | 当次设备会话ID                           |
| request_time | 当次会话开始时间。格式：yyyy-mm-dd hh24:mi:ss。 |
| request_cnt  | 当次会话请求次数                           |
| duration     | 当次会话时长。单位：秒                        |
|              |                                    |


## 数据处理过程

1. 生成当天设备活跃数据、虚假渠道活跃IP表（bing.dw_app_device_dm/bing.dw_app_fake_ip）

从当天 APPLOG 中，按应用、渠道、IP，统计请求设备数、访问请求次数，如果请求设备数大于12的，视为虚假渠道，该IP视为虚假活动IP记入渠道虚假活跃IP表。
从当天 APPLOG 中，按应用、设备ID（如果安卓应用的 uuid 非空，则取“原设备id|uuid”做设备id）、渠道，取首次活跃的时间，版本，IP，并取出当天首次登录时的用户id（非0）。
对安卓应用，取设备id第1段写入 dev_imei，第2段写入 dev_uuid；对苹果应用，取设备id第1段写入 mac_md5，第2段写入 idfa，第3段写入 idfv。设备id的分段使用"|"字符分割。
访问请求次数取所有请求数。有效请求次数排除那些后台定时请求。
后台定时请求包括：安卓菜谱的 notice.getpullnotice / mobiledevice.initandroiddevice / recipe.getfindrecipe / ad.getad_imocha；安卓去哪吃的 /Msg/Pull/getNotice 。
如果某应用、渠道、设备在相应应用、渠道的虚假活跃IP中发生了请求，则该设备的相应虚假标志取1。


--渠道虚假活跃IP表
drop table bing.dw_app_fake_ip;
create table bing.dw_app_fake_ip
(
  app_id       string comment '好豆应用ID',
  channel_id   string comment '渠道ID。格式：渠道编码+版本。',
  userip       string comment '虚假活跃IP地址',
  dev_num      int comment '该IP 下的活跃设备数',
  req_cnt      int comment '该IP 下的访问请求次数'
) comment '渠道虚假活跃IP表'
  partitioned by (statis_date string)
  row format delimited fields terminated by '\001' stored as textfile
;


| req_cnt | 访问请求次数 |
| eff_reqcnt | 有效请求次数 |
| isvirtual | 虚拟机标识。取值：1，是，0，否（缺省） |
| isfake | 虚假标识。取值：1，是，0，否（缺省） |
|  |  |




1. 从当天APPLOG 中，取出设备ID ，以及相应的应用ID，与相应应用的历史设备库中的设备ID 比较。如果该设备ID 不存在历史设备库中，则该设备为新增设备，并将该设备ID 添加到历史设备库中；如果该设备ID 存在历史设备库中，则该设备不记为新增设备（用户）。
2. 基于当天APPLOG 以及历史设备库，计算相关指标。
3. 将计算出的相关指标数据，导入MySQL 数据库。
  注意：由于历史原因，过去的iOS 设备ID 只有第1段，在后来的版本中才增加了IDFA 与IDFV，需要避免由于扩展造成的新增重复计算。

关于虚假判定
目前根据单个渠道发行版本在单IP 的活跃用户数进行虚假判定。如果单个渠道发行版本在单IP 的活跃用户数大于12，则该IP 被视为该渠道发行版本的虚假活动IP，该IP 上的的所有该渠道发行版本的活跃用户都被视为虚假用户。
注意：虚假用户的判断策略需要维护，以保证虚假用户判断的有效性（查全性与查准性）。

# 功能性需求

## 应用概况

### 今日数据 todayData

- 日新增用户数 第一次启动应用的用户（以设备为判断标准）
- 日活跃用户数 启动过应用的用户（去重），启动过一次的用户即视为活跃用户，包括新用户与老用户
- 日留存用户数 昨日新增用户，在当天依旧使用应用的用户数。
- 日平均单次使用时长 单次使用时长的均值，即应用的总使用时长/总启动次数
- 日启动次数 在收到用户发起的一次请求时，如果之前5分钟（超时时长）没有发生请求，则该请求被视为开始一个会话（启动）。*注：友盟口径分为安卓设备与iOS 设备。安卓设备启动是通过再所有Activity 中调用MobclickAgent.onResme() 和MobclickAgent.onPause() 方法来监测的。若用户使用过程中进入home 或其他程序，经过一段时间间隔后才返回之前的应用，如果间隔超过x（x可以由开发者自由设定，默认30）秒，则被认为是两次启动。iOS 设备在iOS4.x之后的系统，由于iOS 开始支持后台运行，进入后台即算是当前统计会话结束，当再次进入前台时，算作一次新的启动行为，并开始新的统计会话。*
- 累计用户 截止到现在，启动过应用的所有独立用户（去重，以设备为判断标准）
- 过去7天活跃用户 过去7天启动过应用的用户（去重），启动过一次的用户即视为活跃用户，包括新用户与老用户
- 过去30天活跃用户 过去30天启动过应用的用户（去重），启动过一次的用户即视为活跃用户，包括新用户与老用户

### 时段分析 periodAna

提供了0-24时各时段内新增用户与启动次数的数据，帮您分析用户使用应用的时段规律。

- 时段新增用户
- 分时启动次数
- 时段累计日活 截止到各个整点时刻的当日活跃用户
- 分时活跃用户 每个小时的活跃用户(去重)

### 整体趋势 appTrend

展示了应用在一段时期内的变化趋势，方便您跟踪和评估应用的运营状况。

- 新增用户：第一次启动应用的用户（以设备为判断标准）
- 活跃用户：启动过应用的用户（去重），启动过一次的用户即视为活跃用户，包括新用户与老用户
- 活跃用户构成：每日活跃用户中新用户与老用户的分布
- 启动次数： 启动是通过在所有Activity中调用MobclickAgent.onResume()和MobclickAgent.onPause()方法来监测的。若用户使用过程中进入home或其他程序，经过一段时间间隔后才返回之前的应用，如间隔超过x（x可以由开发者自由设定，默认30）秒，则被认为是两次启动。
- 平均单次使用时长：单次使用时长的均值，即应用的总使用时长/总启动次数
- 平均上传流量：平均每次使用应用发送到网络的数据流量（单位：KB），只支持Android平台
- 平均下载流量：平均每次使用应用接收网络传回的数据流量（单位：KB），只支持Android平台


## 应用趋势

### 留存分析

包括日留存分析，周留存分析。

**日留存分析**
分析维度：日期，渠道版本
分析指标：新增用户数，1~7天后留存率，14天后留存率，30天后留存率等指标。

**周留存分析**
分析维度：周数，渠道版本
分析指标：新增用户数，1~7周后留存率等指标。


## 功能使用

### 页面访问

**页面访问路径 visitPath**

页面访问路径描述的是用户从每个页面去向其他各个页面的跳转情况，您可以从图中直观地了解到从初始页面到每一页面的到达率。注：友盟页面访问路径的数据是抽样统计的。如果您在Android应用中使用了Fragment页面统计功能，这里的页面包括您指定统计的Activity和Fragment。
其中，默认的起始节点是用户访问次数最多的页面；绿色的路径是到达率最高的路径并默认展开。
点击每个节点右上角的标志，您还可以生成以任意页面为初始节点的树。

**页面访问详情 visitDetail**

页面访问详情展示了用户使用每个页面的访问次数、访问时长以及跳转情况。这些数据可以帮助您分析每个页面的使用情况。
Activity：指页面，即Android系统里的一个Activity
访问次数：用户进入当前Activity的总次数
访问次数占比：当前页面访问次数占全部页面访问次数的比例
平均访问时长：用户每次进入当前Activity的平均停留时间
访问时长占比：用户在当前Activity停留时间总和占用户在全体Activity停留的时间总和的比例
跳出率：用户从当前Activity离开应用程序的概率
跳转情况：用户从当前Activity进入其他Activity的概率分布情况



# 非功能性需求

## 日志
**处理过程日志文件**
后台处理过程应将处理过程的启动，运行期间以及运行结果在日志文件中予以记录。
并支持DEBUG启动方式，将更明细的过程过程内部处理情况输出到日志文件。

**界面操作日志文件**
用户在操作界面上的活动，应该予以记录。用户活动包括但不限于：用户登录，用户注销，菜单项的选择，查询活动的发起等。

## 数据质量

## 性能

## 安全
- 未登录用户不能访问任何功能页面，访问时，跳到登录提示页面。
- 用户不能访问未对其授权的功能页面。

