GENERATED = components-diagram.svg legend.svg components.svg

components-diagram.svg: components.dot
	dot -T svg -o $@ $<

legend.svg: legend.dot
	dot -T svg -o $@ $<

components.svg: $(GENERATED) compose-legend.py
	python3 compose-legend.py components-diagram.svg legend.svg components.svg --x 860 --y 300

all: components.svg

clean:
	rm -f $(GENERATED)
