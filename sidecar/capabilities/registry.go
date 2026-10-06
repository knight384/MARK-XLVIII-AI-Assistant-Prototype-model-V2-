package capabilities

import (
	"context"
	"fmt"
	"sync"
)

type Capability struct {
	ID                  string json:"capability_id"
	Name                string json:"name"
	Version             string json:"version"
	Platform            string json:"platform"
	PermissionsRequired []string json:"permissions_required"
	Available           bool   json:"available"
	RiskClassification  string json:"risk_classification"
}

type Handler func(ctx context.Context, payload []byte) (interface{}, error)

type Registry struct {
	mu           sync.RWMutex
	capabilities map[string]Capability
	handlers     map[string]Handler
}

func NewRegistry() *Registry {
	return &Registry{
		capabilities: make(map[string]Capability),
		handlers:     make(map[string]Handler),
	}
}

func (r *Registry) Register(cap Capability, handler Handler) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.capabilities[cap.ID] = cap
	r.handlers[cap.ID] = handler
}

func (r *Registry) GetCapabilities() []Capability {
	r.mu.RLock()
	defer r.mu.RUnlock()
	list := make([]Capability, 0, len(r.capabilities))
	for _, c := range r.capabilities {
		list = append(list, c)
	}
	return list
}

func (r *Registry) Handle(ctx context.Context, capID string, payload []byte) (interface{}, error) {
	r.mu.RLock()
	handler, ok := r.handlers[capID]
	r.mu.RUnlock()
	
	if !ok {
		return nil, fmt.Errorf("capability %s not found or unsupported on this platform", capID)
	}
	
	return handler(ctx, payload)
}
