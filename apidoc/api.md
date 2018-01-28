## 搜索图书
|URL|Header|Method|
| --- | -- | -- |
|/api/lib/search/| None| GET| 

**URL Params:**
```
keyword: string 
page: int  //可选，默认为1
```

**POST Data: None**

**RETURN Data:**
```
{
	"meta":{
	    "max" : int // 最大页数 
	    "per_page" :int //每页书数
	},
	"result" : [{
				
            "book":  string // 书名
            "author":  string // 作者
            "publisher": string //出版社
            "bid": string // 作用未知，待补充
            "bookurl": string 
            "id": string
	}]
}
```

**Status Code :**
```
200 // 成功 
```

*** 

## 某本图书
|URL|Header|Method|
| --- | -- | -- |
|/api/lib/detail/<int:id>/ （id是图书返回信息中的id）| None| GET| 
 
**URL Params: None**

**POST Data: None**

**RETURN Data:**
```
{
    "bid": string , // 作用未知，待补充
    "book": string , // 书名
    "author": string, // 作者
    "intro": string, // 介绍，来源为豆瓣API。可能为空字符串
    "books": [ // books数组表示所有馆藏书的信息列表，如果这本书还在上架过程，这个数组可能为空数组([])
        {
            "status": string // 状态, 一个enum，可能有值有 [可借|借出|无法借阅|保留本|正在上架|不可借阅] 如果这本书在订购中或者处理中可能还有更多的值，客户端可以default处理为不可借状态
            "room": string // 图书位置，如"5F__中文图书借阅室(五)"
            "tid":  string // 作用未知，待补充
            "bid": string, // 作用未知，待补充
            "date": string, // 若status为借出，date为归还日期，即"YYYY-MM-DD"，否则为空字符串""
        }
    ]
}
```

**Status Code :**
```
200 // 成功 
```

***
## 续借图书 
|URL|Header|Method|
| --- | -- | -- |
|/api/lib/renew/| s:stirng(Phpsessid), captcha :string | POST |

**URL Params: None**

**POST Data:** 
```
{
	"bar_code" : string, 
	"check" : string 
}
```
**RETURN Data：**
```
{
    "msg": string 
}
```

**Status Code :**
```
200 // 成功 
406 // 时间太早不能续借
403 // 超过最大续借次数不能续借
400 // 其他原因不能续借
```
***

## 我的图书
|URL|Header|Method|
| --- | -- | -- |
|/api/lib/me/| s:stirng | GET | 
->**s为Phpsessid**

**URL Params: None**

**POST Data : None** 

**RETURN Data**:
```
[
    {
        "book": string
        "author": string
        "itime": string // 借的时间
        "otime": string // 归还时间
        "time": int 
        "room": string 
        "bar_code": string 
        "check": string 
        "id": string 
    }
]
```

**Status Code :**
```
200 // 成功 
401 // Cookie失效
```

***

## 添加关注图书
|URL|Header|Method|
| --- | -- | -- |
|/api/lib/create/| sid :stirng(学号) | POST | 

**URL Params: None**

**POST Data :** 

```
{
       "book": string,
       "author": string,
       "bid": string,     // 对应返回的bid
       "book_id": string // 对应返回的id
}
``` 

**RETURN Data** 

```
{
       "book": string,
       "author": string,
       "bid": string,    // 对应返回的bid
       "book_id": string   // 对应返回的id 
}
```

**Status Code :**
```
200 // 成功 
401 // 已关注，不能再次关注 
```
***

## 获取所有关注 
|URL|Header|Method|
| --- | -- | -- |
|/api/lib/attention/| sid :string(学号) | GET | 

**URL Params: None**

**POST Data : None** 

**RETURN Data** 
```
{
	[
		"bid" : string, 
		"book" : string, 
		"id" : string, 
		"author" : string, 
		"avb" : string // “y" 或 "n" 
	]
}
```

**Status Code :**
```
200 // 成功 
404 // 没有关注图书 
```
***

## 取消关注图书 
|URL|Header|Method|
| --- | -- | -- |
|/api/lib/delete/| sid :stirng（学号） |  DELETE | 

**URL Params: None**

**POST Data :** 
```
{
	"id" : string   //id即添加时的book_id
}
``` 

**RETURN Data:** 
```
{
	"msg" : string
}
```

**Status Code :**
```
200 // 成功 
404 // 没有关注图书,不能取消关注 
```


