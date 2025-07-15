# InnerSource Measurement Tool - Architecture Documentation

## Overview

The InnerSource Measurement Tool is designed to analyze GitHub repositories and measure the level of cross-team collaboration (InnerSource) happening within them. This document provides detailed architectural information for developers and contributors.

## System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        InnerSource Measurement Tool                             │
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Environment   │  │  Authentication │  │  Report Writer  │  │  Markdown   │ │
│  │  Configuration  │  │     Manager     │  │                 │  │   Helpers   │ │
│  │   (config.py)   │  │   (auth.py)     │  │(markdown_writer │  │(markdown_   │ │
│  │                 │  │                 │  │     .py)        │  │helpers.py)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                      │                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                   Core Analysis Engine                                      │ │
│  │                 (measure_innersource.py)                                   │ │
│  │                                                                             │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │ │
│  │  │ Repository    │  │ Organization  │  │ Team Boundary │  │ Contribution│ │ │
│  │  │ Data Fetcher  │  │ Data Loader   │  │ Detector      │  │ Analyzer    │ │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘  └─────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           External Dependencies                                 │
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   GitHub API    │  │  File System    │  │  org-data.json  │  │  Output     │ │
│  │                 │  │                 │  │                 │  │  Files      │ │
│  │ • Repositories  │  │ • Read/Write    │  │ • Org Structure │  │ • Markdown  │ │
│  │ • Commits       │  │ • File Handling │  │ • Manager Data  │  │ • Reports   │ │
│  │ • Pull Requests │  │                 │  │                 │  │             │ │
│  │ • Issues        │  │                 │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Configuration Management (`config.py`)

**Responsibilities:**

- Parse and validate environment variables
- Provide type-safe configuration access
- Handle default values and required parameters
- Support multiple authentication methods

### 2. Authentication Manager (`auth.py`)

**Responsibilities:**

- Authenticate with GitHub using multiple methods
- Handle GitHub Enterprise Server installations
- Manage JWT tokens for GitHub App authentication
- Provide unified authentication interface

### 3. Core Analysis Engine (`measure_innersource.py`)

**Responsibilities:**

- Orchestrate the entire analysis process
- Implement team boundary detection algorithm
- Manage chunked processing for large repositories
- Calculate InnerSource metrics and ratios

### 4. Report Generation (`markdown_writer.py`)

**Responsibilities:**

- Generate structured Markdown reports
- Format data for human consumption
- Handle edge cases and missing data
- Provide consistent report structure

### 5. Utility Functions (`markdown_helpers.py`)

**Responsibilities:**

- Manage file size constraints
- Split large files intelligently
- Preserve content integrity during splits

## Data Flow Architecture

### Processing Pipeline

```
┌─────────────────┐
│  Start Process  │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Load & Validate │
│ Configuration   │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Authenticate    │
│ with GitHub     │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Fetch Repository│
│ Metadata        │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Load org-data   │
│ .json File      │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Determine Team  │
│ Boundaries      │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Analyze Commits │
│ (Chunked)       │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Analyze PRs     │
│ (Chunked)       │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Analyze Issues  │
│ (Chunked)       │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Calculate       │
│ Metrics         │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Generate Report │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Handle File     │
│ Size Limits     │
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Output Results  │
└─────────────────┘
```

## Error Handling

### Error Categories

1. **Configuration Errors**: Missing or invalid environment variables
2. **Authentication Errors**: Invalid tokens or insufficient permissions
3. **Network Errors**: API timeouts or connectivity issues
4. **Data Errors**: Missing org-data.json or invalid format
5. **Processing Errors**: Unexpected data structures or edge cases
