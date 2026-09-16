# UW Nick Gym Occupancy Tracker

A small but complete full-stack application that collects data about Nick Gym Occupancy. Contains graphs that plot today's occupancy over time, as well as average values over time for each day of the week.

---

## Tech Stack

* **Frontend:** React (Vite), Recharts, CSS3
* **Backend:** Python 3, FastAPI, Uvicorn, APScheduler
* **Database:** SQLite3

---

## Technical Architecture

### Overview
Contains a backend using Python and SQLite, a frontend using React, and a REST API using Uvicorn to integrate the two together. The main components are the data collector and processor, the main REST API program, and the frontend containing the React project.

### Backend (Python and SQLite)
* **Custom Data Collection** Created a custom data collector and processor to catalog data by key values used by the frontend.
* **Deduplication Logic** Ensured that whenever entries are collected, any entries equivalent to existing data are not added to the database.
* **Timeline Database** Stores raw logs in a local SQLite database that is utilized by the REST API

### Frontend (React)
* **Modular Component Architecture** Implements standalone GraphCard components that manage their own fetching state and dropdown selections independently.
* **Dynamic Graphs** Uses Recharts line charts to graph hourly trend lines for each individual target location.
* **Live Status Indicator** Displays connection health to REST API and current percentage full badges for all target gym locations.

### Integration (REST APIs/Uvicorn)
* **FastAPI Framework** Serves data via REST endpoints connected to the SQLite database available for collection by the frontend.
* **Automated Local Data Collection** Uses APScheduler in FastAPI in order to locally collect data at fixed intervals.
