## 概览

飞书的 Python SDK

## 如何安装

```sh
pip3 install cc-feishu
```

## 如何使用

### 引入模块
```python
from cc_feishu.client import Client
feishu = Client(app_id='填写你的机器人的 app_id', app_secret='填写你的机器人的 app_secret')
```

## Test

直接在根目录执行 `pytest` 即可，会读取 pytest.ini 的配置，并进行测试