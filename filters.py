import concurrent.futures
import threading
import logging
from geopy.distance import geodesic

STEP_LENGTH = 0.25
LOG_INTERVAL = 1000
TOTAL_STEP_THRESHOLD_1 = 150
TOTAL_STEP_THRESHOLD_2 = 200
TOTAL_STEP_THRESHOLD_3 = 250
TOTAL_STEP_THRESHOLD_4 = 300

def find_connected_stairs(stairs, candidate, lock):
    visited = set()
    to_visit = [candidate]
    connected_stairs = []

    while to_visit:
        current_point, current_step_count = to_visit.pop()
        if current_point in visited:
            continue

        visited.add(current_point)
        connected_stairs.append((current_point, current_step_count))

        logging.debug(f'Visiting: {current_point}, steps: {current_step_count}')

        dynamic_distance = STEP_LENGTH * current_step_count

        with lock:
            for idx, (point, step_count) in enumerate(stairs):
                if idx % LOG_INTERVAL == 0:
                    logging.info(f"Checking proximity for stair {idx}")
                if point in visited:
                    continue

                if geodesic((current_point.y, current_point.x), (point.y, point.x)).meters <= dynamic_distance:
                    to_visit.append((point, step_count))

    return connected_stairs

def group_stairs(stairs):
    candidates = [stair for stair in stairs if stair[1] > 25]
    grouped_stairs = []
    lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(find_connected_stairs, stairs, candidate, lock): candidate for candidate in candidates}

        for future in concurrent.futures.as_completed(futures):
            connected_stairs = future.result()
            if not connected_stairs:
                continue

            grouped_stairs.append(connected_stairs)
            logging.debug(f'Connected stairs: {connected_stairs}')

    return grouped_stairs

def remove_duplicates(groups):
    unique_stairs = []
    seen = set()

    for group in groups:
        unique_group = []
        for point, step_count in group:
            if (point.x, point.y) not in seen:
                seen.add((point.x, point.y))
                unique_group.append((point, step_count))
        if unique_group:
            unique_stairs.append(unique_group)

    return unique_stairs

def filter_by_step_count(groups):
    categorized_stairs = {
        "150-200": [],
        "200-250": [],
        "250-300": [],
        "300plus": []
    }

    for group in groups:
        total_steps = sum(step_count for _, step_count in group)
        if TOTAL_STEP_THRESHOLD_1 <= total_steps < TOTAL_STEP_THRESHOLD_2:
            categorized_stairs["150-200"].extend(group)
        elif TOTAL_STEP_THRESHOLD_2 <= total_steps < TOTAL_STEP_THRESHOLD_3:
            categorized_stairs["200-250"].extend(group)
        elif TOTAL_STEP_THRESHOLD_3 <= total_steps < TOTAL_STEP_THRESHOLD_4:
            categorized_stairs["250-300"].extend(group)
        elif total_steps >= TOTAL_STEP_THRESHOLD_4:
            categorized_stairs["300plus"].extend(group)

    return categorized_stairs
