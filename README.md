# Community Civic Issue Management System

## 📌 Project Overview

The **Community Civic Issue Management System** is a microservices-based application designed to manage citizens, complaints, and wards independently.

The system is divided into separate services, where each service has its own:

- Frontend
- Backend
- Database

The services communicate through **REST APIs**, and an **API Gateway** acts as the single entry point for client requests.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      Client/User     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    API Gateway      │
                    │      Port 5000       │
                    ├─────────────────────┤
                    │  Request Routing     │
                    │  Load Balancing      │
                    │  Rate Limiting       │
                    │  Logging & Monitoring│
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
 ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
 │ Citizen Service│   │Complaint Service│   │  Ward Service  │
 │    Port 5001   │   │    Port 5002    │   │    Port 5003   │
 └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
         │                     │                     │
         ▼                     ▼                     ▼
 ┌───────────────┐    ┌────────────────┐    ┌───────────────┐
 │  citizen.db   │    │  complaint.db  │    │    ward.db    │
 └───────────────┘    └────────────────┘    └───────────────┘