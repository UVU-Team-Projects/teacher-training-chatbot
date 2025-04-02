# Scripts Directory Guide

This directory contains utility scripts for the Utah Elementary Teacher Training Assistant (UTAH-TTA). These scripts automate common tasks, setup processes, and maintenance operations.

## 📋 Table of Contents
- [Directory Structure](#directory-structure)
- [Setup Scripts](#setup-scripts)
- [Data Processing Scripts](#data-processing-scripts)
- [Monitoring Scripts](#monitoring-scripts)
- [Maintenance Scripts](#maintenance-scripts)
- [Usage Guidelines](#usage-guidelines)

## Directory Structure

```
scripts/
├── setup/                      # Setup and initialization
│   ├── init_database.py       # Database initialization
│   ├── install_deps.sh        # Dependencies installation
│   └── setup_env.sh          # Environment setup
│
├── data_processing/            # Data processing utilities
│   ├── generate_embeddings.py # Embedding generation
│   ├── validate_scenarios.py  # Scenario validation
│   └── export_metrics.py     # Metrics export
│
├── monitoring/                 # Monitoring utilities
│   ├── check_health.py       # Health checks
│   ├── log_analyzer.py       # Log analysis
│   └── performance_mon.py    # Performance monitoring
│
└── maintenance/               # Maintenance utilities
    ├── backup_db.sh          # Database backup
    ├── cleanup_logs.sh       # Log cleanup
    └── update_indices.py     # Index updates
```

## Setup Scripts

### Database Initialization (`setup/init_database.py`)
```python
# Initialize database with required extensions and tables
python scripts/setup/init_database.py --host localhost --port 5432
```

### Dependencies Installation (`setup/install_deps.sh`)
```bash
# Install project dependencies
./scripts/setup/install_deps.sh --env development
```

### Environment Setup (`setup/setup_env.sh`)
```bash
# Set up development environment
./scripts/setup/setup_env.sh --config dev
```

## Data Processing Scripts

### Embedding Generation (`data_processing/generate_embeddings.py`)
```python
# Generate embeddings for scenarios
python scripts/data_processing/generate_embeddings.py --input data/scenarios/approved/
```

### Scenario Validation (`data_processing/validate_scenarios.py`)
```python
# Validate scenario format and content
python scripts/data_processing/validate_scenarios.py --scenarios data/scenarios/drafts/
```

### Metrics Export (`data_processing/export_metrics.py`)
```python
# Export performance metrics
python scripts/data_processing/export_metrics.py --output reports/metrics/
```

## Monitoring Scripts

### Health Checks (`monitoring/check_health.py`)
```python
# Run system health checks
python scripts/monitoring/check_health.py --components all
```

### Log Analysis (`monitoring/log_analyzer.py`)
```python
# Analyze application logs
python scripts/monitoring/log_analyzer.py --logs logs/ --days 7
```

### Performance Monitoring (`monitoring/performance_mon.py`)
```python
# Monitor system performance
python scripts/monitoring/performance_mon.py --metrics cpu,memory,latency
```

## Maintenance Scripts

### Database Backup (`maintenance/backup_db.sh`)
```bash
# Backup database
./scripts/maintenance/backup_db.sh --output backups/
```

### Log Cleanup (`maintenance/cleanup_logs.sh`)
```bash
# Clean up old logs
./scripts/maintenance/cleanup_logs.sh --older-than 30d
```

### Index Updates (`maintenance/update_indices.py`)
```python
# Update database indices
python scripts/maintenance/update_indices.py --rebuild false
```

## Usage Guidelines

### Script Execution
1. **Permissions**
   ```bash
   # Make scripts executable
   chmod +x scripts/**/*.sh
   ```

2. **Environment Variables**
   ```bash
   # Set required variables
   export APP_ENV=development
   export DB_URL=postgresql://localhost:5432/teacher_bot
   ```

3. **Logging**
   ```bash
   # Enable script logging
   export SCRIPT_LOG_LEVEL=INFO
   ```

### Best Practices

1. **Error Handling**
   - Include proper error messages
   - Implement exit codes
   - Add cleanup on failure
   - Log errors appropriately

2. **Documentation**
   - Add usage instructions
   - Document parameters
   - Include examples
   - Explain prerequisites

3. **Security**
   - Validate input parameters
   - Handle sensitive data
   - Use secure connections
   - Implement timeouts

4. **Maintenance**
   - Keep scripts updated
   - Test regularly
   - Version control
   - Document changes

## Scheduling

### Cron Jobs
```bash
# Example cron entries
# Daily database backup
0 0 * * * /path/to/scripts/maintenance/backup_db.sh

# Weekly log cleanup
0 0 * * 0 /path/to/scripts/maintenance/cleanup_logs.sh
```

### Monitoring Schedule
- Health checks: Every 5 minutes
- Log analysis: Daily
- Performance monitoring: Continuous
- Index updates: Weekly

## Additional Resources

- [Automation Guide](../docs/technical/automation.md)
- [Maintenance Procedures](../docs/technical/maintenance.md)
- [Monitoring Guide](../docs/technical/monitoring.md)
- [Backup Strategies](../docs/technical/backup.md)

## Support

For script-related issues:
1. Check script documentation
2. Review logs
3. Contact DevOps team
4. Create an issue with script output 