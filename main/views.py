from django.shortcuts import render
from .models import SearchHistory
import requests

API_KEY = "25af943d7be582a2f47a0de28c706844"

def weather(request):
    weather = None
    errorMessage = None

    # Get recent searches
    recent_searches = SearchHistory.objects.order_by('-searched_at')[:5]

    if request.method == "POST":
        city = request.POST.get('city', '').strip()

        if not city:
            errorMessage = "Please enter a city name."
            return render(request, "main/index.html", {
                "weather": weather,
                "errorMessage": errorMessage,
                "recent_searches": recent_searches
            })

        try:
            # 🌍 Step 1: Geocoding API (fix spelling + get lat/lon)
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
            geo_response = requests.get(geo_url, timeout=5)
            geo_data = geo_response.json()

            if not geo_data:
                errorMessage = f"City '{city}' not found. Please check spelling."
            else:
                lat = geo_data[0]['lat']
                lon = geo_data[0]['lon']
                corrected_city = geo_data[0]['name']

                # 🌦 Step 2: Weather API using lat/lon
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
                response = requests.get(weather_url, timeout=5)
                data = response.json()

                if response.status_code == 200:
                    weather = {
                        'city': f"{corrected_city}, {data['sys']['country']}",
                        'temperature': round(data['main']['temp'], 1),
                        'feels_like': round(data['main']['feels_like'], 1),
                        'humidity': data['main']['humidity'],
                        'pressure': data['main']['pressure'],
                        'description': data['weather'][0]['description'].title(),
                        'icon': data['weather'][0]['icon'],
                        'wind': data.get('wind', {}).get('speed', 0),
                    }

                    # 💾 Save (avoid duplicates)
                    if not SearchHistory.objects.filter(city_name__iexact=corrected_city).exists():
                        SearchHistory.objects.create(
                            city_name=corrected_city,
                            temperature=data['main']['temp'],
                            humidity=data['main']['humidity'],
                            pressure=data['main']['pressure'],
                            description=data['weather'][0]['description'].title()
                        )

                    # Refresh recent searches
                    recent_searches = SearchHistory.objects.order_by('-searched_at')[:5]

                else:
                    errorMessage = "Unable to fetch weather data."

        except requests.RequestException:
            errorMessage = "Network error. Please try again later."

    return render(request, "main/index.html", {
        "weather": weather,
        "errorMessage": errorMessage,
        "recent_searches": recent_searches
    })