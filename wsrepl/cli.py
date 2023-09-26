import argparse

from wsrepl import WSRepl

parser = argparse.ArgumentParser(description='Websocket Client')
# Pass URL either as -u or as a positional argument
parser.add_argument('-u', '--url',               type=str,                                      help='Websocket URL (e.g. wss://echo.websocket.org)')
parser.add_argument('url_positional', nargs='?', type=str,                                      help='Websocket URL (e.g. wss://echo.websocket.org)')

# curl compatible args, this is the stuff that Burp uses in a 'Copy as curl command' menu action
parser.add_argument('-i', '--include',                      action='store_true', default=False, help='No effect, just for curl compatibility')
parser.add_argument('-s', '--silent',                       action='store_true', default=False, help='No effect, just for curl compatibility')
parser.add_argument('-k', '--insecure',                     action='store_true', default=False, help='Disable SSL verification')
parser.add_argument('-X', '--request',            type=str,                                     help='No effect, just for curl compatibility')
parser.add_argument('-H', '--header',                       action='append',                    help='Additional header (e.g. "X-Header: value"), can be used multiple times')
parser.add_argument('-b', '--cookie',                       action='append',                    help='Cookie header (e.g. "name=value"), can be used multiple times')
# curl compatible args, used by Chrome's 'Copy as cURL' menu action
parser.add_argument('--compressed',                         action='store_true', default=False, help='No effect, just for curl compatibility')

parser.add_argument('-S', '--small',                        action='store_true', default=False, help='Smaller UI')
parser.add_argument('-A', '--user-agent',         type=str,                                     help='User-Agent header')
parser.add_argument('-O', '--origin',             type=str,                                     help='Origin header')
parser.add_argument('-F', '--headers-file',       type=str,                                     help='Additional headers file (e.g. "headers.txt")')
parser.add_argument(      '--no-native-ping',               action='store_true', default=False, help='Disable native ping/pong messages')
parser.add_argument(      '--ping-interval',      type=int,                      default=24,    help='Ping interval (seconds)')
parser.add_argument(      '--hide-ping-pong',               action='store_true', default=False, help='Hide ping/pong messages')
parser.add_argument(      '--ping-0x1-interval',  type=int,                      default=24,    help='Fake ping (0x1 opcode) interval (seconds)')
parser.add_argument(      '--ping-0x1-payload',   type=str,                                     help='Fake ping (0x1 opcode) payload')
parser.add_argument(      '--pong-0x1-payload',   type=str,                                     help='Fake pong (0x1 opcode) payload')
parser.add_argument(      '--hide-0x1-ping-pong',           action='store_true', default=False, help='Hide fake ping/pong messages')
parser.add_argument('-t', '--ttl',                type=int,                                     help='Heartbeet interval (seconds)')
parser.add_argument('-p', '--http-proxy',         type=str,                                     help='HTTP Proxy Address (e.g. 127.0.0.1:8080)')
parser.add_argument('-r', '--reconnect-interval', type=int,                      default=2,     help='Reconnect interval (seconds, default: 2)')
parser.add_argument('-I', '--initial-messages',   type=str,                                     help='Send the messages from this file on connect')
parser.add_argument('-P', '--plugin',             type=str,                                     help='Plugin file to load')
parser.add_argument(      '--plugin-provided-url',          action='store_true', default=False, help='Indicates if plugin provided dynamic url for websockets')
parser.add_argument('-v', '--verbose',            type=int,                      default=3,     help='Verbosity level, 1-4 default: 3 (errors, warnings, info), 4 adds debug')

def cli():
    args = parser.parse_args()
    url = args.url or args.url_positional
    if url and args.plugin_provided_url is False:
        # Check and modify the URL protocol if necessary
        if url.startswith('http://'):
            url = url.replace('http://', 'ws://', 1)
        elif url.startswith('https://'):
            url = url.replace('https://', 'wss://', 1)
        elif not url.startswith(('ws://', 'wss://')):
            parser.error('Invalid protocol. Supported protocols are http://, https://, ws://, and wss://.')
    elif args.plugin_provided_url is False and args.plugin is not None:
        parser.error('Please provide a WebSocket URL using -u or use --plugin-provided-url if the WebSocket URL provided in a plugin')
    elif args.plugin_provided_url is False and args.plugin is None:
        parser.error('Please provide either a WebSocket URL using -u or use --plugin-provided-url with --plugin if the WebSocket URL provided in a plugin')

    app = WSRepl(
        url=url,
        small=args.small,
        user_agent=args.user_agent,
        origin=args.origin,
        cookies=args.cookie if isinstance(args.cookie, list) else [args.cookie] if args.cookie else [],
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
        plugin_provided_url=args.plugin_provided_url,
        verbosity=args.verbose,
    )
    app.run()

if __name__ == '__main__':
    cli()
