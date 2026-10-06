package linux

import (
	"context"
)

func GetDeviceStatus(ctx context.Context) (map[string]string, error) {
	return map[string]string{
		"os":      "linux",
		"version": "unknown",
	}, nil
}
