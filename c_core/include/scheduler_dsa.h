#ifndef SCHEDULER_DSA_H
#define SCHEDULER_DSA_H

#ifdef __cplusplus
extern "C" {
#endif

enum ccore_strategy {
    CCORE_STRATEGY_PRIORITY = 0,
    CCORE_STRATEGY_FIFO = 1,
    CCORE_STRATEGY_LIFO = 2
};

int ccore_order_indices(
    int strategy,
    const double *priority_scores,
    const double *created_timestamps,
    int task_count,
    int *out_indices
);

double ccore_average_wait(
    const int *ordered_indices,
    const double *estimated_efforts,
    int task_count
);

int ccore_simulate_strategy(
    int strategy,
    const double *priority_scores,
    const double *created_timestamps,
    const double *estimated_efforts,
    int task_count,
    int *out_completed_count,
    double *out_average_wait_hours
);

#ifdef __cplusplus
}
#endif

#endif
