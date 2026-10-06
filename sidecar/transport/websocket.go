package transport

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/gorilla/websocket"
	"github.com/knight384/MARK-XLVIII-V2-Sidecar/protocol"
)

type WsClient struct {
	conn       *websocket.Conn
	url        string
	token      string
	cancel     context.CancelFunc
	reqChan    chan protocol.RPCRequest
	respChan   chan protocol.RPCResponse
	done       chan struct{}
}

func NewWsClient(url, token string) *WsClient {
	return &WsClient{
		url:      url,
		token:    token,
		reqChan:  make(chan protocol.RPCRequest, 100),
		respChan: make(chan protocol.RPCResponse, 100),
		done:     make(chan struct{}),
	}
}

func (c *WsClient) Connect(ctx context.Context) error {
	headers := make(map[string][]string)
	headers["Authorization"] = []string{"Bearer " + c.token}
	
	conn, resp, err := websocket.DefaultDialer.DialContext(ctx, c.url, headers)
	if err != nil {
		if resp != nil {
			return fmt.Errorf("dial error: %v (status: %d)", err, resp.StatusCode)
		}
		return fmt.Errorf("dial error: %v", err)
	}
	
	c.conn = conn
	
	var ctxCancel context.Context
	ctxCancel, c.cancel = context.WithCancel(ctx)
	
	go c.readPump(ctxCancel)
	go c.writePump(ctxCancel)
	
	return nil
}

func (c *WsClient) Close() {
	if c.cancel != nil {
		c.cancel()
	}
	if c.conn != nil {
		c.conn.Close()
	}
	close(c.done)
}

func (c *WsClient) readPump(ctx context.Context) {
	defer c.Close()
	for {
		select {
		case <-ctx.Done():
			return
		default:
			_, message, err := c.conn.ReadMessage()
			if err != nil {
				log.Printf("read error: %v", err)
				return
			}
			
			var req protocol.RPCRequest
			if err := json.Unmarshal(message, &req); err != nil {
				log.Printf("invalid message format: %v", err)
				continue
			}
			
			c.reqChan <- req
		}
	}
}

func (c *WsClient) writePump(ctx context.Context) {
	ticker := time.NewTicker(30 * time.Second)
	defer func() {
		ticker.Stop()
		c.Close()
	}()
	
	for {
		select {
		case <-ctx.Done():
			return
		case resp := <-c.respChan:
			if err := c.conn.WriteJSON(resp); err != nil {
				log.Printf("write error: %v", err)
				return
			}
		case <-ticker.C:
			if err := c.conn.WriteControl(websocket.PingMessage, []byte{}, time.Now().Add(10*time.Second)); err != nil {
				log.Printf("ping error: %v", err)
				return
			}
		}
	}
}

func (c *WsClient) SendResponse(resp protocol.RPCResponse) {
	c.respChan <- resp
}

func (c *WsClient) ReceiveRequest() <-chan protocol.RPCRequest {
	return c.reqChan
}
