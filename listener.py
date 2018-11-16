import redis
import subprocess as sp
import json
import os

def run(s):
    return sp.check_output(s, shell=True).decode('utf-8').strip()


def bench():
    run('''
      cd {} && \
      rm -fr bench && \
      mkdir bench && cd bench && \
      gcloud compute scp highcpu:esper/app/data/bench.tar.gz . && \
      tar -xf bench.tar.gz'''.format(os.path.expanduser('~/Downloads'))


def main():
    action_dispatch = {'bench': bench}

    host = run(
        'gcloud compute instances describe highcpu --format json | jq -r ".networkInterfaces[0].accessConfigs[0].natIP"'
    )

    r = redis.Redis(host=host, port=6379)
    print('Connected to Redis!')

    p = r.pubsub()
    p.subscribe('main')

    # Listen for messages from Redis
    try:
        for message in p.listen():
            if message['type'] != 'message':
                continue

            data = json.loads(message['data'])

            # Execute requested action
            if data['action'] is not None:
                action_dispatch[data['action']]()

            # Send desktop notification
            sp.check_call(
                'terminal-notifier -message "{}"'.format(data['message']), shell=True)

    except Exception:
        sp.check_call('terminal-notifier -message "Notifier crashed"', shell=True)
        raise


if __name__ == '__main__':
    main()