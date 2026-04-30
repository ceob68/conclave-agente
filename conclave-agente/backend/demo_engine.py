# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
demo_engine.py — CÓNCLAVE Agente Demo Mode

Simulates agent responses without loading any AI model.
Used for UI testing and demonstration purposes when no GPU is available.
"""

import time
import threading

DEMO_RESPONSES = {
    0: [  # Arquitecto
        """Analizando la propuesta desde una perspectiva arquitectónica...

**Estructura propuesta:**
- Capa de presentación: interfaz modular con componentes reutilizables
- Capa de negocio: servicios desacoplados con inyección de dependencias
- Capa de datos: repositorios con abstracción de persistencia

**Tecnologías recomendadas:**
1. Backend: Python con FastAPI para alto rendimiento
2. Base de datos: PostgreSQL con Redis para caché
3. Frontend: React con TypeScript para tipado estático

La separación de responsabilidades es fundamental aquí. Cada componente debe tener una única razón para cambiar, siguiendo el principio de responsabilidad única.""",

        """Desde el punto de vista arquitectónico, propongo un enfoque de microservicios:

**Servicios identificados:**
- Servicio de autenticación (independiente y reutilizable)
- Servicio de negocio principal (stateless para escalabilidad)
- Servicio de notificaciones (asíncrono con cola de mensajes)

**Patrones de diseño aplicables:**
- Event Sourcing para trazabilidad completa
- CQRS para separar lecturas de escrituras
- Circuit Breaker para resiliencia ante fallos""",
    ],
    1: [  # Programador
        """Implementación técnica basada en la propuesta del Arquitecto:

```python
class ServiceManager:
    def __init__(self, config: Config):
        self._config = config
        self._services = {}
        
    def register(self, name: str, service: BaseService):
        self._services[name] = service
        
    async def execute(self, name: str, payload: dict):
        service = self._services.get(name)
        if not service:
            raise ServiceNotFoundError(f"Service {name} not registered")
        return await service.process(payload)
```

**Puntos clave de la implementación:**
- Gestión de errores con excepciones tipadas
- Operaciones asíncronas para no bloquear el event loop
- Registro dinámico de servicios para extensibilidad""",

        """Añadiendo la capa de persistencia:

```python
from dataclasses import dataclass
from typing import Optional
import asyncpg

@dataclass
class Repository:
    pool: asyncpg.Pool
    
    async def find_by_id(self, id: str) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM entities WHERE id = $1", id
            )
    
    async def save(self, entity: dict) -> str:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "INSERT INTO entities (data) VALUES ($1) RETURNING id",
                entity
            )
```

El uso de connection pooling es crítico para rendimiento en producción.""",
    ],
    2: [  # Seguridad
        """**AUDITORÍA DE SEGURIDAD — Vulnerabilidades identificadas:**

🔴 **CRÍTICO:** Sin validación de entrada en endpoints de API
- Vector: Inyección SQL si los parámetros no son sanitizados
- Mitigación: Usar consultas parametrizadas SIEMPRE (ya implementado en código del Programador ✅)

🟡 **ALTO:** Autenticación sin rate limiting
- Vector: Ataques de fuerza bruta en login
- Mitigación: Implementar exponential backoff + bloqueo temporal

🟡 **ALTO:** Ausencia de logs de auditoría
- Vector: Sin trazabilidad en caso de incidente
- Mitigación: Logging estructurado en todas las operaciones críticas

🟢 **MEDIO:** Tokens JWT sin rotación
- Mitigación: Refresh tokens con tiempo de vida corto (15 min access token)""",

        """**Análisis de superficie de ataque:**

El diseño actual expone los siguientes vectores:

1. **API Gateway sin WAF** — Cualquier request llega directo al servicio
2. **Secrets en variables de entorno** — Riesgo si hay acceso al servidor
3. **Sin validación de Content-Type** — Posible confusión de tipos MIME

**Recomendaciones prioritarias:**
- HashiCorp Vault o AWS Secrets Manager para gestión de secretos
- Validación estricta de esquemas con Pydantic o Marshmallow
- Headers de seguridad: HSTS, CSP, X-Frame-Options""",
    ],
    3: [  # QA/UX
        """**ANÁLISIS QA/UX — Escenarios de fallo y mejoras:**

