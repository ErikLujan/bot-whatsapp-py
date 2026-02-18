# WhatsApp Technical Support Bot

Este proyecto es un Bot de Asistencia Técnica Automatizado diseñado para gestionar tickets de soporte a través de la API oficial de WhatsApp (Meta). Implementa una arquitectura limpia (MVC) y escalable, permitiendo a los usuarios reportar problemas de hardware/software y consultar el estado de sus reclamos en tiempo real.

El sistema utiliza una máquina de estados en memoria para gestionar el contexto conversacional del usuario, e integra notificaciones asíncronas para el equipo de soporte técnico.

## Características Principales

* **Flujo Conversacional Inteligente:** Detección de intención y gestión de contexto mediante estados (Menú Principal, Esperando Descripción, Consultando ID).
* **Gestión de Tickets (CRUD):** * Generación automática de IDs únicos y persistencia en base de datos PostgreSQL.
  * Consulta en tiempo real del estado de reparación por parte del cliente.
* **Alertas Asíncronas (Multithreading):** Notificación inmediata vía email al equipo técnico cada vez que se genera un ticket, ejecutada en un hilo secundario (`threading`) para garantizar tiempos de respuesta óptimos (sub-segundo) en el webhook de Meta.
* **Arquitectura Clean Code:** Separación estricta de responsabilidades:
  * `app.py`: Controlador de rutas y webhook.
  * `services.py`: Lógica de negocio, integración de APIs y conexión a base de datos.
  * `mensajes.py`: Diccionario centralizado de copies y plantillas HTML para correos.
* **Modo Híbrido:** Preparado para funcionar en entorno de desarrollo local y en servidores cloud de producción.

## Stack Tecnológico

* **Lenguaje:** Python 3.10+
* **Framework Web:** Flask
* **Base de Datos:** Supabase (PostgreSQL)
* **APIs Externas:** 
  * WhatsApp Cloud API (Meta) - Canal de comunicación frontend.
  * Resend API - Despacho transaccional de correos electrónicos.
* **Infraestructura & Herramientas:** Render (Deploy), Postman, Gunicorn, Threading.

## Instalación y Configuración Local

1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Crear un archivo `.env` en la raíz (ver `.env.example` para las variables requeridas).
5. Ejecutar la aplicación: `python app.py`
