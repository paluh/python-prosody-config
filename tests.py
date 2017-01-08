import unittest
from textwrap import dedent
from prosody_config import parse, ProsodyConfig, VirtualHost

class ParserTestCase(unittest.TestCase):

    def test_parse_simple_assignements(self):
        config = dedent("""
        --Important for systemd
        -- daemonize is important for systemd. if you set this to false the systemd startup will freeze.
        daemonize = true
        pidfile = "/run/prosody/prosody.pid"

        -- Enable use of libevent for better performance under high load
        -- For more information see: https://prosody.im/doc/libevent
        use_libevent = true
        allow_registration = false
        """)

        instance = parse(config)
        self.assertEqual(instance,
                         ProsodyConfig(daemonize=True,
                                       pidfile='/run/prosody/prosody.pid',
                                       use_libevent=True,
                                       allow_registration=False))

    def test_parse_config_with_virtual_host(self):
        self.assertEqual(parse('VirtualHost "example.com"'),
                         ProsodyConfig(virtual_hosts={'example.com': VirtualHost('example.com')}))

if __name__ == '__main__':
    unittest.main()