**Casos límite no contemplados:**
1. ¿Qué pasa si el usuario pierde conexión durante una operación larga?
2. ¿Cómo se comporta el sistema con 10,000 usuarios concurrentes?
3. ¿Qué mensaje ve el usuario cuando un servicio downstream falla?

**Problemas de UX identificados:**
- Los mensajes de error son técnicos (stack traces expuestos al usuario)
- Sin indicador de progreso en operaciones lentas
- Falta de confirmación antes de acciones destructivas

**Mejoras propuestas:**
- Loading states con feedback visual en TODAS las operaciones async
- Mensajes de error amigables: "Algo salió mal, intenta de nuevo" vs HTTP 500
- Modo offline con sincronización posterior""",

        """**Testing strategy recomendada:**

```
Pirámide de testing:
  /\  E2E Tests (10%) — Cypress/Playwright
 /  \ Integration Tests (30%) — pytest + httpx  
/____\ Unit Tests (60%) — pytest + coverage > 80%
```

**Escenarios críticos sin cubrir:**
- Concurrencia: dos usuarios editando el mismo recurso simultáneamente
- Transacciones largas: timeout vs rollback parcial
- Datos malformados: ¿el sistema degrada gracefully?

La deuda técnica en testing es el mayor riesgo de mantenibilidad a largo plazo.""",
    ],
    4: [  # Documentador
        """**SÍNTESIS DEL CICLO — Borrador actualizado:**

## Decisiones arquitectónicas tomadas
1. **Microservicios** con separación clara de responsabilidades (Arquitecto)
2. **Repositorios async** con connection pooling para persistencia (Programador)
3. **Autenticación robusta** con rate limiting y JWT rotation (Seguridad)
4. **UX resiliente** con estados de carga y manejo de errores amigables (QA/UX)

## Riesgos identificados
- Sin WAF ni protección perimetral (prioridad ALTA)
- Cobertura de tests insuficiente (prioridad MEDIA)
- Falta gestión de secretos enterprise (prioridad ALTA)

## Próximas acciones recomendadas
1. Implementar autenticación con rate limiting
2. Agregar capa de validación de entrada (Pydantic)
3. Definir estrategia de testing antes de continuar el desarrollo

**El enjambre continúa refinando la propuesta...**""",

        """**ACTUALIZACIÓN DEL BORRADOR — Ciclo completado:**

## Estado actual del diseño
La arquitectura ha madurado significativamente en este ciclo:

### Fortalezas consolidadas
- Separación de capas bien definida
- Código async de alta calidad
- Identificación temprana de vulnerabilidades

### Áreas de mejora pendientes  
- Testing E2E sin implementar
- Gestión de secretos sin definir
- Monitoreo y observabilidad ausentes

### Recomendación para el próximo ciclo
Profundizar en la estrategia de despliegue (CI/CD, contenedores Docker, orquestación Kubernetes) y en el plan de monitoreo con métricas de negocio.

*— El Documentador, sintetizando para el siguiente ciclo*""",
    ],
}

_response_counters = {}


def get_demo_response(agent_id: int, topic: str, cycle: int) -> str:
    """Get a demo response for the given agent."""
    responses = DEMO_RESPONSES.get(agent_id, ["Procesando respuesta de demostración..."])
    idx = _response_counters.get(agent_id, 0) % len(responses)
    _response_counters[agent_id] = idx + 1
    return responses[idx]


def stream_demo_response(agent_id: int, topic: str, cycle: int,
                          token_callback, stop_event=None,
                          words_per_second: int = 12) -> str:
    """
    Stream a demo response word by word to simulate real inference.
    Returns the full response text.
    """
    full_text = get_demo_response(agent_id, topic, cycle)
    words = full_text.split(" ")
    delay = 1.0 / words_per_second

    output = []
    for i, word in enumerate(words):
        if stop_event and stop_event.is_set():
            break
        token = word + (" " if i < len(words) - 1 else "")
        output.append(token)
        if token_callback:
            token_callback(token)
        time.sleep(delay)

    return "".join(output)
