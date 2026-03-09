# Metriq Architecture

Metriq is a personal health analytics platform designed to aggregate
nutrition, activity, and biometric data.

## Data Sources

MyFitnessPal → Nutrition
Apple Health → Biometrics & Activity
MapMyRun → Walking / Dog Walks

## Pipeline

Sources → Importers → Normalized Database → Analytics Engine → FastAPI

## Core Tables

nutrition_log
activity_log
biometrics_log
metrics_log

## Analytics

- 7 day calorie averages
- activity averages
- estimated fat loss
- weight trend

7700 kcal ≈ 1kg fat
