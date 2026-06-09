#!/usr/bin/env python3

import argparse
import requests


def check_usage(api_key: str, usage_url: str) -> dict:
    resp = requests.get(
        usage_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )

    if resp.status_code != 200:
        raise RuntimeError(
            f"Usage request failed: HTTP {resp.status_code}\n{resp.text}"
        )

    return resp.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-key",
        help="Your DeepSeek student API key",
    )
    parser.add_argument(
        "--usage-url",
        default="http://81.70.208.221:4001/usage",
        help="Usage checker endpoint",
    )
    args = parser.parse_args()
    if not args.api_key:
        import os
        args.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not args.api_key:
            print("Error: API key is required. Provide it via --api-key or DEEPSEEK_API_KEY environment variable.")
            return

    data = check_usage(args.api_key, args.usage_url)

    print("DeepSeek API usage")
    print("-----------------")
    print(f"Spend:      ${data.get('spend_usd', 0):.6f}")
    print(f"Budget:     ${data.get('max_budget_usd', 0):.6f}")

    remaining = data.get("remaining_usd")
    if remaining is not None:
        print(f"Remaining:  ${remaining:.6f}")

    usage_pct = data.get("usage_pct")
    if usage_pct is not None:
        print(f"Used:       {usage_pct:.2f}%")

    print(f"Models:     {data.get('models')}")
    print(f"Student ID: {data.get('key_alias')}")
    print(f"Blocked:    {data.get('blocked')}")


if __name__ == "__main__":
    main()