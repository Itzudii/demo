
- control flow diagram
![App Screenshot](images/logo_transparent.png)
## 📂 Cortex FS – Intelligent File System Manager

**A multi-threaded and multi-process based File System Manager designed to handle:**

- File operations
- CLI commands
- Background tasks
- Vector indexing
- Tag generation
- Logging
- Frontend + API interaction
- The system is built for scalability, modularity, and asynchronous task execution.

## 🏗️ Architecture Overview

### The project is divided into:

- Main Thread (Main Processor)
- Worker Thread
- Separate Tag Generation Process
- Frontend + API Layer
- Logging & OS Watcher Service


### It uses:

- Multithreading (for task execution)

- Multiprocessing (for heavy operations like tag generation)

- Queue-based communication

- Persistent storage (database + vector storage)

  

## 🔷 High-Level Flow

OS Events → Watcher → Log Manager → Controller

↓

Frontend → API → Controller → Task Scheduler

↓

Task Handler

↓

FS Manager

↓

Storage / Index / Vector / Tag Generation Process

  

## 🧠 Core Components Explained

# 1️⃣ Main Thread (Main Processor)

  

**This is the brain of the application.**

  

### Responsibilities:

  

- Initialize all services

- Handle API requests

- Coordinate tasks

- Manage communication between threads and processes

  

# 2️⃣ Startup Loader

###  Responsibilities:

  

Load File System

Load CLI

Initialize Worker Thread

Initialize Tag Generation Process

This ensures everything is ready before user interaction begins.

  

# 3️⃣ Watcher (Background Service)

  

**Monitors OS-level file events.**

###  Listens For:

  

- File creation

- File deletion

- File modification

  

###  Output:

  

- Writes events to: -> active.log

  
  

- This is later consumed by the Log Manager.

  

# 4️⃣ Log Manager

  

### Responsibilities:

- Read active.log

- Parse system events

- Send structured events to Controller

- This allows automatic file system updates.

  

# 5️⃣ API Layer

**it is a pywebview layer**

** Acts as a bridge between: **

Frontend ↔ Controller

  

### Handles:

  

- HTTP Requests

- Response formatting

- Data validation

  

# 6️⃣ Controller

  

**The central coordinator.**

  

### Responsibilities:

  

- Receive input from: API

  


  

- Log Manager

  

- Forward tasks to:

  

- Task Scheduler

  

- Manage process communication

  

- This component ensures clean separation of concerns.

  

### 🔁 Worker Thread

  

- Queue checking and db write done by worker tread

  

# 7️⃣ Task Scheduler

### Responsibilities:

  

- Queue incoming tasks

  

- Distribute tasks to:

  

- Task Handler

  

- Background Executor

  

### Ensures:

  

- Non-blocking execution

  

- Organized processing

  

# 8️⃣ Task Handler

  

- Executes structured tasks by:

- forwards work to:

- Task Performer

  

- CLI Performer

  

# 9️⃣ Task Performer

  

### Handles:

  

- Core FS operations

  

- Data updates

  
- Storage updates request sends

  

# 🔟 CLI Performer

  

**Executes CLI-based commands separately from API-based commands.**

  

### This separation allows:

  

- Dual interface support (CLI + Web)

  

# 🗂️ FSManager (Core Engine)

  

**The heart of file system logic.**

  

### Responsibilities:

  

- Maintain file tree

  

- Coordinate indexing

  

- Communicate with:

  

- Vector Engine

  

- Storage Layer

  

- Tag Generation Process

  

# 📊 Vector Engine (MRVector)

  

###  Handles:

  

- Vector generation

  

- Embeddings

  

- Similarity search

  

- Advanced search capabilities

  

### Used for:

  

- Intelligent file retrieval

  

- Content-based searching

  

# 💾 Indexer / Storage

  

### Persists data in:

  

- database/index.db

  
  

### Stores:

  

- File metadata

  

- Index mappings

  

- Searchable structure

  

