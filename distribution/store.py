"""Store offline-only entry point; policy is code, never user configuration."""

from core.offline_policy import enforce

enforce()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--offline-network-report")
    parser.add_argument("--probe-url", default="http://127.0.0.1:9/forbidden")
    args, _ = parser.parse_known_args()
    if args.offline_network_report:
        from distribution.store_probe import run

        raise SystemExit(run(args.offline_network_report, args.probe_url))
    from distribution.poc import main

    raise SystemExit(main())
