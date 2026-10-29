# HAR API Analyzer

A small Python tool that reads a HAR file exported from Chrome DevTools and turns it into a readable API activity report. It uses only the Python standard library.

## What it does

- Parses the HAR log and lists every request (timestamp, method, endpoint, status, duration)
- Saves everything to a CSV file you can open in Excel
- Prints a summary per endpoint: request count, successes, failures, average and max time
- Lists errors (4xx / 5xx) separately
- Shows the 5 slowest requests
- Strips query strings and never writes cookies, headers, tokens or request bodies to the report

## Requirements

- Python 3.8+
- No third-party packages

## How to use

1. Open Chrome DevTools (F12) on your own browser session and go to the **Network** tab.
2. Turn on **Preserve log**, use the site normally, then right-click the request list and choose **Save all as HAR (sanitized)**.
3. Save the file as `har/activity.har` next to `monitor.py`.
4. Run:

   ```
   py monitor.py
   ```

5. Find the CSV report in `reports/api_activity.csv`.

## Project layout

```
.
├── monitor.py
├── har/          # your exported HAR files (not committed)
└── reports/      # generated CSV reports (not committed)
```

## Privacy

HAR files can contain session tokens and personal data. The `har/` and `reports/` folders are listed in `.gitignore`. Never upload or share a HAR file.

## Limitations

- It analyzes an exported log; it is not a live monitor.
- It only shows traffic from the browser session that produced the HAR file.

## License

MIT
