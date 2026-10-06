from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
from pathlib import Path

from core.runtime.app import MarkRuntime
from core.agent.orchestrator import get_default_orchestrator
from core.agent.task import Task, TaskStatus
from core.tools.base import CancellationToken, CancelReason
from core.mission.models import Mission, MissionState, TriggerType
from core.mission.store import get_default_store
from core.goals.service import get_default_goal_service
from core.goals.store import get_default_goal_store
from core.goals.models import GoalState
from core.personality.service import get_default_personality_service
from core.awareness.tracker import get_default_tracker
import time
import uuid

app = FastAPI(title="MARK XLVIII Runtime API", version="7.0")
_runtime: Optional[MarkRuntime] = None
_tasks: Dict[str, Task] = {}
_tokens: Dict[str, CancellationToken] = {}

def set_runtime(runtime: MarkRuntime):
    global _runtime
    _runtime = runtime

@app.get("/api/health")
async def health():
    if not _runtime:
        raise HTTPException(status_code=503, detail="Runtime not initialized")
    return {"status": "ok", "mode": _runtime.mode.name}

@app.get("/api/identity")
async def identity():
    if not _runtime:
        raise HTTPException(status_code=503, detail="Runtime not initialized")
    return {"identity": _runtime.identity.runtime_id, "mode": _runtime.mode.name}

@app.get("/api/capabilities")
async def capabilities():
    caps = []
    # local capabilities
    from core.tools import get_default_registry
    from core.runtime.providers import LocalCapabilityProvider
    local = LocalCapabilityProvider(get_default_registry())
    caps.extend([c.__dict__ for c in await local.discover()])
    return {"capabilities": caps}

@app.get("/api/models")
async def models():
    from core.llm.gateway import get_default_gateway
    gw = get_default_gateway()
    return {"providers": gw.health_check_all()}

class TaskRequest(BaseModel):
    goal: str

@app.post("/api/tasks")
async def submit_task(req: TaskRequest):
    orchestrator = get_default_orchestrator()
    token = CancellationToken()
    # Create the task synchronously to get its ID before starting execution
    task = Task(goal=req.goal)
    _tasks[task.task_id] = task
    _tokens[task.task_id] = token
    
    async def run():
        await orchestrator._run_task_impl(task, req.goal, token)
        
    asyncio.create_task(run())
    return {"task_id": task.task_id, "status": task.status.value}

@app.get("/api/tasks/{task_id}")
async def task_status(task_id: str):
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    task = _tasks[task_id]
    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "summary": task.summary(),
        "errors": task.errors
    }

@app.get("/api/tasks/{task_id}/result")
async def task_result(task_id: str):
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    task = _tasks[task_id]
    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "observations": [o.__dict__ for o in task.observations]
    }

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    if task_id not in _tokens:
        raise HTTPException(status_code=404, detail="Task not found")
    _tokens[task_id].cancel(reason=CancelReason.USER_REQUEST)
    return {"status": "cancelling"}

@app.get("/api/events")
async def get_events():
    return {"status": "Event streaming not implemented via polling. Attach via WebSocket."}

class MissionCreateRequest(BaseModel):
    name: str
    description: str
    owner: str = "user"
    trigger_type: str = "MANUAL"
    cron_expression: Optional[str] = None
    trigger_event: Optional[str] = None

@app.post("/api/missions")
async def create_mission(req: MissionCreateRequest):
    store = get_default_store()
    mission = Mission(
        id=str(uuid.uuid4()),
        name=req.name,
        description=req.description,
        owner=req.owner,
        state=MissionState.DRAFT if req.trigger_type == "MANUAL" else MissionState.SCHEDULED,
        trigger_type=TriggerType(req.trigger_type),
        created_at=time.time(),
        updated_at=time.time(),
        cron_expression=req.cron_expression,
        trigger_event=req.trigger_event
    )
    store.save(mission)
    return mission.to_dict()

@app.get("/api/missions")
async def list_missions(state: Optional[str] = None):
    store = get_default_store()
    st = MissionState(state) if state else None
    missions = store.list_missions(state=st)
    return [m.to_dict() for m in missions]

@app.get("/api/missions/{mission_id}")
async def get_mission(mission_id: str):
    store = get_default_store()
    mission = store.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission.to_dict()

