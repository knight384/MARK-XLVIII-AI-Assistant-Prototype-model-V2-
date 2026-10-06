from enum import Enum, auto
from typing import Dict, List, Optional, Protocol, runtime_checkable
import logging

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    ERROR = auto()

@runtime_checkable
class Service(Protocol):
    """Protocol for a runtime service."""
    
    @property
    def name(self) -> str:
        ...
        
    async def start(self) -> None:
        ...
        
    async def stop(self) -> None:
        ...
        
    def status(self) -> ServiceStatus:
        ...

class ServiceRegistry:
    """Manages lifecycle of all daemon services."""
    def __init__(self):
        self._services: Dict[str, Service] = {}
        self._status: Dict[str, ServiceStatus] = {}
        self._errors: Dict[str, Optional[str]] = {}
        
    def register(self, service: Service) -> None:
        if service.name in self._services:
            raise ValueError(f"Service '{service.name}' is already registered")
        self._services[service.name] = service
        self._status[service.name] = ServiceStatus.STOPPED
        self._errors[service.name] = None
        logger.info(f"[ServiceRegistry] Registered service: {service.name}")
        
    async def start_all(self) -> None:
        logger.info("[ServiceRegistry] Starting all services...")
        for name in self._services:
            await self.start_service(name)
        logger.info("[ServiceRegistry] All services started")
        
    async def stop_all(self) -> None:
        logger.info("[ServiceRegistry] Stopping all services...")
        for name in reversed(list(self._services.keys())):
            await self.stop_service(name)
        logger.info("[ServiceRegistry] All services stopped")
        
    async def start_service(self, name: str) -> None:
        if name not in self._services:
            raise ValueError(f"Service '{name}' not found")
            
        if self._status[name] == ServiceStatus.RUNNING:
            logger.info(f"[ServiceRegistry] Service '{name}' is already running")
            return
            
        try:
            self._status[name] = ServiceStatus.STARTING
            logger.info(f"[ServiceRegistry] Starting {name}...")
            
            await self._services[name].start()
            
            self._status[name] = ServiceStatus.RUNNING
            self._errors[name] = None
            logger.info(f"[ServiceRegistry] ✓ {name} started")
        except Exception as e:
            self._status[name] = ServiceStatus.ERROR
            self._errors[name] = str(e)
            logger.error(f"[ServiceRegistry] ✗ Failed to start {name}: {e}")
            raise
            
    async def stop_service(self, name: str) -> None:
        if name not in self._services:
            raise ValueError(f"Service '{name}' not found")
            
        if self._status[name] == ServiceStatus.STOPPED:
            logger.info(f"[ServiceRegistry] Service '{name}' is already stopped")
            return
            
        try:
            self._status[name] = ServiceStatus.STOPPING
            logger.info(f"[ServiceRegistry] Stopping {name}...")
            
            await self._services[name].stop()
            
            self._status[name] = ServiceStatus.STOPPED
            self._errors[name] = None
            logger.info(f"[ServiceRegistry] ✓ {name} stopped")
        except Exception as e:
            self._status[name] = ServiceStatus.ERROR
            self._errors[name] = str(e)
            logger.error(f"[ServiceRegistry] ✗ Failed to stop {name}: {e}")
            raise

    def get_status(self) -> Dict[str, ServiceStatus]:
        return dict(self._status)
        
    def get(self, name: str) -> Optional[Service]:
        return self._services.get(name)
        
    def list(self) -> List[str]:
        return list(self._services.keys())
        
    def has(self, name: str) -> bool:
        return name in self._services
import uvicorn
import asyncio
from core.runtime.services import Service, ServiceStatus

class ApiService:
    @property
    def name(self) -> str:
        return "ApiService"
        
    def __init__(self, port=8000):
        self.port = port
        self._server = None
        self._task = None
        self._status = ServiceStatus.STOPPED

    async def start(self) -> None:
        self._status = ServiceStatus.STARTING
        config = uvicorn.Config("core.runtime.api:app", host="127.0.0.1", port=self.port, log_level="info")
        self._server = uvicorn.Server(config)
        
        # Override uvicorn's signal handlers so it doesn't kill the whole process
        self._task = asyncio.create_task(self._server.serve())
        self._status = ServiceStatus.RUNNING
        
    async def stop(self) -> None:
        self._status = ServiceStatus.STOPPING
        if self._server:
            self._server.should_exit = True
            if self._task:
                await self._task
        self._status = ServiceStatus.STOPPED
        
    def status(self) -> ServiceStatus:
        return self._status

from core.workflows.engine import WorkflowEngine
from core.workflows.store import WorkflowStore
from core.workflows.events import EventBus
from pathlib import Path
import asyncio

class WorkflowService:
    @property
    def name(self) -> str:
        return "WorkflowService"
        
    def __init__(self, db_path: Path):
        self.store = WorkflowStore(db_path)
        self.event_bus = EventBus()
        self.engine = WorkflowEngine(self.store, self.event_bus)
        self._status = ServiceStatus.STOPPED

    async def start(self) -> None:
        self._status = ServiceStatus.STARTING
        self.event_bus.start()
        await self.engine.start()
        self._status = ServiceStatus.RUNNING
        
    async def stop(self) -> None:
        self._status = ServiceStatus.STOPPING
        await self.engine.stop()
        await self.event_bus.stop()
        self._status = ServiceStatus.STOPPED
        
    def status(self) -> ServiceStatus:
        return self._status
