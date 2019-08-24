# 简介
    从国科大SEP课程网站上爬取课件、作业等信息。这是我18-19学年一直在用的工具，经历了秋季、春季、夏季三个学期，现在分享出来给学弟学妹们。代码也是基于学长的代码改的：["ucas_course_tool"](https://github.com/cld378632668/ucas_course_tool)。

# 使用
```
usage: download.py [-h] [--homework] [--download] [-i I] [--test][--semester SEMESTER]
   -h, --help  show this help message and exit
  --homework  作业查看功能
  --download  课件下载功能
  -i I        用户信息文件名
  --semester  选择特定学期，格式如: 19-20秋季
```

如果使用win10，可以点击使用两个bat脚本一键同步，注意自行修改脚本中的参数（建议用记事本修改）。

## 其他说明
    - main.py: 用PyQt5搭了一个简单的图形界面，没有花太多时间，可能有bug，请自行选用。
    - install.py: 将程序打包可直接运行的exe程序，水平有限，最后没有成功，运行不了。科研任务繁重，没时间弄了，留给学弟学妹们完善吧~


# 功能
    - 课件下载&同步
    
    - 作业查看

# 用户信息文件内容
    - 内容示例：`SEP_USERNAME_OR_EMAIL PASSWORD ABSOLUTE_DOWNLOAD_PATH (STUDENT_ID)`, 其中`STUDENT_ID`项为可选项,如果你在国科大有本硕博多个学号,这个选项会有用。 ABSOLUTE_DOWNLOAD_PATH为你要将课件下载到的位置，如果这个文件夹不存在，你需要手动创建。