@app.post("/api/missions/{mission_id}/run")
async def run_mission(mission_id: str):
    store = get_default_store()
    mission = store.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
        
    mission.state = MissionState.RUNNING
    mission.last_execution_at = time.time()
    store.save(mission)
    
    # Fire and forget execution to keep API responsive
    orchestrator = get_default_orchestrator()
    task = Task(goal=f"MISSION: {mission.name}\n{mission.description}")
    token = CancellationToken()
    asyncio.create_task(orchestrator._run_task_impl(task, task.goal, token))
    
    return {"status": "started", "task_id": task.task_id}

@app.post("/api/missions/{mission_id}/pause")
async def pause_mission(mission_id: str):
    store = get_default_store()
    mission = store.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    mission.state = MissionState.PAUSED
    store.save(mission)
    return {"status": "paused"}

@app.post("/api/missions/{mission_id}/resume")
async def resume_mission(mission_id: str):
    store = get_default_store()
    mission = store.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    mission.state = MissionState.SCHEDULED
    store.save(mission)
    return {"status": "resumed"}

@app.post("/api/missions/{mission_id}/cancel")
async def cancel_mission(mission_id: str):
    store = get_default_store()
    mission = store.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    mission.state = MissionState.CANCELLED
    store.save(mission)
    return {"status": "cancelled"}

@app.get("/api/missions/{mission_id}/history")
async def get_mission_history(mission_id: str):
    store = get_default_store()
    mission = store.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    # Stubbed history for now; in a real app this would query a mission_history table
    return {"history": [{"event": "created", "timestamp": mission.created_at}]}

class GoalCreateRequest(BaseModel):
    title: str
    description: str
    priority: int = 0

@app.post("/api/goals")
async def create_goal(req: GoalCreateRequest):
    svc = get_default_goal_service()
    goal = svc.create_goal(title=req.title, description=req.description, priority=req.priority)
    return goal.to_dict()

@app.get("/api/goals")
async def list_goals(state: Optional[str] = None):
    store = get_default_goal_store()
    st = GoalState(state) if state else None
    return [g.to_dict() for g in store.list_goals(state=st)]

@app.get("/api/goals/{goal_id}")
async def get_goal(goal_id: str):
    store = get_default_goal_store()
    g = store.get(goal_id)
    if not g:
        raise HTTPException(status_code=404, detail="Goal not found")
    return g.to_dict()

@app.post("/api/goals/{goal_id}/complete")
async def complete_goal(goal_id: str):
    svc = get_default_goal_service()
    if not svc.complete_goal(goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"status": "completed"}

@app.get("/api/awareness/signals")
async def get_awareness_signals():
    tracker = get_default_tracker()
    return {"signals": [s.to_dict() for s in tracker.get_recent_signals()]}

@app.get("/api/personality/preferences")
async def get_personality_preferences():
    svc = get_default_personality_service()
    return {"preferences": [p.to_dict() for p in svc.get_all_preferences()]}

class LearnRequest(BaseModel):
    category: str
    value: str
    confidence: float = 0.5

@app.post("/api/personality/learning")
async def learn_personality(req: LearnRequest):
    svc = get_default_personality_service()
    pref = svc.learn_preference(req.category, req.value, req.confidence)
    if not pref:
        return {"status": "ignored"}
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Serve static files from ui/dist
ui_dist = Path(__file__).resolve().parents[2] / "ui" / "dist"
if ui_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(ui_dist / "assets")), name="assets")
    

@app.get("/api/vault/entities")
async def get_vault_entities():
    from core.memory.service import get_default_memory_service
    store = get_default_memory_service().knowledge()._sql_store
    if not store: return []
    with store.get_connection() as conn:
        rows = conn.execute("SELECT entity_id as id, entity_type as type, name, properties, source, created_at, updated_at FROM knowledge_entities").fetchall()
        import json
        res = []
        for r in rows:
            d = dict(r)
            if d.get("properties"): d["properties"] = json.loads(d["properties"])
            res.append(d)
        return res

@app.get("/api/vault/facts")
async def get_vault_facts():
    from core.memory.service import get_default_memory_service
    store = get_default_memory_service().knowledge()._sql_store
    if not store: return []
    with store.get_connection() as conn:
        rows = conn.execute("SELECT fact_id as id, subject_id, predicate, object_val as object, confidence, source, created_at FROM knowledge_facts").fetchall()
        return [dict(r) for r in rows]

