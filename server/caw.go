package main

import (
    "net"
    "fmt"
    "encoding/json"
    "bufio"
)

type Message struct {
    playerkey string `json:"playerkey"`
    action string `json:"action"`
    value string `json:"value"`
}

func handleconnection(conn net.Conn) {
    sock := bufio.NewReader(conn)
    var err error

    for {
        m := new(Message)
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
        panic("nope")
    }

    for {
        conn, err := listener.Accept()
        if err != nil {
            panic("noper")
        }
        go handleconnection(conn)
    }
}
