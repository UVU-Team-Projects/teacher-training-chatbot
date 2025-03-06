# Development Environment Setup Guide

This guide provides detailed instructions for setting up your development environment for the Utah Elementary Teacher Training Assistant project.

## Prerequisites
- Git
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+

## Setup Options

Choose the setup guide that matches your development environment:

- [Windows with WSL](windows_wsl.md)
- [macOS](macos.md)
- [Linux](linux.md)

## Common Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-org/utah-tta.git
   cd utah-tta
   ```

2. **Environment Setup**
   - [Anaconda Setup](environment.md#anaconda-setup)
   - [Standard Python Setup](environment.md#standard-setup)
   - [Database Configuration](database.md)

3. **Configuration**
   ```bash
   # Copy example config
   cp config/example.env .env
   
   # Edit configuration
   nano .env
   ```

[Rest of the setup content moved here...] 