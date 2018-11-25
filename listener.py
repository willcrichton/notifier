import redis
import subprocess as sp
import json
import os
import argparse
from redis.exceptions import ConnectionError, TimeoutError
import time
import traceback

parser = argparse.ArgumentParser()
parser.add_argument("node")
args = parser.parse_args()
NODE = args.node


def run(s):
    return sp.check_output(s, shell=True).decode('utf-8').strip()


def bench():
    run('''
      cd {downloads} && \
      rm -fr bench && \
      mkdir bench && cd bench && \
      gcloud compute scp {node}:esper/app/data/bench.tar.gz . && \
      tar -xf bench.tar.gz'''.format(
        downloads=os.path.expanduser('~/Downloads'), node=NODE))


def main():
    action_dispatch = {'bench': bench}

    host = run(
        'gcloud compute instances describe {} --format json | jq -r ".networkInterfaces[0].accessConfigs[0].natIP"'.
        format(NODE))

    # Listen for messages from Redis
    try:
        while True:
            try:
                r = redis.Redis(host=host, port=6379, socket_connect_timeout=5)
                p = r.pubsub()
                p.subscribe('main')
                print('Connected!')

                for message in p.listen():
                    if message['type'] != 'message':
                        continue

                    data = json.loads(message['data'])

                    # Execute requested action
                    if data['action'] is not None:
                        action_dispatch[data['action']]()

                    # Send desktop notification
                    sp.check_call(
                        'terminal-notifier -message "{}"'.format(data['message']),
                        shell=True)

            except (ConnectionError, TimeoutError):
                traceback.print_exc()
                print('Retrying...')
                time.sleep(5)

    except Exception:
        sp.check_call('terminal-notifier -message "Notifier crashed"', shell=True)
        raise


if __name__ == '__main__':
    main()
