# leveldb_http
A restful LevelDB server written in Python3 with asyncio



## Usage

>GET /namespace1?ids=a,b
```
[
  null,
  null
]
```

>POST /namespace1 {a: 1, b: 2, c: 3}
```
200 OK
```

>GET /namespace1?ids=a,b
```
[
  "1",
  "2"
]
```

>GET /namespace1?start=b&limit=2
```
[
  [
    "b",
    "2"
  ],
  [
    "c",
    "3"
  ]
]
```

>GET /namespace1?start=a&stop=c
```
[
  [
    "a",
    "1"
  ],
  [
    "b",
    "2"
  ]
]
```

> GET /namespace1?start=c&stop=a
```
[
  [
    "c",
    "3"
  ],
  [
    "b",
    "2"
  ]
]
```

>GET /namespace2?ids=a,b
```
[
  null,
  null
]
```
