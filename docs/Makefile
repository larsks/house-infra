GENERATED = network.svg network.png \
						netgear-r6400v1-ports.svg

D2_LAYOUT=tala
D2_SKETCH=--sketch

D2 = d2 -l $(D2_LAYOUT) $(D2_SKETCH)

%.svg: %.d2
	$(D2) $< $@

%.png: %.d2
	$(D2) $< $@

all: $(GENERATED)

clean:
	rm -f $(GENERATED)
