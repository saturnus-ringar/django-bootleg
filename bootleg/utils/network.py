import ipaddress


def ip_is_in_range(ip, start_ip, end_ip):
    try:
        match_ip = ipaddress.ip_address(ip)
        start_ip_address = ipaddress.ip_address(start_ip)
        end_ip_address = ipaddress.ip_address(end_ip)

        if match_ip >= start_ip_address and match_ip <= end_ip_address:
            return True

        return False

    except TypeError:
        return False
