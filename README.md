# 🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

A comprehensive cricket analytics dashboard that integrates live data from the Cricbuzz API with a SQL database to create an interactive web application.

## 🎯 Project Overview

**Cricbuzz LiveStats** delivers a complete solution for cricket data management and analysis with the following capabilities:

- ⚡ **Real-time Match Updates** - Live scores and detailed match information
- 📊 **Player Statistics** - Top performers and detailed analytics
- 🔍 **SQL-Driven Analytics** - 25+ advanced SQL queries for insights
- 🛠️ **CRUD Operations** - Full database management capabilities
- 📈 **Data Visualization** - Beautiful charts and interactive dashboards

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone or Extract the Project**
   ```bash
   cd d:\test\cricbuzz_app
   ```

2. **Create Virtual Environment** (Optional but Recommended)
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key**
   
   Create a `.streamlit/secrets.toml` file:
   ```toml
   RAPIDAPI_KEY = "your_rapidapi_key_here"
   ```
   
   Get your RapidAPI key from: https://rapidapi.com/api-sports/api/cricbuzz-cricket

### Running the Application

```bash
streamlit run main.py
```

The app will open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
cricbuzz_app/
├── main.py                          # Main Streamlit app entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── utils/
│   ├── api_client.py               # Cricbuzz API integration
│   └── db_connection.py            # Database connection & schema
├── pages/
│   ├── home.py                     # Home page
│   ├── live_matches.py             # Real-time match updates
│   ├── player_stats.py             # Player statistics
│   ├── sql_analytics.py            # SQL queries & analytics
│   └── crud_operations.py          # CRUD operations
└── data/
    └── cricbuzz.db                 # SQLite database (auto-created)
```

## 🌟 Features

### 1. 🏠 Home Page
- Project overview and documentation
- Business use cases
- Technical stack information
- Quick navigation links
- Project statistics

### 2. ⚡ Live Matches
- View live, upcoming, and recent matches
- Filter by match type and series
- Detailed scorecard information
- Match statistics and summaries
- Auto-refresh capability

### 3. 📊 Player Statistics
- Top 10 batsmen rankings
- Top bowlers analytics
- Player performance comparison
- Strike rate and average metrics
- Detailed player profiles

### 4. 🔍 SQL Analytics
- 25 SQL practice queries:
  - **Beginner Level (1-8)**: Basic SELECT, WHERE, GROUP BY
  - **Intermediate Level (9-16)**: JOINs, subqueries, aggregations
  - **Advanced Level (17-25)**: Window functions, CTEs, complex analytics
- Query execution and result display
- CSV export functionality
- Query templates and documentation

### 5. 🛠️ CRUD Operations
- **Players**: Create, Read, Update, Delete player records
- **Matches**: Add and manage cricket matches
- **Venues**: Manage cricket venues
- **Database Summary**: View statistics and top performers
- **Data Export**: Backup database as CSV

## 📊 Database Schema

### Tables

1. **players**
   - player_id (PK)
   - player_name
   - country
   - role
   - batting_style, bowling_style
   - total_runs, total_wickets
   - batting_average, bowling_average

2. **matches**
   - match_id (PK)
   - match_description
   - team1, team2
   - match_format
   - venue_id (FK)
   - match_date
   - winning_team, victory_margin, victory_type
   - toss_winner, toss_decision

3. **venues**
   - venue_id (PK)
   - venue_name
   - city, country
   - capacity

4. **innings**
   - innings_id (PK)
   - match_id (FK)
   - batting_team, bowling_team
   - total_runs, total_wickets, total_overs

5. **batsmen**
   - batsman_id (PK)
   - innings_id (FK)
   - player_id (FK)
   - batting_position
   - runs_scored, balls_faced
   - fours, sixes
   - strike_rate, dismissal_type

6. **bowlers**
   - bowler_id (PK)
   - innings_id (FK)
   - player_id (FK)
   - overs_bowled, maidens
   - runs_conceded, wickets_taken
   - economy_rate

## 🔑 API Integration

### Cricbuzz API Endpoints

- `/matches/v1/live` - Get live matches
- `/matches/v1/upcoming` - Get upcoming matches
- `/matches/v1/recent` - Get recent matches
- `/mcenter/v1/{matchId}/scard` - Get detailed scorecard

### Configuration

Set your RapidAPI key in `.streamlit/secrets.toml`:
```toml
RAPIDAPI_KEY = "your_key_here"
```

## 🧮 SQL Queries Summary

### Beginner Queries (1-8)
1. Find players by country
2. Recent matches with venues
3. Top run scorers
4. Large capacity venues
5. Team wins count
6. Players by role
7. Highest scores by format
8. Series in 2024

### Intermediate Queries (9-16)
9. All-rounder performance
10. Recent match details
11. Multi-format player stats
12. Home vs away analysis
13. Batting partnerships
14. Bowling venue analysis
15. Close match performance
16. Year-over-year trends

### Advanced Queries (17-25)
17. Toss advantage analysis
18. Economical bowlers
19. Consistent batsmen
20. Multi-format analysis
21. Player ranking system
22. Head-to-head predictions
23. Player form analysis
24. Partnership success
25. Career trajectory analysis

## 🔒 Security

### API Key Management
- Store API keys in `.streamlit/secrets.toml`
- Never commit keys to version control
- Use environment variables in production

### Database Security
- Default SQLite for development
- Switch to PostgreSQL for production
- Use parameterized queries (built-in)
- Implement role-based access control

## 📋 Development Guidelines

### Coding Standards
- Follow PEP 8 Python style guidelines
- Use type hints for better code clarity
- Add docstrings to all functions
- Keep functions focused and modular

### Error Handling
- Implement try-except blocks
- Log errors appropriately
- Provide user-friendly error messages
- Handle API timeouts gracefully

### Data Validation
- Validate user inputs
- Check data types
- Handle NULL values
- Implement data quality checks

## 🚀 Deployment

### Local Development
```bash
streamlit run main.py
```

### Production Deployment (Streamlit Cloud)
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Configure secrets in Streamlit Cloud dashboard
4. Deploy

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "main.py"]
```

