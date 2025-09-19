package main

import (
	"fmt"
	"net"
	"os"
	"sync"
)

type proxyS struct {
	localAddr  net.Conn
	remoteAddr net.Conn
}

func main() {
	if len(os.Args) != 3 {
		fmt.Println("  args error ")
		return
	}
	localAddrStr := os.Args[1]
	remoteAddrStr := os.Args[2]

	server, err := net.Listen("tcp", localAddrStr)
	if err != nil {
		fmt.Printf(" listen err %v\n", err)
		return
	}
	for {
		socket, err2 := server.Accept()

		if err2 == nil {
			go startproxy(socket, remoteAddrStr)
		}
	}

}

func startproxy(localSocket net.Conn, remoteAddrStr string) {
	fmt.Printf("start proxylocal %s-->%s\n", localSocket.RemoteAddr(), localSocket.LocalAddr())
	defer localSocket.Close()
	defer fmt.Printf("close localSocket %s-->%s\n", localSocket.RemoteAddr(), localSocket.LocalAddr())
	remoteSocket, err := net.Dial("tcp", remoteAddrStr)
	if err != nil {
		fmt.Printf(" create client socket %s err", remoteAddrStr)
		return
	}
	defer remoteSocket.Close()
	defer fmt.Printf("close remoteSocket %s-->%s\n", remoteSocket.LocalAddr(), remoteSocket.RemoteAddr())
	ch0 := make(chan []byte, 128)
	ch1 := make(chan []byte, 128)
	fmt.Printf("start remote socket %s-->%s\n", remoteSocket.LocalAddr(), remoteSocket.RemoteAddr())
	defer close(ch0)
	defer close(ch1)
	var wt sync.WaitGroup
	var once sync.Once
	wt.Add(1)
	go processData(localSocket, ch0, ch1, &once, &wt)
	go processData(remoteSocket, ch1, ch0, &once, &wt)
	wt.Wait()
}

func processData(socket net.Conn, ch0 chan []byte, ch1 chan []byte, once *sync.Once, wt *sync.WaitGroup) {
	defer once.Do(func() {
		wt.Done()
	})
	go func() {
		b := false
		for {
			data, ok := <-ch1
			if !ok {
				break
			}
			l := len(data)
			s := 0
			for s < l {

				n, err := socket.Write(data[s:])
				//fmt.Printf("write data l =%d,n=%d\n", l, n)
				s += n
				if err != nil {
					b = true
					break
				}
				if b {
					break
				}
			}
		}
	}()

	for {
		data := make([]byte, 4096)
		n, err := socket.Read(data)
		//fmt.Println(string(data[:n]))
		if err != nil {
			break
		}
		ch0 <- data[:n]
	}
}
