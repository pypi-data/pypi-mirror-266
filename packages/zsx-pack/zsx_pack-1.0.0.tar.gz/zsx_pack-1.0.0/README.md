# Example Package

#在此文件内，可使用markdown撰写对包的详细介绍和说明，便于别人熟悉和使用，在此不再赘述
This is a simple example package. You can use
[Github-flavored Markdown](https://github.com/ziyueguyi/zsx_pack)
本函数主要作用是开发一个日志系统，本日志系统不使用logger包，可以有效屏蔽第三方日志信息，
函数：Logger
参数：

`title:日志标题（字符串）date_rotate:是否将日期添加到日志路径里面（false：不加，true：加）
log_dir:日志路径（如果填写日志路径，表示需要永久化保存日志，不填写的话不会将日志保存到本地）
print_level:输出日志的等级，默认为notset
file_level:储存日志默认的最低等级
is_color:是否启用才是输出
file_encoding:文件编码
datetime_format:日期格式
format:日志格式，默认为"[datetime] [[class_name]-[func_name]]|<[log_level]>|([lineno]):[message|extra]"`