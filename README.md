# exam-guard

See:

Makefile

# Features:

## Prevent data loss

To prevent message loss, the data from api endpoint is sent to a RabbitMQ queue with a retry strategy. There are 5 retries available; after these attempts, the messages are moved to the error queue.

API Enpoint example:

http://localhost:8000/exam-guard/monitor-data/stream

src/exam_guard/adapters/api/http/monitor_data.py#add_monitor_data_stream

RabbitMQ confiration and handler:

src/exam_guard/adapters/api/http/router.py

To test it, execute:

```
python fixtures/load_monitor_data_http.py
```

To observe what's happening, open http://localhost:15672/#/queues in your web browser.


# TODO:
- Finish Monitoring UseCases (Add rules)
  - Check monitor time units
- Do the alerts using Pandas
- Add comman to requeue error messages
