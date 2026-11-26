package main

import (
	"context"
	"crypto/subtle"
	"errors"
	"fmt"
	"log"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/route53"
	"github.com/aws/aws-sdk-go-v2/service/route53/types"
)

const (
	defaultTtl = 300
)

// Route53Client is the subset of the Route53 API used by updateRecord.
// It is satisfied by *route53.Client and allows tests to substitute a fake.
type Route53Client interface {
	ChangeResourceRecordSets(ctx context.Context, params *route53.ChangeResourceRecordSetsInput, optFns ...func(*route53.Options)) (*route53.ChangeResourceRecordSetsOutput, error)
}

type RecordUpdater struct {
	ddnsUpdateToken  string
	ddnsHostedZoneID string
	ddnsRecordTTL    int
}

func NewRecordUpdater() *RecordUpdater {
	return &RecordUpdater{
		ddnsRecordTTL: defaultTtl,
	}
}

func (r *RecordUpdater) WithUpdateToken(token string) *RecordUpdater {
	r.ddnsUpdateToken = token
	return r
}

func (r *RecordUpdater) WithHostedZoneId(zoneId string) *RecordUpdater {
	r.ddnsHostedZoneID = zoneId
	return r
}

func (r *RecordUpdater) WithTTL(ttl int) *RecordUpdater {
	r.ddnsRecordTTL = ttl
	return r
}

func (r *RecordUpdater) Build() (*RecordUpdater, error) {
	if r.ddnsUpdateToken == "" {
		return nil, errors.New("DDNS udpate token must not be empty")
	}
	if r.ddnsHostedZoneID == "" {
		return nil, errors.New("DDNS hosted zone id must not be empty")
	}
	return r, nil
}

// updateRecord UPSERTs an A record for hostname in zoneID pointing at ip.
func (r *RecordUpdater) updateRecord(ctx context.Context, client Route53Client, hostname, ip string) (*route53.ChangeResourceRecordSetsOutput, error) {
	input := route53.ChangeResourceRecordSetsInput{
		HostedZoneId: aws.String(r.ddnsHostedZoneID),
		ChangeBatch: &types.ChangeBatch{
			Changes: []types.Change{
				{
					Action: types.ChangeActionUpsert,
					ResourceRecordSet: &types.ResourceRecordSet{
						Name: aws.String(hostname),
						Type: types.RRTypeA,
						TTL:  aws.Int64(int64(r.ddnsRecordTTL)),
						ResourceRecords: []types.ResourceRecord{
							{
								Value: aws.String(ip),
							},
						},
					},
				},
			},
		},
	}

	return client.ChangeResourceRecordSets(ctx, &input)
}

func (r *RecordUpdater) HandleRequest(ctx context.Context, request events.APIGatewayV2HTTPRequest) (events.APIGatewayV2HTTPResponse, error) {
	update_token := r.ddnsUpdateToken
	hosted_zone_id := r.ddnsHostedZoneID

	if len(update_token) == 0 || len(hosted_zone_id) == 0 {
		return apiResponse(500, NewResponse("error", "Missing required configuration")), nil
	}

	clientAddress, err := extractSourceIP(request)
	if err != nil {
		return apiResponse(400, NewResponse("error", "Unknown client address")), nil
	}

	hostName := request.QueryStringParameters["hostname"]
	req_token := request.QueryStringParameters["token"]

	log.Printf("checking request from %s for %s", clientAddress, hostName)
	if !r.tokenValid(req_token) {
		return apiResponse(401, NewResponse("error", "Invalid udpate token")), nil
	}

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return apiResponse(500, NewResponse("error", "Failed to load AWS configuration",
			WithApiResult(err.Error()),
		)), nil
	}
	svc := route53.NewFromConfig(cfg)

	log.Printf("updating %s in zone %s", hostName, hosted_zone_id)

	resp, err := r.updateRecord(ctx, svc, hostName, clientAddress)
	if err != nil {
		return apiResponse(502, NewResponse(
			"error", "Failed to update record",
			WithApiResult(err.Error()),
		)), nil
	}

	return apiResponse(200, NewResponse("success",
		fmt.Sprintf("Updated address for %s", hostName),
		WithHostInfo(hostName, clientAddress),
		WithApiResult(changeInfoString(resp.ChangeInfo)),
	)), nil
}

// apiResponse wraps a Response in an API Gateway v2 HTTP response with an
// explicit status code, so callers (the router's dhclient hook, in
// particular) can rely on the HTTP status rather than parsing the JSON
// body to tell success from failure.
func apiResponse(statusCode int, resp *Response) events.APIGatewayV2HTTPResponse {
	return events.APIGatewayV2HTTPResponse{
		StatusCode: statusCode,
		Body:       resp.String(),
		Headers:    map[string]string{"Content-Type": "application/json"},
	}
}

// changeInfoString renders a Route53 ChangeInfo's useful fields as a plain
// string. ChangeInfo's fields are pointers/typed values, so formatting it
// directly with %+v prints pointer addresses rather than actual values.
func changeInfoString(ci *types.ChangeInfo) string {
	if ci == nil {
		return "no change info returned"
	}
	return fmt.Sprintf("id=%s status=%s", aws.ToString(ci.Id), ci.Status)
}

// extractSourceIP returns the client address as verified by API Gateway.
// It deliberately ignores the (client-controlled) X-Forwarded-For header.
func extractSourceIP(req events.APIGatewayV2HTTPRequest) (string, error) {
	ip := req.RequestContext.HTTP.SourceIP
	if len(ip) == 0 {
		return "", errors.New("missing source IP in request context")
	}
	return ip, nil
}

// tokenValid reports whether got matches want, using a constant-time
// comparison. Empty tokens are never considered valid.
func (r *RecordUpdater) tokenValid(got string) bool {
	if len(got) == 0 || len(r.ddnsUpdateToken) == 0 {
		return false
	}
	return subtle.ConstantTimeCompare([]byte(got), []byte(r.ddnsUpdateToken)) == 1
}

func main() {
	ddnsHostedZoneID := GetenvWithDefault("DDNS_HOSTED_ZONE_ID", "")
	ddnsUpdateToken := GetenvWithDefault("DDNS_UPDATE_TOKEN", "")
	ddnsRecordTTL := GetenvWithDefault("DDNS_RECORD_TTL", defaultTtl)

	r, err := NewRecordUpdater().
		WithHostedZoneId(ddnsHostedZoneID).
		WithUpdateToken(ddnsUpdateToken).
		WithTTL(ddnsRecordTTL).
		Build()
	if err != nil {
		log.Fatalf("failed to initialize: %v", err)
	}
	lambda.Start(r.HandleRequest)
}
