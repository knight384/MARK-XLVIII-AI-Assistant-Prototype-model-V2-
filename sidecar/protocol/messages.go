package protocol

import (
	"encoding/json"
	"time"
)

type ProtocolVersion string

const CurrentVersion ProtocolVersion = "1.0.0"

type RPCRequest struct {
	RequestID       string          json:"request_id"
	SessionID       string          json:"session_id"
	DeviceID        string          json:"device_id"
	Capability      string          json:"capability"
	Operation       string          json:"operation"
	Payload         json.RawMessage json:"payload,omitempty"
	Timestamp       int64           json:"timestamp"
	ProtocolVersion ProtocolVersion json:"protocol_version"
}

type RPCResponse struct {
	RequestID       string          json:"request_id"
	Status          string          json:"status" // "success", "error"
	Result          json.RawMessage json:"result,omitempty"
	Error           string          json:"error,omitempty"
	Timestamp       int64           json:"timestamp"
	ProtocolVersion ProtocolVersion json:"protocol_version"
}

func NewResponse(reqID string, status string, result interface{}, errMsg string) RPCResponse {
	var rawResult json.RawMessage
	if result != nil {
		b, _ := json.Marshal(result)
		rawResult = b
	}
	return RPCResponse{
		RequestID:       reqID,
		Status:          status,
		Result:          rawResult,
		Error:           errMsg,
		Timestamp:       time.Now().UnixMilli(),
		ProtocolVersion: CurrentVersion,
	}
}
