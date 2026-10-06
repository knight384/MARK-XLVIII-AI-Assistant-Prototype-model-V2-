import asyncio
import logging
import time
from typing import Callable, Coroutine, Dict, List, Optional
from core.workflows.models import WorkflowEvent, EventType
from core.observability import registry

logger = logging.getLogger(__name__)

EventCallback = Callable[[WorkflowEvent], Coroutine[None, None, None]]

class EventBus:
    """Async event bus with bounded queues, exception isolation, and backpressure."""
    
    def __init__(self, max_queue_size: int = 100, put_timeout: float = 2.0):
        # Maps event_type to list of subscriber queues
        self._subscribers: Dict[EventType, List[asyncio.Queue]] = {}
        self._all_events_subscribers: List[asyncio.Queue] = []
        self._tasks: List[asyncio.Task] = []
        self._max_queue_size = max_queue_size
        self._put_timeout = put_timeout
        self._running = False
        
    def start(self):
        self._running = True
        logger.info("[EventBus] Started.")
        
    async def stop(self):
        self._running = False
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        self._subscribers.clear()
        self._all_events_subscribers.clear()
        logger.info("[EventBus] Stopped.")

    def subscribe(self, callback: EventCallback, event_type: Optional[EventType] = None) -> asyncio.Queue:
        """Subscribe to events. Returns the bounded queue created for this subscriber."""
        queue = asyncio.Queue(maxsize=self._max_queue_size)
        if event_type:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(queue)
        else:
            self._all_events_subscribers.append(queue)
            
        # Start a worker task for this subscriber
        task = asyncio.create_task(self._subscriber_worker(queue, callback))
        self._tasks.append(task)
        asyncio.create_task(registry.set_gauge("eventbus_subscriber_count", len(self._tasks)))
        return queue
        
    async def _subscriber_worker(self, queue: asyncio.Queue, callback: EventCallback):
        while self._running:
            try:
                event = await queue.get()
                try:
                    start_time = time.time()
                    await callback(event)
                    asyncio.create_task(registry.observe("event_handler_duration", time.time() - start_time))
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"[EventBus] Subscriber error: {e}", exc_info=True)
                    asyncio.create_task(registry.inc("event_subscriber_errors"))
                finally:
                    queue.task_done()
            except asyncio.CancelledError:
                break

    async def publish(self, event: WorkflowEvent):
        """Publish an event to all relevant subscribers."""
        if not self._running:
            return
            
        targets = self._all_events_subscribers.copy()
        if event.event_type in self._subscribers:
            targets.extend(self._subscribers[event.event_type])
            
        asyncio.create_task(registry.inc("eventbus_events_published"))
        for queue in targets:
            try:
                # Apply backpressure but don't block indefinitely
                await asyncio.wait_for(queue.put(event), timeout=self._put_timeout)
            except asyncio.TimeoutError:
                asyncio.create_task(registry.inc("eventbus_events_dropped"))
                logger.warning(f"[EventBus] Subscriber queue full. Dropped event {event.event_id} for one subscriber.")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"[EventBus] Error publishing to queue: {e}")
