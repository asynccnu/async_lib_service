## 续借图书API与restccnu相比有改动

> 图书详情

| URL |  Header | Method |
| ------------- |:-------------:| -----:|
| /api/lib/renew/ | 图书馆Header | POST |


## URL Params
    无

## POST Data(json)
```
{
    'bar_code':图书编号,
    'check' : 图书check编码,
    'captcha' : 验证码
}
```

## Return Data(json)
    {}

## Status Code
    200 成功
    406 不到续借时间
    403 超过最大续借次数
    400 请求无效

## Notes
