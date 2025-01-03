# New 2025.1  Android加固，渠道打包新版
## 1 环境准备
* Python3.10++ 
* 安装python第三方lib库 pip install -r requirements.txt
* 使用加壳功能 需要安装gradle 8.12版本++ java17

## 加固
```
使用aab 加固能使aab内具有apk加固相同的功能
cd ./scripts
AAB:
python main.py protected protectedaab -p {aab_path} -s CC(游戏名称 config目录中配置游戏签名，渠道，需要加固的so等)

APK:
python main.py protected protectedapk -p {apk_path} -s CC(游戏名称 config目录中配置游戏签名，渠道，需要加固的so等)
```



# OLD 2021  Android打包工具
## 1 环境准备
* Python2.7 or Python3.4 pip
* 安装python第三方lib库 pip install -r requirements.txt
* 使用加壳功能 需要安装gradle 4.5以上版本

## 2 脚本执行入口
1.渠道打包
gameid 游戏id 在avalon 那边配置
channelid 渠道id 在渠道这边配置
```bash
cd ./scripts
./main pack pack_game -g gameid -c channelid
```

2.unity mono加密
apk_path 需要加密的android apk路径
unity_ver 5.1 / 5.6 目前只支持 unity5.1 和 5.6的mono 请检查版本对应
```bash
cd ./scripts
./main protected mono_protected -p apk_path -v unity_ver
```

3.apk 加固
-p 加壳原始apk路径
-m 加壳方式 目前2种 360 & klab
-s 签名文件yml 路径为 games/{sign_name}/keystore.yml 默认为Penguin
```bash
cd ./scripts
python main.py protected protectedapk -p {apk_path} -m 360 
#使用360方式加密
```

## 3 APK输出路径
* {{项目根路径}}/output


## 4 AAB 加固
```
使用aab 加固能使aab内具有apk加固相同的功能
cd ./scripts
python main.py protected protectedaab -p {aab_path}
```
