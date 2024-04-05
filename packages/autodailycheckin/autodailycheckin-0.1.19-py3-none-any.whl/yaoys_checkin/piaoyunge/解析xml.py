# -*- coding: utf-8 -*-
# @FileName  :解析xml.py
# @Time      :2023/7/10 20:48
# @Author    :yaoys
# @Desc      :
from lxml import etree
import xml.etree.ElementTree as ElementTree
import re

text = '''
<?xml version="1.0" encoding="gbk"?>
<root><![CDATA[<h3 class="flb">
<em>每日签到</em>
<span><a href="javascript:;" class="flbc" onclick="hideWindow('dsu_paulsign');" title="关闭">关闭</a></span>
</h3>
<form id="qiandao" method="post" action="plugin.php?id=dsu_paulsign:sign&amp;operation=qiandao&amp;infloat=1&amp;sign_as=1" onkeydown="if(event.keyCode==13){showWindow('qwindow', 'qiandao', 'post', '0');return false}">
<div class="f_c" style="width:690px;margin:10px;">
<style>
.qdsmilea{padding:3px;margin:auto;float:left;list-style:none;float:left}
.qdsmilea li{float: left;padding:5px .4em;border:2px #fff solid;}
.qdsmilea li img{margin-bottom:5px;}
.qdsmilea li:hover{cursor:pointer;}
</style>
<h3>今天签到了吗？请选择您此刻的<font color=red>心情图片</font>并写下<font color=blue>今天最想说的话</font>！</h3>
<input type="hidden" name="formhash" value="d96188ea">
<script>
function Icon_selected(sId) {
var oImg = document.getElementsByTagName('li');
for (var i = 0; i < oImg.length; i++) {
  if (oImg[i].id == sId) {
var selectname = document.getElementById(oImg[i].id + "_s");
selectname.checked = true;
oImg[i].style. background = '#EFEFEF';
  } else {
oImg[i].style. background = '';
  }
}
}
</script>
<table width="100%" cellpadding="0" cellspacing="0" align="center">
<tr>
<td>
<ul class="qdsmilea"><input id="kx_s" type="radio" name="qdxq" value="kx" style="display:none"><li id="kx" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/kx.gif"><br>开心<br></center></li>
<input id="ng_s" type="radio" name="qdxq" value="ng" style="display:none"><li id="ng" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/ng.gif"><br>难过<br></center></li>
<input id="ym_s" type="radio" name="qdxq" value="ym" style="display:none"><li id="ym" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/ym.gif"><br>郁闷<br></center></li>
<input id="wl_s" type="radio" name="qdxq" value="wl" style="display:none"><li id="wl" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/wl.gif"><br>无聊<br></center></li>
<input id="nu_s" type="radio" name="qdxq" value="nu" style="display:none"><li id="nu" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/nu.gif"><br>怒<br></center></li>
<input id="ch_s" type="radio" name="qdxq" value="ch" style="display:none"><li id="ch" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/ch.gif"><br>擦汗<br></center></li>
<input id="fd_s" type="radio" name="qdxq" value="fd" style="display:none"><li id="fd" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/fd.gif"><br>奋斗<br></center></li>
<input id="yl_s" type="radio" name="qdxq" value="yl" style="display:none"><li id="yl" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/yl.gif"><br>慵懒<br></center></li>
<input id="shuai_s" type="radio" name="qdxq" value="shuai" style="display:none"><li id="shuai" onclick="Icon_selected(this.id)"><center><img src="source/plugin/dsu_paulsign/img/emot/shuai.gif"><br>衰<br></center></li>
</ul>
</td>
</tr>
<table summary="Qd" cellspacing="0" cellpadding="0" class="tfm">
<tr>
<th>今日最想说模式</th>
<td>
<label><input type="radio" name="qdmode" value="1" checked="checked" onclick="if(checked == true){document.getElementById('mode1').style.display='';document.getElementById('mode2').style.display='none';}">&nbsp;自己填写</label>&nbsp;&nbsp;
<label><input type="radio" name="qdmode" value="2" onclick="if(checked == true){document.getElementById('mode1').style.display='none';document.getElementById('mode2').style.display='';}">&nbsp;快速选择</label>&nbsp;&nbsp;</td>
</tr>
<tr id="mode1" style="display:;">
<th><label for="todaysay">我今天最想说</label></th>
<td><input type="text" name="todaysay" id="todaysay" size="25" class="px" /></td>
<td></td>
</tr>
<tr id="mode2" style="display:none;">
<th>快速语句选择</th>
<td>
<select name="fastreply"><option value="0" style="color:#8058">PYG18周年生日快乐！</option>
<option value="1" style="color:#e8ad8">我爱飘云阁！</option>
<option value="2" style="color:#8c21ac">飘云加油！</option>
<option value="3" style="color:#34b0b">签到拿积分！O(∩_∩)O哈哈~</option>
<option value="4" style="color:#3da4a5">hoho，今天心情超好，签到来了！</option>
<option value="5" style="color:#2c5323">哎...今天够累的，到论坛转转！</option>
<option value="6" style="color:#7796d6">嘿嘿，来论坛找妹纸聊天</option>
<option value="7" style="color:#a08d2f">哈哈，来论坛找好资源</option>
<option value="8" style="color:#c0267b">我就每天上论坛看看，混个脸熟</option>
</select>
</td>
</tr>
</table>
</table>
</div>
<p class="o pns">
<button type="button" class="pn pnc" onclick="showWindow('qwindow', 'qiandao', 'post', '0');return false"><strong>点我签到!</strong></button>
</p>
</form>]]></root>
'''


def parse_with_lxml():
    root = etree.fromstring(text)
    for log in root.xpath("//root"):
        print(log.text)


def parse_with_stdlib():
    root = ElementTree.fromstring(text)
    for log in root.iter('root'):
        print(log.text)


sign = '''
<?xml version="1.0" encoding="gbk"?>
<root><![CDATA[<script type="text/javascript" reload="1">
setTimeout("hideWindow('qwindow')", 3000);
</script>
<div class="f_c">
<h3 class="flb">
<em id="return_win">签到提示</em>
<span>
<a href="javascript:;" class="flbc" onclick="hideWindow('qwindow')" title="关闭">关闭</a></span>
</h3>
<div class="c">
您今日已经签到，请明天再来！ </div>
</div>
]]></root>

'''

if __name__ == '__main__':
    # re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA

    # re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script

    re_style = re.compile('<input type="hidden" name="formhash" value="(.*?)">', re.I)  # style
    # s = re_cdata.sub('', text)  # 去掉CDATA
    # s = re_script.sub('', s)  # 去掉SCRIPT
    s = re.findall(r'<div class="c">(.*?)</div>', sign.replace('\n', ''))  # 去掉style
    # s_s = re.compile(r'<div class="c">(.*?)</div>/gims')
    print(s[0])

    # var = re.findall('<input type="hidden" name="formhash" value="d96188ea">(.*)<input>', text)[0]
