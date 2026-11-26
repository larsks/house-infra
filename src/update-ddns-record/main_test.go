package main

import (
	"context"
	"strings"
	"testing"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-sdk-go-v2/service/route53"
	"github.com/aws/aws-sdk-go-v2/service/route53/types"
)

func TestHandleRequestBadToken(t *testing.T) {
	r, err := NewRecordUpdater().WithUpdateToken("right-token").WithHostedZoneId("Zxxxx").Build()
	if err != nil {
		t.Fatalf("unexpected error building RecordUpdater: %v", err)
	}
	req := events.APIGatewayV2HTTPRequest{
		QueryStringParameters: map[string]string{"hostname": "house.dyn.oddbit.com", "token": "wrong-token"},
	}
	req.RequestContext.HTTP.SourceIP = "203.0.113.5"
	resp, err := r.HandleRequest(context.Background(), req)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.StatusCode != 401 {
		t.Fatalf("expected status 401, got %d (body %s)", resp.StatusCode, resp.Body)
	}
	if !strings.Contains(resp.Body, `"Status":"error"`) {
		t.Fatalf("expected error response, got %s", resp.Body)
	}
	// Assert on the specific rejection message produced by the token-check
	// branch, not just the generic error status. Without this, a broken or
	// disabled token check can still produce an error response (e.g.
	// because the subsequent Route53 call fails due to missing AWS
	// credentials in the test environment), which would let this test pass
	// even though the token check itself never ran.
	if !strings.Contains(resp.Body, "Invalid udpate token") {
		t.Fatalf("expected rejection to come from the token-check branch, got %s", resp.Body)
	}
}

func TestExtractSourceIP(t *testing.T) {
	req := events.APIGatewayV2HTTPRequest{}
	req.RequestContext.HTTP.SourceIP = "203.0.113.5"
	req.Headers = map[string]string{"x-forwarded-for": "10.0.0.1, 203.0.113.5"}
	ip, err := extractSourceIP(req)
	if err != nil || ip != "203.0.113.5" {
		t.Fatalf("got ip=%q err=%v, want ip=203.0.113.5 err=nil", ip, err)
	}
}

func TestExtractSourceIPMissing(t *testing.T) {
	req := events.APIGatewayV2HTTPRequest{}
	_, err := extractSourceIP(req)
	if err == nil {
		t.Fatal("expected an error for missing source IP")
	}
}

func TestTokenValid(t *testing.T) {
	r, err := NewRecordUpdater().WithUpdateToken("secret").WithHostedZoneId("Zxxxx").Build()
	if err != nil {
		t.Fatalf("unexpected error building RecordUpdater: %v", err)
	}
	if !r.tokenValid("secret") {
		t.Error("equal tokens should be valid")
	}
	if r.tokenValid("wrong") {
		t.Error("unequal tokens should be invalid")
	}
	if r.tokenValid("") {
		t.Error("empty got should never be valid")
	}

	// Build() rejects an empty configured token, so this edge case
	// (both sides empty) can only be exercised by constructing the
	// struct directly, same-package, bypassing the builder.
	empty := &RecordUpdater{}
	if empty.tokenValid("") {
		t.Error("empty tokens should never be valid, even when both sides are empty")
	}
}

type fakeRoute53 struct {
	input *route53.ChangeResourceRecordSetsInput
	err   error
}

func (f *fakeRoute53) ChangeResourceRecordSets(ctx context.Context, in *route53.ChangeResourceRecordSetsInput, _ ...func(*route53.Options)) (*route53.ChangeResourceRecordSetsOutput, error) {
	f.input = in
	if f.err != nil {
		return nil, f.err
	}
	return &route53.ChangeResourceRecordSetsOutput{}, nil
}

func TestUpdateRecordBuildsUpsert(t *testing.T) {
	r, err := NewRecordUpdater().WithUpdateToken("sometoken").WithHostedZoneId("Zxxxx").Build()
	if err != nil {
		t.Fatalf("unexpected error building RecordUpdater: %v", err)
	}
	fake := &fakeRoute53{}
	_, err = r.updateRecord(context.Background(), fake, "house.dyn.oddbit.com", "203.0.113.5")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	change := fake.input.ChangeBatch.Changes[0]
	if change.Action != types.ChangeActionUpsert {
		t.Errorf("action = %v, want UPSERT", change.Action)
	}
	if *change.ResourceRecordSet.Name != "house.dyn.oddbit.com" {
		t.Errorf("name = %v", *change.ResourceRecordSet.Name)
	}
	if *change.ResourceRecordSet.ResourceRecords[0].Value != "203.0.113.5" {
		t.Errorf("value = %v", *change.ResourceRecordSet.ResourceRecords[0].Value)
	}
}
