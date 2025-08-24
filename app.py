import os
import logging
import csv
import io
from flask import Flask, render_template, request, flash, redirect, url_for, make_response
from werkzeug.middleware.proxy_fix import ProxyFix
from meal_optimizer import MealOptimizer
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

def load_foods_data():
    """Load foods data from CSV file"""
    try:
        return pd.read_csv('foods.csv')
    except Exception as e:
        logging.error(f"Error loading foods data: {e}")
        return pd.DataFrame()

def calculate_calorie_needs(age, sex, weight, height, activity_level):
    """Calculate daily calorie needs using Mifflin-St Jeor Equation"""
    try:
        age = int(age)
        weight = float(weight)
        height = float(height)
        
        # Base Metabolic Rate
        if sex.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        daily_calories = bmr * multiplier
        
        # Protein needs (0.8-1.2g per kg body weight)
        protein_needs = weight * 1.0
        
        return int(daily_calories), int(protein_needs)
    except Exception as e:
        logging.error(f"Error calculating calorie needs: {e}")
        return 2000, 60  # Default values

@app.route('/')
def index():
    """Render the input form page"""
    foods_df = load_foods_data()
    food_list = foods_df['Food'].tolist() if not foods_df.empty else []
    return render_template('index.html', food_list=food_list)

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    """Generate meal plan based on user inputs"""
    try:
        # Get form data
        age = request.form.get('age')
        sex = request.form.get('sex')
        weight = request.form.get('weight')
        height = request.form.get('height')
        activity_level = request.form.get('activity_level')
        budget = request.form.get('budget')
        dietary_preference = request.form.get('dietary_preference')
        pantry_items = request.form.getlist('pantry_items')
        
        # Validate inputs
        if not all([age, sex, weight, height, activity_level, budget, dietary_preference]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('index'))
        
        try:
            age = int(age)
            weight = float(weight)
            height = float(height)
            budget = float(budget)
        except ValueError:
            flash('Please enter valid numbers for age, weight, height, and budget.', 'error')
            return redirect(url_for('index'))
        
        if age < 1 or age > 120:
            flash('Please enter a valid age between 1 and 120.', 'error')
            return redirect(url_for('index'))
        
        if weight < 10 or weight > 300:
            flash('Please enter a valid weight between 10 and 300 kg.', 'error')
            return redirect(url_for('index'))
        
        if height < 50 or height > 250:
            flash('Please enter a valid height between 50 and 250 cm.', 'error')
            return redirect(url_for('index'))
        
        if budget < 10:
            flash('Budget must be at least ₹10 per day.', 'error')
            return redirect(url_for('index'))
        
        # Calculate nutritional needs
        calorie_needs, protein_needs = calculate_calorie_needs(age, sex, weight, height, activity_level)
        
        # Load foods data
        foods_df = load_foods_data()
        if foods_df.empty:
            flash('Error: Food database not available. Please try again later.', 'error')
            return redirect(url_for('index'))
        
        # Initialize optimizer
        optimizer = MealOptimizer(foods_df)
        
        # Generate meal plan
        result = optimizer.optimize_meal_plan(
            calorie_target=calorie_needs,
            protein_target=protein_needs,
            budget=budget,
            dietary_preference=dietary_preference,
            pantry_items=pantry_items
        )
        
        if result['status'] == 'success':
            return render_template('results.html', 
                                 meal_plan=result['meal_plan'],
                                 nutrition_summary=result['nutrition_summary'],
                                 total_cost=result['total_cost'],
                                 alternatives=result['alternatives'],
                                 user_inputs={
                                     'age': age,
                                     'sex': sex,
                                     'weight': weight,
                                     'height': height,
                                     'activity_level': activity_level,
                                     'budget': budget,
                                     'dietary_preference': dietary_preference,
                                     'calorie_needs': calorie_needs,
                                     'protein_needs': protein_needs
                                 })
        else:
            flash(result['message'], 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logging.error(f"Error generating meal plan: {e}")
        flash('An error occurred while generating your meal plan. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/export_csv')
def export_csv():
    """Export meal plan as CSV"""
    try:
        # Get meal plan data from session or form (simplified for demo)
        # In production, you'd want to store this data properly
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Meal Plan Export'])
        writer.writerow(['Meal', 'Food', 'Quantity (g)', 'Cost (₹)'])
        
        # This would be populated with actual meal plan data
        writer.writerow(['Breakfast', 'Sample Food', '100', '10'])
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=meal_plan.csv'
        
        return response
    except Exception as e:
        logging.error(f"Error exporting CSV: {e}")
        flash('Error exporting CSV. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/export_pdf')
def export_pdf():
    """Export meal plan as PDF"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#d2691e')
        )
        
        elements.append(Paragraph("Smart Indian Meal Planner", title_style))
        elements.append(Spacer(1, 12))
        
        # Add meal plan table (simplified)
        data = [
            ['Meal', 'Food', 'Quantity (g)', 'Cost (₹)'],
            ['Breakfast', 'Sample Food', '100', '10'],
            ['Lunch', 'Sample Food', '150', '15'],
            ['Snack', 'Sample Food', '50', '5'],
            ['Dinner', 'Sample Food', '120', '12']
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d2691e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=meal_plan.pdf'
        
        return response
    except Exception as e:
        logging.error(f"Error exporting PDF: {e}")
        flash('Error exporting PDF. Please try again.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {error}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
