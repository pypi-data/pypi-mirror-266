import getopt
import sys

from .__init__ import *
import configparser
import python_socks


def new_telegram_collector():
    tc = TelegramCollector()
    config_file = 'tg.ini'
    parser = configparser.ConfigParser()
    parser.read(config_file)

    # 参数
    tc.use_proxy = get_config(parser, 'use_proxy', True)
    if tc.use_proxy:
        tc.proxy_type = python_socks.ProxyType.SOCKS5
        tc.proxy_ip = get_config(parser, 'proxy_ip', '127.0.0.1')
        tc.proxy_port = get_config(parser, 'proxy_port', 7890)
        tc.proxy = (tc.proxy_type, tc.proxy_ip, tc.proxy_port)

    tc.api_id = get_config(parser, 'api_id', 0)
    tc.api_hash = get_config(parser, 'api_hash', '0')
    tc.session_name = get_config(parser, 'session_name', 'tg_session')
    tc.src_dialog_ids = get_config(parser, 'src_dialog_ids', [])
    tc.dest_dialog_ids = get_config(parser, 'dest_dialog_ids', [])
    tc.iter_val = get_config(parser, 'iter_val', 1000)
    return tc


def create_example_config_file():
    with open('tg.ini', mode='w') as f:
        f.write('''
                [default]
                api_id=1
                api_hash=1
                src_dialog_ids=-1
                dest_dialog_ids=1
                use_proxy=false
                ''')


def get_opt():
    return getopt.getopt(sys.argv[1:], "c12")


def main():
    opts = get_opt()
    for opt, arg in opts:
        if opt == '-c':
            create_example_config_file()
            return
        if opt == '-1':
            collector = new_telegram_collector()
            collector.send_current_message_src_to_dest()
            return
        if opt == '-2':
            collector = new_telegram_collector()
            collector.send_history_message_src_to_dest()
            return

    print("error")
