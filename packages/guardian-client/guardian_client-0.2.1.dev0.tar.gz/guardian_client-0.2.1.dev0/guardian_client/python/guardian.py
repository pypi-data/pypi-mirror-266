###############################################################################################
# Guardian API Client
# Submits a model URI to the Guardian API for scanning and checking scan status.
#
# Usage:
# python guardian.py <base_url> <model_uri> [--block-on-errors] [--log-level <log-level>] | echo ?
#
# Arguments:
#  base_url: The base URL of the Guardian API.
#  model_uri: The model URI to scan.
# --block-on-errors: Block on scan errors. Default is False.
# --report-only: Report only, do not evaluate scan results. Default is False.
#  --log-level: The log level. Default is "info".
# --silent: Do not print anything to stdout. Default is False.
# --poll-interval-secs: The interval in seconds to poll for scan status. Default is 5.
#
# Exit Codes:
#  0 - Scan successful and no issues > Guardian's threshold
#  1 - Scan successful but with issues >= Guardian's threshold
#  2 - Scan failed (for any other reason)
#
# Example:
#  python guardian.py https://api.guardian.example.com/guardian s3://bucket/key || echo $?
###############################################################################################


import json
import sys

from guardian_client.python.api import GuardianAPIClient

import click

LOW, MEDIUM, HIGH, CRITICAL = "low", "medium", "high", "critical"
CRITICAL, ERROR, INFO, DEBUG = "critical", "error", "info", "debug"


@click.command()
@click.argument("base_url", required=True)
@click.argument("model_uri", required=True)
@click.option(
    "--block-on-scan-errors",
    is_flag=True,
    help="Block if the scanning process failed on an incomplete scan",
)
@click.option(
    "--report-only",
    is_flag=True,
    help="Generate a JSON report only without evaluating scan results",
)
@click.option("--silent", is_flag=True, help="Do not print anything to stdout")
@click.option(
    "--log-level",
    default=INFO,
    type=str,
    required=False,
    help="Logging level if not silent (critical, error, info, debug)",
)
@click.option(
    "--poll-interval-secs",
    default=5,
    type=int,
    required=False,
    help="Logging level if not silent (critical, error, info, debug)",
)
def cli(
    base_url: str,
    model_uri: str,
    block_on_scan_errors: bool = True,
    report_only: bool = False,
    silent: bool = True,
    log_level: str = INFO,
    poll_interval_secs: int = 5,
) -> None:
    try:
        guardian = GuardianAPIClient(
            base_url, log_level=log_level if not silent else CRITICAL
        )

        response = guardian.scan(model_uri, poll_interval_secs=poll_interval_secs)

        http_status_code = response.get("http_status_code")
        if not http_status_code or http_status_code != 200:
            click.echo(
                f"Error: Scan failed with status code: {http_status_code}, message: {response.get('error')}",
                err=True,
            )
            sys.exit(2)

        if not silent:
            click.echo(json.dumps(response["scan_status_json"], indent=4))

        if report_only:
            sys.exit(0)

        if (
            response["scan_status_json"]["aggregate_eval_outcome"] == "ERROR"
            and block_on_scan_errors
        ):
            click.echo(
                f"Error: Scan failed with code: {response['scan_status_json']['error_code']}, message: {response['scan_status_json']['error_message']}",
                err=True,
            )
            sys.exit(2)

        if response["scan_status_json"]["aggregate_eval_outcome"] == "FAIL":
            click.echo(
                f"Error: Scan failed because it failed your organization's security policies",
                err=True,
            )
            sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: Invalid arguments {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"Error: Scan submission failed: {e}", err=True)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    cli()
