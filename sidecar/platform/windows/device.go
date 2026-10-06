package windows

import (
	"context"
)

func GetDeviceStatus(ctx context.Context) (map[string]string, error) {
	return map[string]string{
		"os":      "windows",
		"version": "10.0",
	}, nil
}
