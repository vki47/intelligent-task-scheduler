CC := gcc
CFLAGS := -std=c11 -Wall -Wextra -Werror -O2 -Iinclude
LDFLAGS :=

SRC := src/scheduler_dsa.c
SHARED := libscheduler_dsa.so
TEST_BIN := tests/test_scheduler_dsa
TEST_SRC := tests/test_scheduler_dsa.c

.PHONY: all clean test

all: $(SHARED)

$(SHARED): $(SRC) include/scheduler_dsa.h
	$(CC) $(CFLAGS) -shared -fPIC $(SRC) -o $@

$(TEST_BIN): $(TEST_SRC) $(SRC) include/scheduler_dsa.h
	$(CC) $(CFLAGS) $(TEST_SRC) $(SRC) -lm -o $@

test: $(TEST_BIN)
	./$(TEST_BIN)

clean:
	rm -f $(SHARED) $(TEST_BIN)
