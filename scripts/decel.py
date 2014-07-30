#!/usr/bin/python

import argparse
import math

parser = argparse.ArgumentParser(
        description = 'Generate jsontoolpath for a deceleration',
        epilog = 'All coordinates are relative, there is no need'
        ' to modify any axes in the generated commands.')

def pos_float(f):
    v = float(f)
    if v < 0:
        raise ValueError(str(f) + ' must be non-negative')
    return v

def at_least_2(i):
    v = int(i)
    if v < 2:
        raise ValueError(str(i) + ' must be at least 2')
    return v

parser.add_argument('-i', '--initial-velocity', dest = 'vi', type = pos_float,
        help = 'Initial velocity in the positive x direction',
        required = True)
parser.add_argument('-f', '--final-velocity', dest = 'vf', type = pos_float,
        default = 0.0, help = 'Optional final velocity in the positive x'
        'direction, defaults to %(default)s')
parser.add_argument('-d', '--distance', dest = 'distance', type = pos_float,
        help = 'Distance over which to decelerate', required = True)
parser.add_argument('-n', '--number', type = at_least_2,
        dest = 'n', help = 'Compute this many increments.'
        ' Higher numbers result in finer increments',
        required = True)
parser.add_argument('-e', '--exponential', action = 'store_true',
        help = 'Decelerate exponentially instead of linearly. '
        'Assume 5 time constants')

args = parser.parse_args()

def generate_command(x_distance, speed):
    '''
    Get a command that moves the gantry x_distance at speed
    '''
    ret = "{\"command\":{\"function\":\"move\","\
    "\"parameters\":{"\
        "\"x\":%s,"\
        "\"y\":0,"\
        "\"z\":0,"\
        "\"a\":0,"\
        "\"feedrate\":%s"\
    "},\"tags\":[\"Move\"],"\
    "\"metadata\":{"\
        "\"relative\":{"\
            "\"x\":true,"\
            "\"y\":true,"\
            "\"z\":true,"\
            "\"a\":true"\
        "}"\
    "}}},"
    return ret % (x_distance, speed)
    return str(speed) + ', '

def compute_acceleration(initial_velocity, final_velocity, distance):
    '''
    Compute the acceleration that changes the velocity from initial_velocity to
    final_velocity over the specified distance.
    
    Distance may not be 0, the average velocity may not be 0
    
    Returns a tuple, (acceleration, time)
    '''
    average_velocity = 0.5 * (initial_velocity + final_velocity)
    delta_time = distance / average_velocity
    delta_velocity = final_velocity - initial_velocity
    a = delta_velocity / delta_time
    return (a, delta_time)

def compute_exponential_params(initial_velocity, final_velocity, distance):
    '''
    Compute time constant and duration for exponential acceleration.
    
    Initial and final velocity must be non-negative. Initial velocity
    must be greater than final velocity. Distance must be positive.
    
    We assume after 5 time periods, speed is approximately 0
    '''
    vd = initial_velocity - final_velocity
    vda = 0.2 * vd
    va = final_velocity + vda
    t = distance / va
    return (5.0 / t, t)

def time_pair_to_command_args(initial_velocity, acceleration, time_pair):
    velocity_pair = tuple(initial_velocity + acceleration * t
            for t in time_pair)
    distance_pair = tuple(initial_velocity * t +
            (0.5 * acceleration * (t ** 2)) for t in time_pair)
    vel_avg = sum(velocity_pair) / len(velocity_pair)
    distance = distance_pair[1] - distance_pair[0]
    return (distance, vel_avg)

def exponential_command_args(initial_velocity, final_velocity,
        time_constant, time_pair):
    v_diff = initial_velocity - final_velocity
    def foo(t):
        return final_velocity + v_diff * math.exp(-time_constant * t)
    def antifoo(t):
        return final_velocity * t + (v_diff * (-1.0 / time_constant) *
                math.exp(-time_constant * t))
    distance = antifoo(time_pair[1]) - antifoo(time_pair[0])
    vel_avg = distance / (time_pair[1] - time_pair[0])
    return (distance, vel_avg)
    # return (antifoo(time_pair[1]) - antifoo(0), vel_avg)

if not args.exponential:
    (acceleration, time) = compute_acceleration(args.vi, args.vf, args.distance)
    n = args.n
    times = [time * float(t) / n for t in xrange(n + 1)]
    time_pairs = zip(times[:-1], times[1:])
    command_args = (time_pair_to_command_args(args.vi, acceleration, tp)
            for tp in time_pairs)
    
else:
    (tau, time) = compute_exponential_params(args.vi, args.vf, args.distance)
    n = args.n
    times = [time * float(t) / n for t in xrange(n + 1)]
    time_pairs = zip(times[:-1], times[1:])
    command_args = (exponential_command_args(args.vi, args.vf, tau, tp)
            for tp in time_pairs)

commands = (generate_command(*ca) for ca in command_args)
for c in commands:
    print c


