import argparse
from udp import MarshallConnection

parser = argparse.ArgumentParser(description='Control Marshall camera.')
group = parser.add_mutually_exclusive_group(required=True)


parser.add_argument('-i', '--ip', metavar='Camera IP Address', action='store', type=str, required=True)
group.add_argument('-s', '--set', metavar='Memory Number', action='store', type=int)
group.add_argument('-r', '--reset', metavar='Memory Number', action='store', type=int)
group.add_argument('-c', '--call', metavar='Memory Number', action='store', type=int)
group.add_argument('--on', action='store_true')
group.add_argument('--off', action='store_true')

args = parser.parse_args()

conn = MarshallConnection(udp_ip=args.ip)

if args.on:
    conn.power_on()

if args.off:
    conn.power_off()

if args.set is not None:
    conn.set_preset(args.set)

if args.call is not None:
    conn.recall_preset(args.call)

if args.reset is not None:
    conn.reset_preset(args.reset)