package main

import "encoding/json"

type (
	Response struct {
		Status   string
		Message  string
		Hostname string `json:",omitempty"`
		Address  string `json:",omitempty"`
		Result   string `json:",omitempty"`
	}

	ResponseModifier func(*Response)
)

func NewResponse(status, message string, mods ...ResponseModifier) *Response {
	resp := Response{
		Status:  status,
		Message: message,
	}

	for _, mod := range mods {
		mod(&resp)
	}

	return &resp
}

func WithHostInfo(hostname, address string) ResponseModifier {
	return func(resp *Response) {
		resp.Hostname = hostname
		resp.Address = address
	}
}

func WithApiResult(res string) ResponseModifier {
	return func(resp *Response) {
		resp.Result = res
	}
}

func (resp *Response) String() string {
	text, err := json.Marshal(resp)
	if err != nil {
		panic(err)
	}

	return string(text)
}
