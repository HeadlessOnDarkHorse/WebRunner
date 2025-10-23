# How to Run the Web Automation Framework with Podman

This guide provides the instructions to build and run the web automation framework using Podman. The containerized setup ensures a consistent and hassle-free environment.

## Step 1: Build the Podman Image

Navigate to the root directory of this repository in your terminal and run the following command to build the container image. This will install all dependencies and package the application.

```bash
podman build -t web-scanner .
```

This command will create a new Podman image tagged as `web-scanner`. This step only needs to be done once, or whenever you make changes to the source code.

## Step 2: Run the Scanner

To run the scanner, use the following command. The `-it` flag runs the container in interactive mode, which is necessary to allow the script to prompt you for input.

```bash
podman run -it --rm web-scanner
```

The container will start, and the `run_scanner.sh` script will prompt you for the following information:
- The URL to scan
- The crawl depth
- Whether to run the AODA scan
- Your Azure username and password

After you provide the inputs, the scan will begin. The reports (`object_repository.json`, `aoda_report.json`, etc.) will be generated *inside* the container. If you need to access these reports, you will need to mount a volume (e.g., `podman run -it --rm -v ./reports:/app/reports web-scanner`).

---
*This container is designed to be self-contained. All dependencies are included in the image.*
