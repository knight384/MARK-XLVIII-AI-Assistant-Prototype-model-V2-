package device

import (
	"crypto/rand"
	"encoding/hex"
	"os"
	"path/filepath"
)

type Identity struct {
	DeviceID string json:"device_id"
}

func LoadOrGenerateIdentity(configDir string) (*Identity, error) {
	identityPath := filepath.Join(configDir, "identity.json")
	
	if _, err := os.Stat(identityPath); os.IsNotExist(err) {
		// Generate new identity
		bytes := make([]byte, 16)
		if _, err := rand.Read(bytes); err != nil {
			return nil, err
		}
		
		id := &Identity{
			DeviceID: hex.EncodeToString(bytes),
		}
		
		// In a real app we'd JSON encode and save with 0600 permissions
		return id, nil
	}
	
	// Stub load
	return &Identity{DeviceID: "existing-device-id"}, nil
}
