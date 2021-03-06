<?xml version="1.0" encoding="utf-8"?>
<!--
@since Dec,2008
@Author $Author: wgzhao $
$Date: 2009-11-29 23:02:52 +0800 (日, 2009-11-29) $
$Id: xunjian.xsl 7 2009-11-29 15:02:52Z wgzhao $
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:template match="/">
<html>
<head>
<style>
body{
font-size:9pt;
font-family:San Serif；
}
table
{
border:0;
border-collapse:collapse;
border-top:solid windowtext 1.5pt;
border-left:solid windowtext 1.5pt;
border-bottom:solid windowtext 1.5pt;
border-right:solid windowtext 1.5pt;
margin-left:10pt;
}
td{
padding:2px;
border:1px solid black;
}
th{
background-color:gray;
color:white;
height:20px;
margin-top:1px;
padding-top:2px;
}
</style>
<title>邮政全国巡检结果表</title>
<meta author="wgzhao" />
</head>
<body>
<table>
<tr>
<th colspan="4">服务器巡检明细表</th>
</tr>

<xsl:for-each  select="//server">
<tr>
<td rowspan="11">服务器<xsl:value-of select="position()"></xsl:value-of></td>
<td>主机名</td><td width="280px"><xsl:value-of select="hostname"></xsl:value-of></td>
<td width="280px">主机IP <xsl:value-of select="ip"></xsl:value-of></td>
</tr>
<tr>
<td>操作系统环境</td>
<td>□系统版本 <xsl:value-of select="version"></xsl:value-of></td>
<td>□产品有效性(是否注册序列号)<xsl:value-of select="license"></xsl:value-of></td>
</tr>
<tr>
<td rowspan="5" align="center">操作系统状态<br/>检查</td>
<td>□CPU负载  <xsl:value-of select="cpuload"></xsl:value-of></td>
<td>□内存使用率 <xsl:value-of select="memload"></xsl:value-of></td>
</tr>
<tr>
<td>□磁盘使用率   <xsl:value-of select="diskuse"></xsl:value-of></td>
<td>□磁盘读写负载 <xsl:value-of select="diskio"></xsl:value-of></td>
</tr>
<tr>
<td>□日志轮询 <xsl:value-of select="logrotate"></xsl:value-of></td>
<td>□进程个数  <xsl:value-of select="procnum"></xsl:value-of></td>
</tr>
<tr>
<td>□打开文件数  <xsl:value-of select="filenum"></xsl:value-of></td>
<td>□用户登录数  <xsl:value-of select="loginnum"></xsl:value-of></td>
</tr>
<tr>
<td colspan="2">□系统时间 <xsl:value-of select="sysdate"></xsl:value-of></td>
</tr>
<tr>
<td rowspan="3" align="center">HA Cluster<br/><br/> 状态检查</td>
</tr>
<tr>
<td>□HA功能测试</td>
<td>□灾难恢复测试</td>
</tr>
<tr>
<td>□应用服务启停测试</td>
<td>□应用服务切换测试</td>
</tr>
<tr>
<td colspan="2">注：此检查为可选项，请确认用户有HA软件且方便停机做此项测试 </td>
</tr>
</xsl:for-each>
</table>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
