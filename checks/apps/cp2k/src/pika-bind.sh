#!/bin/bash

# This is a simplified version of pika-bind shipped with pika. It's provided
# here to avoid depending on a CP2K uenv always having pika-bind available, or
# having to detect if pika-bind is available.

export PIKA_PROCESS_MASK=$(hwloc-bind --get --taskset)

$@
