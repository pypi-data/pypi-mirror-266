import requests
import click
from collections import Counter


def get_ip():
    try:
        response = requests.get('https://checkip.amazonaws.com/')
        ip = response.text.strip()
        return ip
    except requests.RequestException as e:
        print(f"request error: {e}")
        return None


@click.command()
@click.argument('count', default=1, type=int)
def main(count):
    """Simple program that gets IP addresses a specified number of times."""
    ip_addresses = []

    for _ in range(count):
        ip = get_ip()
        if ip:
            ip_addresses.append(ip)

    ip_count = Counter(ip_addresses)
    unique_ips = len(ip_count)

    click.echo(f"Number of IP POOL: {unique_ips}")
    for ip, times in ip_count.items():
        if ip is not None:
            click.echo(f"IP address count: {ip}  {times}")
        else:
            click.echo(f"Failed requests count: {times}")

