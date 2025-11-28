def generate_recommendations(data):
    """
    Generates personalized recommendations
    """
    recommendations = {
        0: "You're in the 'Low Consumption' group. Maintain good habits!",
        1: "You're in the 'Moderate Consumption' group. Consider turning off appliances when not in use.",
        2: "You're in the 'High Consumption' group. Reduce usage during peak hours and switch to energy-efficient appliances."
    }
    data['Recommendation'] = data['Cluster'].map(recommendations)
    return data