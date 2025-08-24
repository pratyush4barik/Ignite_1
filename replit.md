# Smart Indian Meal Planner

## Overview

The Smart Indian Meal Planner is a Flask web application that uses linear programming optimization to generate personalized daily meal plans for Indian cuisine. The application calculates users' nutritional needs based on their physical characteristics and activity level, then optimizes food selection to meet calorie and protein targets while staying within budget constraints and respecting dietary preferences.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive design
- **Styling**: Custom CSS with warm, earthy color scheme (orange, green, cream) optimized for mobile-first design
- **JavaScript**: Vanilla JavaScript for form validation, real-time calorie estimation, and interactive elements
- **UI Components**: Card-based layout for meal display, sidebar form for inputs, animated transitions

### Backend Architecture
- **Web Framework**: Flask with ProxyFix middleware for deployment compatibility
- **Optimization Engine**: PuLP library for linear programming-based meal optimization
- **Data Processing**: Pandas for CSV data manipulation and analysis
- **PDF Generation**: ReportLab for generating downloadable meal plan reports
- **Session Management**: Flask sessions with configurable secret key

### Core Business Logic
- **Calorie Calculation**: Mifflin-St Jeor Equation for determining daily calorie needs based on age, sex, weight, height, and activity level
- **Meal Optimization**: Linear programming solver that optimizes food selection across 4 meal types (Breakfast, Lunch, Snack, Dinner) to meet nutritional targets within budget
- **Dietary Filtering**: Support for vegetarian, non-vegetarian, and eggetarian preferences with food exclusion rules
- **Pantry Integration**: Preference weighting for user-selected pantry items

### Data Storage
- **Food Database**: CSV file containing Indian food items with nutritional data (calories, protein, fat, carbs, fiber, iron) and cost per 100g
- **No Persistent Storage**: Application processes data in-memory without storing user information

### Export Functionality
- **CSV Export**: Meal plan data export for spreadsheet analysis
- **PDF Export**: Formatted meal plan reports with nutrition summaries and cost breakdowns

## External Dependencies

### Python Libraries
- **Flask**: Web framework for handling HTTP requests and responses
- **PuLP**: Linear programming library for optimization algorithms
- **Pandas**: Data manipulation and analysis for CSV processing
- **ReportLab**: PDF generation library for meal plan reports
- **Werkzeug**: WSGI utilities including ProxyFix middleware

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design and UI components
- **Font Awesome 6.4.0**: Icon library for visual elements
- **CDN Dependencies**: External hosting for CSS and JavaScript libraries

### Data Sources
- **foods.csv**: Local CSV file containing Indian food nutritional database with cost information

### Deployment Requirements
- **Environment Variables**: SESSION_SECRET for Flask session security
- **File System**: Read access to CSV data files
- **Network**: HTTP server capabilities for web serving