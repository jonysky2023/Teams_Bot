# Catálogo de microservicios disponibles en Flexxible
# Claude usará las descripciones para decidir cuál ejecutar

MICROSERVICES = [
    {
        "id": "6731bbeee636d88d51cdedec",
        "name": "Deshabilitar servicio Spooler",
        "description": "Deshabilita el servicio de cola de impresión (Spooler) en el dispositivo. Útil cuando hay problemas con impresoras o el servicio está bloqueado.",
        "keywords": ["spooler", "impresora", "cola impresión", "deshabilitar spooler"]
    },
    {
        "id": "6745da6fc062c421a01a4654",
        "name": "Limpieza de temporales",
        "description": "Elimina archivos temporales del sistema para liberar espacio en disco y mejorar el rendimiento.",
        "keywords": ["temporales", "limpiar disco", "liberar espacio", "temp", "limpieza"]
    },
    {
        "id": "68a8557c04251ae4a7cd3ab6",
        "name": "Restablecer cola de impresión",
        "description": "Reinicia y restablece la cola de impresión del dispositivo. Útil cuando los documentos se quedan atascados en la cola.",
        "keywords": ["cola impresión", "reiniciar impresora", "atascado", "restablecer impresión"]
    },
    {
        "id": "68cabe36cbe8922b3bf96dd9",
        "name": "Vaciar papelera de reciclaje",
        "description": "Vacía la papelera de reciclaje para todos los usuarios del dispositivo, liberando espacio en disco.",
        "keywords": ["papelera", "vaciar papelera", "recycle bin", "liberar espacio"]
    },
    {
        "id": "652e71c6411291005b02bdd3",
        "name": "Borrar caché de Microsoft Edge",
        "description": "Borra la memoria caché del navegador Microsoft Edge para resolver problemas de navegación o liberar espacio.",
        "keywords": ["edge", "caché", "cache", "navegador", "microsoft edge", "borrar caché"]
    },
    {
        "id": "69e1040e9ac2c51da41611db",
        "name": "Instalar 7-zip",
        "description": "Descarga e instala 7-zip en el dispositivo.",
        "keywords": ["7-zip", "7zip", "rar", "zip", "instalar 7-zip"]
    }
]


def get_microservices_catalog() -> str:
    """Devuelve el catálogo formateado para el system prompt de Claude."""
    lines = ["Microservicios disponibles para ejecutar en el dispositivo:"]
    for ms in MICROSERVICES:
        lines.append(f"- [{ms['id']}] {ms['name']}: {ms['description']}")
    return "\n".join(lines)


def get_microservice_by_id(microservice_id: str) -> dict | None:
    for ms in MICROSERVICES:
        if ms["id"] == microservice_id:
            return ms
    return None
