import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import ValidationError

from src.domain.ingress.schema import ExyPayload
from src.domain.ingress.security import SecurityProvider, get_security_provider
from src.domain.orchestrator.agent import ExyAgentCore, get_orchestrator


router  = APIRouter(tags = ["Ingress Channels"])
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_ingress(
    websocket: WebSocket,
    security: SecurityProvider = Depends(get_security_provider),
    agent: ExyAgentCore = Depends(get_orchestrator),
):
    """Univarsal Websocket interface for Exy OS"""
    await websocket.accept()
    logger.info("Websocket connected")

    try:
        while True:
            raw_data = await websocket.receive_json()

            try:
                payload = ExyPayload(**raw_data)

                if not security.verify(payload.user_id):
                    logger.warning("Terminating connection: Failed security verification.")
                    await websocket.send_json({"error": "Access Denied"})
                    await websocket.close(code=4003)
                    break
            
                logger.info(f"Authorized received from {payload.platform} : {payload.raw_text} Sending to Agent")
                response = await agent.process_intent(payload)

                await websocket.send_json({
                    "status": "success",
                    "received": response,
                    "message_id": payload.message_id
                })

            except ValidationError as ve:
                logger.error("Schema Mismatch: Incoming data did not match ExyPayload.")
                await websocket.send_json({
                    "error": "Invalid payload structure"
                })
    except WebSocketDisconnect as e:
        logger.info("Ingress Websocket Disconnected")

