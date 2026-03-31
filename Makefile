CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall
TARGET = code
SRC = code.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET) *.o

.PHONY: all clean
