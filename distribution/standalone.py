"""Standalone entry point: offline policy is compiled in, independent of Store identity."""

from core.offline_policy import enforce

enforce()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--binding-report")
    parser.add_argument("--offline-network-report")
    parser.add_argument("--probe-url", default="http://127.0.0.1:9/forbidden")
    args, _ = parser.parse_known_args()
    if args.binding_report:
        from distribution.standalone_support import binding_report

        binding_report(args.binding_report)
        raise SystemExit(0)
    if args.offline_network_report:
        from distribution.store_probe import run

        raise SystemExit(run(args.offline_network_report, args.probe_url))
    from distribution.poc import main

    raise SystemExit(main())