## 📚 Documentation Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Cricbuzz API Documentation](https://rapidapi.com/api-sports/api/cricbuzz-cricket)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python Documentation](https://docs.python.org/3/)

## 🎓 Learning Outcomes

By completing this project, you'll gain expertise in:

1. **Web Development**
   - Building interactive web applications with Streamlit
   - UI/UX design principles
   - Navigation and page management

2. **API Integration**
   - RESTful API consumption
   - JSON data parsing
   - Error handling and rate limiting

3. **Database Management**
   - Schema design
   - SQL query optimization
   - Data normalization

4. **Data Analysis**
   - Statistical analysis
   - Data visualization
   - Performance metrics

5. **Python Development**
   - PEP 8 compliance
   - Code modularity
   - Documentation practices

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 Project Guidelines

- **Timeline**: 14 days from assignment
- **Submission**: Source code, database schema, documentation
- **Testing**: Test all features before submission
- **Documentation**: Clear comments and docstrings required
- **Version Control**: Use Git for tracking changes

## 👥 Project Team

- **Created By**: Subhash Govindharaj
- **Verified By**: Shadiya P P
- **Approved By**: Nehlath Harmain

## 📞 Support

### Project Doubt Clarification Session
- **Timing**: Monday-Saturday (3:30 PM - 4:30 PM)
- **Book Before**: 12:00 PM on the same day
- **Link**: [Book Session](https://forms.gle/XC553oSbMJ2GcfugLIVE)

### Live Evaluation Session
- **Timing**: Monday-Saturday (5:30 PM - 7:00 PM)
- **Available**: Saturday (after 2 PM) & Sunday
- **Link**: [Book Session](https://forms.gle/1m2Gsro41fLtZurRA)

## 📄 License

This project is for educational purposes.

## 🎯 Project Stats

- **SQL Queries**: 25+ (all difficulty levels)
- **API Endpoints**: 5+ (real-time data)
- **Database Tables**: 6 (normalized schema)
- **CRUD Operations**: Full Create, Read, Update, Delete
- **Lines of Code**: 2000+
- **Documentation**: Comprehensive

## 🔄 Version History

- **v1.0** (2025-11-11): Initial release
  - Complete Cricbuzz API integration
  - 25 SQL queries implemented
  - Full CRUD operations
  - Multi-page Streamlit application
  - Database schema and utilities

---

**Happy Coding! 🏏📊**

For more information, visit the project documentation or contact the project team.
#   C r i c b u z z  
 #   C r i c b u z z  
 