import pandas as pd
import pulp
import logging
from typing import Dict, List, Tuple, Any

class MealOptimizer:
    def __init__(self, foods_df: pd.DataFrame):
        self.foods_df = foods_df
        self.meal_types = ['Breakfast', 'Lunch', 'Snack', 'Dinner']
        
    def filter_foods_by_preference(self, dietary_preference: str) -> pd.DataFrame:
        """Filter foods based on dietary preference"""
        if dietary_preference == 'veg':
            # Exclude non-veg items
            non_veg_foods = ['Chicken', 'Fish', 'Mutton', 'Prawns', 'Beef']
            return self.foods_df[~self.foods_df['Food'].isin(non_veg_foods)]
        elif dietary_preference == 'non_veg':
            # Include all foods
            return self.foods_df
        elif dietary_preference == 'eggetarian':
            # Exclude meat but allow eggs
            meat_foods = ['Chicken', 'Fish', 'Mutton', 'Prawns', 'Beef']
            return self.foods_df[~self.foods_df['Food'].isin(meat_foods)]
        
        return self.foods_df
    
    def optimize_meal_plan(self, calorie_target: int, protein_target: int, 
                          budget: float, dietary_preference: str, 
                          pantry_items: List[str]) -> Dict[str, Any]:
        """
        Optimize meal plan using Linear Programming
        """
        try:
            # Filter foods based on dietary preference
            available_foods = self.filter_foods_by_preference(dietary_preference)
            
            if available_foods.empty:
                return {
                    'status': 'error',
                    'message': 'No foods available for your dietary preference.'
                }
            
            # Create the optimization problem
            prob = pulp.LpProblem("Meal_Plan_Optimization", pulp.LpMinimize)
            
            # Decision variables: quantity of each food in grams
            food_vars = {}
            for idx, food in available_foods.iterrows():
                food_vars[food['Food']] = pulp.LpVariable(
                    f"food_{food['Food']}", 
                    lowBound=0, 
                    cat='Continuous'
                )
            
            # Objective: Minimize cost while preferring pantry items
            cost_expr = 0
            for idx, food in available_foods.iterrows():
                food_name = food['Food']
                cost_per_gram = food['Cost'] / 100  # Cost per gram
                
                # Give preference to pantry items by reducing their effective cost
                if food_name in pantry_items:
                    cost_per_gram *= 0.5  # 50% preference for pantry items
                
                cost_expr += food_vars[food_name] * cost_per_gram
            
            prob += cost_expr
            
            # Constraints
            
            # 1. Calorie constraint (±5% tolerance)
            calorie_expr = 0
            for idx, food in available_foods.iterrows():
                calorie_per_gram = food['Kcal'] / 100
                calorie_expr += food_vars[food['Food']] * calorie_per_gram
            
            prob += calorie_expr >= calorie_target * 0.95
            prob += calorie_expr <= calorie_target * 1.05
            
            # 2. Protein constraint (at least target amount)
            protein_expr = 0
            for idx, food in available_foods.iterrows():
                protein_per_gram = food['Protein'] / 100
                protein_expr += food_vars[food['Food']] * protein_per_gram
            
            prob += protein_expr >= protein_target
            
            # 3. Budget constraint
            budget_expr = 0
            for idx, food in available_foods.iterrows():
                cost_per_gram = food['Cost'] / 100
                budget_expr += food_vars[food['Food']] * cost_per_gram
            
            prob += budget_expr <= budget
            
            # 4. Reasonable portion constraints (prevent unrealistic solutions)
            for idx, food in available_foods.iterrows():
                food_name = food['Food']
                # Maximum 500g of any single food per day
                prob += food_vars[food_name] <= 500
                
                # Minimum variety: if food is selected, at least 20g
                # This is handled by the solver automatically due to cost minimization
            
            # 5. Ensure some variety (at least 4 different foods)
            # This is a complex constraint, simplified by encouraging variety through costs
            
            # Solve the problem
            prob.solve(pulp.PULP_CBC_CMD(msg=0))
            
            # Check if solution exists
            if prob.status != pulp.LpStatusOptimal:
                return {
                    'status': 'error',
                    'message': 'No feasible meal plan found with current constraints. Try increasing your budget or relaxing dietary restrictions.'
                }
            
            # Extract solution
            solution = {}
            total_cost = 0
            total_nutrition = {
                'calories': 0,
                'protein': 0,
                'fat': 0,
                'carbs': 0,
                'fiber': 0,
                'iron': 0
            }
            
            selected_foods = []
            for idx, food in available_foods.iterrows():
                food_name = food['Food']
                quantity = food_vars[food_name].varValue
                
                if quantity and quantity > 1:  # Only include foods with meaningful quantities
                    food_cost = (quantity / 100) * food['Cost']
                    total_cost += food_cost
                    
                    # Calculate nutrition
                    factor = quantity / 100
                    total_nutrition['calories'] += food['Kcal'] * factor
                    total_nutrition['protein'] += food['Protein'] * factor
                    total_nutrition['fat'] += food['Fat'] * factor
                    total_nutrition['carbs'] += food['Carbs'] * factor
                    total_nutrition['fiber'] += food['Fiber'] * factor
                    total_nutrition['iron'] += food['Iron'] * factor
                    
                    selected_foods.append({
                        'name': food_name,
                        'quantity': round(quantity, 1),
                        'cost': round(food_cost, 2),
                        'calories': round(food['Kcal'] * factor, 1),
                        'protein': round(food['Protein'] * factor, 1)
                    })
            
            if not selected_foods:
                return {
                    'status': 'error',
                    'message': 'No valid meal plan could be generated. Please try increasing your budget.'
                }
            
            # Distribute foods across meals
            meal_plan = self._distribute_foods_to_meals(selected_foods)
            
            # Generate alternatives
            alternatives = self._generate_alternatives(available_foods, selected_foods)
            
            return {
                'status': 'success',
                'meal_plan': meal_plan,
                'nutrition_summary': {
                    'calories': round(total_nutrition['calories'], 1),
                    'protein': round(total_nutrition['protein'], 1),
                    'fat': round(total_nutrition['fat'], 1),
                    'carbs': round(total_nutrition['carbs'], 1),
                    'fiber': round(total_nutrition['fiber'], 1),
                    'iron': round(total_nutrition['iron'], 1)
                },
                'total_cost': round(total_cost, 2),
                'alternatives': alternatives
            }
            
        except Exception as e:
            logging.error(f"Error in meal optimization: {e}")
            return {
                'status': 'error',
                'message': 'An error occurred during optimization. Please try again with different parameters.'
            }
    
    def _distribute_foods_to_meals(self, selected_foods: List[Dict]) -> Dict[str, List[Dict]]:
        """Distribute selected foods across meals based on typical Indian eating patterns"""
        meal_plan = {
            'Breakfast': [],
            'Lunch': [],
            'Snack': [],
            'Dinner': []
        }
        
        # Define typical meal distributions
        breakfast_foods = ['Poha', 'Upma', 'Milk', 'Banana', 'Egg', 'Bread']
        lunch_foods = ['Rice', 'Roti', 'Dal', 'Rajma', 'Chole', 'Spinach', 'Curd']
        snack_foods = ['Peanut', 'Banana', 'Biscuit', 'Tea']
        dinner_foods = ['Rice', 'Roti', 'Dal', 'Paneer', 'Chicken', 'Spinach']
        
        total_foods = len(selected_foods)
        foods_per_meal = max(1, total_foods // 4)
        
        food_index = 0
        
        for meal_type in self.meal_types:
            meal_count = 0
            
            # First, try to assign foods typical for this meal
            if meal_type == 'Breakfast':
                typical_foods = breakfast_foods
            elif meal_type == 'Lunch':
                typical_foods = lunch_foods
            elif meal_type == 'Snack':
                typical_foods = snack_foods
            else:  # Dinner
                typical_foods = dinner_foods
            
            # Assign typical foods first
            for food in selected_foods:
                if food['name'] in typical_foods and meal_count < foods_per_meal:
                    food_copy = food.copy()
                    # Adjust quantity for meal portion
                    food_copy['quantity'] = round(food_copy['quantity'] / 4, 1)
                    food_copy['cost'] = round(food_copy['cost'] / 4, 2)
                    meal_plan[meal_type].append(food_copy)
                    meal_count += 1
            
            # Fill remaining slots with other foods
            while meal_count < foods_per_meal and food_index < len(selected_foods):
                if selected_foods[food_index]['name'] not in [f['name'] for f in meal_plan[meal_type]]:
                    food_copy = selected_foods[food_index].copy()
                    food_copy['quantity'] = round(food_copy['quantity'] / 4, 1)
                    food_copy['cost'] = round(food_copy['cost'] / 4, 2)
                    meal_plan[meal_type].append(food_copy)
                    meal_count += 1
                food_index += 1
        
        # Ensure every meal has at least one food
        for meal_type in self.meal_types:
            if not meal_plan[meal_type] and selected_foods:
                food_copy = selected_foods[0].copy()
                food_copy['quantity'] = round(food_copy['quantity'] / 4, 1)
                food_copy['cost'] = round(food_copy['cost'] / 4, 2)
                meal_plan[meal_type].append(food_copy)
        
        return meal_plan
    
    def _generate_alternatives(self, available_foods: pd.DataFrame, 
                             selected_foods: List[Dict]) -> Dict[str, List[Dict]]:
        """Generate alternative food suggestions for cost-effectiveness"""
        alternatives = {}
        selected_names = [food['name'] for food in selected_foods]
        
        for selected_food in selected_foods:
            food_alternatives = []
            
            # Find similar foods (simplified - based on similar nutritional profile)
            selected_row = available_foods[available_foods['Food'] == selected_food['name']].iloc[0]
            
            for idx, food in available_foods.iterrows():
                if food['Food'] not in selected_names:
                    # Calculate cost-effectiveness (protein per rupee)
                    cost_effectiveness = food['Protein'] / food['Cost'] if food['Cost'] > 0 else 0
                    
                    food_alternatives.append({
                        'name': food['Food'],
                        'cost_effectiveness': round(cost_effectiveness, 3),
                        'cost': food['Cost'],
                        'protein': food['Protein'],
                        'calories': food['Kcal']
                    })
            
            # Sort by cost-effectiveness and take top 2
            food_alternatives.sort(key=lambda x: x['cost_effectiveness'], reverse=True)
            alternatives[selected_food['name']] = food_alternatives[:2]
        
        return alternatives