# 🧩 Separate Tag Generation Process

  

**Runs in a completely different process (not thread).**

  

**Why separate process?**

  

- Tag generation is CPU-intensive

  

- Avoid blocking main system

  

- Better scalability

  

### Communication:

  

- Uses a Multiprocessing Queue

  

- FSManager → Queue → Tag Generation Process

  

# 🎨 Frontend

  

### Provides:

  

- HTML

  

- CSS

  

- JS

  

**Communicates with backend using API request/response model.**


# 📁 Data Flow Example
- control flow diagram
![App Screenshot](images/control_flow.png)


# 🔐 Design Principles

  

- Modular architecture

  

- Separation of concerns

  

- Asynchronous execution

  

- Scalable processing

  

- Clean layered structure

  

# 🚀 Key Features

  

✅ Real-time file monitoring

  

✅ Vector-based intelligent search

  

✅ Tag auto-generation

  
✅ CLI + Web Interface

  

✅ Multi-threaded task processing

  

✅ Multi-process heavy computation

  

✅ Persistent indexed storage

  

# 📦 Project Structure (Conceptual)
FS/
│
├── api.py
├── cli.py
├── controller.py
├── fsmanager.py
├── tag.py
├── task.py
│
├── frontend/
│   ├── css/
│   │   ├── app_container_and_webkit.css
│   │   ├── background_particle.css
│   │   ├── body.css
│   │   ├── cli.css
│   │   ├── context_menu.css
│   │   ├── details_panel.css
│   │   ├── global.css
│   │   ├── grid_and_list_view.css
│   │   ├── menu_bar.css
│   │   ├── rename-styles.css
│   │   ├── responsive.css
│   │   ├── root.css
│   │   ├── side_bar.css
│   │   ├── title_bar.css
│   │   └── tool_bar.css
│   │
│   ├── font/
│   │   ├── font.woff2
│   │   │
│   ├── img/
│   │   ├── logo_transparent.png
│   │   └── logo.jpeg
│   │
│   ├── js/
│   │   ├── cli.js
│   │   ├── rename-functionality.js
│   │   ├── script-main.js
│   │   ├── script.js
│   │   └── search.js
│   │
│   ├── cli.html
│   ├── file-search.html
│   └── main-window.html
│
├── .database/
│   └── index.db
│
├── .save/
│
├── logs/
│   ├── error.log
│   └── debug.log
│
├── model/
│   ├── all-MiniLM-L6-v2/
│   ├── qwen2.5-1.5b-instruct-q8_0.gguf
│   └── llama-2-7b-chat.Q4_K_M.gguf
│
├── watcher/
│    ├── logs/
│    │   └── active.log
│    ├── config.py
│    ├── event_logger.py
│    ├── fs_startup_sync.py
│    ├── internal_tree.py
│    ├── watcher_service.py
│    └── run_watcher.bat
│
├── .gitignore
├── README.md
├── requirements.txt
│
├── images/
│   ├── control_flow.png
│   ├── logo_transparent.png
│   └── logo.jpeg
│   └── new2.drawio
│
└── model/
    │
    ├── all-MiniLM-L6-v2/
    │   ├── 1_Pooling/
    │   ├── 2_Normalize/
    │   ├── config_sentence_transformers.json
    │   ├── config.json
    │   ├── model.safetensors
    │   ├── modules.json
    │   ├── README.md
    │   ├── sentence_bert_config.json
    │   ├── special_tokens_map.json
    │   ├── tokenizer_config.json
    │   ├── tokenizer.json
    │   └── vocab.txt
    │
    ├── llama-2-7b-chat.Q4_K_M.gguf
    └── qwen2.5-1.5b-instruct-q8_0.gguf
 
  

# 🔮 Future Improvements

  

- Distributed processing

  

- Cloud storage integration

  

- Advanced AI-based tagging

  

- Caching layer (Redis)

  

- WebSocket real-time updates

- Recycle bin