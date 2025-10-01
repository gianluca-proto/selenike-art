import unittest
import sys
import os
sys.path.append(os.path.abspath('.'))
from routes import security

class TestCountsFromMap(unittest.TestCase):
    def test_ipv4_port_dedup_prefers_latest(self):
        m = {
            '1.2.3.4': {'device': 'mobile', 'counts': {'mobile': 2}, 'last_seen': '2025-01-01T00:00:00Z'},
            '1.2.3.4:5000': {'device': 'desktop', 'counts': {'desktop': 1}, 'last_seen': '2025-01-02T00:00:00Z'},
        }
        counts = security._counts_from_map(m)
        # normalized IP 1.2.3.4 should be counted once and pick the entry with later last_seen (desktop)
        self.assertEqual(counts['desktop'], 1)
        self.assertEqual(counts['mobile'], 0)

    def test_ipv6_brackets_and_plain_dedup_prefers_latest(self):
        m = {
            '[::1]': {'device': 'desktop', 'counts': {'desktop': 1}, 'last_seen': '2025-01-03T00:00:00Z'},
            '::1': {'device': 'mobile', 'counts': {'mobile': 3}, 'last_seen': '2025-01-04T00:00:00Z'},
        }
        counts = security._counts_from_map(m)
        # normalized ::1 should be counted once and pick the later entry (mobile)
        self.assertEqual(counts['mobile'], 1)
        self.assertEqual(counts['desktop'], 0)

    def test_mixed_multiple_ips(self):
        m = {
            '10.0.0.1': {'device': 'desktop', 'counts': {'desktop': 1}, 'last_seen': '2025-01-01T00:00:00Z'},
            '10.0.0.2:8080': {'device': 'mobile', 'counts': {'mobile': 2}, 'last_seen': '2025-01-02T00:00:00Z'},
            '[2001:db8::1]': {'device': 'tablet', 'counts': {'tablet': 1}, 'last_seen': '2025-01-03T00:00:00Z'},
            '2001:db8::1': {'device': 'tablet', 'counts': {'tablet': 2}, 'last_seen': '2025-01-04T00:00:00Z'},
            'malformed': {'device': 'desktop', 'counts': {'desktop': 1}, 'last_seen': '2025-01-05T00:00:00Z'},
        }
        counts = security._counts_from_map(m)
        # Expect normalized unique IPs: 10.0.0.1 (desktop), 10.0.0.2 (mobile), 2001:db8::1 (tablet)
        self.assertEqual(counts['desktop'], 1)
        self.assertEqual(counts['mobile'], 1)
        self.assertEqual(counts['tablet'], 1)

    def test_counts_from_lines_unique_ips_desktop(self):
        from routes.security import _counts_from_lines_unique_ips
        lines = [
            '2025-09-30 16:22:56,766 - 10.1.34.91 - 200 OK - /antro-1986/ - Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
            '2025-09-30 16:23:01,806 - 10.1.34.91 - 200 OK - /antro-1986/security-dashboard - Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
            '2025-09-30 16:23:10,731 - 10.1.34.91 - 200 OK - /antro-1986/security-dashboard - Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
        ]
        counts = _counts_from_lines_unique_ips(lines)
        assert counts['desktop'] == 1, f"Conteggio desktop errato: {counts['desktop']}"


if __name__ == '__main__':
    unittest.main()
