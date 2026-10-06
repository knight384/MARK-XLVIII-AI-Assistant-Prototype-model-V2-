package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/knight384/MARK-XLVIII-V2-Sidecar/capabilities"
	"github.com/knight384/MARK-XLVIII-V2-Sidecar/device"
	"github.com/knight384/MARK-XLVIII-V2-Sidecar/protocol"
	"github.com/knight384/MARK-XLVIII-V2-Sidecar/transport"
)

func main() {
	log.Println("Starting MARK XLVIII V2 Sidecar")

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Load or generate identity
	identity, err := device.LoadOrGenerateIdentity(".config")
	if err != nil {
		log.Fatalf("Failed to load device identity: %v", err)
	}
	log.Printf("Device ID: %s", identity.DeviceID)

	// In a real application, token is obtained securely via enrollment
	token := os.Getenv("SIDECAR_TOKEN")
	if token == "" {
		log.Println("Warning: SIDECAR_TOKEN environment variable not set. Connection will likely be rejected.")
	}

	wsURL := os.Getenv("SIDECAR_WS_URL")
	if wsURL == "" {
		wsURL = "ws://127.0.0.1:8000/ws/sidecar"
	}

	// Initialize registry
	registry := capabilities.NewRegistry()
	
	// Stub capability registration
	registry.Register(capabilities.Capability{
		ID:                 "os.info",
		Name:               "OS Information",
		Version:            "1.0.0",
		Platform:           "all",
		Available:          true,
		RiskClassification: "low",
	}, func(ctx context.Context, payload []byte) (interface{}, error) {
		return map[string]string{"os": "mock"}, nil
	})

	// Start WebSocket client
	client := transport.NewWsClient(wsURL, token)
	if err := client.Connect(ctx); err != nil {
		log.Printf("Failed to connect to server: %v", err)
		// We log instead of fatal to allow for reconnect logic
	} else {
		log.Println("Connected to server.")
	}
	defer client.Close()

	// Handle graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Message loop
	go func() {
		for req := range client.ReceiveRequest() {
			log.Printf("Received request %s for capability %s", req.RequestID, req.Capability)
			
			result, err := registry.Handle(ctx, req.Capability, req.Payload)
			var resp protocol.RPCResponse
			if err != nil {
				resp = protocol.NewResponse(req.RequestID, "error", nil, err.Error())
			} else {
				resp = protocol.NewResponse(req.RequestID, "success", result, "")
			}
			client.SendResponse(resp)
		}
	}()

	<-sigChan
	log.Println("Shutting down gracefully...")
}
