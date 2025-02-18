OBJECTS = $(filter-out %.c,$(notdir $(patsubst %.cc,%.o,$(SOURCES)))) \
	  $(filter-out %.cc,$(notdir $(patsubst %.c,%.o,$(SOURCES))))

LDFLAGS +=   -Wl,-rpath ${PATH_TO_LIB} -L${PATH_TO_LIB} -lOpenGL -lEGL

# Comment out to build without debug info.
CXXFLAGS += -g -I.

SOURCES = tinyegl.cc

BIN = tinyegl

$(BIN): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) $(LDFLAGS) -o $@

.PHONY: clean
clean:
	rm -f $(BIN) *.o
