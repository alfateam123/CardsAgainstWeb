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

func HandleError(err error) {
    if err != nil {
        fmt.Println(err)
    }
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
            playerExists := false
            writer := bufio.NewWriter(conn)

            for _, pl := range *players {
                if pl.Nick == m.Playerkey {
                    playerExists = true
                }
            }

            if !playerExists {
                var p Player
                p.Nick = m.Playerkey
                p.Socket = conn
                *players = append(*players, p)

                m.Value = "accepted"
                response, err := json.Marshal(m)
                HandleError(err)

                writer.WriteString(string(response))
                writer.Flush()
                fmt.Println("New player " + m.Playerkey + " connected!")
            } else {
                m.Value = "playerkey_already_present"
                response, err := json.Marshal(m)
                HandleError(err)

                writer.WriteString(string(response))
                writer.Flush()
                fmt.Println("Someone tried to connect with the playerkey " + m.Playerkey + " but a player with that key was already connected.")
            }
        } else {
            fmt.Println(m)
        }
    }
}

func main() {
    var players []Player
    listener, err := net.Listen("tcp", ":12345")
    HandleError(err)

    for {
        conn, err := listener.Accept()
        HandleError(err)
        go HandleNewConnection(conn, &players)
    }
}