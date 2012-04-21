This script parses input from stdin and sends it to RabbitMQ (AMQP) message
queues based on regular expressions in a config file. It can be used to tail
logs and send some log lines to a message queue for notification or other
processing.

Example config file:


```json
{
    "routes": [
        {
            "regex": "(?i)^error on server (.*) user (.*)",
            "dests": [
                {
                    "server": "amqp://localhost/",
                    "exchange": "test", 
                    "routing_keys": [
                        "key1", 
                        "key2"
                    ]
                }
            ]
        }
    ]
}

```

Each route has a regular expression and one or more AMQP destinations. An
AMQP destination is an AMQP URI, an exchange name, and routing keys. Any
lines from stdin matching the regular expression will be sent to all
destinations. Any captured groups in the regular expression will be sent
as routing keys in addition to the routing keys defined in the destination.

Example usage:

```sh
tail -F /var/log/some.log | python cat2queue.py -c cat2queue_config.json

ssh somewhere tail -F /var/log/some.log | pv | python cat2queue.py -c cat2queue_config.json
```

The MIT License

Copyright (c) 2012 Matthew M. Boedicker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
