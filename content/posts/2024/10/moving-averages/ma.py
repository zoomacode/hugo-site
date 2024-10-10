#!/usr/bin/env python3

import numpy as np


def moving_average(data, window_size):
    """Calculates the moving average of a list of numbers."""
    moving_averages = []
    for i in range(len(data)):
        window = data[max(0, i - window_size + 1) : i + 1]
        moving_averages.append(sum(window) / len(window))
    return moving_averages


def exponential_moving_average(data, alpha):
    """Calculates the exponential moving average of a list of numbers."""
    ema = [data[0]]
    for i in range(1, len(data)):
        ema.append(alpha * data[i] + (1 - alpha) * ema[i - 1])
    return ema


def variable_exponential_moving_average(data, tau, timestamps):
    """Calculates the exponential moving average with variable alpha based on time differences."""
    ema = [data[0]]
    for i in range(1, len(data)):
        delta_t = timestamps[i] - timestamps[i - 1]
        alpha = 1 - np.exp(-delta_t / tau)
        ema.append(alpha * data[i] + (1 - alpha) * ema[i - 1])
    return ema


def gaussian_weighted_moving_average(data, timestamps, lag, sigma):
    """Calculates the Gaussian Weighted Moving Average of a list of numbers using timestamps."""
    gwma = []
    N = len(data)
    for i in range(N):
        # Compute time differences centered at (timestamps[i] + lag)
        time_diffs = np.array(timestamps) - (timestamps[i] + lag)
        weights = np.exp(-(time_diffs**2) / (2 * sigma**2))
        weights /= weights.sum()
        gwma.append(np.dot(weights, data))
    return gwma


def exponential_moving_percentage(data, alpha, percentile):
    """Calculates the exponential moving percentage of a list of numbers."""
    emp = []
    prev_emp = data[0]
    neg_percentile = 1 - percentile

    for d in data:
        if d < prev_emp:
            prev_emp -= alpha / percentile
        elif d > prev_emp:
            prev_emp += alpha / neg_percentile
        emp.append(prev_emp)
    return emp


def moving_percentage(data, window_size, percentile):
    """Calculates the moving percentage of a list of numbers."""
    moving_percentages = []
    for i in range(len(data)):
        window = data[max(0, i - window_size + 1) : i + 1].copy()
        window.sort()
        index = int(len(window) * percentile)
        index = min(index, len(window) - 1)  # Ensure index is within bounds
        moving_percentages.append(window[index])
    return moving_percentages


def generated_input_data(n: int):
    """
    Generates a list of n random numbers where
    first n numbers are random numbers between 0 and 4,
    the next n numbers are random numbers between 6 and 10,
    introduces a time gap,
    and the last n numbers are random numbers between 2 and 8.
    Returns data and timestamps.
    """
    import random

    data = []
    timestamps = []
    current_time = 0

    # First segment
    for _ in range(n):
        data.append(random.uniform(0, 4))
        timestamps.append(current_time)
        current_time += 1  # Time step of 1

    # Second segment
    for _ in range(n):
        data.append(random.uniform(6, 10))
        timestamps.append(current_time)
        current_time += 1  # Time step of 1

    # Introduce time gap
    current_time += n  # Time gap of 50 units

    # Third segment
    for _ in range(n):
        data.append(random.uniform(2, 5))
        timestamps.append(current_time)
        current_time += 1  # Time step of 1

    return data, timestamps


def draw(
    timestamps,
    data,
    metric: list[float],
    title: str,
    file_name: str,
):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(title)
    ax.plot(timestamps, data, label="Data", marker=".", linestyle="", alpha=0.5)
    ax.plot(timestamps, metric, label=title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.legend()
    plt.savefig(file_name)
    plt.close(fig)  # Close the figure to free memory


def main():
    data, timestamps = generated_input_data(1000)
    window_size = 500
    # Alpha is computed so that the EMA is close to the moving average
    alpha = 2 / (window_size + 1)
    percentile = 0.9

    moving_averages = moving_average(data, window_size)
    ema = exponential_moving_average(data, alpha)
    ema2 = exponential_moving_average(data, alpha * 2)
    ema4 = exponential_moving_average(data, alpha * 4)
    emps = [
        (exponential_moving_percentage(data, sigma, percentile), sigma)
        for sigma in [0.01, 0.05, 0.1]
    ]
    moving_percentages = moving_percentage(data, window_size, percentile)

    # Parameters for variable exponential moving average
    tau = window_size / 2  # Adjust tau as needed
    vema = variable_exponential_moving_average(data, tau, timestamps)
    vema2 = variable_exponential_moving_average(data, tau / 2, timestamps)
    vema4 = variable_exponential_moving_average(data, tau / 4, timestamps)

    # Parameters for Gaussian weighted moving average
    lag = 0  # No lag
    sigma = window_size / 2  # Adjust sigma as needed
    gwma = gaussian_weighted_moving_average(data, timestamps, lag, sigma)
    # Experiment with different lags and sigmas
    lag2 = -50  # Emphasize data from 50 time units ago
    sigma2 = window_size / 4
    gwma2 = gaussian_weighted_moving_average(data, timestamps, lag2, sigma2)

    draw(timestamps, data, moving_averages, "Moving Average", "ma.png")
    draw(
        timestamps,
        data,
        ema,
        f"Exponential Moving Average (alpha={alpha:.4f})",
        "ema.png",
    )
    draw(
        timestamps,
        data,
        ema2,
        f"Exponential Moving Average (alpha={alpha*2:.4f})",
        "ema2.png",
    )
    draw(
        timestamps,
        data,
        ema4,
        f"Exponential Moving Average (alpha={alpha*4:.4f})",
        "ema4.png",
    )
    for emp, sigma_emp in emps:
        draw(
            timestamps,
            data,
            emp,
            f"Exponential Moving Percentile (p={percentile}, sigma={sigma_emp})",
            f"emp_{sigma_emp}.png",
        )
    draw(
        timestamps,
        data,
        moving_percentages,
        f"Moving Percentage (p={percentile})",
        "mp.png",
    )

    # Draw variable EMA
    draw(timestamps, data, vema, f"Variable EMA (tau={tau})", "vema.png")
    draw(timestamps, data, vema2, f"Variable EMA (tau={tau/2})", "vema2.png")
    draw(timestamps, data, vema4, f"Variable EMA (tau={tau/4})", "vema4.png")

    # Draw Gaussian Weighted Moving Average
    draw(
        timestamps,
        data,
        gwma,
        f"Gaussian Weighted MA (lag={lag}, sigma={sigma})",
        "gwma.png",
    )
    draw(
        timestamps,
        data,
        gwma2,
        f"Gaussian Weighted MA (lag={lag2}, sigma={sigma2})",
        "gwma2.png",
    )


if __name__ == "__main__":
    main()
