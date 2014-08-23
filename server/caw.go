package main

import (
    "net"
    "fmt"
    "encoding/json"
    "bufio"
)

type Player struct {
    Nick string
    Socket net.Conn
}

type Points struct {
    Player string
    Points int
}

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

func HandleNewConnection(conn net.Conn, players *[]Player) {
    sock := bufio.NewReader(conn)
    var m Message

    for {
        dec := json.NewDecoder(sock)
        err := dec.Decode(&m)
        if err != nil {
            fmt.Println(err)
            continue
        }
        if m.Playerkey != "" && m.Action == "connect" {
            var p Player
            p.Nick = m.Playerkey
            p.Socket = conn
            *players = append(*players, p)

            m.Value = "accepted"
            response, err := json.Marshal(m)
            if err != nil {
                fmt.Println(err)
            }
            writer := bufio.NewWriter(conn)
            writer.WriteString(string(response))
            writer.Flush()
            fmt.Println(players)
        } else {
            fmt.Println(m)
        }
    }
}

func main() {
    var players []Player
    listener, err := net.Listen("tcp", ":12345")
    if err != nil {
        panic(err)
    }

    for {
        conn, err := listener.Accept()
        if err != nil {
            panic(err)
        }
        go HandleNewConnection(conn, &players)
    }
}
