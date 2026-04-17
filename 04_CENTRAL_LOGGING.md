# DEV2IL: Observability

## Logging

### Collecting Logs in a Central Place

In order to be able to analyze logs, you need to collect the logs of all your services in a central place and
make them searchable. We use [Loki](https://grafana.com/oss/loki/) to store logs and [Grafana](https://grafana.com/)
to query and visualize them.

**Loki** is a log aggregation system designed to store and index logs efficiently. Think of it as a database 
specifically built for logs. It collects log messages from all your services and stores them in one place, 
making it easy to search through logs from multiple services at once.

**Grafana** is a visualization and analytics platform. It provides a user-friendly web interface where you can 
search, filter, and visualize your logs. While Loki stores the logs, Grafana helps you explore and understand them.

![logging_config.yaml](logging-loki.png)

The image above shows the updated logging configuration. Notice that we now have **two handlers**:
1. **Console handler**: Continues to display logs in your terminal (like before)
2. **Loki handler**: A new handler that sends the same log records to Loki over the network

When a log message is created, both handlers receive it. This means your logs appear both in your terminal and in Loki.

- Download the file [logging_config_loki.yaml](https://github.com/peterrietzler/ais-dev2il-smoothie-shop/blob/logging/logging_config_loki.yaml)
and store it in the root directory of the project. This is the same as the previous logging configuration, but with an additional handler that sends logs to Loki.
- Download the file [docker-compose.yml](https://github.com/peterrietzler/ais-dev2il-smoothie-shop/blob/logging/docker-compose.yml)
and store it in the root directory of the project. Make sure you understand it!

> **📄 What does the docker-compose.yml do?**
>
> The file starts two services with a single command:
>
> - **Loki** — the log storage backend. Your app sends logs here.
> - **Grafana** — the web UI you use to explore those logs.
>
> ```yaml
> services:
>   loki:
>     image: grafana/loki:2.9.3   # pre-built Docker image from Docker Hub
>     ports:
>       - "3100:3100"             # make port 3100 reachable from your laptop
>     ...
>
>   grafana:
>     image: grafana/grafana:10.2.3
>     ports:
>       - "3000:3000"             # Grafana UI → open http://localhost:3000
>     depends_on:
>       - loki                    # wait for Loki to start first
> ```
>
> **🔌 What is a network — and why do we need one?**
>
> Each Docker container is like a **separate mini-computer**. By default they cannot talk to each other.
> A Docker network connects them, like plugging them together with a network cable (or connecting them to the same switch).
>
> ```yaml
> networks:
>   observability:
>     driver: bridge   # a virtual "switch" that connects the containers
> ```
>
> Both `loki` and `grafana` are attached to the `observability` network.
> Inside this network, containers can reach each other **by their service name**.
> That is why later you set Grafana's Loki URL to `http://loki:3100` — `loki` is simply the service name, resolved automatically within the network.
>
> Without the shared network, Grafana could not reach Loki at all.

- Start Grafana and Loki by running `docker-compose up -d`.
- Stop the kitchen service and start it again using 
`uv run uvicorn kitchen_service:app --port 8001 --reload --log-config logging_config_loki.yaml`.

Your logs are now sent to Loki in addition to the console output. You can now use Grafana to explore the logs.
1. Open Grafana at http://localhost:3000
1. Navigate to _Menu > Connections > Add new connection_ 
1. Search for the _Loki_ data source and add it
1. Set the connection URL to: `http://loki:3100`
1. Click _Save & Test_
1. Navigate to _Menu > Explore_ and make sure that the _Loki_ data source is selected

You can either use the _Builder_  or _Code_ view to query your logs. Start off with the 
builder, but later on get familiar with the code view as well, as this is the quickest and most 
powerful way to explore logs. You can first build a query and then switch to the _Code_ 
view to see the query that was generated. Learn more about Loki queries in the 
[LogQL documentation](https://grafana.com/docs/loki/latest/query/).

- Find all logs created in the last 5 minutes from the kitchen service that contain the word _cook_ 
- Find all 503 HTTP errors across services that occurred in the last 5 minutes

### 🚀 Level Up

#### Challenge 1: Use Structured Information in Logs

Adding structured information (extra attributes) to your log messages makes them much more 
powerful. Instead of just text, you can attach key-value pairs like `num_cooks=3` or `flavor="Mango"`. This structured 
data allows you to filter and query logs more precisely in Grafana/Loki. For example, you can find all logs where 
`num_cooks < 2` or all smoothie orders for a specific flavor.

Attach more information, such as the number of cooks and the number of busy cooks in the kitchen service log outputs. 
Use extra attributes with log messages.

**Example:** Instead of `logger.info(f"Processing order for {order.flavor}")`, use:
```python
logger.info("Processing order", extra={"tags": {"flavor": order.flavor, "num_cooks": str(NUM_COOKS)}})
```

Then inspect the logs in Grafana/Loki and search for them. You can filter by these attributes using LogQL queries like 
`{logger="kitchen_service"} | flavor="Mango"` to find all logs for Mango smoothies.

You can always find more information on how to use loggers by contacting the 
[Python logging documentation](https://docs.python.org/3/library/logging.html#logging.Logger.debug)).

#### Challenge 2: Store Logs in a File

Logging to files gives you persistence - even if your application crashes or restarts, the logs 
remain on disk for later inspection.

Let's modify the `logging_config_loki.yaml` file to add a third handler that writes logs to a file.

**Step 1:** Add a file handler to the `handlers` section:

```yaml
handlers:
  console:
    # ... existing console handler ...
  
  loki:
    # ... existing loki handler ...
  
  file:
    class: logging.FileHandler
    formatter: console
    filename: logs/smoothie-shop.log
```

**Step 2:** Add the `file` handler to the root logger's handler list:

```yaml
root:
  handlers:
    - console
    - loki
    - file  # Add this line
```

**Step 3:** Create the `logs/` directory and restart your service:

```bash
mkdir -p logs
uv run uvicorn kitchen_service:app --port 8001 --reload --log-config logging_config_loki.yaml
```

**Test it:** Generate some traffic and check that `logs/smoothie-shop.log` contains your log messages:

```bash
cat logs/smoothie-shop.log
``` 

#### Pro Tip: Use a Log Collector for Reliable Log Shipping

Sending log messages directly from your application to Loki has several problems:
- If the network is down or your application crashes, logs are lost
- If Loki is slow when accepting logs, your application will be slow as well
- Your application becomes tightly coupled to your logging infrastructure

**The better approach:** Log to standard output (stdout) or files, and use a separate log collector process that reads 
those logs and forwards them to your logging system. This decouples your application from the logging infrastructure and 
ensures logs are preserved even if the network fails.

**Real-world cloud setups:** In production cloud environments (AWS, Azure, GCP), there are typically pre-configured tools 
that automatically collect JSON log lines from stdout and send them to cloud-specific logging services (like Google Cloud Logging). 
You simply write logs to stdout in JSON format, and the infrastructure handles the rest.

**Open source option:** The [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/) is an open source tool 
that can collect logs from files or stdout and forward them to various destinations including Loki. It's vendor-neutral 
and widely used.

💡 **Note:** Setting up a log collector is beyond the scope of this lecture. This is provided 
as informational background to show you how logging works in real production systems.