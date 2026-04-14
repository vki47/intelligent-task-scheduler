#include "scheduler_dsa.h"
#include <stddef.h>
#include <stdlib.h>

static void init_indices(int *indices, int task_count) {
    for (int i = 0; i < task_count; ++i) {
        indices[i] = i;
    }
}

static int should_swap(
    int strategy,
    int left,
    int right,
    const double *priority_scores,
    const double *created_timestamps
) {
    if (strategy == CCORE_STRATEGY_PRIORITY) {
        if (priority_scores[left] > priority_scores[right]) {
            return 1;
        }
        if (priority_scores[left] == priority_scores[right]) {
            return created_timestamps[left] > created_timestamps[right];
        }
        return 0;
    }

    if (strategy == CCORE_STRATEGY_FIFO) {
        if (created_timestamps[left] > created_timestamps[right]) {
            return 1;
        }
        return left > right;
    }

    if (strategy == CCORE_STRATEGY_LIFO) {
        if (created_timestamps[left] < created_timestamps[right]) {
            return 1;
        }
        return left > right;
    }

    return 0;
}

int ccore_order_indices(
    int strategy,
    const double *priority_scores,
    const double *created_timestamps,
    int task_count,
    int *out_indices
) {
    if (!priority_scores || !created_timestamps || !out_indices || task_count < 0) {
        return -1;
    }

    if (strategy != CCORE_STRATEGY_PRIORITY &&
        strategy != CCORE_STRATEGY_FIFO &&
        strategy != CCORE_STRATEGY_LIFO) {
        return -2;
    }

    init_indices(out_indices, task_count);

    for (int i = 0; i < task_count - 1; ++i) {
        for (int j = 0; j < task_count - i - 1; ++j) {
            int left = out_indices[j];
            int right = out_indices[j + 1];
            if (should_swap(strategy, left, right, priority_scores, created_timestamps)) {
                int temp = out_indices[j];
                out_indices[j] = out_indices[j + 1];
                out_indices[j + 1] = temp;
            }
        }
    }

    return 0;
}

double ccore_average_wait(
    const int *ordered_indices,
    const double *estimated_efforts,
    int task_count
) {
    if (!ordered_indices || !estimated_efforts || task_count <= 0) {
        return 0.0;
    }

    double wait_sum = 0.0;
    double elapsed = 0.0;

    for (int i = 0; i < task_count; ++i) {
        int idx = ordered_indices[i];
        wait_sum += elapsed;
        elapsed += estimated_efforts[idx];
    }

    return wait_sum / (double)task_count;
}

int ccore_simulate_strategy(
    int strategy,
    const double *priority_scores,
    const double *created_timestamps,
    const double *estimated_efforts,
    int task_count,
    int *out_completed_count,
    double *out_average_wait_hours
) {
    if (!estimated_efforts || !out_completed_count || !out_average_wait_hours) {
        return -1;
    }

    if (task_count <= 0) {
        *out_completed_count = 0;
        *out_average_wait_hours = 0.0;
        return 0;
    }

    int *ordered = (int *)malloc(sizeof(int) * (size_t)task_count);
    if (!ordered) {
        return -3;
    }
    int order_status = ccore_order_indices(
        strategy,
        priority_scores,
        created_timestamps,
        task_count,
        ordered
    );

    if (order_status != 0) {
        free(ordered);
        return order_status;
    }

    *out_completed_count = task_count;
    *out_average_wait_hours = ccore_average_wait(ordered, estimated_efforts, task_count);
    free(ordered);
    return 0;
}
