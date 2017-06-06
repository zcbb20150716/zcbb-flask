# Flask
解决nginx上传文件大小限制
1.打开nginx配置文件 nginx.conf, 路径一般是：/etc/nginx/nginx.conf。
2.在http{}段中加入 client_max_body_size 20m; 20m为允许最大上传的大小。
3.保存后重启nginx，问题解决。
解决mysql上传文件过大,kill掉链接问题
mysql> set global max_allowed_packet=1024*1024*20;
mysql> show global variables like 'max_allowed_packet';