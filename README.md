在物联网测试场景中，需要模拟设备进行测试,但是模拟并不能全部真实。
因此将线上真实设备发送的的mqtt数据导入到本地是有必要的

配置一份 info.yaml，即可使用

```yaml
source_host: "mqtt.***.com"
source_port: 1883
source_topic: "ces/ces/post/+"
source_user: "ces"
source_password: "ces"

target_host: "192.168.1.*"
target_topic: "ces/ces/post/lingpao_0033"
target_port: 1883
target_user: "ces"
target_password: "ces"
```
