import random
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "q_table.json")


def load_q_table():

    if not os.path.exists(Q_TABLE_FILE):
        return {}

    with open(Q_TABLE_FILE, "r") as f:
        return json.load(f)

def save_q_table(q_table):

    with open(Q_TABLE_FILE, "w") as f:
        json.dump(q_table, f)


def get_state(queue_lengths, avg_times, service_type):

    state = {
        "queues": queue_lengths,
        "speeds": avg_times,
        "service": service_type
    }

    return str(state)


def choose_action(queue_lengths, avg_times, service_type, counters):

    q_table = load_q_table()

    state = get_state(queue_lengths, avg_times, service_type)

    if state not in q_table:
        q_table[state] = [0] * len(counters)

    if len(q_table[state]) < len(counters):
        q_table[state].extend([0] * (len(counters) - len(q_table[state])))
    elif len(q_table[state]) > len(counters):
        q_table[state] = q_table[state][:len(counters)]

    if random.random() < 0.2:
        action = random.randint(0, len(counters)-1)
    else:
        try:
            action = q_table[state].index(max(q_table[state]))
        except ValueError:
            action = 0

    if action >= len(counters):
        action = len(counters) - 1

    save_q_table(q_table)

    return action


def update_q_table(queue_lengths, avg_times, service_type, action, reward):

    q_table = load_q_table()

    state = get_state(queue_lengths, avg_times, service_type)

    if state not in q_table:
        return

    learning_rate = 0.1

    try:
        if action < len(q_table[state]):
            q_table[state][action] += learning_rate * reward
            save_q_table(q_table)
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error updating Q-table natively: {e}")