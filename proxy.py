import json
import argparse
from decouple import config
from klein import Klein
from pythonosc.udp_client import SimpleUDPClient

collider_client = SimpleUDPClient(config('COLLIDER_IP'), int(config('COLLIDER_PORT')))
visuals_client = SimpleUDPClient(config('VISUALS_IP'), int(config('VISUALS_PORT')))


class Proxy(object):
    app = Klein()

    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    @app.route(config('PROXY_ADDRESS'), methods=['POST'])
    def forward(self, request, name='NONE'):
        request.setHeader('Content-Type', 'application/json')
        body = json.loads(request.content.read())
        if self.dry_run:
            print('Running under dry-run. Ignoring: ', body)
        else:
            print('forwarding: ', body)
            collider_client.send_message(config('COLLIDER_ROUTE'), body)
            visuals_client.send_message(config('VISUALS_ROUTE'), json.dumps(body))
        return json.dumps({'success': True})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', default=False, action='store_true')
    args = parser.parse_args()
    proxy = Proxy(dry_run=args.dry_run)
    proxy.app.run(config('HOSTNAME'), config('PORT'))