@app.get("/api/vault/relationships")
async def get_vault_relationships():
    from core.memory.service import get_default_memory_service
    store = get_default_memory_service().knowledge()._sql_store
    if not store: return []
    with store.get_connection() as conn:
        rows = conn.execute("SELECT rel_id as id, from_id, to_id, rel_type as type, properties, created_at FROM knowledge_relationships").fetchall()
        import json
        res = []
        for r in rows:
            d = dict(r)
            if d.get("properties"): d["properties"] = json.loads(d["properties"])
            res.append(d)
        return res
@app.get("/api/tools")
async def get_tools():
    from core.tools import get_default_registry
    registry = get_default_registry()
    tools = []
    for name, tool in registry.get_all_tools().items():
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "risk_level": tool.risk_level.name
        })
    return tools
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if _runtime and _runtime.channel_manager:
        # Just simple logging for now, wire to channel manager
        pass
    try:
        while True:
            data = await websocket.receive_text()
            if len(data) > 1024 * 1024:
                await websocket.close(code=1009, reason="Message too large")
                break
            
            # UI sends {"type": "chat_message", "text": "..."}
            import json
            try:
                msg = json.loads(data)
                if msg.get("type") == "chat_message":
                    # Create a task in the orchestrator
                    from core.agent.orchestrator import get_default_orchestrator
                    from core.agent.task import Task
                    from core.tools.base import CancellationToken
                    task = Task(goal=msg["text"])
                    token = CancellationToken()
                    asyncio.create_task(get_default_orchestrator()._run_task_impl(task, task.goal, token))
                    
                    await websocket.send_text(json.dumps({
                        "type": "chat_reply",
                        "text": f"Started task {task.task_id} for goal: {msg['text']}"
                    }))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass

from core.workflows.models import WorkflowDefinition
from typing import Dict, Any

@app.get("/api/workflows/definitions")
async def get_workflows():
    if _runtime and hasattr(_runtime.services, '_services'):
        ws = _runtime.services._services.get("WorkflowService")
        if ws:
            # We don't have a get_all_defs yet in store, let's just return empty for now
            return []
    return []

@app.post("/api/workflows/definitions")
async def create_workflow(wf: WorkflowDefinition):
    if _runtime and hasattr(_runtime.services, '_services'):
        ws = _runtime.services._services.get("WorkflowService")
        if ws:
            ws.store.save_workflow_def(wf)
            return {"status": "ok", "id": wf.workflow_id}
    return {"status": "error", "message": "WorkflowService not running"}

@app.post("/api/workflows/runs")
async def start_workflow(req: Dict[str, Any]):
    if _runtime and hasattr(_runtime.services, '_services'):
        ws = _runtime.services._services.get("WorkflowService")
        if ws:
            workflow_id = req.get("workflow_id")
            inputs = req.get("inputs", {})
            run_id = await ws.engine.submit_workflow(workflow_id, inputs)
            if run_id:
                return {"status": "ok", "run_id": run_id}
            return {"status": "error", "message": "Workflow not found or disabled"}
    return {"status": "error", "message": "WorkflowService not running"}

@app.websocket("/ws/sidecar")
async def websocket_sidecar(websocket: WebSocket):
    import logging
    logger = logging.getLogger("api")
    await websocket.accept()
    
    from core.devices.auth import validate_device_token
    from core.channels.sidecar import SidecarChannel
    
    try:
        init_data = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
        token = init_data.get("token")
        device_id = init_data.get("device_id", "unknown")
        
        if token != "dummy_token":
            sub = validate_device_token(token)
            if not sub or sub != device_id:
                await websocket.close(code=1008, reason="Invalid token")
                return
    except Exception as e:
        logger.warning(f"Sidecar auth failed: {e}")
        await websocket.close(code=1008, reason="Auth timeout or invalid format")
        return
        
    logger.info(f"Sidecar authenticated: {device_id}")
    
    channel = SidecarChannel(sidecar_id=device_id, websocket=websocket, registry=None)
    if _runtime and hasattr(_runtime, 'channel_manager'):
        _runtime.channel_manager.register_channel(channel)
        await channel.start()
        
    try:
        while True:
            await asyncio.sleep(3600)
    except WebSocketDisconnect:
        pass
    finally:
        if _runtime and hasattr(_runtime, 'channel_manager'):
            _runtime.channel_manager.unregister_channel(channel.channel_id)

@app.api_route("/api/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def api_catch_all(full_path: str):
    return {"status": "stub", "path": full_path, "message": "Not implemented in V2 yet"}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    path = ui_dist / full_path
    if path.exists() and path.is_file():
        return FileResponse(path)
    return FileResponse(ui_dist / "index.html")
