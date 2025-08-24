# app/main.py
import asyncio
from contextlib import asynccontextmanager
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.database.mongo_assignment import MongoAssignmentRepository
from app.services.assignment_service import AssignmentService
from app.services.publisher_service import AssignmentPublisher
from app.routers.v1 import health
from app.routers.v1 import assignment

logging.basicConfig(
    level=logging.INFO,  # cambia in DEBUG quando debuggiamo
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    stream=sys.stdout,
)

# opzionale: più verboso solo per i nostri namespace
logging.getLogger("report.publisher").setLevel(logging.DEBUG)

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        client = AsyncIOMotorClient(settings.mongo_uri, uuidRepresentation="standard")
        db = client[settings.mongo_db_name]
        repo = MongoAssignmentRepository(db)
        await repo.ensure_indexes()
        app.state.assignment_repo = repo   # repo disponibile alle routes

        # --- RabbitMQ Publisher ---
        publisher = AssignmentPublisher(
            rabbitmq_url=settings.rabbitmq_url,
            heartbeat= 30,
            exchange="elearning.reports",
            routing_key="assignments.reports",
        )

        await publisher.connect(max_retries=10, delay=5)
        app.state.assignment_publisher = publisher

        stop_event = asyncio.Event()

        async def deadline_loop():
            while not stop_event.is_set():
                try:
                    assignment_ids = await AssignmentService.sweep_deadlines(repo)
                    if assignment_ids:
                        tasks = [
                            asyncio.create_task(
                                publisher.publish_assignment_status(
                                    assignmentId = assignment_id,
                                    teacherId = None,
                                    status ="completed")
                            )
                            for assignment_id in assignment_ids
                        ]
                        # aspetta tutte, senza far esplodere il loop se una fallisce
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        for r in results:
                            if isinstance(r, Exception):
                                logging.exception("Publish fallito", exc_info=r)
                except Exception:
                    logging.exception("Errore sweep deadlines")
                    # attesa 30s o uscita se stop_event settato
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=30)
                except asyncio.TimeoutError:
                    pass

        bg_task = asyncio.create_task(deadline_loop())

        try:
            yield
        finally:
            stop_event.set()
            publisher.close()
            await bg_task
            client.close()

    app = FastAPI(
        title="Assignment Microservice",
        description="Microservizio per la gestione degli assignment",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )

    app.include_router(health.router,     prefix="/api/v1", tags=["health"])
    app.include_router(assignment.router, prefix="/api/v1", tags=["assignments"])
    return app

app = create_app()
