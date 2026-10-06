package darwin

import (
	"context"
)

func GetDeviceStatus(ctx context.Context) (map[string]string, error) {
	return map[string]string{
		"os":      "darwin",
		"version": "13.0",
	}, nil
}
