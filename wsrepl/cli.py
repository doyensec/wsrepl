import argparse

from wsrepl import WSRepl

parser = argparse.ArgumentParser(description='Websocket Client')
parser.add_argument('-u', '--url',                type=str,          required=True,             help='Websocket URL (e.g. wss://echo.websocket.org)')
parser.add_argument('-s', '--small',                        action='store_true', default=False, help='Smaller UI')
parser.add_argument('-A', '--user-agent',         type=str,                                     help='User-Agent header')
parser.add_argument('-O', '--origin',             type=str,                                     help='Origin header')
parser.add_argument('-H', '--header',                       action="append",                    help='Additional header (e.g. "X-Header: value"), can be used multiple times')
parser.add_argument('-F', '--headers-file',       type=str,                                     help='Additional headers file (e.g. "headers.txt")')
parser.add_argument('--no-native-ping',                     action='store_true', default=False, help='Disable native ping/pong messages')
parser.add_argument('--ping-interval',            type=int,                      default=24,    help='Ping interval (seconds)')
parser.add_argument('--hide-ping-pong',                     action='store_true', default=False, help='Hide ping/pong messages')
parser.add_argument('--ping-0x1-interval',        type=int,                      default=24,    help='Fake ping (0x1 opcode) interval (seconds)')
parser.add_argument('--ping-0x1-payload',         type=str,                                     help='Fake ping (0x1 opcode) payload')
parser.add_argument('--pong-0x1-payload',         type=str,                                     help='Fake pong (0x1 opcode) payload')
parser.add_argument('--hide-0x1-ping-pong',                  action='store_true', default=False, help='Hide fake ping/pong messages')
parser.add_argument('-t', '--ttl',                type=int,                                     help='Heartbeet interval (seconds)')
parser.add_argument('-p', '--http-proxy',         type=str,                                     help='HTTP Proxy Address (e.g. 127.0.0.1:8080)')
parser.add_argument('-k', '--insecure',                     action='store_true', default=False, help='Disable SSL verification')
parser.add_argument('-r', '--reconnect-interval', type=int,                      default=2,     help='Reconnect interval (seconds, default: 2)')
parser.add_argument('-i', '--initial-messages',   type=str,                                     help='Send the messages from this file on connect')
parser.add_argument('-P', '--plugin',             type=str,                                     help='Plugin file to load')
parser.add_argument('-v', '--verbose',            type=int,                      default=3,     help='Verbosity level, 1-4 default: 3 (errors, warnings, info), 4 adds debug')

def cli():
    args = parser.parse_args()

    app = WSRepl(
        url=args.url,
        small=args.small,
        user_agent=args.user_agent,
        origin=args.origin,
        headers=args.header if isinstance(args.header, list) else [args.header] if args.header else [],
        headers_file=args.headers_file,
        ping_interval=args.ping_interval,
        hide_ping_pong=args.hide_ping_pong,
        ping_0x1_interval=args.ping_0x1_interval,
        ping_0x1_payload=args.ping_0x1_payload,
        pong_0x1_payload=args.pong_0x1_payload,
        hide_0x1_ping_pong=args.hide_0x1_ping_pong,
        reconnect_interval=args.reconnect_interval,
        proxy=args.http_proxy,
        verify_tls=not args.insecure,
        initial_msgs_file=args.initial_messages,
        plugin_path=args.plugin,
        verbosity=args.verbose,
    )
    app.run()

if __name__ == '__main__':
    cli()
