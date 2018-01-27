## 搜索图书
|URL|Header|Method|
| --- | -- | -- |
|/api/lib/search/| None| GET| 

**URL Params:**
```
keyword: string 
page: int  //没有默认为1
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
            "bid": string 
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
    "bid": string ,
    "book": string ,
    "author": string,
    "intro": string,
    "books": [
        {
            "status": string // 状态
            "room": string // 在哪,
            "tid":  string 
            "bid":"fff",
            "date": 若未可借为 "YYYY-MM-DD" 否则为 string 
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


