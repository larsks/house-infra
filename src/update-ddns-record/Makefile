GOFILES = $(wildcard *.go)

all: bootstrap

.INTERMEDIATE: function.zip
function.zip: bootstrap
	# pin file mtime to the date of the last commit that touched
	# this directory. that ensures that function.zip doesn't change
	# so we don't keep uploading it when running tofu apply
	touch -d @$$(git log -1 --format=%ct -- .) $^
	zip -X -o $@ $^

bootstrap: $(GOFILES)
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o bootstrap

update: .lastupdate

.lastupdate: function.zip
	aws lambda update-function-code \
		--function-name update-ddns-record \
		--zip-file fileb://function.zip
	touch $@

clean:
	rm -f bootstrap function.zip .lastupdate
