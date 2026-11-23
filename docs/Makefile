GENERATED = network.svg network.png

D2_LAYOUT=tala
D2_SKETCH=--sketch

D2 = d2 -l $(D2_LAYOUT) $(D2_SKETCH)

all: $(GENERATED)

network.svg: network.d2
	$(D2) $< $@

network.png: network.d2
	$(D2) $< $@

clean:
	rm -f $(GENERATED)
