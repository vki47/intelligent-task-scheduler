#include <math.h>
#include <stdio.h>

#include "scheduler_dsa.h"

static int assert_int_eq(const char *name, int got, int expected) {
    if (got != expected) {
        printf("FAIL: %s (got %d, expected %d)\n", name, got, expected);
        return 1;
    }
    return 0;
}

static int assert_double_near(const char *name, double got, double expected) {
    if (fabs(got - expected) > 0.01) {
        printf("FAIL: %s (got %.2f, expected %.2f)\n", name, got, expected);
        return 1;
    }
    return 0;
}

int main(void) {
    int failures = 0;
    double priorities[] = {40.0, 20.0, 30.0};
    double created[] = {100.0, 200.0, 300.0};
    double efforts[] = {1.0, 2.0, 3.0};
    int out[3] = {0};

    failures += assert_int_eq("priority sort status", ccore_order_indices(CCORE_STRATEGY_PRIORITY, priorities, created, 3, out), 0);
    failures += assert_int_eq("priority first", out[0], 1);
    failures += assert_int_eq("priority second", out[1], 2);
    failures += assert_int_eq("priority third", out[2], 0);

    failures += assert_int_eq("fifo sort status", ccore_order_indices(CCORE_STRATEGY_FIFO, priorities, created, 3, out), 0);
    failures += assert_int_eq("fifo first", out[0], 0);
    failures += assert_int_eq("fifo third", out[2], 2);

    failures += assert_int_eq("lifo sort status", ccore_order_indices(CCORE_STRATEGY_LIFO, priorities, created, 3, out), 0);
    failures += assert_int_eq("lifo first", out[0], 2);
    failures += assert_int_eq("lifo third", out[2], 0);

    int completed = 0;
    double avg_wait = 0.0;
    failures += assert_int_eq(
        "simulate status",
        ccore_simulate_strategy(CCORE_STRATEGY_FIFO, priorities, created, efforts, 3, &completed, &avg_wait),
        0
    );
    failures += assert_int_eq("simulate completed", completed, 3);
    failures += assert_double_near("simulate avg wait", avg_wait, 1.33);

    if (failures == 0) {
        printf("PASS: c_core scheduler DSA tests\n");
        return 0;
    }

    return 1;
}
