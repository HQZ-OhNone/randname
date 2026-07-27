```ascii art
                      _                            
  _ __ __ _ _ __   __| |_ __   __ _ _ __ ___   ___  
 | '__/ _` | '_ \ / _` | '_ \ / _` | '_ ` _ \ / _ \ 
 | | | (_| | | | | (_| | | | | (_| | | | | | |  __/ 
 |_|  \__,_|_| |_|\__,_|_| |_|\__,_|_| |_| |_|\___| 
---HQZ-OhNone <ohnone_hqz@outlook.com>
```
## 全新的課堂小工具

### 特點
- **簡潔易用**，無需任何經驗、開箱即用、上手就會，學習成本極低。
- **功能豐富**，支持單抽、減量抽等多種不同模式。
- **開源免費**，本程序在 [GPL v3.0](./doc/LICENCE.md) 下發佈，任何人可以使用。

### 技術實現
- python3.12.10
- qt6.11.1

### 許可證
[GNU General Public License v3.0](./doc/LICENCE.md)

-----

### 使用

#### 方案一、使用預編譯程序
1. 請從 [releases](https://github.com/HQZ-OhNone/randname/releases) 下載預編譯程序
2. 將壓縮包解壓到合適的目錄
3. 運行 ```randname``` 程序

#### 方案二、從 Python 源碼運行
1. 在本機配置 Python 環境，可贊考 [Python官方網站](https://www.python.org/)
2. 將倉庫克隆到本地，如：
```git
git clone https://github.com/HQZ-OhNone/randname.git
```
3. 安裝 ```pyside6``` 庫，推薦使用 ```pip```，如：
```pip
pip install pyside6
```
4. 運行 main.py

#### 方案三、自行編譯二進制文件
1. 在本機配置 Python 環境，可贊考 [Python官方網站](https://www.python.org/)
2. 將倉庫克隆到本地，如：
```git
git clone https://github.com/HQZ-OhNone/randname.git
```
3. 安裝 ```pyside6``` 庫，推薦使用 ```pip```，如：
```pip
pip install pyside6
```
4. 安裝 ```nuitka``` 庫，推薦使用 ```pip```，如：
```pip
pip install nuitka
```
5. 使用 Nuitka 經行編譯，如：
- Linux
```nuitka
nuitka \
--standalone \
--enable-plugin=pyside6 \
--include-data-dir=config=config \
--include-data-dir=ui=ui \
--include-data-dir=doc=doc \
--output-dir=build \
--output-filename=randname \
--show-progress \
--lto=yes \
--assume-yes-for-downloads \
main.py
```
- Windows
```nuitka
nuitka `
--standalone `
--enable-plugin=pyside6 `
--include-data-dir=config=config `
--include-data-dir=ui=ui `
--include-data-dir=doc=doc `
--output-dir=build `
--output-filename=randname.exe `
--show-progress `
--lto=yes `
--assume-yes-for-downloads `
--windows-disable-console `
main.py
```
6. 找到 ```build``` 目錄下的可執行文件，運行即可。
7. 編譯完成後亦可打包分發
- Linux
```Zsh
cd build
mv main.dist randname-3.1
tar -cavf randname-3.1_linux.tar.zst randname-3.1
```

-----

### 未來開發
可查看 [TODO](./doc/TODO.md)。

### 反饋
歡迎提 issue 或發郵件

-----
HQZ-OhNone \<ohnone_hqz@outlook.com>  
lastedit: 2026-07-27
