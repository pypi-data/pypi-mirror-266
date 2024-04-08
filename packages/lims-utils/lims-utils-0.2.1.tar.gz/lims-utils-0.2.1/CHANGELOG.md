# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2024-04-05

### Changed

- Updated table models to schema version 4.1.0

## [0.2.0] - 2024-02-14

### Added

- `ProposalReference` model and `parse_proposal`, for parsing proposal reference strings
- `Database()` now exposes `paginate`, for inserting pagination into queries, and `fast_count`, for counting total items rapidly
- `Settings()`, which provides a base settings model that reads from JSON files

### Changed

- Updated table models

## [0.1.2] - 2024-02-08

### Removed

- Unused dependencies (MySQL related dependencies)

### Changed

- Updated table models
