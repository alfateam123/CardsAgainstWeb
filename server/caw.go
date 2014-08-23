package main

import (
    "net"
    "fmt"
    "encoding/json"
    "bufio"
)

type Message struct {
    Playerkey string `json:"playerkey"`
    Action string `json:"action"`
    Value string `json:"value"`
    Missing []string `json:"missing"`
    Cards []string `json:"cards"`
    Card_Text []string `json:"card_text"`
    PointList []Points `json:"points"`
    Status string `json:"status"`
    IsReady bool `json:"is_ready"`
    Played bool `json:"played"`
}

func Handle(conn net.Conn) {
    sock := bufio.NewReader(conn)
    var err error
    var m Message

    for {
        dec := json.NewDecoder(sock)
        if err != nil {
            fmt.Println(err)
            continue
        }
        err := dec.Decode(&m)
        if err != nil {
            fmt.Println(err)
            continue
        }
        fmt.Println(m)
    }
}

func main() {
    listener, err := net.Listen("tcp", ":12345")
    if err != nil {
        panic(err)
    }

    for {
        conn, err := listener.Accept()
        if err != nil {
            panic(err)
        }
        go Handle(conn)
    }
}
