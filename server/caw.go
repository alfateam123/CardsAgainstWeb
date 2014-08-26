package main

import (
    "net"
    "fmt"
    "encoding/json"
    "bufio"
    "sync"
)

type Player struct {
    Connection net.Conn
    Nick string
    CardPlayed string
}

type Points struct {
    Playerkey string
    Points int
}

type Message struct {
    Playerkey string `json:"playerkey"`
    Action string `json:"action"`
    Value string `json:"value"`
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

func HandleNewConnection(conn net.Conn, expectedPlayers int, players *[]Player) {
    sock := bufio.NewReader(conn)
    var m Message

    dec := json.NewDecoder(sock)
    err := dec.Decode(&m)
    if err != nil {
        fmt.Println(err)
        return
    }

    if m.Playerkey != "" && m.Action == "connect" && len(*players) < expectedPlayers {
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
            p.Connection = conn
            *players = append(*players, p)

            m.Value = "accepted"
            response, err := json.Marshal(m)
            HandleError(err)

            writer.Write(response)
            writer.Flush()
            fmt.Println("New player " + m.Playerkey + " connected! Total players connected: " + string(len(*players)) + " out of " + string(expectedPlayers) + " expected players.")

            if len(*players) == expectedPlayers {
                go StartGame(players, expectedPlayers)
            }
        } else {
            m.Value = "playerkey_already_present"
            response, err := json.Marshal(m)
            HandleError(err)

            writer.Write(response)
            writer.Flush()
            fmt.Println("Someone tried to connect with the playerkey " + m.Playerkey + " but a player with that key was already connected.")
        }
    } else {
        m.Value = "game_already_started"
        response, err := json.Marshal(m)
        HandleError(err)
        sock := bufio.NewWriter(conn)
        sock.Write(response)
        sock.Flush()
        fmt.Println("Player " + m.Playerkey + " tried to connect to a running game D:")
    }
}

func StartGame(players *[]Player, expectedPlayers int) {
    var wg sync.WaitGroup
    wg.Add(expectedPlayers)
    var m Message

    for _, pl := range *players {
        m.Playerkey = pl.Nick
        m.Action = "ready"
        m.Value = "false"
        response, err := json.Marshal(m)
        HandleError(err)
        sock := bufio.NewWriter(pl.Connection)
        sock.Write(response)
        sock.Flush()

        go WaitForReady(pl, &wg)
    }
    wg.Wait()
    fmt.Println("All players ready! Distributing cards.") //TODO: Distribute cards
}

func WaitForReady(pl Player, wg *sync.WaitGroup) {
    defer wg.Done()

    sock := bufio.NewReader(pl.Connection)
    var m Message

    for {
        dec := json.NewDecoder(sock)
        err := dec.Decode(&m)
        HandleError(err)

        if pl.Nick == m.Playerkey && m.Action == "ready" && m.Value == "true" {
            m.Value = "accepted"
            response, err := json.Marshal(m)
            HandleError(err)
            writer := bufio.NewWriter(pl.Connection)
            writer.Write(response)
            writer.Flush()
            fmt.Println("Player " + pl.Nick + " is ready!")
            return
        }
    }

}

func main() {
    var players []Player
    expectedPlayers := 2
    listener, err := net.Listen("tcp", ":12345")
    HandleError(err)

    for {
        conn, err := listener.Accept()
        HandleError(err)
        go HandleNewConnection(conn, expectedPlayers, &players)
    }
}