# WhatsApp Technical Support Bot

Este proyecto es un **Bot de Asistencia Técnica Automatizado** diseñado para gestionar tickets de soporte a través de WhatsApp. Implementa una arquitectura limpia y escalable, permitiendo a los usuarios reportar problemas y consultar el estado de sus reclamos en tiempo real mediante una base de datos en la nube.

El sistema utiliza una **Máquina de Estados** para gestionar el flujo de la conversación, recordando el contexto del usuario (si está saludando, describiendo un problema o consultando un ID).

## 📋 Características Principales

* **Flujo Conversacional Inteligente:** Detecta la intención del usuario y gestiona el contexto mediante estados en memoria.
* **Gestión de Tickets (CRUD):**
    * Creación de nuevos tickets de soporte con descripción del problema.
    * Consulta de estado de tickets existentes mediante ID.
* **Integración con Base de Datos:** Persistencia de datos en tiempo real usando **Supabase** (PostgreSQL).
* **Arquitectura Modular:** Separación de responsabilidades entre el servidor (`app.py`), la configuración (`config.py`) y la lógica de negocio (`services.py`).
* **Modo Híbrido:** Preparado para funcionar tanto en entorno local (simulación vía Postman) como en producción (API Oficial de Meta).

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.10+
* **Framework Web:** Flask
* **Base de Datos:** Supabase (PostgreSQL)
* **API Externa:** WhatsApp Cloud API (Meta)
* **Herramientas de Desarrollo:** Postman, Ngrok, Gunicorn.
