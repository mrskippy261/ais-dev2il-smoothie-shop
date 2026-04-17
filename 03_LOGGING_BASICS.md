# DEV2IL: Observability

## Logging

### Providing More Insights Through Log Outputs

Before we are going to start changing our services, let's get familiar with the code. 
Have a closer look at `kitchen_service.py` and `order_service.py`. Discuss these questions with your partner:
- How do the services work? 
- How are are they connected to each other? 
- Why does the kitchen sometimes returns a 503 error?

We are now providing more insights into the smoothie shop by adding logging to the application. 

Python's [logging module](https://docs.python.org/3/howto/logging.html) provides a flexible way 
to record what your application is doing. A **logger** is an object that you use to write log messages. You can call 
methods like `logger.info()`, `logger.debug()`, `logger.error()` to record messages at different severity levels. 

Logging is **configurable**: you can decide where logs go (console, file, network), how they're formatted (timestamps, 
colors), and which messages to show (e.g., only `INFO` and above, or include `DEBUG` for troubleshooting).

Here are some hints on which logging level to choose from 
the [Python logging HOWTO](https://docs.python.org/3/howto/logging.html#when-to-use-logging): 

| Level     | When it’s used                                                                                       |
|-----------|------------------------------------------------------------------------------------------------------|
| DEBUG     | Detailed information, typically of interest only when diagnosing problems.                           |
| INFO      | Confirmation that things are working as expected.                                                    |
| WARNING   | An indication that something unexpected happened, or indicative of some problem in the near future. (e.g. ‘disk space low’). The software is still working as expected. |
| ERROR     | Due to a more serious problem, the software has not been able to perform some function.              |
| CRITICAL  | A serious error, indicating that the program itself may be unable to continue running.               |

Let's get started to modify `kitchen_service.py`.

After the existing imports create a logger for the module
```python
import logging
logger = logging.getLogger(__name__)
``` 

💡 Using `logging.getLogger(__name__)` is a best practice. It creates a logger named after your module 
(e.g., `kitchen_service`). This makes it easy to identify where log messages come from and allows you 
to configure logging levels differently for each Python module.

Add these log messages to the `prepare_smoothie` function. Find the right places to add them on your own. 
```python
logger.info(f"Received order to prepare a smoothie with flavor {order.flavor}")
logger.debug(f"Waiting for a cook to become available")
logger.error(f"Can't process the order: {NUM_COOKS} cooks are currently busy. Consider increasing NUM_COOKS.")
logger.info(f"Smoothie with flavor {order.flavor} prepared")
```

**Configuring Logging:** To control how logging works, we need to configure it. Python's logging system has three main parts:
- **Logger**: Creates log messages (what you use in your code with `logger.info()`, `logger.debug()`, etc.)
- **Handler**: Decides where log messages go (e.g., console, file, network)
- **Formatter**: Defines how log messages look like (e.g., add timestamp, log level, message)

The `logging_config.yaml` file is a YAML format that Python's logging module understands. It lets you configure 
loggers, handlers, and formatters without changing your code.

![logging_config.yaml](logging-config.png)

We want all our logging messages to contain the logging level, a timestamp when the message was logged and 
the message itself. In addition, we want to be able to define the logging level for each logger individually. 

Download the file [logging_config.yaml](https://github.com/peterrietzler/ais-dev2il-smoothie-shop/blob/logging/logging_config.yaml)
and store it in the root directory of the project.

Stop the kitchen service and start it again using 
`uv run uvicorn kitchen_service:app --port 8001 --reload --log-config logging_config.yaml`.  

🎉 You are now able to get more insights into what your application is actually doing and
you should thus be able to figure out what is going wrong and how to fix it.

💡 Make sure that you understand `logging_config.yaml` and how it works before you continue. Match it 
to the structural picture from above.

### 🚀 Level Up

#### Challenge 1: Log the Service Startup

Add a log message that is written when the kitchen service starts. Include helpful configuration information such as
the service name and the value of `NUM_COOKS`.

This helps you understand that logs are not only useful while handling requests, but also when checking how a service
was started.

#### Challenge 2: Introduce Logging in the Order Service

Introduce a logger in `order_service.py` and add meaningful log messages for the most important steps of handling an 
order. For example, you could log when an order is received, when the order service calls the kitchen service, and 
whether the smoothie order was completed successfully or failed.

Choose log levels that make sense for the different messages. Keep the logging simple and focus on messages that help 
you understand the flow of a single order.

#### Challenge 3: Experiment with Log Levels

Change the log levels in `logging_config.yaml` and compare what you can see with `INFO` and `DEBUG`. Remember to 
restart the kitchen service after you changed the logging configuration.

Try to answer these questions:
- Which messages do you only see with `DEBUG`?
- Which messages are useful during normal operation?
- Which messages are mainly helpful for troubleshooting?
